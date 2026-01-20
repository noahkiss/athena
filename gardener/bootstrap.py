"""Bootstrap script to initialize the Athena knowledge base structure."""

import os
import shutil
from pathlib import Path

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))

# .gitignore content for the data directory
GITIGNORE = """# Athena Knowledge Base .gitignore

# Gardener state (machine-specific, not version controlled)
.gardener/

# Logs and temporary files
logs/
*.log
tmp/
cache/

# OS files
.DS_Store
Thumbs.db

# Editor artifacts
*~
*.swp
*.swo
.*.swp

# Python cache (if scripts run in data dir)
__pycache__/
*.pyc
"""

# Default content for system files
AGENTS_MD = """# ATHENA SYSTEM CONTEXT (Live Document)

**Role:** You are Athena, the central knowledge base for a tech-savvy user.
**User Profile:**
- **Interests:** (customize: hobbies, work, projects)
- **Personality:** Prefers raw data over overly sanitized summaries.
- **Philosophy:** "Notes in, Answers out." Capture fast, organize later via agents.

**System Architecture:**
- This directory is the source of truth.
- `/inbox`: Where new thoughts land.
- `/atlas`: The permanent storage (living structure - categories may evolve).
- `/meta`: Machine-generated indexes (do not edit manually).
- `/tasks.md`: Ambiguity log for notes the Gardener couldn't classify.

**Interaction Rules:**
1. **Never** delete the user's raw input. If you summarize, keep the original text in a `## Raw Source` section.
2. **Be Agentic:** If you see a task in a note, log it. If you see a date, note it.
3. **Cross-Link:** If a note mentions a person, link to their file in `/atlas/people/`.
"""

GARDENER_MD = """# THE GARDENER PROTOCOL

**Goal:** Process files in `/inbox` and move them to `/atlas`.

## Classification Rules
Analyze the content and move to the best matching directory:

1. **Projects** (`/atlas/projects`): Business ideas, coding projects, "one-off" builds.
2. **People** (`/atlas/people`): CRM data, gift ideas, relationship notes.
3. **Home** (`/atlas/home`): HVAC, plumbing, cars, woodworking, DIY maintenance.
4. **Wellness** (`/atlas/wellness`): Health logs, workout stats, diet.
5. **Tech** (`/atlas/tech`): Server configs, homelab documentation, reference material.
6. **Journal** (`/atlas/journal`): Life philosophy, parenting, brain dumps.
7. **Reading** (`/atlas/reading`): Book notes, article summaries, media consumption.

> **Note:** This structure is living. If a note clearly belongs to a new category, you may create a new subdirectory and document it here.

## File Format Standard
When moving a file, rewrite it to match this format:

```markdown
---
title: {Suggested Title}
date: {YYYY-MM-DD}
tags: [tag1, tag2]
status: {seed|active|archive}
---

# {Title}

{Summary/Refined Notes}

## Action Items
- [ ] {Task extracted from note}

---
## Raw Source
{Original content verbatim}
```

## Ambiguity Handling
- If you are < 80% sure where a note belongs, do NOT move it.
- Append the content to `/tasks.md` with the header: `## Unsorted Note {Date}` and add a question: "Gardener Query: Where does this go?"
"""

TASKS_MD = """# Ambiguity Log

Notes the Gardener couldn't confidently classify will appear here.
Review periodically and manually sort, or provide guidance in GARDENER.md.
"""


def bootstrap(force: bool = False) -> dict:
    """
    Initialize the Athena knowledge base structure.

    Args:
        force: If True, overwrite existing config files.

    Returns:
        Dict with created/skipped paths.
    """
    results = {"created": [], "skipped": [], "exists": []}

    # Directories to create
    directories = [
        DATA_DIR / "inbox",
        DATA_DIR / "atlas" / "projects",
        DATA_DIR / "atlas" / "people",
        DATA_DIR / "atlas" / "home",
        DATA_DIR / "atlas" / "wellness",
        DATA_DIR / "atlas" / "tech",
        DATA_DIR / "atlas" / "journal",
        DATA_DIR / "atlas" / "reading",
        DATA_DIR / "meta",
    ]

    # Files to create with their content
    files = {
        DATA_DIR / "AGENTS.md": AGENTS_MD,
        DATA_DIR / "GARDENER.md": GARDENER_MD,
        DATA_DIR / "tasks.md": TASKS_MD,
        DATA_DIR / ".gitignore": GITIGNORE,
    }

    # Create directories
    for dir_path in directories:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            results["created"].append(str(dir_path))
        else:
            results["exists"].append(str(dir_path))

    # Create files
    for file_path, content in files.items():
        if not file_path.exists() or force:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            results["created"].append(str(file_path))
        else:
            results["skipped"].append(str(file_path))

    # Initialize git repo if not exists
    git_dir = DATA_DIR / ".git"
    git_initialized = False
    if not git_dir.exists():
        import subprocess
        try:
            subprocess.run(["git", "init"], cwd=DATA_DIR, check=True, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "gardener@athena.local"],
                cwd=DATA_DIR, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Athena Gardener"],
                cwd=DATA_DIR, check=True, capture_output=True
            )
            results["created"].append(str(git_dir))
            git_initialized = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # Git not available, that's okay

    # Make baseline commit if we just initialized git and created files
    if git_initialized and results["created"]:
        import subprocess
        try:
            subprocess.run(["git", "add", "-A"], cwd=DATA_DIR, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Athena: Initialize knowledge base"],
                cwd=DATA_DIR, check=True, capture_output=True
            )
            results["baseline_commit"] = True
        except subprocess.CalledProcessError:
            results["baseline_commit"] = False

    # Initialize state database
    try:
        from state import init_db, get_current_head, record_processed_commit, get_current_branch, update_repo_root_hash, get_repo_root_hash
        init_db()
        results["state_db_initialized"] = True

        # Record baseline commit in state if we just made one
        if results.get("baseline_commit"):
            head = get_current_head()
            if head:
                branch = get_current_branch()
                record_processed_commit(head, branch, "Bootstrap baseline commit")
                repo_hash = get_repo_root_hash()
                if repo_hash:
                    update_repo_root_hash(repo_hash)
    except Exception:
        results["state_db_initialized"] = False

    return results


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Bootstrap Athena knowledge base")
    parser.add_argument("--force", action="store_true", help="Overwrite existing config files")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = bootstrap(force=args.force)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("Athena Knowledge Base Bootstrap")
        print("=" * 40)
        if results["created"]:
            print("\nCreated:")
            for p in results["created"]:
                print(f"  + {p}")
        if results["skipped"]:
            print("\nSkipped (already exists):")
            for p in results["skipped"]:
                print(f"  - {p}")
        if results["exists"]:
            print("\nDirectories already existed:")
            for p in results["exists"]:
                print(f"  . {p}")
        print("\nBootstrap complete!")
