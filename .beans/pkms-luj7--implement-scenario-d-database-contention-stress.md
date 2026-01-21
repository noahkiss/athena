---
# pkms-luj7
title: 'Implement Scenario D: Database contention stress'
status: completed
type: task
priority: normal
created_at: 2026-01-21T07:31:33Z
updated_at: 2026-01-21T16:18:55Z
parent: pkms-9qpq
---

Force SQLite locking failures to test error handling and recovery.

## Setup

- 100 concurrent threads
- Maximum DB contention (no throttling)
- All endpoints that write to state DB

## Operations

- POST /api/inbox (writes file_state)
- Trigger gardener (writes processed_commits)
- POST /api/snapshot (writes edit_provenance)

## Metrics to Collect

- Database lock error count
- Failed transactions
- Retry success rate
- Deadlock detection

## Verification

- System recovers gracefully (no corruption)
- Error messages clear and logged
- State DB integrity check passes

## Deliverables

- `gardener/tests/stress/test_stress_db_contention.py`
- DB lock error simulator
- Integrity verification tools

## Checklist
- [x] Implement DB lock simulator/helper for contention testing
- [x] Add Scenario D stress test with metrics + integrity checks
- [x] Wire Scenario D into stress runner
- [x] Update TESTS.md for Scenario D coverage
