---
# pkms-xuvh
title: 'Implement Scenario B: Sustained concurrent operations'
status: completed
type: task
priority: normal
created_at: 2026-01-21T07:31:16Z
updated_at: 2026-01-21T15:48:39Z
parent: pkms-9qpq
---

Validate raw data preservation under mixed concurrent load.

## Setup

- 20 threads submitting new notes (5 req/s total)
- 10 threads browsing atlas (/api/browse)
- 10 threads searching (/api/ask)
- 5 threads refining notes (/api/refine)
- Duration: 10 minutes

## Metrics to Collect

- Total notes processed
- Errors by endpoint
- Archive completeness
- Data loss detection (inbox count vs archive count)
- File system consistency (no orphaned files)

## Verification

- All submitted notes present in archive with original content intact
- No empty archive files
- No truncated content (compare content hashes)
- Git commits successful for all operations

## Deliverables

- `gardener/tests/stress/test_stress_concurrent.py`
- Multi-endpoint load simulator
- Data integrity checker

## Checklist
- [x] Add sustained mixed-load stress test skeleton
- [x] Emit JSON metrics summary when configured
- [x] Add integrity report hook (optional)
- [x] Add data loss verification (archive vs inbox counts)
