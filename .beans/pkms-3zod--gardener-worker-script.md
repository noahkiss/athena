---
# pkms-3zod
title: Gardener worker script
status: completed
type: feature
priority: normal
created_at: 2026-01-19T08:01:53Z
updated_at: 2026-01-19T08:29:57Z
parent: pkms-uvam
---

Core inbox processing logic using Claude.

## Workflow
1. Scan /data/inbox for .md files
2. For each file:
   - Read AGENTS.md + GARDENER.md for context
   - Send note + context to Claude (Sonnet)
   - Request JSON: {action: create|append|task, path: ..., content: ...}
   - Execute file operation
   - Git commit the change
   - Delete original inbox file

## Requirements
- Use anthropic Python SDK
- Structured output parsing
- Error handling for LLM failures
- Respect GARDENER.md classification rules

## Files to create
- `gardener/workers/gardener.py`
- Add anthropic to dependencies
