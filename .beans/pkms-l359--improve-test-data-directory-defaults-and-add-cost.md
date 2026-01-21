---
# pkms-l359
title: Improve test data directory defaults and add cost guidance
status: completed
type: task
priority: normal
created_at: 2026-01-21T21:46:48Z
updated_at: 2026-01-21T21:53:46Z
---

Address test directory pollution and missing cost guidance in TESTS.md.

## Issues
1. Tests default to $HOME/.pkms-test and $HOME/.pkms-stress (pollutes home dir)
2. No guidance in TESTS.md about preferring low-cost test runs
3. Current defaults made sense initially but should be reconsidered

## Proposed Changes
1. Change default test dirs to repo-tracked tests/ subdirectories
   - Structure: tests/TEST-RESULT-YYYY-MM-DD/ for stress tests (matches report filename)
   - Structure: tests/TEST-E2E-YYYY-MM-DD/ for E2E tests
   - Allows test data to be validated alongside reports
   - Version-controlled and reviewable (generated synthetic data)
   - Still configurable via TEST_DATA_DIR and STRESS_DATA_DIR env vars
2. Add tests/.gitignore to track reports but ignore large data subdirs if needed
3. Add 'Cost Management' section to TESTS.md explaining:
   - Why we prefer low-cost runs (API costs)
   - How to configure AI call caps and data sizes
   - Recommended defaults vs full-scale runs
4. Update Scenario D defaults documentation to reflect realistic params

## Checklist
- [x] Review current directory usage and rationale
- [x] Create tests/.gitignore to track reports but ignore data subdirs
- [x] Update run_stress_tests.sh to use tests/TEST-RESULT-{date}/
- [x] Update test_e2e_full.sh to use tests/TEST-E2E-{timestamp}/
- [x] Add 'Cost Management' section to TESTS.md
- [x] Update Scenario D defaults documentation in TESTS.md
- [x] Update cleanup instructions and add test data organization section

## Summary

All changes complete:
- Test data now goes to repo-tracked tests/ subdirectories
- Stress tests: tests/TEST-RESULT-YYYY-MM-DD/ (matches report filename)
- E2E tests: tests/TEST-E2E-YYYY-MM-DD-HHMMSS/ (timestamped)
- Added .gitignore to track reports/metrics but ignore large data subdirs
- Added comprehensive Cost Management section explaining low-cost approach
- Updated Scenario D defaults to realistic parameters with explanatory notes