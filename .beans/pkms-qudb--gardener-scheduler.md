---
# pkms-qudb
title: Gardener scheduler
status: completed
type: task
priority: normal
created_at: 2026-01-19T08:01:56Z
updated_at: 2026-01-19T08:30:55Z
parent: pkms-uvam
---

Automate inbox processing on a schedule.

## Options (pick one)
1. APScheduler running in FastAPI process
2. Simple while-loop with sleep in separate process
3. Manual trigger via `POST /api/trigger-gardener`

## Recommendation
Start with manual trigger endpoint for easier testing, add scheduler later.

## Acceptance
- Can trigger gardener processing via API call
- Processing runs without blocking the API