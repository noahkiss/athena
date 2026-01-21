"""Utilities for stress/soak test scenarios."""

from __future__ import annotations

import hashlib
import sqlite3
import subprocess
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import httpx


@dataclass(frozen=True)
class RequestSpec:
    method: str
    path: str
    json_body: dict | None = None
    params: dict | None = None
    headers: dict | None = None
    timeout: float | None = None


@dataclass(frozen=True)
class RequestResult:
    method: str
    path: str
    status_code: int | None
    elapsed_ms: float
    ok: bool
    error: str | None = None
    response_bytes: int | None = None


class StressClient:
    """Threaded HTTP client for load generation."""

    def __init__(
        self,
        base_url: str,
        *,
        concurrency: int = 10,
        timeout: float = 30.0,
        headers: dict | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.concurrency = concurrency
        self.timeout = timeout
        self.headers = headers or {}
        self._local = threading.local()
        self._clients: list[httpx.Client] = []
        self._clients_lock = threading.Lock()

    def _get_client(self) -> httpx.Client:
        client = getattr(self._local, "client", None)
        if client is None:
            client = httpx.Client(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self.timeout,
            )
            self._local.client = client
            with self._clients_lock:
                self._clients.append(client)
        return client

    def request(self, spec: RequestSpec) -> RequestResult:
        start = time.perf_counter()
        try:
            response = self._get_client().request(
                spec.method,
                spec.path,
                json=spec.json_body,
                params=spec.params,
                headers=spec.headers,
                timeout=spec.timeout,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            return RequestResult(
                method=spec.method,
                path=spec.path,
                status_code=response.status_code,
                elapsed_ms=elapsed_ms,
                ok=response.is_success,
                response_bytes=len(response.content),
            )
        except Exception as exc:  # noqa: BLE001 - surfaced in metrics
            elapsed_ms = (time.perf_counter() - start) * 1000
            return RequestResult(
                method=spec.method,
                path=spec.path,
                status_code=None,
                elapsed_ms=elapsed_ms,
                ok=False,
                error=str(exc),
            )

    def run(self, specs: Iterable[RequestSpec]) -> list[RequestResult]:
        results: list[RequestResult] = []
        with concurrent_executor(self.concurrency) as executor:
            futures = [executor.submit(self.request, spec) for spec in specs]
            for future in futures:
                results.append(future.result())
        return results

    def close(self) -> None:
        for client in self._clients:
            client.close()

    def __enter__(self) -> "StressClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


class MetricsCollector:
    """Collects latency and error metrics from RequestResult entries."""

    def __init__(self) -> None:
        self.results: list[RequestResult] = []

    def record(self, result: RequestResult) -> None:
        self.results.append(result)

    def extend(self, results: Iterable[RequestResult]) -> None:
        self.results.extend(results)

    def summary(self) -> dict:
        latencies = [result.elapsed_ms for result in self.results]
        status_counts: dict[str, int] = {}
        error_count = 0
        ok_count = 0
        for result in self.results:
            if result.ok:
                ok_count += 1
            else:
                error_count += 1
            key = "error" if result.status_code is None else str(result.status_code)
            status_counts[key] = status_counts.get(key, 0) + 1

        return {
            "total": len(self.results),
            "ok": ok_count,
            "errors": error_count,
            "latency_ms": {
                "p50": percentile(latencies, 50),
                "p95": percentile(latencies, 95),
                "p99": percentile(latencies, 99),
                "max": max(latencies) if latencies else None,
            },
            "status_counts": status_counts,
        }

    def as_dict(self) -> dict:
        return {
            "summary": self.summary(),
            "results": [asdict(result) for result in self.results],
        }


class IntegrityChecker:
    """Verifies archive/data integrity for stress test runs."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.inbox_dir = self.data_dir / "inbox"
        self.archive_dir = self.inbox_dir / "archive"
        self.atlas_dir = self.data_dir / "atlas"

    def list_markdown(self, root: Path) -> list[Path]:
        if not root.exists():
            return []
        return [path for path in root.rglob("*.md") if path.is_file()]

    def hash_file(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def find_empty_files(self, paths: Iterable[Path]) -> list[Path]:
        return [path for path in paths if path.stat().st_size == 0]

    def duplicate_hashes(self, paths: Iterable[Path]) -> dict[str, list[Path]]:
        hashes: dict[str, list[Path]] = {}
        for path in paths:
            digest = self.hash_file(path)
            hashes.setdefault(digest, []).append(path)
        return {digest: items for digest, items in hashes.items() if len(items) > 1}

    def db_integrity_check(self, db_path: Path) -> str | None:
        if not db_path.exists():
            return None
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute("PRAGMA integrity_check;")
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    def git_commit_count(self, repo_dir: Path) -> int | None:
        return git_commit_count(repo_dir)

    def report(self) -> dict:
        inbox_files = self.list_markdown(self.inbox_dir)
        archive_files = self.list_markdown(self.archive_dir)
        archive_empty = self.find_empty_files(archive_files)
        duplicates = self.duplicate_hashes(archive_files)
        return {
            "inbox_count": len(inbox_files),
            "archive_count": len(archive_files),
            "archive_empty": [str(path) for path in archive_empty],
            "archive_duplicates": {
                digest: [str(path) for path in paths] for digest, paths in duplicates.items()
            },
        }


class DBLockSimulator:
    """Hold an exclusive SQLite lock for contention testing."""

    def __init__(self, db_path: Path, *, timeout: float = 0.0) -> None:
        self.db_path = Path(db_path)
        self.timeout = timeout
        self._conn: sqlite3.Connection | None = None

    def acquire(self) -> None:
        if self._conn is not None:
            return
        self._conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        self._conn.execute("BEGIN EXCLUSIVE")

    def release(self) -> None:
        if self._conn is None:
            return
        try:
            self._conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        self._conn.close()
        self._conn = None

    def hold_for(self, seconds: float) -> None:
        self.acquire()
        time.sleep(seconds)
        self.release()


def git_commit_count(repo_dir: Path) -> int | None:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(repo_dir), "rev-list", "--count", "HEAD"],
            stderr=subprocess.STDOUT,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    try:
        return int(output.decode("utf-8").strip())
    except ValueError:
        return None


def timed_command(command: list[str]) -> tuple[float | None, str | None]:
    start = time.perf_counter()
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return None, str(exc)
    return (time.perf_counter() - start) * 1000, None


def measure_git_ops(repo_dir: Path) -> dict:
    timings: dict[str, float | str | None] = {"commit_count": git_commit_count(repo_dir)}
    for label, cmd in (
        ("git_status_ms", ["git", "-C", str(repo_dir), "status", "--porcelain"]),
        ("git_diff_ms", ["git", "-C", str(repo_dir), "diff", "--stat"]),
    ):
        elapsed_ms, error = timed_command(cmd)
        timings[label] = elapsed_ms
        if error:
            timings[f"{label}_error"] = error
    return timings


def read_rss_kb(pid: int) -> int | None:
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


def measure_db_scan(db_path: Path) -> dict | None:
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


class concurrent_executor:
    """Context wrapper for thread pool without importing concurrent.futures at module import."""

    def __init__(self, max_workers: int) -> None:
        self.max_workers = max_workers
        self._executor = None

    def __enter__(self):
        from concurrent.futures import ThreadPoolExecutor

        self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self._executor

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._executor:
            self._executor.shutdown(wait=True)


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    rank = (len(values) - 1) * (pct / 100.0)
    low = int(rank)
    high = min(low + 1, len(values) - 1)
    if low == high:
        return values[low]
    weight = rank - low
    return values[low] * (1 - weight) + values[high] * weight
