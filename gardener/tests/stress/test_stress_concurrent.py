"""Scenario B: Sustained concurrent operations stress test."""

from __future__ import annotations

import json
import os
import random
from functools import partial
import threading
import time
from pathlib import Path

import pytest

from tests.stress.utils import IntegrityChecker, RequestSpec, concurrent_executor


pytestmark = pytest.mark.stress

if os.environ.get("RUN_STRESS_TESTS") != "1":
    pytest.skip("RUN_STRESS_TESTS=1 is required for stress tests.", allow_module_level=True)


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

    stop_time = time.time() + duration_s
    lock = threading.Lock()
    def _record(result):
        with lock:
            metrics_collector.record(result)

    per_thread_rps = submit_rps / submit_threads if submit_threads > 0 else 0.0
    submit_interval = 1.0 / per_thread_rps if per_thread_rps > 0 else 0.0

    def _submit_worker(seed: int):
        rng = random.Random(seed)
        while time.time() < stop_time:
            path = rng.choice(note_paths)
            content = path.read_text(encoding="utf-8")
            spec = RequestSpec(method="POST", path="/api/inbox", json_body={"content": content})
            _record(stress_client.request(spec))
            if submit_interval:
                time.sleep(submit_interval)

    def _browse_worker(seed: int):
        rng = random.Random(seed)
        paths = ["/api/browse", "/api/browse/projects", "/api/browse/journal"]
        while time.time() < stop_time:
            spec = RequestSpec(method="GET", path=rng.choice(paths))
            _record(stress_client.request(spec))
            time.sleep(0.5)

    def _ask_worker(seed: int):
        rng = random.Random(seed)
        while time.time() < stop_time:
            spec = RequestSpec(method="POST", path="/api/ask", json_body={"question": rng.choice(questions)})
            _record(stress_client.request(spec))
            time.sleep(0.8)

    def _refine_worker(seed: int):
        rng = random.Random(seed)
        while time.time() < stop_time:
            spec = RequestSpec(method="POST", path="/api/refine", json_body={"content": rng.choice(refine_snippets)})
            _record(stress_client.request(spec))
            time.sleep(1.2)

    workers = []
    workers.extend(partial(_submit_worker, seed) for seed in range(submit_threads))
    workers.extend(partial(_browse_worker, seed + 1000) for seed in range(browse_threads))
    workers.extend(partial(_ask_worker, seed + 2000) for seed in range(ask_threads))
    workers.extend(partial(_refine_worker, seed + 3000) for seed in range(refine_threads))

    start = time.perf_counter()
    with concurrent_executor(len(workers)) as executor:
        futures = [executor.submit(worker) for worker in workers]
        for future in futures:
            future.result()
    elapsed_s = time.perf_counter() - start

    summary = metrics_collector.summary()
    summary["elapsed_s"] = elapsed_s

    data_dir = os.environ.get("STRESS_DATA_DIR")
    if data_dir:
        integrity = IntegrityChecker(Path(data_dir))
        summary["integrity"] = integrity.report()
        summary["db_integrity"] = integrity.db_integrity_check(
            Path(data_dir) / ".gardener" / "state.db"
        )

    metrics_path = os.environ.get("STRESS_METRICS_PATH")
    if metrics_path:
        payload = {"scenario": "B", "summary": summary}
        Path(metrics_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert summary["errors"] == 0
