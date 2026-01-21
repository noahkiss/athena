"""File state tracking and reconciliation for Gardener."""

import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import TypedDict

import config
from db import get_db_connection, init_db
from git_state import (
    check_repo_identity,
    get_current_head,
    get_repo_state,
    get_dirty_files,
    update_repo_root_hash,
)


class FileInfo(TypedDict):
    file_path: str
    location: str
    content_hash: str
    mtime: float
    size: int
    last_checked: str


class ReconcileRun(TypedDict):
    id: int
    run_at: str
    from_sha: str | None
    to_sha: str | None
    files_changed: int
    inbox_changes: int
    atlas_changes: int
    meta_changes: int
    tasks_generated: list[str]


class ChangedFile(TypedDict):
    path: str
    location: str
    status: str  # 'added', 'modified', 'deleted', 'renamed'
    old_path: str | None  # For renames


def classify_location(file_path: Path) -> str:
    """Classify a file's location (archive, inbox, atlas, meta, or root)."""
    try:
        file_path = file_path.resolve()
        if file_path.is_relative_to(config.ARCHIVE_DIR.resolve()):
            return "archive"
        if file_path.is_relative_to(config.INBOX_DIR.resolve()):
            return "inbox"
        if file_path.is_relative_to(config.ATLAS_DIR.resolve()):
            return "atlas"
        if file_path.is_relative_to(config.META_DIR.resolve()):
            return "meta"
    except (ValueError, RuntimeError):
        pass
    return "root"


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file contents."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def update_file_state(file_path: Path) -> FileInfo:
    """Update the state tracking for a file."""
    abs_path = file_path.resolve()
    rel_path = str(abs_path.relative_to(config.DATA_DIR.resolve()))
    stat = abs_path.stat()
    content_hash = compute_file_hash(abs_path)
    location = classify_location(abs_path)

    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO file_state
               (file_path, location, content_hash, mtime, size, last_checked)
               VALUES (?, ?, ?, ?, ?, datetime('now'))""",
            (rel_path, location, content_hash, stat.st_mtime, stat.st_size),
        )
        conn.commit()

        return FileInfo(
            file_path=rel_path,
            location=location,
            content_hash=content_hash,
            mtime=stat.st_mtime,
            size=stat.st_size,
            last_checked=datetime.now().isoformat(),
        )
    finally:
        conn.close()


def get_file_state(file_path: Path) -> FileInfo | None:
    """Get the tracked state for a file."""
    abs_path = file_path.resolve()
    try:
        rel_path = str(abs_path.relative_to(config.DATA_DIR.resolve()))
    except ValueError:
        return None

    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT file_path, location, content_hash, mtime, size, last_checked FROM file_state WHERE file_path = ?",
            (rel_path,),
        ).fetchone()
        if row:
            return FileInfo(
                file_path=row["file_path"],
                location=row["location"],
                content_hash=row["content_hash"],
                mtime=row["mtime"],
                size=row["size"],
                last_checked=row["last_checked"],
            )
        return None
    finally:
        conn.close()


def remove_file_state(file_path: Path) -> None:
    """Remove tracking for a deleted file."""
    abs_path = file_path.resolve()
    try:
        rel_path = str(abs_path.relative_to(config.DATA_DIR.resolve()))
    except ValueError:
        return

    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM file_state WHERE file_path = ?", (rel_path,))
        conn.commit()
    finally:
        conn.close()


def get_files_by_location(location: str) -> list[FileInfo]:
    """Get all tracked files in a location."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT file_path, location, content_hash, mtime, size, last_checked FROM file_state WHERE location = ?",
            (location,),
        ).fetchall()
        return [
            FileInfo(
                file_path=row["file_path"],
                location=row["location"],
                content_hash=row["content_hash"],
                mtime=row["mtime"],
                size=row["size"],
                last_checked=row["last_checked"],
            )
            for row in rows
        ]
    finally:
        conn.close()


