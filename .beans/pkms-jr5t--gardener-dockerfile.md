---
# pkms-jr5t
title: Gardener Dockerfile
status: completed
type: task
priority: normal
created_at: 2026-01-19T08:01:28Z
updated_at: 2026-01-19T08:18:15Z
parent: pkms-rpqb
---

Create Dockerfile for the Gardener (backend) service.

## Requirements
- Python 3.12+ base image
- Install dependencies via uv
- Working directory /app
- Expose port 8000

## Acceptance
- `docker build ./gardener` succeeds
- Container runs uvicorn successfully