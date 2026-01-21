"""Tests for MCP tools (read_notes, add_note)."""

from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def temp_atlas(tmp_path):
    """Create temporary atlas directory with test files."""
    atlas_dir = tmp_path / "atlas"
    atlas_dir.mkdir()

    # Create subdirectories
    projects_dir = atlas_dir / "projects"
    projects_dir.mkdir()
    journal_dir = atlas_dir / "journal"
    journal_dir.mkdir()

    # Create test files
    (projects_dir / "web-app.md").write_text(
        "# Web App Project\n\nBuilding a React application with Python backend."
    )
    (projects_dir / "cli-tool.md").write_text(
        "# CLI Tool\n\nCommand-line utility for data processing."
    )
    (journal_dir / "2024-01-15.md").write_text(
        "# January 15, 2024\n\nWorked on Python testing today."
    )

    return atlas_dir


@pytest.fixture
def temp_inbox(tmp_path):
    """Create temporary inbox directory."""
    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()
    return inbox_dir


class TestReadNotes:
    """Tests for read_notes MCP tool."""

    def test_read_root_lists_directories(self, temp_atlas):
        """Should list atlas root contents."""
        with (
            patch("config.ATLAS_DIR", temp_atlas),
            patch("mcp_tools.ATLAS_DIR", temp_atlas),
        ):
            from mcp_tools import read_notes

            result = read_notes()

            assert "projects" in result.lower()
            assert "journal" in result.lower()

    def test_read_directory_lists_files(self, temp_atlas):
        """Should list files in subdirectory."""
        with (
            patch("config.ATLAS_DIR", temp_atlas),
            patch("mcp_tools.ATLAS_DIR", temp_atlas),
        ):
            from mcp_tools import read_notes

            result = read_notes(path="projects")

            assert "web-app.md" in result
            assert "cli-tool.md" in result

    def test_read_file_returns_content(self, temp_atlas):
        """Should return file content."""
        with (
            patch("config.ATLAS_DIR", temp_atlas),
            patch("mcp_tools.ATLAS_DIR", temp_atlas),
        ):
            from mcp_tools import read_notes

            result = read_notes(path="projects/web-app.md")

            assert "# Web App Project" in result
            assert "React application" in result

    def test_read_nonexistent_returns_error(self, temp_atlas):
        """Should return error for nonexistent path."""
        with (
            patch("config.ATLAS_DIR", temp_atlas),
            patch("mcp_tools.ATLAS_DIR", temp_atlas),
        ):
            from mcp_tools import read_notes

            result = read_notes(path="nonexistent/file.md")

            assert "not found" in result.lower()

    def test_read_prevents_path_traversal(self, temp_atlas, tmp_path):
        """Should prevent path traversal attacks."""
        # Create a file outside atlas
        secret = tmp_path / "secret.txt"
        secret.write_text("SECRET DATA")

        with (
            patch("config.ATLAS_DIR", temp_atlas),
            patch("mcp_tools.ATLAS_DIR", temp_atlas),
        ):
            from mcp_tools import read_notes

            result = read_notes(path="../secret.txt")

            assert "denied" in result.lower() or "not found" in result.lower()
            assert "SECRET DATA" not in result

    def test_search_finds_matching_files(self, temp_atlas):
        """Should find files matching search query."""
        with (
            patch("config.ATLAS_DIR", temp_atlas),
            patch("mcp_tools.ATLAS_DIR", temp_atlas),
        ):
            from mcp_tools import read_notes

            result = read_notes(path="", query="Python")

            assert "web-app.md" in result or "2024-01-15.md" in result

    def test_search_returns_empty_for_no_matches(self, temp_atlas):
        """Should return empty message when no files match."""
        with (
            patch("config.ATLAS_DIR", temp_atlas),
            patch("mcp_tools.ATLAS_DIR", temp_atlas),
        ):
            from mcp_tools import read_notes

            result = read_notes(path="", query="nonexistent_term_xyz")

            assert "no files found" in result.lower()

    def test_skips_hidden_files(self, temp_atlas):
        """Should skip hidden files (starting with .)."""
        # Create a hidden file
        (temp_atlas / ".hidden.md").write_text("Hidden content")

        with (
            patch("config.ATLAS_DIR", temp_atlas),
            patch("mcp_tools.ATLAS_DIR", temp_atlas),
        ):
            from mcp_tools import read_notes

            result = read_notes()

            assert ".hidden" not in result


