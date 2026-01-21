"""Scenario A: High-volume inbox ingestion stress test."""

from __future__ import annotations

import json
import os
import random
import time
from pathlib import Path

import pytest

from tests.stress.utils import IntegrityChecker, RequestSpec, concurrent_executor


pytestmark = pytest.mark.stress

if os.environ.get("RUN_STRESS_TESTS") != "1":
    pytest.skip("RUN_STRESS_TESTS=1 is required for stress tests.", allow_module_level=True)


def _chunk_notes(note_paths: list[Path], buckets: int) -> list[list[Path]]:
    chunks: list[list[Path]] = [[] for _ in range(buckets)]
    for idx, path in enumerate(note_paths):
        chunks[idx % buckets].append(path)
    return chunks


def test_high_volume_ingestion(
    tmp_path: Path,
    note_generator,
    stress_client,
    metrics_collector,
):
    concurrency = int(os.environ.get("STRESS_CONCURRENCY", "50"))
    notes_per_client = int(os.environ.get("STRESS_NOTES_PER_CLIENT", "20"))
    total_notes = int(os.environ.get("STRESS_NOTE_COUNT", str(concurrency * notes_per_client)))
    min_kb = int(os.environ.get("STRESS_MIN_KB", "1"))
    max_kb = int(os.environ.get("STRESS_MAX_KB", "50"))
    stagger_max = float(os.environ.get("STRESS_STAGGER_MAX", "10"))

    out_dir = tmp_path / "generated-notes"
    manifest = note_generator(
        count=total_notes,
        min_kb=min_kb,
        max_kb=max_kb,
        out_dir=out_dir,
        seed=42,
    )
    note_paths = [out_dir / entry.filename for entry in manifest]

    rng = random.Random(42)
    chunks = _chunk_notes(note_paths, concurrency)
    delays = [rng.uniform(0.0, stagger_max) if stagger_max > 0 else 0.0 for _ in chunks]

    def _worker(paths: list[Path], delay: float):
        if delay > 0:
            time.sleep(delay)
        results = []
        for path in paths:
            content = path.read_text(encoding="utf-8")
            spec = RequestSpec(method="POST", path="/api/inbox", json_body={"content": content})
            results.append(stress_client.request(spec))
        return results

    start = time.perf_counter()
    with concurrent_executor(concurrency) as executor:
        futures = [executor.submit(_worker, chunk, delay) for chunk, delay in zip(chunks, delays)]
        for future in futures:
            metrics_collector.extend(future.result())
    elapsed_s = time.perf_counter() - start

    summary = metrics_collector.summary()
    summary["notes_submitted"] = total_notes
    summary["elapsed_s"] = elapsed_s
    summary["throughput_per_s"] = total_notes / elapsed_s if elapsed_s > 0 else None

    data_dir = os.environ.get("STRESS_DATA_DIR")
    if data_dir:
        integrity = IntegrityChecker(Path(data_dir))
        summary["integrity"] = integrity.report()
        summary["db_integrity"] = integrity.db_integrity_check(
            Path(data_dir) / ".gardener" / "state.db"
        )
        if os.environ.get("STRESS_EXPECT_ARCHIVE") == "1":
            assert summary["integrity"]["archive_count"] >= total_notes
            assert not summary["integrity"]["archive_empty"]

    metrics_path = os.environ.get("STRESS_METRICS_PATH")
    if metrics_path:
        payload = {"scenario": "A", "summary": summary}
        Path(metrics_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert summary["errors"] == 0
    assert summary["ok"] == total_notes
