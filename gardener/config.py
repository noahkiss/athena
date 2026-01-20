"""Centralized configuration for Gardner."""

import os
from pathlib import Path

# Data directories
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
INBOX_DIR = DATA_DIR / "inbox"
ATLAS_DIR = DATA_DIR / "atlas"
TASKS_FILE = DATA_DIR / "tasks.md"
AGENTS_FILE = DATA_DIR / "AGENTS.md"
GARDNER_FILE = DATA_DIR / "GARDNER.md"

# Gardener automation settings
GARDENER_AUTO = os.environ.get("GARDENER_AUTO", "false").lower() in ("true", "1", "yes")
GARDENER_MODE = os.environ.get("GARDENER_MODE", "watch")  # "watch" or "poll"
GARDENER_POLL_INTERVAL = int(os.environ.get("GARDENER_POLL_INTERVAL", "300"))  # seconds
GARDENER_DEBOUNCE = float(os.environ.get("GARDENER_DEBOUNCE", "5.0"))  # seconds
