"""Tests for the gardener worker - path validation and action execution."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from backends.base import GardenerAction


class TestExecuteActionPathValidation:
    """Test path validation security in execute_action."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary atlas and tasks directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            atlas_dir = Path(tmpdir) / "atlas"
            atlas_dir.mkdir()
            tasks_file = atlas_dir / "tasks.md"

            with (
                patch("workers.gardener.ATLAS_DIR", atlas_dir),
                patch("workers.gardener.TASKS_FILE", tasks_file),
            ):
                yield {"atlas": atlas_dir, "tasks": tasks_file}

    def test_rejects_absolute_path(self, temp_dirs):
        """Absolute paths should be rejected and content goes to tasks."""
        from workers.gardener import execute_action

        action = GardenerAction(
            action="create",
            path="/etc/passwd",
            content="Malicious content",
            reasoning="test",
        )

        result = execute_action(action)

        # Should go to tasks file instead
        assert result == temp_dirs["tasks"]
        assert temp_dirs["tasks"].exists()
        assert "Malicious content" in temp_dirs["tasks"].read_text()

    def test_rejects_path_traversal(self, temp_dirs):
        """Path traversal attempts should be rejected."""
        from workers.gardener import execute_action

        action = GardenerAction(
            action="create",
            path="../../../etc/passwd",
            content="Malicious content",
            reasoning="test",
        )

        result = execute_action(action)

        # Should go to tasks file instead
        assert result == temp_dirs["tasks"]

    def test_rejects_null_byte(self, temp_dirs):
        """Null bytes in path should be rejected."""
        from workers.gardener import execute_action

        action = GardenerAction(
            action="create",
            path="test\x00.md",
            content="Content",
            reasoning="test",
        )

        result = execute_action(action)
        assert result == temp_dirs["tasks"]

    def test_rejects_empty_path(self, temp_dirs):
        """Empty paths should be rejected."""
        from workers.gardener import execute_action

        action = GardenerAction(
            action="create",
            path="   ",
            content="Content",
            reasoning="test",
        )

        result = execute_action(action)
        assert result == temp_dirs["tasks"]

    def test_allows_valid_relative_path(self, temp_dirs):
        """Valid relative paths should work."""
        from workers.gardener import execute_action

        action = GardenerAction(
            action="create",
            path="projects/my-note.md",
            content="Valid content",
            reasoning="test",
        )

        result = execute_action(action)

        expected = temp_dirs["atlas"] / "projects" / "my-note.md"
        assert result == expected
        assert expected.exists()
        assert expected.read_text() == "Valid content"

    def test_allows_simple_filename(self, temp_dirs):
        """Simple filenames should work."""
        from workers.gardener import execute_action

        action = GardenerAction(
            action="create",
            path="note.md",
            content="Simple note",
            reasoning="test",
        )

        result = execute_action(action)

        expected = temp_dirs["atlas"] / "note.md"
        assert result == expected
        assert expected.read_text() == "Simple note"


class TestExecuteActionOperations:
    """Test file operations in execute_action."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary atlas and tasks directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            atlas_dir = Path(tmpdir) / "atlas"
            atlas_dir.mkdir()
            tasks_file = atlas_dir / "tasks.md"

            with (
                patch("workers.gardener.ATLAS_DIR", atlas_dir),
                patch("workers.gardener.TASKS_FILE", tasks_file),
            ):
                yield {"atlas": atlas_dir, "tasks": tasks_file}

    def test_create_action_creates_file(self, temp_dirs):
        """Create action should create a new file."""
        from workers.gardener import execute_action

        action = GardenerAction(
            action="create",
            path="new-file.md",
            content="New content",
            reasoning="test",
        )

        result = execute_action(action)

        assert result.exists()
        assert result.read_text() == "New content"

    def test_create_action_creates_subdirectories(self, temp_dirs):
        """Create action should create parent directories."""
        from workers.gardener import execute_action

        action = GardenerAction(
            action="create",
            path="deep/nested/path/file.md",
            content="Nested content",
            reasoning="test",
        )

        result = execute_action(action)

        assert result.exists()
        assert "deep/nested/path" in str(result)

    def test_append_action_appends_to_existing(self, temp_dirs):
        """Append action should add content with timestamp header."""
        from workers.gardener import execute_action

        # Create initial file
        existing_file = temp_dirs["atlas"] / "existing.md"
        existing_file.write_text("Existing content")

        action = GardenerAction(
            action="append",
            path="existing.md",
            content="Appended content",
            reasoning="test",
        )

        result = execute_action(action)

        content = result.read_text()
        assert "Existing content" in content
        assert "Appended content" in content
        assert "## Update" in content  # Timestamp header

    def test_append_action_creates_if_missing(self, temp_dirs):
        """Append action should create file if it doesn't exist."""
        from workers.gardener import execute_action

        action = GardenerAction(
            action="append",
            path="new-append.md",
            content="First content",
            reasoning="test",
        )

        result = execute_action(action)

        assert result.exists()
        assert "First content" in result.read_text()

    def test_task_action_appends_to_tasks(self, temp_dirs):
        """Task action should append to tasks.md."""
        from workers.gardener import execute_action

        action = GardenerAction(
            action="task",
            path="ignored",
            content="Task content",
            reasoning="Uncertain classification",
        )

        result = execute_action(action)

        assert result == temp_dirs["tasks"]
        content = result.read_text()
        assert "Task content" in content
        assert "Unsorted Note" in content
        assert "Gardener Query" in content


class TestClassifyNote:
    """Test classify_note function with mock backends."""

    @pytest.fixture
    def mock_backend(self):
        """Create a mock backend that returns predictable results."""
        from unittest.mock import MagicMock

        backend = MagicMock()
        backend.classify.return_value = GardenerAction(
            action="create",
            path="test.md",
            content="Processed content",
            reasoning="Test reasoning",
        )
        return backend

    def test_calls_backend_with_context(self, mock_backend):
        """classify_note should pass context to backend."""
        with (
            patch("workers.gardener.AGENTS_FILE") as mock_agents,
            patch("workers.gardener.GARDENER_FILE") as mock_gardener,
        ):
            mock_agents.exists.return_value = False
            mock_gardener.exists.return_value = False

            from workers.gardener import classify_note

            result = classify_note(mock_backend, "Note content", "test.md")

            mock_backend.classify.assert_called_once()
            args = mock_backend.classify.call_args
            assert args[0][0] == "Note content"
            assert args[0][1] == "test.md"
            assert result.action == "create"
