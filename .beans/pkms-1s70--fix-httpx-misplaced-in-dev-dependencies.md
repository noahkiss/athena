---
# pkms-1s70
title: Fix httpx misplaced in dev dependencies
status: completed
type: bug
priority: normal
created_at: 2026-01-19T20:32:54Z
updated_at: 2026-01-19T20:33:13Z
---

httpx is placed in [dependency-groups] dev in pyproject.toml, but it's imported and used in production code (ai_client.py). The Dockerfile uses 'uv sync --no-dev', so the Docker container will fail at runtime when any AI feature is used.