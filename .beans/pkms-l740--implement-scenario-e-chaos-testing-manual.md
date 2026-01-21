---
# pkms-l740
title: 'Implement Scenario E: Chaos testing (manual)'
status: draft
type: task
created_at: 2026-01-21T07:31:43Z
updated_at: 2026-01-21T07:31:43Z
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