"""The Gardener - AI-powered inbox processor for Athena PKMS."""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

from backends import GardenerAction, GardenerBackend, get_backend
from config import DATA_DIR, INBOX_DIR, ATLAS_DIR, TASKS_FILE, AGENTS_FILE, GARDNER_FILE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_context_files() -> str:
    """Read AGENTS.md and GARDNER.md for context."""
    context_parts = []

    if AGENTS_FILE.exists():
        context_parts.append(f"# System Context\n{AGENTS_FILE.read_text()}")

    if GARDNER_FILE.exists():
        context_parts.append(f"# Classification Rules\n{GARDNER_FILE.read_text()}")

    return "\n\n---\n\n".join(context_parts)


def classify_note(backend: GardenerBackend, note_content: str, filename: str) -> GardenerAction:
    """Send note to AI backend for classification."""
    context = read_context_files()
    return backend.classify(note_content, filename, context)


def execute_action(action: GardenerAction) -> Path:
    """Execute the file operation based on gardener's decision."""
    if action.action == "task":
        # Append to tasks.md
        TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TASKS_FILE, "a") as f:
            f.write(f"\n\n## Unsorted Note {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(action.content)
            f.write(f"\n\n> Gardener Query: {action.reasoning}\n")
        return TASKS_FILE

    target_path = ATLAS_DIR / action.path
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if action.action == "create":
        target_path.write_text(action.content)
    elif action.action == "append":
        existing = target_path.read_text() if target_path.exists() else ""
        timestamp_header = f"\n\n---\n## Update {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        target_path.write_text(existing + timestamp_header + action.content)

    return target_path


def is_git_available() -> bool:
    """Check if git is installed and available."""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def ensure_git_repo() -> bool:
    """Initialize git repo in DATA_DIR if it doesn't exist."""
    if not is_git_available():
        logger.warning("Git is not installed, skipping version control")
        return False

    git_dir = DATA_DIR / ".git"
    if git_dir.exists():
        return True

    try:
        subprocess.run(["git", "init"], cwd=DATA_DIR, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "gardener@athena.local"],
            cwd=DATA_DIR,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Athena Gardener"],
            cwd=DATA_DIR,
            check=True,
            capture_output=True,
        )
        logger.info("Initialized git repository in data directory")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to initialize git repo: {e}")
        return False


def git_commit(file_path: Path, message: str) -> bool:
    """Commit changes to git."""
    if not is_git_available():
        return False

    try:
        subprocess.run(["git", "add", str(file_path)], cwd=DATA_DIR, check=True, capture_output=True)
        # Check if there are staged changes before committing
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=DATA_DIR,
            capture_output=True,
        )
        if result.returncode != 0:  # There are staged changes
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=DATA_DIR,
                check=True,
                capture_output=True,
            )
            return True
        return False  # No changes to commit
    except subprocess.CalledProcessError as e:
        logger.warning(f"Git commit failed: {e}")
        return False


def process_inbox(backend: GardenerBackend | None = None) -> list[dict]:
    """Process all files in the inbox.

    Args:
        backend: Optional backend instance. If not provided, creates one from env.
    """
    if not INBOX_DIR.exists():
        logger.info("Inbox directory does not exist")
        return []

    # Ensure git repo exists for version control
    ensure_git_repo()

    results = []
    own_backend = backend is None

    if own_backend:
        backend = get_backend()

    try:
        for inbox_file in INBOX_DIR.glob("*.md"):
            logger.info(f"Processing: {inbox_file.name}")

            try:
                note_content = inbox_file.read_text()
                action = classify_note(backend, note_content, inbox_file.name)

                logger.info(f"Action: {action.action} -> {action.path}")
                logger.info(f"Reasoning: {action.reasoning}")

                target_path = execute_action(action)

                # Git commit
                git_commit(target_path, f"Gardener: Processed {inbox_file.name}")

                # Delete original
                inbox_file.unlink()

                # Also commit the deletion
                git_commit(inbox_file, f"Gardener: Removed {inbox_file.name} from inbox")

                results.append({
                    "file": inbox_file.name,
                    "action": action.action,
                    "path": str(action.path),
                    "success": True,
                })

            except Exception as e:
                logger.error(f"Failed to process {inbox_file.name}: {e}")
                results.append({
                    "file": inbox_file.name,
                    "action": "error",
                    "error": str(e),
                    "success": False,
                })
    finally:
        if own_backend:
            backend.close()

    return results


if __name__ == "__main__":
    results = process_inbox()
    for r in results:
        print(json.dumps(r))
