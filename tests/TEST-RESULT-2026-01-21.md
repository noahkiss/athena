# Stress Test Report (2026-01-21)

## Run Metadata

- Date/time: 2026-01-21T20:07:14Z
- Run ID: 20260121-150640-A
- Operator: Codex (automated)
- Commit SHA: 71ed4651cda4909deaac6279b55c4ec2110c5028
- Branch: main
- Runner command: `RUN_ID=20260121-150640-A KEEP_DATA=1 STRESS_SCENARIOS=A ./scripts/run_stress_tests.sh`
- Additional runs:
  - `RUN_ID=20260121-154353-B KEEP_DATA=1 STRESS_SCENARIOS=B STRESS_DURATION_S=60 STRESS_SUBMIT_THREADS=1 STRESS_BROWSE_THREADS=1 STRESS_ASK_THREADS=1 STRESS_REFINE_THREADS=1 STRESS_SUBMIT_RPS=1 STRESS_AI_CALL_MULTIPLIER=3 STRESS_EXPECT_ARCHIVE=0 ./scripts/run_stress_tests.sh` (working tree dirty: ai-call cap changes pending)
  - `RUN_ID=20260121-155938-C KEEP_DATA=1 STRESS_SCENARIOS=C STRESS_LARGE_FILE_COUNT=200 STRESS_LARGE_COMMIT_COUNT=200 STRESS_LARGE_MIN_KB=1 STRESS_LARGE_MAX_KB=5 STRESS_RECONCILE_TIMEOUT=120 STRESS_SEARCH_TIMEOUT=30 ./scripts/run_stress_tests.sh` (failed during commit seeding; no metrics)
  - `RUN_ID=20260121-160023-C KEEP_DATA=1 STRESS_SCENARIOS=C STRESS_LARGE_FILE_COUNT=200 STRESS_LARGE_COMMIT_COUNT=1 STRESS_LARGE_MIN_KB=1 STRESS_LARGE_MAX_KB=5 STRESS_RECONCILE_TIMEOUT=120 STRESS_SEARCH_TIMEOUT=30 ./scripts/run_stress_tests.sh`
  - `RUN_ID=20260121-160137-D KEEP_DATA=1 STRESS_SCENARIOS=D STRESS_DB_THREADS=20 STRESS_DB_DURATION_S=30 STRESS_DB_LOCK_HOLD_S=0.2 STRESS_DB_LOCK_IDLE_S=0.05 STRESS_DB_LOCK_CYCLES=100 STRESS_DB_TIMEOUT_S=0 STRESS_DB_RETRY_COUNT=3 STRESS_DB_RETRY_DELAY_S=0.05 STRESS_DB_EXPECT_RECOVERY=1 ./scripts/run_stress_tests.sh` (failed: deadlock_like > 0)

## Environment

- Host/OS: Linux worker-9000 6.14.0-37-generic #37-Ubuntu SMP PREEMPT_DYNAMIC Fri Nov 14 22:10:32 UTC 2025 x86_64
- CPU/RAM: Intel(R) Core(TM) i5-8600 CPU @ 3.10GHz (3 cores), 7.3GiB RAM
- Python version: 3.12.12
- uv version: 0.9.22
- Backend provider/model(s): N/A (classification disabled)
- Auth enabled: Not set (ATHENA_AUTH_TOKEN not set)
- Notes: default stress test settings

## Run Configuration

- Scenarios: A
- Data dir: `/home/flight/.pkms-stress/20260121-150640-A`
- Base URL: `http://127.0.0.1:8000`
- CI smoke: 0
- Timeouts: defaults
- Key env vars: `RUN_ID=20260121-150640-A`, `KEEP_DATA=1`, `STRESS_SCENARIOS=A`

## Scenario Results

### Scenario A (Ingestion throughput)

- Metrics file: `/home/flight/.pkms-stress/20260121-150640-A/metrics/scenario-A.json`
- Summary:
  - total/ok/errors: 1000 / 1000 / 0
  - latency_ms p50/p95/p99/max: 10.84 / 43.88 / 70.94 / 153.02
  - elapsed_s: 9.99
  - throughput_per_s: 100.06
