---
# pkms-erh9
title: FastAPI backend skeleton
status: completed
type: feature
priority: normal
created_at: 2026-01-19T08:01:33Z
updated_at: 2026-01-19T08:11:44Z
parent: pkms-rpqb
---

Initialize FastAPI application with core endpoints.

## Endpoints
- `POST /api/inbox` - Accept note content, save to /data/inbox as timestamped markdown
- `GET /api/status` - Health check endpoint

## Requirements
- Use pydantic for request/response models
- Type hints throughout
- Save files as `YYYY-MM-DD_HHMM-{uuid}.md`

## Files to create
- `gardner/main.py` - FastAPI app
- `gardner/pyproject.toml` - Dependencies (fastapi, uvicorn, pydantic)
- `gardner/requirements.txt` or use uv