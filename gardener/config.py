"""Centralized configuration for Gardener."""

import logging
import os
import sys
from pathlib import Path

# Logging configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.environ.get(
    "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def setup_logging() -> None:
    """Configure logging for the application.

    Log levels (set via LOG_LEVEL env var):
        DEBUG: Detailed debugging information
        INFO: General operational messages (default)
        WARNING: Something unexpected happened
        ERROR: A serious problem occurred
        CRITICAL: The application may not be able to continue
    """
    level = getattr(logging, LOG_LEVEL, logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Quiet down noisy libraries unless we're in DEBUG mode
    if level > logging.DEBUG:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("watchfiles").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


# Data directories
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
INBOX_DIR = DATA_DIR / "inbox"
ARCHIVE_DIR = INBOX_DIR / "archive"
ATLAS_DIR = DATA_DIR / "atlas"
META_DIR = DATA_DIR / "meta"
TASKS_FILE = DATA_DIR / "tasks.md"
AGENTS_FILE = DATA_DIR / "AGENTS.md"
GARDENER_FILE = DATA_DIR / "GARDENER.md"

# State tracking (SQLite)
STATE_DIR = DATA_DIR / ".gardener"
STATE_DB = STATE_DIR / "state.db"

# Gardener automation settings
GARDENER_AUTO = os.environ.get("GARDENER_AUTO", "false").lower() in ("true", "1", "yes")
GARDENER_MODE = os.environ.get("GARDENER_MODE", "watch")  # "watch" or "poll"
GARDENER_POLL_INTERVAL = int(os.environ.get("GARDENER_POLL_INTERVAL", "300"))  # seconds
GARDENER_DEBOUNCE = float(os.environ.get("GARDENER_DEBOUNCE", "5.0"))  # seconds

# Authentication (opt-in, disabled by default)
# Set ATHENA_AUTH_TOKEN to enable token authentication for API and MCP endpoints
AUTH_TOKEN = os.environ.get("ATHENA_AUTH_TOKEN", "").strip()
AUTH_ENABLED = bool(AUTH_TOKEN)

# Input validation
MAX_CONTENT_SIZE = int(os.environ.get("MAX_CONTENT_SIZE", "102400"))  # 100KB default
