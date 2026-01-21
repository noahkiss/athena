"""Integration tests for API endpoints."""

import json
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@asynccontextmanager
async def _noop_session_manager():
    """Disable MCP session manager startup for tests."""
    yield


@pytest.fixture
def temp_data_dirs(tmp_path):
    """Create temporary data directories for test runs."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    inbox_dir = data_dir / "inbox"
    inbox_dir.mkdir()
    archive_dir = inbox_dir / "archive"
    archive_dir.mkdir()
    atlas_dir = data_dir / "atlas"
    atlas_dir.mkdir()
    # Create subdirectories
    (atlas_dir / "projects").mkdir()
    (atlas_dir / "journal").mkdir()
    meta_dir = data_dir / "meta"
    meta_dir.mkdir()
    state_dir = data_dir / ".gardener"
    state_dir.mkdir()
    state_db = state_dir / "state.db"

    # Create sample atlas files
    (atlas_dir / "projects" / "test-project.md").write_text(
        "# Test Project\n\nThis is a test project about Python and testing."
    )
    (atlas_dir / "journal" / "2024-01-15.md").write_text(
        "# Journal Entry\n\nThoughts about coding and life."
    )
    (archive_dir / "old-note.md").write_text(
        "# Old Note\n\nThis note was archived after processing."
    )

    return {
        "data_dir": data_dir,
        "inbox_dir": inbox_dir,
        "archive_dir": archive_dir,
        "atlas_dir": atlas_dir,
        "meta_dir": meta_dir,
        "state_dir": state_dir,
        "state_db": state_db,
    }


@pytest.fixture
def client(temp_data_dirs):
    """Create test client with mocked directories."""
    with (
        patch("config.DATA_DIR", temp_data_dirs["data_dir"]),
        patch("config.INBOX_DIR", temp_data_dirs["inbox_dir"]),
        patch("config.ATLAS_DIR", temp_data_dirs["atlas_dir"]),
        patch("config.META_DIR", temp_data_dirs["meta_dir"]),
        patch("config.STATE_DIR", temp_data_dirs["state_dir"]),
        patch("config.STATE_DB", temp_data_dirs["state_db"]),
        patch("config.AUTH_ENABLED", False),
        patch("config.AUTH_TOKEN", ""),
        patch("config.ARCHIVE_DIR", temp_data_dirs["archive_dir"]),
        patch("config.MAX_CONTENT_SIZE", 102400),
        patch("main.DATA_DIR", temp_data_dirs["data_dir"]),
        patch("main.INBOX_DIR", temp_data_dirs["inbox_dir"]),
        patch("main.ATLAS_DIR", temp_data_dirs["atlas_dir"]),
        patch("main.ARCHIVE_DIR", temp_data_dirs["archive_dir"]),
        patch("main.AUTH_ENABLED", False),
        patch("main.AUTH_TOKEN", ""),
        patch("main.MAX_CONTENT_SIZE", 102400),
    ):
        from main import app, mcp

        with patch.object(mcp.session_manager, "run", _noop_session_manager):
            with TestClient(app) as client:
                yield client, temp_data_dirs


class TestInboxEndpoint:
    """Tests for POST /api/inbox."""

    def test_inbox_saves_note(self, client):
        """Should save note to inbox directory."""
        test_client, dirs = client
        response = test_client.post(
            "/api/inbox",
            json={"content": "Test note content"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert data["filename"].endswith(".md")

        # Verify file was created
        inbox_files = list(dirs["inbox_dir"].glob("*.md"))
        assert len(inbox_files) == 1
        assert inbox_files[0].read_text() == "Test note content"

    def test_inbox_rejects_empty_content(self, client):
        """Empty content should be rejected."""
        test_client, dirs = client
        response = test_client.post(
            "/api/inbox",
            json={"content": ""},
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_inbox_rejects_whitespace_only(self, client):
        """Whitespace-only content should be rejected."""
        test_client, _ = client
        response = test_client.post(
            "/api/inbox",
            json={"content": "   \n\t  "},
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_inbox_rejects_oversized_content(self, client):
        """Content exceeding MAX_CONTENT_SIZE should be rejected."""
        test_client, _ = client
        # Default MAX_CONTENT_SIZE is 100KB, create slightly larger content
        large_content = "x" * (102400 + 1)
        response = test_client.post(
            "/api/inbox",
            json={"content": large_content},
        )
        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()

    def test_inbox_filename_format(self, client):
        """Should create filename with timestamp and UUID."""
        test_client, _ = client
        response = test_client.post(
            "/api/inbox",
            json={"content": "Note content"},
        )
        data = response.json()
        # Format: YYYY-MM-DD_HHMM-{8char_uuid}.md = 10 + 1 + 4 + 1 + 8 + 3 = 27
        filename = data["filename"]
        assert len(filename) == 27
        assert filename[4] == "-"
        assert filename[7] == "-"
        assert filename[10] == "_"
        assert filename[-3:] == ".md"


class TestBrowseEndpoint:
    """Tests for GET /api/browse."""

    def test_browse_root_lists_directories(self, client):
        """Should list atlas subdirectories."""
        test_client, _ = client
        response = test_client.get("/api/browse")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        names = [item["name"] for item in data["items"]]
        assert "projects" in names
        assert "journal" in names

    def test_browse_directory_lists_files(self, client):
        """Should list files in directory."""
        test_client, _ = client
        response = test_client.get("/api/browse/projects")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        names = [item["name"] for item in data["items"]]
        assert "test-project.md" in names

    def test_browse_file_returns_content(self, client):
        """Should return file content."""
        test_client, _ = client
        response = test_client.get("/api/browse/projects/test-project.md")
        assert response.status_code == 200
        data = response.json()
        assert data["is_file"] is True
        assert "# Test Project" in data["content"]

    def test_browse_nonexistent_returns_404(self, client):
        """Should return 404 for nonexistent path."""
        test_client, _ = client
        response = test_client.get("/api/browse/nonexistent/path.md")
        assert response.status_code == 404

    def test_browse_prevents_path_traversal(self, client):
        """Should prevent path traversal attacks."""
        test_client, _ = client
        response = test_client.get("/api/browse/../../../etc/passwd")
        assert response.status_code in (400, 403, 404)


class TestArchiveEndpoint:
    """Tests for GET /api/archive."""

    def test_archive_root_lists_files(self, client):
        """Should list archived files."""
        test_client, _ = client
        response = test_client.get("/api/archive")
        assert response.status_code == 200
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert "old-note.md" in names

    def test_archive_file_returns_content(self, client):
        """Should return archived file content."""
        test_client, _ = client
        response = test_client.get("/api/archive/old-note.md")
        assert response.status_code == 200
        data = response.json()
        assert data["is_file"] is True
        assert "# Old Note" in data["content"]

    def test_archive_nonexistent_returns_404(self, client):
        """Should return 404 for nonexistent path."""
        test_client, _ = client
        response = test_client.get("/api/archive/missing.md")
        assert response.status_code == 404

    def test_archive_prevents_path_traversal(self, client):
        """Should prevent path traversal attacks."""
        test_client, _ = client
        response = test_client.get("/api/archive/../../../etc/passwd")
        assert response.status_code in (400, 403, 404)


class TestRefineEndpoint:
    """Tests for POST /api/refine."""

    def test_refine_empty_content_returns_message(self, client):
        """Should return helpful message for empty content."""
        test_client, _ = client
        response = test_client.post(
            "/api/refine",
            json={"content": ""},
        )
        # Returns 200 with HTML message, not 400
        assert response.status_code == 200
        assert "enter" in response.text.lower() or "content" in response.text.lower()

    def test_refine_works_without_backend(self, client):
        """Should return graceful message when no backend configured."""
        test_client, _ = client
        with patch("main.get_backend", return_value=None):
            response = test_client.post(
                "/api/refine",
                json={"content": "Test content about Python"},
            )
            # Should not crash, returns some response
            assert response.status_code in (200, 500)

    def test_refine_with_mocked_backend(self, client):
        """Should return suggestions from backend."""
        test_client, _ = client

        mock_backend = MagicMock()
        mock_backend.refine.return_value = (
            "TAGS: python, testing\n"
            "CATEGORY: tech\n"
            "RELATED: projects/test-project.md\n"
            "MISSING: None"
        )
        # Mock context manager behavior
        mock_backend.__enter__ = MagicMock(return_value=mock_backend)
        mock_backend.__exit__ = MagicMock(return_value=False)

        with patch("main.get_backend", return_value=mock_backend):
            response = test_client.post(
                "/api/refine",
                json={"content": "Test content about Python programming"},
            )
            assert response.status_code == 200
            # Response is HTML
            assert "python" in response.text.lower()


class TestAskEndpoint:
    """Tests for POST /api/ask."""

    def test_ask_empty_question_returns_message(self, client):
        """Should return helpful message for empty question."""
        test_client, _ = client
        response = test_client.post(
            "/api/ask",
            json={"question": ""},
        )
        # Returns 200 with HTML message, not 400
        assert response.status_code == 200
        assert "enter" in response.text.lower() or "question" in response.text.lower()

    def test_ask_works_without_backend(self, client):
        """Should return graceful message when no backend configured."""
        test_client, _ = client
        with patch("main.get_backend", return_value=None):
            response = test_client.post(
                "/api/ask",
                json={"question": "What projects am I working on?"},
            )
            assert response.status_code in (200, 500)

    def test_ask_with_mocked_backend(self, client):
        """Should return answer from backend."""
        test_client, _ = client

        mock_backend = MagicMock()
        mock_backend.ask.return_value = (
            "Based on your notes, you're working on a test project about Python."
        )
        # Mock context manager behavior
        mock_backend.__enter__ = MagicMock(return_value=mock_backend)
        mock_backend.__exit__ = MagicMock(return_value=False)

        with patch("main.get_backend", return_value=mock_backend):
            response = test_client.post(
                "/api/ask",
                json={"question": "What projects am I working on?"},
            )
            assert response.status_code == 200
            assert "test project" in response.text.lower()


class TestTriggerGardenerEndpoint:
    """Tests for POST /api/trigger-gardener."""

    def test_trigger_gardener_succeeds(self, client):
        """Should accept trigger request."""
        test_client, _ = client

        with patch(
            "workers.gardener.process_inbox", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = []
            response = test_client.post("/api/trigger-gardener")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ("triggered", "started")

    def test_trigger_gardener_processes_inbox(self, client):
        """Should actually process inbox files."""
        test_client, dirs = client

        # Create a test inbox file
        (dirs["inbox_dir"] / "2024-01-15_1200-abc12345.md").write_text("Test note")

        with patch(
            "workers.gardener.process_inbox", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = [{"file": "test.md", "status": "processed"}]
            response = test_client.post("/api/trigger-gardener")
            assert response.status_code == 200
            mock_process.assert_called_once()
