# Project Athena - Agent Instructions

**IMPORTANT**: Before starting work, run `beans prime` and follow its guidance.

## Development Environment

This project uses **uv** for Python package and project management.

**Key commands:**
- `uv add <package>` - Add a dependency
- `uv run <command>` - Run a command in the project environment
- `uv sync` - Sync dependencies from lockfile
- `uv lock` - Update the lockfile

Always prefix Python commands with `uv run` (e.g., `uv run pytest`, `uv run uvicorn ...`).

## Project Structure

```
pkms/
├── athena/          # The Data Skeleton (source of truth, git-versioned)
├── gardner/         # Python/FastAPI backend + AI worker
├── scribe/          # Astro/HTMX frontend
└── docker-compose.yml
```

Each component has its own `AGENTS.md` with specific context. Read the relevant one before working on that component.

## Task Tracking

Use `beans` for all work tracking. See `.beans.yml` for configuration.
