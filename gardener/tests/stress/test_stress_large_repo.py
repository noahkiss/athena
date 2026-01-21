"""Scenario C: Large repository stress test."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import time
from pathlib import Path

import pytest

from tests.stress.utils import MetricsCollector, RequestSpec


pytestmark = pytest.mark.stress

if os.environ.get("RUN_STRESS_TESTS") != "1":
    pytest.skip("RUN_STRESS_TESTS=1 is required for stress tests.", allow_module_level=True)


def _ensure_structure(data_dir: Path) -> None:
    (data_dir / "inbox" / "archive").mkdir(parents=True, exist_ok=True)
    (data_dir / "atlas").mkdir(parents=True, exist_ok=True)
    (data_dir / "meta").mkdir(parents=True, exist_ok=True)
    for category in ["home", "journal", "people", "projects", "reading", "tech", "wellness"]:
        (data_dir / "atlas" / category).mkdir(parents=True, exist_ok=True)
    (data_dir / "AGENTS.md").write_text("# Stress Test Data\n", encoding="utf-8")
    (data_dir / "GARDENER.md").write_text("# Stress Test Guidance\n", encoding="utf-8")


def _ensure_git_repo(data_dir: Path) -> None:
    if (data_dir / ".git").exists():
        return
    subprocess.check_call(["git", "-C", str(data_dir), "init"])
    subprocess.check_call(["git", "-C", str(data_dir), "config", "user.email", "stress@example.com"])
    subprocess.check_call(["git", "-C", str(data_dir), "config", "user.name", "Stress Test"])


def _commit_all(data_dir: Path, message: str, *, allow_empty: bool = False) -> None:
    subprocess.check_call(["git", "-C", str(data_dir), "add", "."])
    args = ["git", "-C", str(data_dir), "commit"]
    if allow_empty:
        args.append("--allow-empty")
    args.extend(["-m", message])
    subprocess.check_call(args)


def _seed_atlas(data_dir: Path, note_generator, tmp_path: Path, file_count: int) -> None:
    notes_dir = tmp_path / "large-repo-notes"
    manifest = note_generator(
        count=file_count,
        min_kb=int(os.environ.get("STRESS_LARGE_MIN_KB", "1")),
        max_kb=int(os.environ.get("STRESS_LARGE_MAX_KB", "20")),
        out_dir=notes_dir,
        seed=4242,
    )
    for entry in manifest:
        src = notes_dir / entry.filename
        target = data_dir / "atlas" / entry.category / entry.filename
        target.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def _add_commits(data_dir: Path, commit_count: int, *, start_index: int = 0) -> None:
    log_path = data_dir / "meta" / "stress-commits.log"
    for offset in range(commit_count):
        idx = start_index + offset
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"commit {idx}\n")
        _commit_all(data_dir, f"stress commit {idx}")


def _git_commit_count(data_dir: Path) -> int | None:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(data_dir), "rev-list", "--count", "HEAD"],
            stderr=subprocess.STDOUT,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    try:
        return int(output.decode("utf-8").strip())
    except ValueError:
        return None


def _timed_command(command: list[str]) -> tuple[float | None, str | None]:
    start = time.perf_counter()
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return None, str(exc)
    return (time.perf_counter() - start) * 1000, None


def _measure_git_ops(data_dir: Path) -> dict:
    timings: dict[str, float | str | None] = {}
    for label, cmd in (
        ("git_status_ms", ["git", "-C", str(data_dir), "status", "--porcelain"]),
        ("git_diff_ms", ["git", "-C", str(data_dir), "diff", "--stat"]),
    ):
        elapsed_ms, error = _timed_command(cmd)
        timings[label] = elapsed_ms
        if error:
            timings[f"{label}_error"] = error
    return timings


def _read_rss_kb(pid: int) -> int | None:
    status_path = Path("/proc") / str(pid) / "status"
    try:
        text = status_path.read_text(encoding="utf-8")
    except OSError:
        return None
    for line in text.splitlines():
        if line.startswith("VmRSS:"):
            parts = line.split()
            if len(parts) >= 2:
                try:
                    return int(parts[1])
                except ValueError:
                    return None
    return None


def _measure_db_scan(data_dir: Path) -> dict | None:
    db_path = data_dir / ".gardener" / "state.db"
    if not db_path.exists():
        return None
    conn = sqlite3.connect(db_path)
    try:
        start = time.perf_counter()
        row = conn.execute("SELECT COUNT(*) FROM file_state").fetchone()
        count = row[0] if row else 0
        count_ms = (time.perf_counter() - start) * 1000
        start = time.perf_counter()
        cursor = conn.execute("SELECT file_path FROM file_state")
        for _ in cursor:
            pass
        scan_ms = (time.perf_counter() - start) * 1000
        return {
            "row_count": count,
            "count_ms": count_ms,
            "scan_ms": scan_ms,
        }
    finally:
        conn.close()


def test_large_repository_stress(tmp_path: Path, note_generator, stress_client):
    data_dir_env = os.environ.get("STRESS_DATA_DIR")
    if not data_dir_env:
        pytest.skip("STRESS_DATA_DIR must be set for large repo stress test.")

    data_dir = Path(data_dir_env)
    file_count = int(os.environ.get("STRESS_LARGE_FILE_COUNT", "10000"))
    commit_target = int(os.environ.get("STRESS_LARGE_COMMIT_COUNT", "20000"))
    reconcile_timeout = float(os.environ.get("STRESS_RECONCILE_TIMEOUT", "300"))
    search_timeout = float(os.environ.get("STRESS_SEARCH_TIMEOUT", "60"))

    _ensure_structure(data_dir)
    _ensure_git_repo(data_dir)
    _seed_atlas(data_dir, note_generator, tmp_path, file_count)
    _commit_all(data_dir, "seed large repo data", allow_empty=True)
    current_commits = _git_commit_count(data_dir) or 0
    if current_commits < commit_target:
        _add_commits(
            data_dir,
            commit_target - current_commits,
            start_index=current_commits,
        )

    metrics = MetricsCollector()

    start = time.perf_counter()
    gardener_pid = os.environ.get("STRESS_GARDENER_PID")
    rss_before_reconcile = None
    if gardener_pid:
        try:
            rss_before_reconcile = _read_rss_kb(int(gardener_pid))
        except ValueError:
            rss_before_reconcile = None

    metrics.record(stress_client.request(RequestSpec("GET", "/api/status")))
    metrics.record(
        stress_client.request(
            RequestSpec("POST", "/api/reconcile", timeout=reconcile_timeout)
        )
    )

    rss_after_reconcile = None
    if gardener_pid:
        try:
            rss_after_reconcile = _read_rss_kb(int(gardener_pid))
        except ValueError:
            rss_after_reconcile = None

    questions = [
        "Summarize recent project updates.",
        "What should I read next about monitoring?",
        "Any notes on deployment latency?",
    ]
    for question in questions:
        metrics.record(
            stress_client.request(
                RequestSpec(
                    "POST",
                    "/api/ask",
                    json_body={"question": question},
                    timeout=search_timeout,
                )
            )
        )

    refine_samples = [
        "Meeting notes on database performance and latency trends.",
        "Reading summary: monitoring alerts and infrastructure health.",
    ]
    for content in refine_samples:
        metrics.record(
            stress_client.request(
                RequestSpec(
                    "POST",
                    "/api/refine",
                    json_body={"content": content},
                    timeout=search_timeout,
                )
            )
        )

    metrics.record(
        stress_client.request(
            RequestSpec("POST", "/api/inbox", json_body={"content": "Stress test note for large repo."})
        )
    )
    metrics.record(stress_client.request(RequestSpec("POST", "/api/trigger-gardener")))
    elapsed_s = time.perf_counter() - start

    summary = metrics.summary()
    summary["elapsed_s"] = elapsed_s
    summary["file_count"] = file_count
    summary["commit_target"] = commit_target
    summary["commit_count"] = _git_commit_count(data_dir)
    summary["git_ops"] = _measure_git_ops(data_dir)
    summary["db_scan"] = _measure_db_scan(data_dir)
    summary["memory_kb"] = {
        "rss_before_reconcile": rss_before_reconcile,
        "rss_after_reconcile": rss_after_reconcile,
    }

    metrics_path = os.environ.get("STRESS_METRICS_PATH")
    if metrics_path:
        payload = {"scenario": "C", "summary": summary}
        Path(metrics_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert summary["errors"] == 0
