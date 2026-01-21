---
# pkms-4ela
title: 'Implement Scenario C: Large repository stress'
status: completed
type: task
priority: normal
created_at: 2026-01-21T07:31:25Z
updated_at: 2026-01-21T15:42:29Z
parent: pkms-9qpq
---

Test performance degradation with accumulated data (long-term simulation).

## Setup

- Pre-populate atlas with 10,000 files
- Git history with 20,000 commits
- Run operations on large repository

## Operations to Test

- Run reconciliation (/api/reconcile)
- Perform atlas searches with various keywords
- Check status endpoint (/api/status)
- Submit new notes and process

## Metrics to Collect

- Reconciliation time
- Search latency
- Git operation times (diff, status)
- Memory usage during reconciliation
- Database query times (file_state table scans)

## Verification

- Reconciliation completes successfully
- Search results accurate (not corrupted)
- No performance cliff (exponential degradation)

## Deliverables

- `gardener/tests/stress/test_stress_large_repo.py`
- Large data fixture generator
- Performance benchmark tracking

## Checklist
- [x] Seed atlas with large note set and git history
- [x] Exercise reconcile/search/status/inbox operations
- [x] Record latency, git ops, and DB scan metrics
- [x] Capture memory usage during reconciliation when possible
- [x] Wire scenario C into `scripts/run_stress_tests.sh`
