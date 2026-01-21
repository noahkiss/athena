---
# pkms-fcaj
title: Create stress test fixtures and utilities
status: in-progress
type: task
created_at: 2026-01-21T07:31:53Z
updated_at: 2026-01-21T14:20:52Z
parent: pkms-9qpq
---

Implement shared testing infrastructure for stress tests.

## Components to Implement

### StressClient
- Multi-threaded API client simulator
- Configurable concurrency level
- Request timing and error tracking

### IntegrityChecker
- Archive completeness verification
- Git history consistency checks
- Database consistency validation
- Content hash comparison

### MetricsCollector
- Latency tracking (p50, p95, p99)
- Database metrics (lock errors, query times)
- File system metrics (queue depth, disk I/O)
- Git metrics (commit count, repo size, operation times)
- Memory & CPU monitoring

### Pytest Fixtures
- `stress_data_dir` - Large pre-populated data directory
- `note_generator` - Factory for generating realistic notes
- `stress_client` - Multi-threaded API client
- `integrity_checker` - Data integrity validation

## Deliverables

- Extend `gardener/tests/conftest.py` with stress fixtures
- Implement utility classes in test helpers
- Add metrics reporting (JSON output format)

## Checklist
- [x] Implement StressClient request runner
- [x] Implement IntegrityChecker helpers
- [x] Implement MetricsCollector with latency summary
- [x] Add stress fixtures to `gardener/tests/conftest.py`
- [ ] Add richer system metrics (DB/file/git)
