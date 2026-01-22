"""Scenario D: Database contention stress test.

This test simulates realistic database contention by having multiple threads
compete for SQLite locks while a background thread holds exclusive locks.

Default parameters are tuned for graceful recovery under realistic contention:
- db_timeout: 5.0s - Allow operations to wait for locks to be released
- retry_count: 10 - Sufficient retries to handle transient lock contention
- retry_delay: 0.1s - Reasonable backoff between retry attempts
- lock_idle_s: 0.15s - Breathing room between lock cycles

These defaults ensure that under normal contention levels, all operations
should eventually succeed through retry logic. Set STRESS_DB_EXPECT_RECOVERY=1
to assert zero deadlock-like failures.

For extreme stress testing (documenting system breaking points), reduce
timeouts and retries while keeping STRESS_DB_EXPECT_RECOVERY=0.
"""

from __future__ import annotations

import json
import os
import random
import sqlite3
import threading
import time
from pathlib import Path

import pytest

from tests.stress.utils import (
    DBLockSimulator,
    IntegrityChecker,
    MetricsCollector,
    RequestSpec,
    concurrent_executor,
)

pytestmark = pytest.mark.stress

if os.environ.get("RUN_STRESS_TESTS") != "1":
    pytest.skip(
        "RUN_STRESS_TESTS=1 is required for stress tests.", allow_module_level=True
    )


def _is_lock_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "locked" in message or "busy" in message


def _attempt_db_write(
    db_path: Path,
    *,
    file_path: str,
    retries: int,
    retry_delay: float,
    timeout: float,
    metadata: dict | None = None,
) -> tuple[bool, int, int, str | None]:
    lock_errors = 0
    retries_used = 0
    while True:
        try:
            conn = sqlite3.connect(db_path, timeout=timeout)
            try:
                conn.execute(
                    "INSERT INTO edit_provenance (file_path, commit_sha, source, metadata) VALUES (?, ?, ?, ?)",
                    (file_path, None, "stress", json.dumps(metadata or {})),
                )
                conn.commit()
            finally:
                conn.close()
            return True, lock_errors, retries_used, None
        except sqlite3.OperationalError as exc:
            if _is_lock_error(exc):
                lock_errors += 1
                if retries_used >= retries:
                    return False, lock_errors, retries_used, str(exc)
                retries_used += 1
                time.sleep(retry_delay)
                continue
            return False, lock_errors, retries_used, str(exc)
        except Exception as exc:  # noqa: BLE001 - surfaced in metrics
            return False, lock_errors, retries_used, str(exc)


