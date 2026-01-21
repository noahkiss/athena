"""OpenAI-compatible backend for gardener.

Works with:
- OpenAI directly
- LiteLLM proxy
- Azure OpenAI (with appropriate base_url)
- Ollama and other OpenAI-compatible APIs
"""

import logging

import httpx

from .base import (
    BackendConfig,
    GardenerAction,
    GardenerBackend,
    ParseError,
    parse_gardener_action,
)

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

ASK_PROMPT = """You are a knowledge assistant for a personal knowledge base.

Question:
{question}
{related_context}

Provide a concise answer based on the related context. If the notes don't contain enough information, say so and suggest what to capture next.
"""


class OpenAIBackend(GardenerBackend):
    """OpenAI-compatible backend using httpx."""

    def __init__(self, config: BackendConfig):
        super().__init__(config)
        base_url = config.base_url or "https://api.openai.com/v1"
        self._client = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=config.timeout,
        )

    @property
    def name(self) -> str:
        return "openai"

    def _chat(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """Send a chat completion request."""
        if not self.config.api_key:
            raise ValueError("API key not configured")

        if system:
            messages = [{"role": "system", "content": system}] + messages

        model_name = model or self.config.model_thinking
        response = self._client.post(
            "/chat/completions",
            json={
                "model": model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def classify(
        self,
        note_content: str,
        filename: str,
        context: str,
        max_retries: int = 2,
    ) -> GardenerAction:
        """Classify a note using OpenAI chat completions.

        Args:
            note_content: The raw note content
            filename: Original filename for context
            context: AGENTS.md + GARDENER.md content
            max_retries: Number of retries on parse errors (default 2)

        Returns:
            GardenerAction with classification result

        Raises:
            ParseError: If classification fails after all retries
        """
        user_message = f"""Please classify and process this note.

## Context Files
{context}

## Note to Process
**Filename:** {filename}
**Content:**
{note_content}

Respond with a JSON object specifying the action, path, and formatted content."""

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response_text = self._chat(
                    messages=[{"role": "user", "content": user_message}],
                    system=SYSTEM_PROMPT,
                    model=self.config.model_thinking,
                    temperature=0.3,
                )

                return parse_gardener_action(response_text)

            except ParseError as e:
                last_error = e
                if attempt < max_retries:
                    logger.info(
                        f"Parse error on attempt {attempt + 1}/{max_retries + 1} "
                        f"for {filename}, retrying..."
                    )
                    # Add hint to the message for retry
                    user_message = f"""Your previous response could not be parsed as valid JSON.
Error: {e}

Please try again with a properly formatted JSON response.

## Context Files
{context}

## Note to Process
**Filename:** {filename}
**Content:**
{note_content}

Respond with ONLY a valid JSON object (no markdown, no explanation):
{{"action": "create|append|task", "path": "...", "content": "...", "reasoning": "..."}}"""

        # All retries exhausted
        logger.error(
            f"Classification failed for {filename} after {max_retries + 1} attempts"
        )
        raise last_error

    def refine(self, content: str, related_context: str) -> str:
        """Get refinement suggestions."""
        prompt = REFINE_PROMPT.format(
            content=content,
            related_context=f"\n\nRelated files in knowledge base:\n{related_context}"
            if related_context
            else "",
        )

        return self._chat(
            messages=[{"role": "user", "content": prompt}],
            model=self.config.model_fast,
            max_tokens=1024,
            temperature=0.7,
        )

    def ask(self, question: str, related_context: str) -> str:
        """Answer a question using the knowledge base."""
        prompt = ASK_PROMPT.format(
            question=question,
            related_context=f"\n\nRelated files in knowledge base:\n{related_context}"
            if related_context
            else "",
        )

        return self._chat(
            messages=[{"role": "user", "content": prompt}],
            model=self.config.model_thinking,
            max_tokens=1024,
            temperature=0.4,
        )

    def close(self):
        """Close the HTTP client."""
        self._client.close()
