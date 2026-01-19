"""Native Anthropic Claude backend for gardener.

Uses the Anthropic SDK directly for:
- Native Claude features
- Prompt caching support
- Better error handling
"""

import json
import logging

import anthropic

from .base import BackendConfig, GardenerBackend, GardenerAction

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Gardener, an AI agent responsible for organizing notes in a Personal Knowledge Management System.

Your task is to analyze incoming notes and decide where they belong in the knowledge base.

You MUST respond with a valid JSON object matching this schema:
{
  "action": "create" | "append" | "task",
  "path": "relative path from /atlas, e.g., 'projects/my-project.md'",
  "content": "the formatted markdown content to write",
  "reasoning": "brief explanation of your decision"
}

Actions:
- "create": Create a new file at the specified path
- "append": Append to an existing file (include timestamp header)
- "task": Add to tasks.md because classification is uncertain (<80% confidence)

IMPORTANT: Always preserve the user's exact words in a "## Raw Source" section at the end of the file."""

REFINE_PROMPT = """Analyze this note and provide brief suggestions.

Note content:
{content}
{related_context}

Respond in this exact format (keep it brief):
TAGS: tag1, tag2, tag3
CATEGORY: suggested category (projects/people/home/wellness/tech/journal/reading)
RELATED: any related topics or files mentioned above
MISSING: what context might improve this note (1 sentence)"""


class AnthropicBackend(GardenerBackend):
    """Native Anthropic Claude backend."""

    def __init__(self, config: BackendConfig):
        super().__init__(config)
        self._client = anthropic.Anthropic(
            api_key=config.api_key,
            timeout=config.timeout,
        )

    @property
    def name(self) -> str:
        return "anthropic"

    def _chat(
        self,
        user_message: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """Send a message to Claude."""
        if not self.config.api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")

        response = self._client.messages.create(
            model=self.config.model,
            max_tokens=max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": user_message}],
            temperature=temperature,
        )

        return response.content[0].text

    def classify(
        self,
        note_content: str,
        filename: str,
        context: str,
    ) -> GardenerAction:
        """Classify a note using Claude."""
        user_message = f"""Please classify and process this note.

## Context Files
{context}

## Note to Process
**Filename:** {filename}
**Content:**
{note_content}

Respond with a JSON object specifying the action, path, and formatted content."""

        response_text = self._chat(
            user_message=user_message,
            system=SYSTEM_PROMPT,
            temperature=0.3,
        )

        # Extract JSON from response
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text.strip()

        data = json.loads(json_str)
        return GardenerAction(**data)

    def refine(self, content: str, related_context: str) -> str:
        """Get refinement suggestions."""
        prompt = REFINE_PROMPT.format(
            content=content,
            related_context=f"\n\nRelated files in knowledge base:\n{related_context}" if related_context else "",
        )

        return self._chat(
            user_message=prompt,
            max_tokens=1024,
            temperature=0.7,
        )

    def close(self):
        """Close the Anthropic client."""
        self._client.close()