def get_file_counts_by_location() -> dict[str, int]:
    """Get count of tracked files by location."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT location, COUNT(*) as count FROM file_state GROUP BY location"
        ).fetchall()
        return {row["location"]: row["count"] for row in rows}
    finally:
        conn.close()


def get_dirty_summary() -> dict[str, int]:
    """Get summary of dirty files by location."""
    dirty = get_dirty_files()
    summary: dict[str, int] = {
        "archive": 0,
        "inbox": 0,
        "atlas": 0,
        "meta": 0,
        "root": 0,
    }

    for file_path in dirty:
        path = config.DATA_DIR / file_path
        location = classify_location(path)
        summary[location] = summary.get(location, 0) + 1

    return summary


def cleanup_stale_files() -> int:
    """Remove file state entries for files that no longer exist.

    Returns the number of records deleted.
    """
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT id, file_path FROM file_state").fetchall()
        to_delete = []

        for row in rows:
            full_path = config.DATA_DIR / row["file_path"]
            if not full_path.exists():
                to_delete.append(row["id"])

        if to_delete:
            placeholders = ",".join("?" * len(to_delete))
            conn.execute(
                f"DELETE FROM file_state WHERE id IN ({placeholders})", to_delete
            )
            conn.commit()

        return len(to_delete)
    finally:
        conn.close()


# --- Reconciliation functions ---


def get_changes_since_sha(from_sha: str | None) -> list[ChangedFile]:
    """Get list of changed files since a given SHA.

    Uses git diff to detect additions, modifications, deletions, and renames.
    """
    if from_sha is None:
        # No previous SHA, return all tracked files
        return get_all_current_files()

    try:
        # Use git diff with rename detection
        result = subprocess.run(
            ["git", "diff", "--name-status", "-M", from_sha, "HEAD"],
            cwd=config.DATA_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []

        changes: list[ChangedFile] = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split("\t")
            status_code = parts[0]

            if status_code.startswith("R"):  # Rename
                old_path = parts[1]
                new_path = parts[2]
                changes.append(
                    ChangedFile(
                        path=new_path,
                        location=classify_location(config.DATA_DIR / new_path),
                        status="renamed",
                        old_path=old_path,
                    )
                )
            elif status_code == "A":  # Added
                file_path = parts[1]
                changes.append(
                    ChangedFile(
                        path=file_path,
                        location=classify_location(config.DATA_DIR / file_path),
                        status="added",
                        old_path=None,
                    )
                )
            elif status_code == "M":  # Modified
                file_path = parts[1]
                changes.append(
                    ChangedFile(
                        path=file_path,
                        location=classify_location(config.DATA_DIR / file_path),
                        status="modified",
                        old_path=None,
                    )
                )
            elif status_code == "D":  # Deleted
                file_path = parts[1]
                changes.append(
                    ChangedFile(
                        path=file_path,
                        location=classify_location(config.DATA_DIR / file_path),
                        status="deleted",
                        old_path=None,
                    )
                )

        return changes
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_all_current_files() -> list[ChangedFile]:
    """Get all tracked files in the repo as 'added' changes."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=config.DATA_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []

        return [
            ChangedFile(
                path=f,
                location=classify_location(config.DATA_DIR / f),
                status="added",
                old_path=None,
            )
            for f in result.stdout.strip().split("\n")
            if f
        ]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def generate_maintenance_tasks(changes: list[ChangedFile]) -> list[str]:
    """Generate maintenance task descriptions based on detected changes.

    Source-of-truth rules:
    - Inbox changes: process as normal ingestion
    - Atlas changes: never auto-rewrite; generate review tasks
    - Meta changes: can be regenerated; flag for reindex
    """
    tasks: list[str] = []

    inbox_changes = [c for c in changes if c["location"] == "inbox"]
    atlas_changes = [c for c in changes if c["location"] == "atlas"]
    meta_changes = [c for c in changes if c["location"] == "meta"]

    # Inbox: trigger gardener processing
    if inbox_changes:
        added = [c for c in inbox_changes if c["status"] == "added"]
        if added:
            tasks.append(f"Process {len(added)} new inbox file(s)")

    # Atlas: manual edits are source of truth - generate review tasks only
    if atlas_changes:
        modified = [c for c in atlas_changes if c["status"] == "modified"]
        added = [c for c in atlas_changes if c["status"] == "added"]
        deleted = [c for c in atlas_changes if c["status"] == "deleted"]
        renamed = [c for c in atlas_changes if c["status"] == "renamed"]

        if modified:
            tasks.append(
                f"Review {len(modified)} modified note(s) in atlas (manual edits preserved)"
            )
        if added:
            tasks.append(f"Index {len(added)} new note(s) added to atlas")
        if deleted:
            tasks.append(f"Clean up references to {len(deleted)} deleted note(s)")
        if renamed:
            tasks.append(f"Update links for {len(renamed)} renamed note(s)")

    # Meta: derived artifacts can be regenerated
    if meta_changes:
        tasks.append("Regenerate meta indexes (derived artifacts may be stale)")

    # Cross-cutting tasks
    if any(c["status"] in ("renamed", "deleted") for c in changes):
        tasks.append("Refresh backlinks and cross-references")

    if atlas_changes or meta_changes:
        tasks.append("Run consistency check on knowledge base")

    return tasks


