---
# pkms-0k8s
title: Create stress test orchestration script
status: in-progress
type: task
created_at: 2026-01-21T07:32:01Z
updated_at: 2026-01-21T14:33:27Z
parent: pkms-9qpq
---

Implement a script to run all stress tests and verify integrity.

## Requirements

- Set up isolated test environment
- Generate test data
- Start gardener in background
- Run all stress test scenarios
- Verify data integrity after each scenario
- Generate comprehensive report
- Clean up test environment

## Deliverables

- `scripts/run_stress_tests.sh` - Main orchestration script
- JSON metrics output format
- CI integration (optional, for regression detection)

## Checklist
- [x] Create initial runner script with env wiring
- [x] Start/stop gardener and bootstrap data dir
- [x] Add report aggregation across scenarios
- [ ] Add optional CI smoke mode

## CI Integration (Optional)

Add limited stress test to CI for regression detection:
- Run on main branch pushes only
- Use smaller dataset (100 notes instead of 1000)
- Quick smoke test for critical scenarios
