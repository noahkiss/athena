---
# pkms-38ug
title: Refine endpoint
status: completed
type: feature
priority: normal
created_at: 2026-01-19T08:02:15Z
updated_at: 2026-01-19T08:34:48Z
parent: pkms-38nj
---

Pre-submission context injection using AI.

## Endpoint
`POST /api/refine`
- Input: {content: 'partial text...'}
- Output: HTML snippet (for HTMX swap)

## Logic
1. Search /data/atlas for keywords in content
2. Send content + found file summaries to Claude Haiku
3. Ask: 'What tags apply? Related projects? What's missing?'
4. Return suggestions as HTML

## Frontend Integration
- Enable Refine button
- hx-post='/api/refine' targeting suggestion div
- Show suggestions below textarea