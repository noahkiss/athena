---
# pkms-mejp
title: Scribe Dockerfile
status: completed
type: task
priority: normal
created_at: 2026-01-19T08:01:31Z
updated_at: 2026-01-19T08:28:23Z
parent: pkms-rpqb
---

Create Dockerfile for the Scribe (frontend) service.

## Requirements
- Node 20+ base image
- Working directory /app
- Expose port 3000

## Acceptance
- `docker build ./scribe` succeeds
- Container runs Astro dev server successfully