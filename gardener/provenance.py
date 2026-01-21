"""Edit provenance tracking for Gardener."""

from pathlib import Path
from typing import TypedDict

import config
from db import get_db_connection


class EditProvenance(TypedDict):
    id: int
    file_path: str
    commit_sha: str | None
    source: str
    recorded_at: str
    metadata: dict | None


# Standard source identifiers for provenance
PROVENANCE_GARDENER = "gardener"
PROVENANCE_MANUAL = "manual"
PROVENANCE_EXTERNAL_CLAUDE = "external:claude-code"
PROVENANCE_EXTERNAL_MCP = "external:mcp"
PROVENANCE_EXTERNAL_SCRIPT = "external:script"


def record_provenance(
    file_path: str | Path,
    source: str,
    commit_sha: str | None = None,
    metadata: dict | None = None,
) -> int:
    """Record edit provenance for a file.

    Args:
        file_path: Path to the file (relative to DATA_DIR)
        source: Source identifier (use PROVENANCE_* constants)
        commit_sha: Optional commit SHA associated with this edit
        metadata: Optional additional context as dict

    Returns:
        The provenance record ID
    """
    import json

    if isinstance(file_path, Path):
        try:
            file_path = str(file_path.resolve().relative_to(config.DATA_DIR.resolve()))
        except ValueError:
            file_path = str(file_path)

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO edit_provenance (file_path, commit_sha, source, metadata)
               VALUES (?, ?, ?, ?)""",
            (file_path, commit_sha, source, json.dumps(metadata) if metadata else None),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_file_provenance(file_path: str | Path, limit: int = 10) -> list[EditProvenance]:
    """Get provenance history for a file.

    Args:
        file_path: Path to the file (relative to DATA_DIR)
        limit: Maximum number of records to return

    Returns:
        List of provenance records, most recent first
    """
    import json

    if isinstance(file_path, Path):
        try:
            file_path = str(file_path.resolve().relative_to(config.DATA_DIR.resolve()))
        except ValueError:
            file_path = str(file_path)

    conn = get_db_connection()
    try:
        rows = conn.execute(
            """SELECT id, file_path, commit_sha, source, recorded_at, metadata
               FROM edit_provenance
               WHERE file_path = ?
               ORDER BY recorded_at DESC
               LIMIT ?""",
            (file_path, limit),
        ).fetchall()

        return [
            EditProvenance(
                id=row["id"],
                file_path=row["file_path"],
                commit_sha=row["commit_sha"],
                source=row["source"],
                recorded_at=row["recorded_at"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else None,
            )
            for row in rows
        ]
    finally:
        conn.close()


def get_provenance_by_source(source: str, limit: int = 50) -> list[EditProvenance]:
    """Get all provenance records for a given source.

    Args:
        source: Source identifier to filter by
        limit: Maximum number of records to return

    Returns:
        List of provenance records, most recent first
    """
    import json

    conn = get_db_connection()
    try:
        rows = conn.execute(
            """SELECT id, file_path, commit_sha, source, recorded_at, metadata
               FROM edit_provenance
               WHERE source = ?
               ORDER BY recorded_at DESC
               LIMIT ?""",
            (source, limit),
        ).fetchall()

        return [
            EditProvenance(
                id=row["id"],
                file_path=row["file_path"],
                commit_sha=row["commit_sha"],
                source=row["source"],
                recorded_at=row["recorded_at"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else None,
            )
            for row in rows
        ]
    finally:
        conn.close()


def format_commit_message(source: str, action: str) -> str:
    """Format a commit message with proper source attribution.

    Standard commit message formats:
    - Gardener: "Gardener: <action>"
    - Manual: "Manual: <action>"
    - External: "External[<tool>]: <action>"

    Args:
        source: Source identifier (use PROVENANCE_* constants)
        action: Description of the action taken

    Returns:
        Formatted commit message
    """
    if source == PROVENANCE_GARDENER:
        return f"Gardener: {action}"
    if source == PROVENANCE_MANUAL:
        return f"Manual: {action}"
    if source.startswith("external:"):
        tool = source.split(":", 1)[1]
        return f"External[{tool}]: {action}"
    return f"{source}: {action}"


def parse_commit_source(message: str) -> str:
    """Parse source from a commit message.

    Args:
        message: Git commit message

    Returns:
        Source identifier
    """
    if message.startswith("Gardener:"):
        return PROVENANCE_GARDENER
    if message.startswith("Manual:"):
        return PROVENANCE_MANUAL
    if message.startswith("External["):
        # Extract tool name from "External[tool]: action"
        end = message.find("]:")
        if end > 9:
            tool = message[9:end]
            return f"external:{tool}"
    if message.startswith("Athena:"):
        return "athena"
    return "unknown"
