"""Tests for LLM JSON response parsing."""

import pytest

from backends.base import (
    GardenerAction,
    ParseError,
    extract_json_from_response,
    parse_gardener_action,
)


class TestExtractJsonFromResponse:
    """Test JSON extraction from various response formats."""

    def test_extracts_from_json_code_block(self):
        """Should extract JSON from ```json ... ``` blocks."""
        response = """Here is my response:

```json
{"action": "create", "path": "test.md", "content": "Hello", "reasoning": "test"}
```

That's the classification."""

        result = extract_json_from_response(response)
        assert '"action": "create"' in result
        assert '"path": "test.md"' in result

    def test_extracts_from_generic_code_block(self):
        """Should extract JSON from ``` ... ``` blocks."""
        response = """```
{"action": "append", "path": "notes.md", "content": "Content", "reasoning": "why"}
```"""

        result = extract_json_from_response(response)
        assert '"action": "append"' in result

    def test_extracts_bare_json(self):
        """Should extract JSON when not in a code block."""
        response = """{"action": "task", "path": "tasks.md", "content": "Todo", "reasoning": "uncertain"}"""

        result = extract_json_from_response(response)
        assert result == response

    def test_extracts_json_with_surrounding_text(self):
        """Should find JSON object in surrounding text."""
        response = """I'll classify this as:
{"action": "create", "path": "new.md", "content": "New note", "reasoning": "new file"}
Let me know if you need anything else."""

        result = extract_json_from_response(response)
        assert '"action": "create"' in result


class TestParseGardenerAction:
    """Test parsing and validation of GardenerAction."""

    def test_parses_valid_json(self):
        """Should parse valid JSON into GardenerAction."""
        response = '{"action": "create", "path": "test.md", "content": "Hello", "reasoning": "test"}'

        result = parse_gardener_action(response)

        assert isinstance(result, GardenerAction)
        assert result.action == "create"
        assert result.path == "test.md"
        assert result.content == "Hello"
        assert result.reasoning == "test"

    def test_parses_json_in_code_block(self):
        """Should handle JSON in markdown code block."""
        response = """```json
{"action": "append", "path": "log.md", "content": "Entry", "reasoning": "log entry"}
```"""

        result = parse_gardener_action(response)
        assert result.action == "append"

    def test_raises_on_invalid_json(self):
        """Should raise ParseError for invalid JSON."""
        response = "This is not JSON at all"

        with pytest.raises(ParseError) as exc_info:
            parse_gardener_action(response)

        assert "Invalid JSON" in str(exc_info.value)
        assert exc_info.value.response_text == response

    def test_raises_on_missing_fields(self):
        """Should raise ParseError when required fields are missing."""
        response = (
            '{"action": "create", "path": "test.md"}'  # missing content and reasoning
        )

        with pytest.raises(ParseError) as exc_info:
            parse_gardener_action(response)

        assert "missing required fields" in str(exc_info.value).lower()

    def test_raises_on_invalid_action(self):
        """Should raise ParseError for invalid action values."""
        response = (
            '{"action": "delete", "path": "test.md", "content": "x", "reasoning": "y"}'
        )

        with pytest.raises(ParseError) as exc_info:
            parse_gardener_action(response)

        # Pydantic validation error for invalid literal
        assert exc_info.value.original_error is not None

    def test_handles_extra_fields(self):
        """Should ignore extra fields in the response."""
        response = """{"action": "create", "path": "test.md", "content": "Hello",
                      "reasoning": "test", "extra_field": "ignored"}"""

        result = parse_gardener_action(response)
        assert result.action == "create"

    def test_handles_multiline_content(self):
        """Should handle JSON with multiline content."""
        response = """{"action": "create", "path": "test.md",
        "content": "Line 1\\nLine 2\\nLine 3",
        "reasoning": "multi-line note"}"""

        result = parse_gardener_action(response)
        assert "Line 1" in result.content


class TestParseErrorDetails:
    """Test that ParseError contains useful debugging information."""

    def test_contains_response_text(self):
        """ParseError should contain the original response text."""
        bad_response = "not json {broken"

        with pytest.raises(ParseError) as exc_info:
            parse_gardener_action(bad_response)

        assert exc_info.value.response_text == bad_response

    def test_contains_original_error(self):
        """ParseError should contain the original exception."""
        bad_response = "not json"

        with pytest.raises(ParseError) as exc_info:
            parse_gardener_action(bad_response)

        assert exc_info.value.original_error is not None
