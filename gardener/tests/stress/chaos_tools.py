"""Failure injection helpers for chaos stress testing."""

from __future__ import annotations

import os
import shutil
import signal
import sqlite3
import subprocess
from pathlib import Path


_ALLOWED_TABLES = {"processed_commits", "repo_state", "file_state", "reconcile_runs", "edit_provenance"}


def kill_process(pid: int) -> None:
    """Terminate a process immediately."""
    os.kill(pid, signal.SIGKILL)


def corrupt_state_db(db_path: Path, *, table: str = "file_state", limit: int = 10) -> int:
    """Delete rows from a table to simulate data loss."""
    if table not in _ALLOWED_TABLES:
        raise ValueError(f"Unsupported table: {table}")
    if not db_path.exists():
        return 0
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            f"SELECT id FROM {table} ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        ids = [row[0] for row in rows]
        if ids:
            placeholders = ",".join("?" * len(ids))
            conn.execute(
                f"DELETE FROM {table} WHERE id IN ({placeholders})",
                ids,
            )
            conn.commit()
        return len(ids)
    finally:
        conn.close()


def delete_inbox_files(
    inbox_dir: Path,
    *,
    limit: int = 5,
    backup_dir: Path | None = None,
) -> int:
    """Delete or move inbox files to simulate loss during processing."""
    if not inbox_dir.exists():
        return 0
    files = sorted(inbox_dir.glob("*.md"))
    targets = files[:limit]
    if backup_dir:
        backup_dir.mkdir(parents=True, exist_ok=True)
        for path in targets:
            shutil.move(str(path), backup_dir / path.name)
    else:
        for path in targets:
            path.unlink(missing_ok=True)
    return len(targets)


def rewrite_git_history(data_dir: Path, *, commits: int = 1) -> bool:
    """Rewrite git history by resetting HEAD backward."""
    if commits <= 0:
        return False
    try:
        subprocess.run(
            ["git", "-C", str(data_dir), "rev-parse", "--verify", f"HEAD~{commits}"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(data_dir), "reset", "--hard", f"HEAD~{commits}"],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def fill_disk_space(
    data_dir: Path,
    *,
    megabytes: int = 100,
    filename: str = "chaos-fill.bin",
) -> Path:
    """Create a large file to simulate disk pressure."""
    target = data_dir / filename
    size = max(0, megabytes) * 1024 * 1024
    with target.open("wb") as handle:
        handle.truncate(size)
    return target