def record_reconcile_run(
    from_sha: str | None,
    to_sha: str | None,
    changes: list[ChangedFile],
    tasks: list[str],
) -> int:
    """Record a reconciliation run in the database.

    Returns the run ID.
    """
    import json

    inbox_changes = len([c for c in changes if c["location"] == "inbox"])
    atlas_changes = len([c for c in changes if c["location"] == "atlas"])
    meta_changes = len([c for c in changes if c["location"] == "meta"])

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO reconcile_runs
               (from_sha, to_sha, files_changed, inbox_changes, atlas_changes, meta_changes, tasks_generated)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                from_sha,
                to_sha,
                len(changes),
                inbox_changes,
                atlas_changes,
                meta_changes,
                json.dumps(tasks),
            ),
        )
        run_id = cursor.lastrowid

        # Update last reconcile SHA
        if to_sha:
            conn.execute(
                "UPDATE repo_state SET last_reconcile_sha = ?, last_updated = datetime('now') WHERE id = 1",
                (to_sha,),
            )

        conn.commit()
        return run_id
    finally:
        conn.close()


def get_last_reconcile_run() -> ReconcileRun | None:
    """Get the most recent reconciliation run."""
    import json

    conn = get_db_connection()
    try:
        row = conn.execute(
            """SELECT id, run_at, from_sha, to_sha, files_changed,
                      inbox_changes, atlas_changes, meta_changes, tasks_generated
               FROM reconcile_runs ORDER BY run_at DESC LIMIT 1"""
        ).fetchone()

        if row:
            return ReconcileRun(
                id=row["id"],
                run_at=row["run_at"],
                from_sha=row["from_sha"],
                to_sha=row["to_sha"],
                files_changed=row["files_changed"],
                inbox_changes=row["inbox_changes"],
                atlas_changes=row["atlas_changes"],
                meta_changes=row["meta_changes"],
                tasks_generated=json.loads(row["tasks_generated"])
                if row["tasks_generated"]
                else [],
            )
        return None
    finally:
        conn.close()


def run_reconcile() -> ReconcileRun:
    """Run reconciliation: detect changes, generate tasks, record run.

    This is the main entry point for the reconcile operation.
    If repo identity has changed (history rewritten), forces a full scan.
    """
    init_db()

    # Check repo identity - if invalid, force full scan
    identity_valid, current_hash = check_repo_identity()

    # Get current state
    repo_state = get_repo_state()
    to_sha = get_current_head()

    if not identity_valid:
        # History was rewritten - force full scan by ignoring previous SHA
        from_sha = None
        # Update the repo identity to the new one
        if current_hash:
            update_repo_root_hash(current_hash)
    else:
        from_sha = repo_state["last_reconcile_sha"] or repo_state["last_processed_sha"]

    # Detect changes
    changes = get_changes_since_sha(from_sha)

    # Generate maintenance tasks
    tasks = generate_maintenance_tasks(changes)

    # If we did a full scan due to identity change, add a note
    if not identity_valid:
        tasks.insert(0, "Repository history changed - performed full scan")

    # Record the run
    run_id = record_reconcile_run(from_sha, to_sha, changes, tasks)

    return ReconcileRun(
        id=run_id,
        run_at=datetime.now().isoformat(),
        from_sha=from_sha,
        to_sha=to_sha,
        files_changed=len(changes),
        inbox_changes=len([c for c in changes if c["location"] == "inbox"]),
        atlas_changes=len([c for c in changes if c["location"] == "atlas"]),
        meta_changes=len([c for c in changes if c["location"] == "meta"]),
        tasks_generated=tasks,
    )
