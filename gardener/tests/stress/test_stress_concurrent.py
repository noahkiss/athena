"""Scenario B: Sustained concurrent operations stress test."""

from __future__ import annotations

import json
import math
import os
import random
import threading
import time
from functools import partial
from pathlib import Path

import pytest

from tests.stress.utils import IntegrityChecker, RequestSpec, concurrent_executor

pytestmark = pytest.mark.stress

if os.environ.get("RUN_STRESS_TESTS") != "1":
    pytest.skip(
        "RUN_STRESS_TESTS=1 is required for stress tests.", allow_module_level=True
    )


def test_sustained_concurrent_operations(
    tmp_path: Path,
    note_generator,
    stress_client,
    metrics_collector,
):
    duration_s = int(os.environ.get("STRESS_DURATION_S", "600"))
    submit_threads = int(os.environ.get("STRESS_SUBMIT_THREADS", "20"))
    browse_threads = int(os.environ.get("STRESS_BROWSE_THREADS", "10"))
    ask_threads = int(os.environ.get("STRESS_ASK_THREADS", "10"))
    refine_threads = int(os.environ.get("STRESS_REFINE_THREADS", "5"))
    submit_rps = float(os.environ.get("STRESS_SUBMIT_RPS", "5"))
    ai_call_multiplier = float(os.environ.get("STRESS_AI_CALL_MULTIPLIER", "3"))

    note_pool_dir = tmp_path / "note-pool"
    manifest = note_generator(
        count=200,
        min_kb=1,
        max_kb=10,
        out_dir=note_pool_dir,
        seed=123,
    )
    note_paths = [note_pool_dir / entry.filename for entry in manifest]

    questions = [
        "What are the latest project updates?",
        "Summarize recent journal entries.",
        "Any notes about database performance?",
        "What follow-ups are pending?",
    ]
    refine_snippets = [
        "Outline the next steps for the deployment.",
        "Summarize meeting notes and action items.",
        "Draft a brief status update.",
    ]

    data_dir = os.environ.get("STRESS_DATA_DIR")
    baseline_integrity = None
    if data_dir:
        baseline_integrity = IntegrityChecker(Path(data_dir)).report()

    ask_interval = 0.8
    refine_interval = 1.2

    expected_ask = 0
    expected_refine = 0
    expected_total = 0
    ai_call_cap = None
    if ai_call_multiplier > 0:
        if ask_threads > 0:
            expected_ask = int((math.ceil(duration_s / ask_interval) + 1) * ask_threads)
        if refine_threads > 0:
            expected_refine = int(
                (math.ceil(duration_s / refine_interval) + 1) * refine_threads
            )
        expected_total = expected_ask + expected_refine
        if expected_total > 0:
            ai_call_cap = int(math.ceil(expected_total * ai_call_multiplier))

    stop_time = time.time() + duration_s
    stop_event = threading.Event()
    lock = threading.Lock()
    ai_lock = threading.Lock()
    ask_count = 0
    refine_count = 0
    cap_triggered = False
    cap_reason = None

    def _reserve_ai_call(kind: str) -> bool:
        nonlocal ask_count, refine_count, cap_triggered, cap_reason
        with ai_lock:
            if stop_event.is_set():
                return False
            total = ask_count + refine_count
            if ai_call_cap is not None and total + 1 > ai_call_cap:
                cap_triggered = True
                cap_reason = f"ai_call_cap_exceeded total={total} cap={ai_call_cap}"
                stop_event.set()
                return False
            if kind == "ask":
                ask_count += 1
            else:
                refine_count += 1
        return True

    def _record(result):
        with lock:
            metrics_collector.record(result)

    per_thread_rps = submit_rps / submit_threads if submit_threads > 0 else 0.0
    submit_interval = 1.0 / per_thread_rps if per_thread_rps > 0 else 0.0

    def _submit_worker(seed: int):
        rng = random.Random(seed)
        while time.time() < stop_time and not stop_event.is_set():
            path = rng.choice(note_paths)
            content = path.read_text(encoding="utf-8")
            spec = RequestSpec(
                method="POST", path="/api/inbox", json_body={"content": content}
            )
            _record(stress_client.request(spec))
            if submit_interval:
                time.sleep(submit_interval)

    def _browse_worker(seed: int):
        rng = random.Random(seed)
        paths = ["/api/browse", "/api/browse/projects", "/api/browse/journal"]
        while time.time() < stop_time and not stop_event.is_set():
            spec = RequestSpec(method="GET", path=rng.choice(paths))
            _record(stress_client.request(spec))
            time.sleep(0.5)

    def _ask_worker(seed: int):
        rng = random.Random(seed)
        while time.time() < stop_time and not stop_event.is_set():
            if not _reserve_ai_call("ask"):
                break
            spec = RequestSpec(
                method="POST",
                path="/api/ask",
                json_body={"question": rng.choice(questions)},
            )
            _record(stress_client.request(spec))
            time.sleep(ask_interval)

    def _refine_worker(seed: int):
        rng = random.Random(seed)
        while time.time() < stop_time and not stop_event.is_set():
            if not _reserve_ai_call("refine"):
                break
            spec = RequestSpec(
                method="POST",
                path="/api/refine",
                json_body={"content": rng.choice(refine_snippets)},
            )
            _record(stress_client.request(spec))
            time.sleep(refine_interval)

    workers = []
    workers.extend(partial(_submit_worker, seed) for seed in range(submit_threads))
    workers.extend(
        partial(_browse_worker, seed + 1000) for seed in range(browse_threads)
    )
    workers.extend(partial(_ask_worker, seed + 2000) for seed in range(ask_threads))
    workers.extend(
        partial(_refine_worker, seed + 3000) for seed in range(refine_threads)
    )

    start = time.perf_counter()
    with concurrent_executor(len(workers)) as executor:
        futures = [executor.submit(worker) for worker in workers]
        for future in futures:
            future.result()
    elapsed_s = time.perf_counter() - start

    summary = metrics_collector.summary()
    summary["elapsed_s"] = elapsed_s
    summary["ai_calls"] = {
        "ask": ask_count,
        "refine": refine_count,
        "total": ask_count + refine_count,
    }
    summary["ai_call_expected"] = {
        "ask": expected_ask,
        "refine": expected_refine,
        "total": expected_total,
    }
    summary["ai_call_cap"] = ai_call_cap
    summary["ai_call_cap_multiplier"] = ai_call_multiplier
    summary["ai_call_cap_triggered"] = cap_triggered
    if cap_triggered:
        summary["ai_call_cap_reason"] = cap_reason
    submitted_total = sum(
        1 for result in metrics_collector.results if result.path == "/api/inbox"
    )
    submitted_ok = sum(
        1
        for result in metrics_collector.results
        if result.path == "/api/inbox" and result.ok
    )
    summary["submitted_total"] = submitted_total
    summary["submitted_ok"] = submitted_ok

    if data_dir:
        integrity = IntegrityChecker(Path(data_dir))
        summary["integrity"] = integrity.report()
        summary["db_integrity"] = integrity.db_integrity_check(
            Path(data_dir) / ".gardener" / "state.db"
        )
        baseline = baseline_integrity or {"inbox_count": 0, "archive_count": 0}
        inbox_new = summary["integrity"]["inbox_count"] - baseline["inbox_count"]
        archive_new = summary["integrity"]["archive_count"] - baseline["archive_count"]
        stored_new = inbox_new + archive_new
        missing = max(0, submitted_ok - stored_new)
        summary["data_loss"] = {
            "inbox_new": inbox_new,
            "archive_new": archive_new,
            "stored_new": stored_new,
            "submitted_ok": submitted_ok,
            "missing": missing,
        }
        if os.environ.get("STRESS_EXPECT_ARCHIVE") == "1":
            assert missing == 0

    metrics_path = os.environ.get("STRESS_METRICS_PATH")
    if metrics_path:
        payload = {"scenario": "B", "summary": summary}
        Path(metrics_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if cap_triggered:
        pytest.fail(f"AI call cap exceeded: {cap_reason}")
    assert summary["errors"] == 0
