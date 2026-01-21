"""Abstract base class for gardener AI backends."""

import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class GardenerAction(BaseModel):
    """Response model for gardener classification."""

    action: Literal["create", "append", "task"]
    path: str
    content: str
    reasoning: str


class ParseError(Exception):
    """Raised when LLM response cannot be parsed into GardenerAction."""

    def __init__(
        self, message: str, response_text: str, original_error: Exception | None = None
    ):
        super().__init__(message)
        self.response_text = response_text
        self.original_error = original_error


def extract_json_from_response(response_text: str) -> str:
    """Extract JSON string from LLM response, handling markdown code blocks.

    Args:
        response_text: Raw response from the LLM

    Returns:
        Extracted JSON string

    Raises:
        ParseError: If no valid JSON structure can be found
    """
    text = response_text.strip()

    # Try markdown code block with json tag
    if "```json" in text:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

    # Try generic markdown code block
    if "```" in text:
        match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

    # Try to find JSON object directly (starts with { and ends with })
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)

    # Return the whole text as a last resort
    return text


def parse_gardener_action(response_text: str) -> GardenerAction:
    """Parse LLM response into a GardenerAction.

    Args:
        response_text: Raw response from the LLM

    Returns:
        Validated GardenerAction

    Raises:
        ParseError: If the response cannot be parsed or validated
    """
    try:
        json_str = extract_json_from_response(response_text)
        data = json.loads(json_str)
        return GardenerAction(**data)
    except json.JSONDecodeError as e:
        logger.warning(
            f"JSON parse error: {e}. Response preview: {response_text[:500]}"
        )
        raise ParseError(
            f"Invalid JSON in response: {e}",
            response_text=response_text,
            original_error=e,
        )
    except ValidationError as e:
        logger.warning(
            f"Validation error: {e}. Response preview: {response_text[:500]}"
        )
        raise ParseError(
            f"Response missing required fields: {e}",
            response_text=response_text,
            original_error=e,
        )


@dataclass
class BackendConfig:
    """Base configuration for all backends."""

    api_key: str
    model_thinking: str
    model_fast: str
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
            context: Concatenated AGENTS.md + GARDENER.md content

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

    @abstractmethod
    def ask(self, question: str, related_context: str) -> str:
        """Answer a question using related knowledge base context.

        Args:
            question: The user's question
            related_context: Related files found in atlas

        Returns:
            A concise answer
        """
        ...

    def close(self):
        """Clean up resources. Override if needed."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
