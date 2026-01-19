"""Gardener backend factory and exports."""

import os
import logging
from typing import Literal

from .base import BackendConfig, GardenerBackend, GardenerAction
from .openai import OpenAIBackend
from .anthropic import AnthropicBackend

logger = logging.getLogger(__name__)

BackendType = Literal["openai", "anthropic"]

# Default models for each backend
DEFAULT_MODELS = {
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-20250514",
}


def get_backend_config() -> tuple[BackendType, BackendConfig]:
    """Load backend configuration from environment variables.

    Environment variables:
        GARDENER_BACKEND: Backend type (openai, anthropic). Default: openai
        AI_API_KEY: API key (falls back to OPENAI_API_KEY or ANTHROPIC_API_KEY)
        AI_MODEL: Model to use (defaults vary by backend)
        AI_BASE_URL: Base URL for API (OpenAI backend only)
        AI_TIMEOUT: Request timeout in seconds. Default: 120
    """
    backend_type: BackendType = os.environ.get("GARDENER_BACKEND", "openai")  # type: ignore

    if backend_type not in ("openai", "anthropic"):
        logger.warning(f"Unknown backend '{backend_type}', falling back to openai")
        backend_type = "openai"

    # Get API key with fallbacks
    api_key = os.environ.get("AI_API_KEY", "")
    if not api_key:
        if backend_type == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        else:
            api_key = os.environ.get("OPENAI_API_KEY", "")

    model = os.environ.get("AI_MODEL", DEFAULT_MODELS.get(backend_type, "gpt-4o"))
    base_url = os.environ.get("AI_BASE_URL")
    timeout = float(os.environ.get("AI_TIMEOUT", "120"))

    config = BackendConfig(
        api_key=api_key,
        model=model,
        base_url=base_url,
        timeout=timeout,
    )

    return backend_type, config


def get_backend() -> GardenerBackend:
    """Get a configured gardener backend instance.

    Returns the appropriate backend based on GARDENER_BACKEND env var.
    """
    backend_type, config = get_backend_config()

    if backend_type == "anthropic":
        logger.info(f"Using Anthropic backend with model {config.model}")
        return AnthropicBackend(config)
    else:
        logger.info(f"Using OpenAI backend with model {config.model}")
        return OpenAIBackend(config)


__all__ = [
    "BackendConfig",
    "GardenerBackend",
    "GardenerAction",
    "OpenAIBackend",
    "AnthropicBackend",
    "get_backend",
    "get_backend_config",
]