- Integrity:
  - inbox_count: 1000
  - archive_count: 0
  - db_integrity: ok
- Notes: scenario does not trigger gardener processing, so archive remains empty.

### Scenario B (Concurrent load)

- Run ID: 20260121-154353-B
- Metrics file: `/home/flight/.pkms-stress/20260121-154353-B/metrics/scenario-B.json`
- Summary:
  - total/ok/errors: 22 / 22 / 0
  - latency_ms p50/p95/p99/max: 13198.46 / 17631.39 / 17735.17 / 17761.75
  - elapsed_s: 67.60
  - ai_calls ask/refine/total: 4 / 5 / 9 (cap 381, expected 127, multiplier 3.0)
- Data loss:
  - inbox_new: 4
  - archive_new: 0
  - stored_new: 4
  - submitted_ok: 4
  - missing: 0
- Notes: low-cost run (1 ask + 1 refine thread, 60s duration).

### Scenario C (Large repo)

- Run ID (failed attempt): 20260121-155938-C
- Failure: git commit failed during commit seeding (`nothing to commit`), no metrics emitted.
- Run ID: 20260121-160023-C
- Metrics file: `/home/flight/.pkms-stress/20260121-160023-C/metrics/scenario-C.json`
- Summary:
  - total/ok/errors: 9 / 9 / 0
  - latency_ms p50/p95/p99/max: 2231.90 / 13948.58 / 14006.87 / 14021.45
  - elapsed_s: 46.97
  - file_count: 200
  - commit_target/commit_count: 1 / 2
- Git/DB/memory:
  - git_status_ms: 16.21
  - git_diff_ms: 13.43
  - db_scan row_count/scan_ms: 0 / 0.11
  - rss_before/after_reconcile_kb: 36468 / 36468
- Notes: low-cost run (5 ask/refine calls total).

### Scenario D (DB contention)

- Run ID: 20260121-160137-D
- Metrics file: `/home/flight/.pkms-stress/20260121-160137-D/metrics/scenario-D.json`
- Summary:
  - total/ok/errors: 525 / 525 / 0
  - latency_ms p50/p95/p99/max: 1025.90 / 2200.95 / 3427.73 / 3575.60
  - elapsed_s: 30.50
  - operations inbox/trigger/snapshot/db_write: 267 / 130 / 128 / 85
- Lock errors/retries:
  - lock_errors: 97
  - retry_attempts: 80 (retry_success: 23)
  - deadlock_like: 17 (failed: 17)
  - lock_acquire_errors: 67 (lock_cycles: 100)
- Integrity:
  - inbox_count: 267
  - archive_count: 0
  - db_integrity: ok
- Notes: low-cost run (20 threads, 30s); failed assertion because deadlock_like > 0 with recovery expectations enabled.

### Scenario E (Chaos/manual)

- Metrics file: not run
- Actions executed: not run
- Recovery checks: not run
- Integrity: not run
- Notes:

## Aggregated Metrics

- Summary file: `/home/flight/.pkms-stress/20260121-150640-A/metrics/summary.json`
- Summary file: `/home/flight/.pkms-stress/20260121-154353-B/metrics/summary.json`
- Summary file: `/home/flight/.pkms-stress/20260121-160023-C/metrics/summary.json`
- Highlights: scenario A + scenario B low-cost run + scenario C low-cost run (see above)

## Anomalies / Regressions

- Pytest warns about unknown mark `stress` (pytest.mark.stress not registered).
- Deprecation warnings in test data generator: `datetime.utcnow()` usage (2000 warnings).
- Scenario B latency is high (p50 ~13s), likely dominated by LLM response time.
- Scenario C first attempt failed during commit seeding (git reported nothing to commit).
- Scenario D deadlock_like > 0 caused assertion failure under recovery expectations.

## Follow-ups

- Register `stress` pytest marker to remove warnings.
- Update test data generator to use timezone-aware timestamps.
