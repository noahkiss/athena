"""Tests for Gardener state modules."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestStateDatabase:
    """Test database initialization and operations."""

    @pytest.fixture
    def temp_state(self):
        """Create a temporary state database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / ".gardener"
            state_db = state_dir / "state.db"
            data_dir = Path(tmpdir) / "data"
            data_dir.mkdir()
            inbox_dir = data_dir / "inbox"
            inbox_dir.mkdir()
            archive_dir = inbox_dir / "archive"
            archive_dir.mkdir()
            atlas_dir = data_dir / "atlas"
            atlas_dir.mkdir()
            meta_dir = data_dir / ".meta"
            meta_dir.mkdir()

            with (
                patch("config.STATE_DIR", state_dir),
                patch("config.STATE_DB", state_db),
                patch("config.DATA_DIR", data_dir),
                patch("config.INBOX_DIR", inbox_dir),
                patch("config.ARCHIVE_DIR", archive_dir),
                patch("config.ATLAS_DIR", atlas_dir),
                patch("config.META_DIR", meta_dir),
            ):
                yield {
                    "state_dir": state_dir,
                    "state_db": state_db,
                    "data_dir": data_dir,
                    "inbox_dir": inbox_dir,
                    "atlas_dir": atlas_dir,
                    "meta_dir": meta_dir,
                }

    def test_init_db_creates_tables(self, temp_state):
        """init_db should create all required tables."""
        from db import get_db_connection, init_db

        init_db()

        conn = get_db_connection()
        try:
            # Check tables exist
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [t["name"] for t in tables]

            assert "processed_commits" in table_names
            assert "repo_state" in table_names
            assert "file_state" in table_names
            assert "reconcile_runs" in table_names
            assert "edit_provenance" in table_names
            assert "schema_version" in table_names
        finally:
            conn.close()

    def test_repo_state_singleton(self, temp_state):
        """repo_state should have exactly one row."""
        from db import init_db
        from git_state import get_repo_state

        init_db()

        state = get_repo_state()
        assert state["last_seen_sha"] is None
        assert state["last_processed_sha"] is None


class TestRepoStateOperations:
    """Test repo state tracking."""

    @pytest.fixture
    def temp_state(self):
        """Create a temporary state database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / ".gardener"
            state_db = state_dir / "state.db"
            data_dir = Path(tmpdir) / "data"
            data_dir.mkdir()

            with (
                patch("config.STATE_DIR", state_dir),
                patch("config.STATE_DB", state_db),
                patch("config.DATA_DIR", data_dir),
                patch("config.INBOX_DIR", data_dir / "inbox"),
                patch("config.ARCHIVE_DIR", data_dir / "inbox" / "archive"),
                patch("config.ATLAS_DIR", data_dir / "atlas"),
                patch("config.META_DIR", data_dir / ".meta"),
            ):
                from db import init_db

                init_db()
                yield {"data_dir": data_dir}

    def test_update_last_seen_sha(self, temp_state):
        """update_last_seen_sha should update the SHA."""
        from git_state import get_repo_state, update_last_seen_sha

        update_last_seen_sha("abc123")

        state = get_repo_state()
        assert state["last_seen_sha"] == "abc123"

    def test_update_last_processed_sha(self, temp_state):
        """update_last_processed_sha should update the SHA."""
        from git_state import get_repo_state, update_last_processed_sha

        update_last_processed_sha("def456")

        state = get_repo_state()
        assert state["last_processed_sha"] == "def456"

    def test_record_processed_commit(self, temp_state):
        """record_processed_commit should create commit record and update state."""
        from git_state import (
            get_processed_commits,
            get_repo_state,
            record_processed_commit,
        )

        record_processed_commit("sha123", "main", "Test commit")

        # Check state was updated
        state = get_repo_state()
        assert state["last_processed_sha"] == "sha123"
        assert state["last_seen_sha"] == "sha123"

        # Check commit was recorded
        commits = get_processed_commits(limit=1)
        assert len(commits) == 1
        assert commits[0]["sha"] == "sha123"
        assert commits[0]["branch"] == "main"
        assert commits[0]["note"] == "Test commit"


class TestFileStateOperations:
    """Test file state tracking."""

    @pytest.fixture
    def temp_state(self):
        """Create a temporary state database with test file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / ".gardener"
            state_db = state_dir / "state.db"
            data_dir = Path(tmpdir) / "data"
            data_dir.mkdir()
            inbox_dir = data_dir / "inbox"
            inbox_dir.mkdir()
            archive_dir = inbox_dir / "archive"
            archive_dir.mkdir()
            atlas_dir = data_dir / "atlas"
            atlas_dir.mkdir()
            meta_dir = data_dir / ".meta"
            meta_dir.mkdir()

            # Create a test file
            test_file = atlas_dir / "test.md"
            test_file.write_text("Test content")

            with (
                patch("config.STATE_DIR", state_dir),
                patch("config.STATE_DB", state_db),
                patch("config.DATA_DIR", data_dir),
                patch("config.INBOX_DIR", inbox_dir),
                patch("config.ARCHIVE_DIR", archive_dir),
                patch("config.ATLAS_DIR", atlas_dir),
                patch("config.META_DIR", meta_dir),
            ):
                from db import init_db

                init_db()
                yield {
                    "data_dir": data_dir,
                    "atlas_dir": atlas_dir,
                    "test_file": test_file,
                }

    def test_update_file_state(self, temp_state):
        """update_file_state should track file info."""
        from file_state import get_file_state, update_file_state

        info = update_file_state(temp_state["test_file"])

        assert info["location"] == "atlas"
        assert info["size"] == len("Test content")
        assert info["content_hash"] is not None

        # Verify can retrieve it
        retrieved = get_file_state(temp_state["test_file"])
        assert retrieved is not None
        assert retrieved["content_hash"] == info["content_hash"]

    def test_remove_file_state(self, temp_state):
        """remove_file_state should delete file tracking."""
        from file_state import get_file_state, remove_file_state, update_file_state

        update_file_state(temp_state["test_file"])

        # Verify it's tracked
        assert get_file_state(temp_state["test_file"]) is not None

        # Remove tracking
        remove_file_state(temp_state["test_file"])

        # Verify it's gone
        assert get_file_state(temp_state["test_file"]) is None

    def test_classify_location(self, temp_state):
        """classify_location should correctly identify file locations."""
        from file_state import classify_location

        atlas_file = temp_state["atlas_dir"] / "note.md"
        assert classify_location(atlas_file) == "atlas"

        inbox_file = temp_state["data_dir"] / "inbox" / "new.md"
        assert classify_location(inbox_file) == "inbox"

        archive_file = temp_state["data_dir"] / "inbox" / "archive" / "old.md"
        assert classify_location(archive_file) == "archive"

        meta_file = temp_state["data_dir"] / ".meta" / "index.json"
        assert classify_location(meta_file) == "meta"

        root_file = temp_state["data_dir"] / "README.md"
        assert classify_location(root_file) == "root"


