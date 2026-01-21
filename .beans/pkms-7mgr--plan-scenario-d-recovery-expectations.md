---
# pkms-7mgr
title: Plan Scenario D recovery expectations
status: in-progress
type: task
created_at: 2026-01-21T21:15:20Z
updated_at: 2026-01-21T21:15:20Z
---

Define a fix for Scenario D (DB contention) recovery expectations so tests can pass meaningfully. Reference investigation bean pkms-pt6j.

## Checklist
- [ ] Summarize findings from pkms-pt6j and decide desired behavior
- [ ] Propose config/threshold changes (e.g., deadlock tolerance or retry policy)
- [ ] Identify any code changes + tests/docs to update
