"""AI client abstraction supporting OpenAI-compatible endpoints (including LiteLLM)."""

import os
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class AIConfig:
    """Configuration for AI provider."""

    base_url: str
    api_key: str
    model_fast: str  # For quick tasks (refine suggestions)
    model_thinking: str  # For complex tasks (classification)

    @classmethod
    def from_env(cls) -> "AIConfig":
        """Load configuration from environment variables."""
        return cls(
            base_url=os.environ.get("AI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.environ.get("AI_API_KEY", os.environ.get("OPENAI_API_KEY", "")),
            model_fast=os.environ.get("AI_MODEL_FAST", "gpt-4o-mini"),
            model_thinking=os.environ.get("AI_MODEL_THINKING", "gpt-4o"),
        )


class AIClient:
    """
    OpenAI-compatible AI client.

    Works with:
    - OpenAI directly
    - LiteLLM proxy
    - Azure OpenAI (with appropriate base_url)
    - Any OpenAI-compatible API
    """

    def __init__(self, config: AIConfig | None = None):
        self.config = config or AIConfig.from_env()
        self._client = httpx.Client(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to model_thinking)
            system: Optional system prompt (prepended to messages)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            The assistant's response text
        """
        if not self.config.api_key:
            raise ValueError("AI_API_KEY or OPENAI_API_KEY environment variable not set")

        model = model or self.config.model_thinking

        # Prepend system message if provided
        if system:
            messages = [{"role": "system", "content": system}] + messages

        response = self._client.post(
            "/chat/completions",
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    def chat_fast(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> str:
        """Chat using the fast model (for quick tasks like suggestions)."""
        return self.chat(
            messages=messages,
            model=self.config.model_fast,
            system=system,
            max_tokens=max_tokens,
            temperature=0.7,
        )

    def chat_thinking(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> str:
        """Chat using the thinking model (for complex tasks like classification)."""
        return self.chat(
            messages=messages,
            model=self.config.model_thinking,
            system=system,
            max_tokens=max_tokens,
            temperature=0.3,  # Lower temperature for more consistent classification
        )

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# Convenience function for one-off calls
def get_client() -> AIClient:
    """Get an AI client configured from environment."""
    return AIClient()
