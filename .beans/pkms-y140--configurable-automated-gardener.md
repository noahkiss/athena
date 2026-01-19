---
# pkms-y140
title: Configurable & Automated Gardener
status: completed
type: epic
priority: normal
created_at: 2026-01-19T21:10:55Z
updated_at: 2026-01-19T21:22:38Z
---

Make the gardener system more flexible and autonomous:

1. **Configurable AI backends** - Support multiple AI providers (Claude, OpenAI, local LLMs, etc.) with a clean abstraction layer
2. **Automated processing** - Trigger gardener automatically instead of manual API calls

## Goals
- Users can choose their preferred AI provider via configuration
- Gardener processes inbox automatically without manual intervention
- System remains simple and maintainable

## Non-Goals
- Complex plugin architecture (keep it simple)
- Real-time streaming classification (batch is fine)