class TestProvenanceTracking:
    """Test edit provenance recording."""

    @pytest.fixture
    def temp_state(self):
        """Create a temporary state database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / ".gardener"
            state_db = state_dir / "state.db"
            data_dir = Path(tmpdir) / "data"
            data_dir.mkdir()

            with (
                patch("config.STATE_DIR", state_dir),
                patch("config.STATE_DB", state_db),
                patch("config.DATA_DIR", data_dir),
                patch("config.INBOX_DIR", data_dir / "inbox"),
                patch("config.ARCHIVE_DIR", data_dir / "inbox" / "archive"),
                patch("config.ATLAS_DIR", data_dir / "atlas"),
                patch("config.META_DIR", data_dir / ".meta"),
            ):
                from db import init_db

                init_db()
                yield {"data_dir": data_dir}

    def test_record_provenance(self, temp_state):
        """record_provenance should create provenance records."""
        from provenance import (
            PROVENANCE_GARDENER,
            get_file_provenance,
            record_provenance,
        )

        record_provenance(
            "atlas/test.md", PROVENANCE_GARDENER, "abc123", {"action": "create"}
        )

        records = get_file_provenance("atlas/test.md")
        assert len(records) == 1
        assert records[0]["source"] == PROVENANCE_GARDENER
        assert records[0]["commit_sha"] == "abc123"
        assert records[0]["metadata"]["action"] == "create"

    def test_get_provenance_by_source(self, temp_state):
        """get_provenance_by_source should filter by source."""
        from provenance import (
            PROVENANCE_GARDENER,
            PROVENANCE_MANUAL,
            get_provenance_by_source,
            record_provenance,
        )

        record_provenance("file1.md", PROVENANCE_GARDENER)
        record_provenance("file2.md", PROVENANCE_GARDENER)
        record_provenance("file3.md", PROVENANCE_MANUAL)

        gardener_records = get_provenance_by_source(PROVENANCE_GARDENER)
        assert len(gardener_records) == 2

        manual_records = get_provenance_by_source(PROVENANCE_MANUAL)
        assert len(manual_records) == 1


class TestCommitMessageFormatting:
    """Test commit message formatting and parsing."""

    def test_format_gardener_message(self):
        """Should format gardener commit messages."""
        from provenance import PROVENANCE_GARDENER, format_commit_message

        msg = format_commit_message(PROVENANCE_GARDENER, "Processed note.md")
        assert msg == "Gardener: Processed note.md"

    def test_format_manual_message(self):
        """Should format manual commit messages."""
        from provenance import PROVENANCE_MANUAL, format_commit_message

        msg = format_commit_message(PROVENANCE_MANUAL, "Updated README")
        assert msg == "Manual: Updated README"

    def test_format_external_message(self):
        """Should format external tool commit messages."""
        from provenance import PROVENANCE_EXTERNAL_CLAUDE, format_commit_message

        msg = format_commit_message(PROVENANCE_EXTERNAL_CLAUDE, "Refactored code")
        assert msg == "External[claude-code]: Refactored code"

    def test_parse_gardener_source(self):
        """Should parse gardener source from commit message."""
        from provenance import PROVENANCE_GARDENER, parse_commit_source

        source = parse_commit_source("Gardener: Processed file")
        assert source == PROVENANCE_GARDENER

    def test_parse_manual_source(self):
        """Should parse manual source from commit message."""
        from provenance import PROVENANCE_MANUAL, parse_commit_source

        source = parse_commit_source("Manual: Updated config")
        assert source == PROVENANCE_MANUAL

    def test_parse_external_source(self):
        """Should parse external tool source from commit message."""
        from provenance import parse_commit_source

        source = parse_commit_source("External[claude-code]: Made changes")
        assert source == "external:claude-code"

    def test_parse_unknown_source(self):
        """Should return 'unknown' for unrecognized messages."""
        from provenance import parse_commit_source

        source = parse_commit_source("Some random commit message")
        assert source == "unknown"
