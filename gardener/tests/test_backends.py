"""Tests for LLM backend implementations."""

from unittest.mock import MagicMock, patch

import pytest

from backends.base import BackendConfig, GardenerAction, ParseError


@pytest.fixture
def backend_config():
    """Standard backend configuration for tests."""
    return BackendConfig(
        api_key="test-api-key",
        model_thinking="test-model",
        model_fast="test-model-fast",
        base_url="https://api.example.com",
        timeout=30.0,
    )


class TestOpenAIBackend:
    """Tests for OpenAI-compatible backend."""

    def test_initialization(self, backend_config):
        """Should initialize with config."""
        with patch("httpx.Client"):
            from backends.openai import OpenAIBackend

            backend = OpenAIBackend(backend_config)
            assert backend.name == "openai"
            assert backend.config == backend_config

    def test_classify_success(self, backend_config):
        """Should parse valid classification response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"action": "create", "path": "projects/new.md", "content": "# New Project", "reasoning": "Test"}'
                    }
                }
            ]
        }

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            from backends.openai import OpenAIBackend

            backend = OpenAIBackend(backend_config)
            result = backend.classify(
                note_content="New project idea",
                filename="test.md",
                context="User context here",
            )

            assert isinstance(result, GardenerAction)
            assert result.action == "create"
            assert result.path == "projects/new.md"

    def test_classify_with_markdown_json(self, backend_config):
        """Should extract JSON from markdown code blocks."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": """Here's my classification:

```json
{
  "action": "append",
  "path": "journal/daily.md",
  "content": "Entry here",
  "reasoning": "Fits journal pattern"
}
```

Let me know if you need anything else."""
                    }
                }
            ]
        }

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            from backends.openai import OpenAIBackend

            backend = OpenAIBackend(backend_config)
            result = backend.classify(
                note_content="Daily thoughts",
                filename="test.md",
                context="Context",
            )

            assert result.action == "append"
            assert result.path == "journal/daily.md"

    def test_classify_invalid_json_raises(self, backend_config):
        """Should raise ParseError on invalid JSON."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This is not JSON at all"}}]
        }

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            from backends.openai import OpenAIBackend

            backend = OpenAIBackend(backend_config)
            with pytest.raises(ParseError):
                backend.classify(
                    note_content="Test note",
                    filename="test.md",
                    context="Context",
                )

    def test_refine_returns_suggestions(self, backend_config):
        """Should return refinement suggestions."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "TAGS: python, testing\nCATEGORY: tech\nRELATED: None\nMISSING: None"
                    }
                }
            ]
        }

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            from backends.openai import OpenAIBackend

            backend = OpenAIBackend(backend_config)
            result = backend.refine(
                content="Python testing tips",
                related_context="Related files here",
            )

            assert "TAGS" in result
            assert "python" in result.lower()

    def test_ask_returns_answer(self, backend_config):
        """Should return answer to question."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Based on your notes, you have 3 active projects."}}
            ]
        }

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            from backends.openai import OpenAIBackend

            backend = OpenAIBackend(backend_config)
            result = backend.ask(
                question="How many projects do I have?",
                related_context="Project files here",
            )

            assert "3" in result
            assert "projects" in result.lower()


class TestAnthropicBackend:
    """Tests for Anthropic Claude backend."""

    def test_initialization(self, backend_config):
        """Should initialize with config."""
        with patch("anthropic.Anthropic"):
            from backends.anthropic import AnthropicBackend

            backend = AnthropicBackend(backend_config)
            assert backend.name == "anthropic"

    def test_classify_success(self, backend_config):
        """Should parse valid classification response."""
        mock_message = MagicMock()
        mock_message.content = [
            MagicMock(
                text='{"action": "create", "path": "tech/servers.md", "content": "# Server Setup", "reasoning": "Technical content"}'
            )
        ]

        with patch("anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            from backends.anthropic import AnthropicBackend

            backend = AnthropicBackend(backend_config)
            result = backend.classify(
                note_content="Server configuration notes",
                filename="test.md",
                context="User context",
            )

            assert isinstance(result, GardenerAction)
            assert result.action == "create"
            assert result.path == "tech/servers.md"

    def test_classify_retries_on_parse_error(self, backend_config):
        """Should retry on ParseError up to max_retries."""
        # First call returns invalid, second returns valid
        mock_message_invalid = MagicMock()
        mock_message_invalid.content = [MagicMock(text="Not valid JSON")]

        mock_message_valid = MagicMock()
        mock_message_valid.content = [
            MagicMock(
                text='{"action": "task", "path": "tasks.md", "content": "Unclear note", "reasoning": "Uncertain"}'
            )
        ]

        with patch("anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.side_effect = [
                mock_message_invalid,
                mock_message_valid,
            ]
            mock_anthropic.return_value = mock_client

            from backends.anthropic import AnthropicBackend

            backend = AnthropicBackend(backend_config)
            result = backend.classify(
                note_content="Ambiguous note",
                filename="test.md",
                context="Context",
            )

            assert result.action == "task"
            assert mock_client.messages.create.call_count == 2

    def test_classify_raises_after_max_retries(self, backend_config):
        """Should raise ParseError after exhausting retries."""
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Never valid JSON")]

        with patch("anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            from backends.anthropic import AnthropicBackend

            backend = AnthropicBackend(backend_config)
            with pytest.raises(ParseError):
                backend.classify(
                    note_content="Test",
                    filename="test.md",
                    context="Context",
                )

    def test_refine_returns_suggestions(self, backend_config):
        """Should return refinement suggestions."""
        mock_message = MagicMock()
        mock_message.content = [
            MagicMock(text="TAGS: homelab, docker\nCATEGORY: tech\nRELATED: None\nMISSING: None")
        ]

        with patch("anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            from backends.anthropic import AnthropicBackend

            backend = AnthropicBackend(backend_config)
            result = backend.refine(
                content="Docker container setup",
                related_context="Related docs",
            )

            assert "TAGS" in result
            assert "docker" in result.lower()

    def test_ask_returns_answer(self, backend_config):
        """Should return answer to question."""
        mock_message = MagicMock()
        mock_message.content = [
            MagicMock(text="Your homelab runs Docker on a Proxmox host.")
        ]

        with patch("anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            from backends.anthropic import AnthropicBackend

            backend = AnthropicBackend(backend_config)
            result = backend.ask(
                question="What does my homelab run?",
                related_context="Homelab notes",
            )

            assert "Docker" in result


class TestBackendFactory:
    """Tests for backend factory function."""

    def test_get_backend_config_returns_empty_key_without_api_key(self):
        """Should return empty api_key when no API key configured."""
        from backends import get_backend_config

        # Test with empty environment
        with patch.dict(
            "os.environ",
            {"AI_API_KEY": "", "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""},
            clear=False,
        ):
            # get_backend_config returns (backend_type, config)
            backend_type, config = get_backend_config()
            # If no API key in env, config.api_key will be empty
            assert config.api_key == ""

    def test_get_backend_selects_openai(self):
        """Should select OpenAI backend when configured."""
        with patch("anthropic.Anthropic"):
            with patch.dict(
                "os.environ",
                {
                    "GARDENER_BACKEND": "openai",
                    "AI_API_KEY": "test-key",
                    "AI_MODEL_THINKING": "gpt-4o",
                    "AI_MODEL_FAST": "gpt-4o-mini",
                },
            ):
                from backends import get_backend
                from backends.openai import OpenAIBackend

                result = get_backend()
                assert isinstance(result, OpenAIBackend)

    def test_get_backend_selects_anthropic(self):
        """Should select Anthropic backend when configured."""
        with patch("anthropic.Anthropic"):
            with patch.dict(
                "os.environ",
                {
                    "GARDENER_BACKEND": "anthropic",
                    "AI_API_KEY": "test-key",
                    "AI_MODEL_THINKING": "claude-sonnet-4-20250514",
                    "AI_MODEL_FAST": "claude-3-haiku-20240307",
                },
            ):
                from backends import get_backend
                from backends.anthropic import AnthropicBackend

                result = get_backend()
                assert isinstance(result, AnthropicBackend)


class TestGardenerActionValidation:
    """Tests for GardenerAction model validation."""

    def test_valid_create_action(self):
        """Should accept valid create action."""
        action = GardenerAction(
            action="create",
            path="projects/new.md",
            content="# New Project",
            reasoning="New project note",
        )
        assert action.action == "create"

    def test_valid_append_action(self):
        """Should accept valid append action."""
        action = GardenerAction(
            action="append",
            path="journal/daily.md",
            content="New entry",
            reasoning="Daily journal update",
        )
        assert action.action == "append"

    def test_valid_task_action(self):
        """Should accept valid task action."""
        action = GardenerAction(
            action="task",
            path="tasks.md",
            content="Unclear note",
            reasoning="Uncertain classification",
        )
        assert action.action == "task"

    def test_rejects_invalid_action_type(self):
        """Should reject invalid action types."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            GardenerAction(
                action="delete",  # Invalid action
                path="file.md",
                content="Content",
                reasoning="Reason",
            )

    def test_rejects_missing_fields(self):
        """Should reject missing required fields."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            GardenerAction(
                action="create",
                # Missing path, content, reasoning
            )

    def test_accepts_extra_fields(self):
        """Should accept (and ignore) extra fields from LLM."""
        action = GardenerAction(
            action="create",
            path="test.md",
            content="Content",
            reasoning="Reason",
            extra_field="ignored",  # LLMs sometimes add extra fields
        )
        assert action.action == "create"
        assert not hasattr(action, "extra_field")
