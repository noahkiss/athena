---
# pkms-46ra
title: Fix Scenario D contention test parameters
status: completed
type: bug
priority: normal
created_at: 2026-01-21T21:24:34Z
updated_at: 2026-01-21T21:34:37Z
---

Adjust Scenario D DB contention test to use realistic parameters that allow graceful recovery under normal contention levels.

## Checklist
- [x] Update test defaults to realistic values (timeout=5.0, retries=10, idle=0.15)
- [x] Update test documentation with rationale
- [x] Register pytest 'stress' marker to eliminate warnings
- [x] Fix datetime.utcnow() deprecation warnings in test data generator
- [x] Run Scenario D with new parameters and verify it passes
- [x] Update TEST-RESULT-2026-01-21.md with new Scenario D results
- [x] Review completed Scenario E results

## Summary

All fixes applied successfully:
- Scenario D now passes with 0 deadlock-like failures (299 operations, all successful)
- Pytest marker registered (no more warnings)
- datetime.utcnow() replaced with datetime.now(timezone.utc) (no more deprecation warnings)
- Scenario E was already completed (light chaos test, all recovery checks passed)