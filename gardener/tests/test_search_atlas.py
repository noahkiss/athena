"""Tests for atlas search functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestSearchAtlas:
    """Test search_atlas function."""

    @pytest.fixture
    def temp_atlas(self):
        """Create a temporary atlas directory with test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            atlas_dir = Path(tmpdir) / "atlas"
            atlas_dir.mkdir()

            # Create test files
            (atlas_dir / "python.md").write_text(
                "# Python Programming\nPython is a great language for data science."
            )
            (atlas_dir / "javascript.md").write_text(
                "# JavaScript\nJavaScript is used for web development."
            )
            (atlas_dir / "data-science.md").write_text(
                "# Data Science\nData science uses Python and statistics."
            )

            # Create nested file
            nested = atlas_dir / "projects"
            nested.mkdir()
            (nested / "ml-project.md").write_text(
                "# ML Project\nMachine learning project using Python and TensorFlow."
            )

            with patch("main.ATLAS_DIR", atlas_dir):
                # Also clear the cache for each test
                from main import _atlas_content_cache

                _atlas_content_cache.clear()
                yield {"atlas_dir": atlas_dir}

    def test_finds_matching_files(self, temp_atlas):
        """Should find files containing keywords."""
        from main import search_atlas

        results = search_atlas(["python"])

        assert len(results) >= 2
        paths = [r["path"] for r in results]
        assert "python.md" in paths

    def test_scores_multiple_matches_higher(self, temp_atlas):
        """Files with more keyword matches should score higher."""
        from main import search_atlas

        results = search_atlas(["python", "data", "science"])

        # data-science.md mentions all three terms
        assert results[0]["path"] == "data-science.md"

    def test_returns_preview(self, temp_atlas):
        """Should include preview of matched files."""
        from main import search_atlas

        results = search_atlas(["javascript"])

        assert len(results) == 1
        assert "preview" in results[0]
        assert "JavaScript" in results[0]["preview"]

    def test_respects_max_files(self, temp_atlas):
        """Should limit results to max_files."""
        from main import search_atlas

        results = search_atlas(["python"], max_files=1)

        assert len(results) == 1

    def test_finds_nested_files(self, temp_atlas):
        """Should find files in subdirectories."""
        from main import search_atlas

        results = search_atlas(["tensorflow"])

        assert len(results) == 1
        assert "projects/ml-project.md" in results[0]["path"]

    def test_returns_empty_for_no_matches(self, temp_atlas):
        """Should return empty list when no matches found."""
        from main import search_atlas

        results = search_atlas(["nonexistent", "keyword"])

        assert results == []

    def test_case_insensitive_search(self, temp_atlas):
        """Should match keywords case-insensitively."""
        from main import search_atlas

        results = search_atlas(["PYTHON"])

        assert len(results) >= 2

    def test_handles_missing_atlas_dir(self):
        """Should return empty list if atlas directory doesn't exist."""
        with patch("main.ATLAS_DIR", Path("/nonexistent/path")):
            from main import search_atlas

            results = search_atlas(["test"])
            assert results == []


class TestFileContentCache:
    """Test the file content cache."""

    def test_cache_stores_content(self):
        """Cache should store and retrieve content."""
        from main import FileContentCache

        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileContentCache()
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Hello, World!")

            cache.put(test_file, "Hello, World!")
            result = cache.get(test_file)

            assert result == "Hello, World!"

    def test_cache_invalidates_on_mtime_change(self):
        """Cache should invalidate when file is modified."""
        import time

        from main import FileContentCache

        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileContentCache()
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Original content")

            cache.put(test_file, "Original content")

            # Modify the file
            time.sleep(0.01)  # Ensure mtime changes
            test_file.write_text("Modified content")

            result = cache.get(test_file)
            assert result is None  # Should be invalidated

    def test_cache_returns_none_for_missing(self):
        """Cache should return None for uncached paths."""
        from main import FileContentCache

        cache = FileContentCache()
        result = cache.get(Path("/nonexistent/file.txt"))

        assert result is None

    def test_cache_evicts_oldest_when_full(self):
        """Cache should evict oldest entry when at capacity."""
        import time

        from main import FileContentCache

        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileContentCache(max_entries=2)

            f1 = Path(tmpdir) / "file1.txt"
            f2 = Path(tmpdir) / "file2.txt"
            f3 = Path(tmpdir) / "file3.txt"
            f1.write_text("content1")
            f2.write_text("content2")
            f3.write_text("content3")

            cache.put(f1, "content1")
            time.sleep(0.01)
            cache.put(f2, "content2")
            time.sleep(0.01)
            cache.put(f3, "content3")  # Should evict f1

            assert cache.get(f1) is None  # Evicted
            assert cache.get(f2) == "content2"
            assert cache.get(f3) == "content3"


class TestExtractKeywords:
    """Test keyword extraction."""

    def test_extracts_words(self):
        """Should extract non-stopword words."""
        from main import extract_keywords

        keywords = extract_keywords("Python is a programming language")

        assert "python" in keywords
        assert "programming" in keywords
        assert "language" in keywords

    def test_removes_stopwords(self):
        """Should remove common stopwords."""
        from main import extract_keywords

        keywords = extract_keywords("this is about that with some other")

        assert "this" not in keywords
        assert "about" not in keywords
        assert "that" not in keywords

    def test_removes_short_words(self):
        """Should remove words with 3 or fewer characters."""
        from main import extract_keywords

        keywords = extract_keywords("a to an the big dog")

        assert "a" not in keywords
        assert "to" not in keywords
        assert "an" not in keywords
        assert "the" not in keywords

    def test_limits_keyword_count(self):
        """Should limit to 20 keywords max."""
        from main import extract_keywords

        long_text = " ".join([f"word{i}" for i in range(100)])
        keywords = extract_keywords(long_text)

        assert len(keywords) <= 20
