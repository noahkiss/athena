"""Abstract base class for gardener AI backends."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel


class GardenerAction(BaseModel):
    """Response model for gardener classification."""

    action: Literal["create", "append", "task"]
    path: str
    content: str
    reasoning: str


@dataclass
class BackendConfig:
    """Base configuration for all backends."""

    api_key: str
    model: str
    base_url: str | None = None
    timeout: float = 120.0


class GardenerBackend(ABC):
    """Abstract base class for gardener AI backends.

    Each backend implements a different way to classify notes:
    - OpenAI: Standard chat completions API
    - Anthropic: Native Claude API with prompt caching
    - Agentic: Tool-use pattern for complex classification
    """

    def __init__(self, config: BackendConfig):
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the backend name for logging/status."""
        ...

    @abstractmethod
    def classify(
        self,
        note_content: str,
        filename: str,
        context: str,
    ) -> GardenerAction:
        """Classify a note and return the action to take.

        Args:
            note_content: The raw note content from inbox
            filename: Original filename (for context)
            context: Concatenated AGENTS.md + GARDNER.md content

        Returns:
            GardenerAction with action type, path, content, and reasoning
        """
        ...

    @abstractmethod
    def refine(self, content: str, related_context: str) -> str:
        """Get refinement suggestions for content.

        Args:
            content: The note content to refine
            related_context: Related files found in atlas

        Returns:
            Formatted suggestions (TAGS, CATEGORY, RELATED, MISSING)
        """
        ...

    def close(self):
        """Clean up resources. Override if needed."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