def test_database_contention(
    tmp_path: Path,
    note_generator,
    stress_client,
    metrics_collector: MetricsCollector,
):
    data_dir_env = os.environ.get("STRESS_DATA_DIR")
    if not data_dir_env:
        pytest.skip("STRESS_DATA_DIR must be set for DB contention stress test.")

    data_dir = Path(data_dir_env)
    state_db = data_dir / ".gardener" / "state.db"
    if not state_db.exists():
        try:
            from db import init_db

            init_db()
        except Exception as exc:  # noqa: BLE001 - best-effort init
            pytest.skip(f"Failed to initialize state DB: {exc}")

    worker_count = int(os.environ.get("STRESS_DB_THREADS", "100"))
    duration_s = float(os.environ.get("STRESS_DB_DURATION_S", "60"))
    lock_hold_s = float(os.environ.get("STRESS_DB_LOCK_HOLD_S", "0.25"))
    lock_idle_s = float(os.environ.get("STRESS_DB_LOCK_IDLE_S", "0.15"))
    lock_cycles = int(os.environ.get("STRESS_DB_LOCK_CYCLES", "200"))
    db_timeout = float(os.environ.get("STRESS_DB_TIMEOUT_S", "5.0"))
    retry_count = int(os.environ.get("STRESS_DB_RETRY_COUNT", "10"))
    retry_delay = float(os.environ.get("STRESS_DB_RETRY_DELAY_S", "0.1"))
    expect_recovery = os.environ.get("STRESS_DB_EXPECT_RECOVERY") == "1"

    note_pool_dir = tmp_path / "note-pool"
    manifest = note_generator(
        count=200,
        min_kb=1,
        max_kb=5,
        out_dir=note_pool_dir,
        seed=911,
    )
    note_contents = [
        (note_pool_dir / entry.filename).read_text(encoding="utf-8")
        for entry in manifest
    ]

    op_counts = {"inbox": 0, "trigger": 0, "snapshot": 0, "db_write": 0}
    db_stats = {
        "writes": 0,
        "lock_errors": 0,
        "retry_success": 0,
        "retry_attempts": 0,
        "failed": 0,
        "deadlock_like": 0,
        "other_errors": 0,
    }
    lock_stats = {"lock_acquire_errors": 0, "lock_cycles": 0}
    lock = threading.Lock()

    def _record_op(op: str) -> None:
        with lock:
            op_counts[op] += 1

    def _record_db(
        *,
        success: bool,
        lock_errors: int,
        retries_used: int,
        error: str | None,
    ) -> None:
        with lock:
            db_stats["writes"] += 1
            db_stats["lock_errors"] += lock_errors
            db_stats["retry_attempts"] += retries_used
            if retries_used and success:
                db_stats["retry_success"] += 1
            if not success:
                db_stats["failed"] += 1
                if error and _is_lock_error(Exception(error)):
                    db_stats["deadlock_like"] += 1
                else:
                    db_stats["other_errors"] += 1

    stop_time = time.time() + duration_s

    lock_simulator = DBLockSimulator(state_db, timeout=db_timeout)

    def _lock_loop() -> None:
        cycles = 0
        while time.time() < stop_time and cycles < lock_cycles:
            try:
                lock_simulator.hold_for(lock_hold_s)
            except sqlite3.OperationalError:
                with lock:
                    lock_stats["lock_acquire_errors"] += 1
            finally:
                lock_simulator.release()
            cycles += 1
            if lock_idle_s > 0:
                time.sleep(lock_idle_s)
        with lock:
            lock_stats["lock_cycles"] += cycles

    snapshot_dir = data_dir / "meta"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _record_http(spec: RequestSpec) -> None:
        result = stress_client.request(spec)
        with lock:
            metrics_collector.record(result)

    def _snapshot_action(worker_id: int, counter: int) -> None:
        snapshot_path = snapshot_dir / f"stress-snapshot-{worker_id}.md"
        with snapshot_path.open("a", encoding="utf-8") as handle:
            handle.write(f"snapshot {worker_id}-{counter} {time.time()}\n")
        _record_http(
            RequestSpec(
                method="POST",
                path="/api/snapshot",
                json_body={"message": f"Stress snapshot {worker_id}-{counter}"},
            )
        )

    def _inbox_action(rng: random.Random) -> None:
        content = rng.choice(note_contents)
        _record_http(
            RequestSpec(
                method="POST", path="/api/inbox", json_body={"content": content}
            )
        )

    def _trigger_action() -> None:
        _record_http(RequestSpec(method="POST", path="/api/trigger-gardener"))

    def _db_write_action(worker_id: int, counter: int) -> None:
        success, lock_errors, retries_used, error = _attempt_db_write(
            state_db,
            file_path=f"meta/stress-db-{worker_id}-{counter}.md",
            retries=retry_count,
            retry_delay=retry_delay,
            timeout=db_timeout,
            metadata={"worker": worker_id, "counter": counter},
        )
        _record_db(
            success=success,
            lock_errors=lock_errors,
            retries_used=retries_used,
            error=error,
        )

    def _worker(seed: int) -> None:
        rng = random.Random(seed)
        counter = 0
        while time.time() < stop_time:
            roll = rng.random()
            if roll < 0.45:
                _record_op("inbox")
                _inbox_action(rng)
            elif roll < 0.65:
                _record_op("trigger")
                _trigger_action()
            elif roll < 0.85:
                _record_op("snapshot")
                _snapshot_action(seed, counter)
            else:
                _record_op("db_write")
                _db_write_action(seed, counter)
            counter += 1

    start = time.perf_counter()
    lock_thread = threading.Thread(target=_lock_loop, daemon=True)
    lock_thread.start()
    with concurrent_executor(worker_count) as executor:
        futures = [executor.submit(_worker, seed) for seed in range(worker_count)]
        for future in futures:
            future.result()
    lock_thread.join()
    elapsed_s = time.perf_counter() - start

    summary = metrics_collector.summary()
    summary["elapsed_s"] = elapsed_s
    summary["operations"] = op_counts
    summary["db_contention"] = db_stats
    summary["db_locks"] = lock_stats
    integrity = IntegrityChecker(data_dir)
    summary["integrity"] = integrity.report()
    summary["db_integrity"] = integrity.db_integrity_check(state_db)

    metrics_path = os.environ.get("STRESS_METRICS_PATH")
    if metrics_path:
        payload = {"scenario": "D", "summary": summary}
        Path(metrics_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if expect_recovery:
        assert summary["db_integrity"] in ("ok", None)
        assert summary["db_contention"]["deadlock_like"] == 0
        assert summary["ok"] > 0