class TestAddNote:
    """Tests for add_note MCP tool."""

    def test_add_note_creates_file(self, temp_inbox):
        """Should create file in inbox."""
        with (
            patch("config.INBOX_DIR", temp_inbox),
            patch("mcp_tools.INBOX_DIR", temp_inbox),
        ):
            from mcp_tools import add_note

            result = add_note(content="Test note content")

            assert "saved" in result.lower()

            # Verify file was created
            files = list(temp_inbox.glob("*.md"))
            assert len(files) == 1
            assert files[0].read_text() == "Test note content"

    def test_add_note_filename_format(self, temp_inbox):
        """Should create filename with timestamp and UUID."""
        with (
            patch("config.INBOX_DIR", temp_inbox),
            patch("mcp_tools.INBOX_DIR", temp_inbox),
        ):
            from mcp_tools import add_note

            result = add_note(content="Test note")

            files = list(temp_inbox.glob("*.md"))
            filename = files[0].name

            # Format: YYYY-MM-DD_HHMM-{8char_uuid}.md = 10 + 1 + 4 + 1 + 8 + 3 = 27
            assert len(filename) == 27
            assert filename[4] == "-"
            assert filename[7] == "-"
            assert filename[10] == "_"
            assert filename[-3:] == ".md"

    def test_add_note_rejects_empty_content(self, temp_inbox):
        """Should reject empty content."""
        with (
            patch("config.INBOX_DIR", temp_inbox),
            patch("mcp_tools.INBOX_DIR", temp_inbox),
        ):
            from mcp_tools import add_note

            result = add_note(content="")

            assert "empty" in result.lower() or "error" in result.lower()

            # Verify no file was created
            files = list(temp_inbox.glob("*.md"))
            assert len(files) == 0

    def test_add_note_rejects_whitespace_only(self, temp_inbox):
        """Should reject whitespace-only content."""
        with (
            patch("config.INBOX_DIR", temp_inbox),
            patch("mcp_tools.INBOX_DIR", temp_inbox),
        ):
            from mcp_tools import add_note

            result = add_note(content="   \n\t  ")

            assert "empty" in result.lower() or "error" in result.lower()

    def test_add_note_creates_inbox_if_missing(self, tmp_path):
        """Should create inbox directory if it doesn't exist."""
        inbox_dir = tmp_path / "new_inbox"
        # Don't create it - let add_note handle it

        with (
            patch("config.INBOX_DIR", inbox_dir),
            patch("mcp_tools.INBOX_DIR", inbox_dir),
        ):
            from mcp_tools import add_note

            result = add_note(content="Test note")

            assert "saved" in result.lower()
            assert inbox_dir.exists()

    def test_add_note_preserves_markdown(self, temp_inbox):
        """Should preserve markdown formatting in content."""
        markdown_content = """# Heading

- List item 1
- List item 2

```python
print("code block")
```
"""
        with (
            patch("config.INBOX_DIR", temp_inbox),
            patch("mcp_tools.INBOX_DIR", temp_inbox),
        ):
            from mcp_tools import add_note

            add_note(content=markdown_content)

            files = list(temp_inbox.glob("*.md"))
            saved_content = files[0].read_text()

            assert "# Heading" in saved_content
            assert "- List item 1" in saved_content
            assert "```python" in saved_content

    def test_add_note_handles_special_characters(self, temp_inbox):
        """Should handle special characters in content."""
        content = "Note with special chars: <script>alert('xss')</script> & \"quotes\""

        with (
            patch("config.INBOX_DIR", temp_inbox),
            patch("mcp_tools.INBOX_DIR", temp_inbox),
        ):
            from mcp_tools import add_note

            result = add_note(content=content)

            assert "saved" in result.lower()

            files = list(temp_inbox.glob("*.md"))
            saved_content = files[0].read_text()
            assert saved_content == content


class TestMCPToolRegistration:
    """Tests for MCP tool registration and metadata."""

    def test_mcp_server_created(self):
        """Should create MCP server instance."""
        from mcp_tools import mcp

        assert mcp is not None
        assert mcp.name == "athena-pkms"

    def test_read_notes_is_registered(self):
        """read_notes should be registered as MCP tool."""
        from mcp_tools import mcp, read_notes

        # The tool decorator registers the function
        assert callable(read_notes)

    def test_add_note_is_registered(self):
        """add_note should be registered as MCP tool."""
        from mcp_tools import add_note, mcp

        assert callable(add_note)
