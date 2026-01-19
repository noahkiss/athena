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
