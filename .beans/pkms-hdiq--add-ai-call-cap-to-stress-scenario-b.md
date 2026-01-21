---
# pkms-hdiq
title: Add AI call cap to stress scenario B
status: completed
type: task
priority: normal
created_at: 2026-01-21T20:40:13Z
updated_at: 2026-01-21T20:43:22Z
---

Add a safety cap for AI call volume in Scenario B so runs can stop if ask/refine calls exceed expected counts by a configurable multiplier.

## Checklist
- [x] Define expected call count logic + config vars (document defaults)
- [x] Implement cap in Scenario B test and include in summary output
- [x] Update TESTS.md with the new cap controls
