---
# pkms-87re
title: 'Implement Scenario A: High-volume inbox ingestion'
status: in-progress
type: task
created_at: 2026-01-21T07:31:07Z
updated_at: 2026-01-21T14:20:42Z
parent: pkms-9qpq
---

Test classification accuracy and system stability under high concurrent load.

## Setup

- Generate 1,000 notes
- 50 concurrent API clients
- Each submits 20 notes sequentially
- Stagger start times (0-10 seconds)

## Metrics to Collect

- Classification accuracy (correct category assignment)
- Processing time per note
- Database lock errors (sqlite3.OperationalError)
- API response times (p50, p95, p99)
- Queue depth over time

## Verification

- All 1,000 notes archived to /inbox/archive/
- All 1,000 notes classified to atlas (or tasks.md)
- No duplicate files
- Git history consistent (2,000 total commits)
- SQLite state DB matches filesystem state

## Deliverables

- `gardener/tests/stress/test_stress_ingestion.py`
- Concurrent client simulator
- Metrics collection and reporting

## Checklist
- [x] Add ingestion stress test skeleton with env gating
- [x] Emit JSON metrics summary when configured
- [x] Add archive/integrity verification hooks
- [ ] Add classification accuracy verification
