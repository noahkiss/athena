---
# pkms-byys
title: Add CI test/lint gate
status: completed
type: task
priority: normal
created_at: 2026-01-21T00:10:55Z
updated_at: 2026-01-21T01:46:41Z
---

Add automated checks beyond image builds so regressions are caught on PRs.

Refs: .github/workflows/docker-publish.yml, TESTS.md

## Checklist
- [x] Decide on minimum CI checks (lint, typecheck, or E2E smoke)
- [x] Wire checks into GitHub Actions
- [x] Ensure CI uses uv + node install per repo guidance
- [x] Document how to run the checks locally

## Changes Made

### .github/workflows/ci.yml (new)
Created CI workflow with 3 parallel jobs:
- **gardener-test**: Runs pytest with uv
- **gardener-lint**: Runs ruff check and ruff format --check
- **scribe-build**: Runs npm ci && npm run build

### gardener/pyproject.toml
- Added ruff as dev dependency
- Added ruff configuration (target-version, line-length, lint rules)
- Added pytest configuration

### Code formatting
- Ran `ruff format` on all Python files (11 files)
- Fixed 4 lint issues (unused imports)

## Running Checks Locally

**Gardener (Python):**
```bash
cd gardener
uv sync --dev
uv run pytest tests/ -v        # Run tests
uv run ruff check .            # Lint
uv run ruff format --check .   # Check formatting
uv run ruff format .           # Auto-format
```

**Scribe (Node):**
```bash
cd scribe
npm ci
npm run build
```