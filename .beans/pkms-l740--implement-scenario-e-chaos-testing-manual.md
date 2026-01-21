---
# pkms-l740
title: 'Implement Scenario E: Chaos testing (manual)'
status: completed
type: task
priority: normal
created_at: 2026-01-21T07:31:43Z
updated_at: 2026-01-21T16:19:12Z
parent: pkms-9qpq
---

Test resilience and data integrity under failure conditions (manual execution only).

## Failure Modes to Test

- Kill gardener process mid-processing
- Corrupt SQLite DB (delete rows)
- Delete inbox files during processing
- Rewrite git history (force push)
- Fill disk space during archive operation

## Metrics to Collect

- Data loss (missing archive files)
- Partial state (inbox deleted, archive missing)
- Recovery time after failure
- Manual intervention required

## Verification

- Archive data never lost (critical requirement)
- System detects inconsistencies (reconciliation)
- Clear error messages guide recovery

## Deliverables

- `gardener/tests/stress/test_stress_chaos.py` (marked as manual-only)
- Failure injection tools
- Recovery procedure documentation

## Checklist
- [x] Add chaos failure injection helpers
- [x] Implement Scenario E manual stress test
- [x] Document chaos recovery procedures
- [x] Wire Scenario E into stress runner
- [x] Update TESTS.md for Scenario E coverage
