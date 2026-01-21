"""Tests for XSS sanitization in HTML rendering functions."""


class TestFormatRefineHtmlSanitization:
    """Test that format_refine_html properly escapes dangerous content."""

    def test_escapes_script_tags_in_tags(self):
        """Script tags in TAGS field should be escaped."""
        from main import format_refine_html

        malicious = 'TAGS: <script>alert("xss")</script>'
        result = format_refine_html(malicious)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_escapes_script_tags_in_category(self):
        """Script tags in CATEGORY field should be escaped."""
        from main import format_refine_html

        malicious = 'CATEGORY: <script>alert("xss")</script>'
        result = format_refine_html(malicious)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_escapes_script_tags_in_related(self):
        """Script tags in RELATED field should be escaped."""
        from main import format_refine_html

        malicious = 'RELATED: <script>alert("xss")</script>'
        result = format_refine_html(malicious)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_escapes_script_tags_in_missing(self):
        """Script tags in MISSING field should be escaped."""
        from main import format_refine_html

        malicious = 'MISSING: <script>alert("xss")</script>'
        result = format_refine_html(malicious)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_escapes_event_handlers(self):
        """Event handlers like onload should be escaped."""
        from main import format_refine_html

        malicious = 'TAGS: <img src=x onerror="alert(1)">'
        result = format_refine_html(malicious)
        assert 'onerror="alert(1)"' not in result
        assert "&lt;img" in result

    def test_escapes_javascript_urls(self):
        """JavaScript URLs should be escaped."""
        from main import format_refine_html

        malicious = 'TAGS: <a href="javascript:alert(1)">click</a>'
        result = format_refine_html(malicious)
        assert "javascript:" not in result or 'href="javascript:' not in result
        assert "&lt;a" in result


class TestFormatAskHtmlSanitization:
    """Test that format_ask_html properly escapes dangerous content."""

    def test_escapes_script_tags_in_answer(self):
        """Script tags in answer should be escaped."""
        from main import format_ask_html

        malicious = '<script>alert("xss")</script>'
        result = format_ask_html(malicious, [])
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_escapes_script_tags_in_related_paths(self):
        """Script tags in related file paths should be escaped."""
        from main import format_ask_html

        related = [{"path": '<script>alert("xss")</script>'}]
        result = format_ask_html("answer", related)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_escapes_html_entities_in_answer(self):
        """HTML entities in answer should be escaped."""
        from main import format_ask_html

        malicious = '<img src=x onerror="alert(1)">'
        result = format_ask_html(malicious, [])
        assert 'onerror="alert(1)"' not in result
        assert "&lt;img" in result


class TestMultipleFieldsInRefine:
    """Test sanitization with multiple fields at once."""

    def test_all_fields_escaped(self):
        """All fields in a multi-line result should be escaped."""
        from main import format_refine_html

        malicious = """TAGS: <script>1</script>
CATEGORY: <script>2</script>
RELATED: <script>3</script>
MISSING: <script>4</script>"""
        result = format_refine_html(malicious)
        assert result.count("<script>") == 0
        assert result.count("&lt;script&gt;") == 4
