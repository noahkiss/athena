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

- Metrics file: not run
- Summary: not run
- Git/DB/memory: not run
- Notes:

### Scenario D (DB contention)

- Metrics file: not run
- Summary: not run
- Lock errors/retries: not run
- Integrity: not run
- Notes:

### Scenario E (Chaos/manual)

- Metrics file: not run
- Actions executed: not run
- Recovery checks: not run
- Integrity: not run
- Notes:

## Aggregated Metrics

- Summary file: `/home/flight/.pkms-stress/20260121-150640-A/metrics/summary.json`
- Summary file: `/home/flight/.pkms-stress/20260121-154353-B/metrics/summary.json`
- Highlights: scenario A + scenario B low-cost run (see above)

## Anomalies / Regressions

- Pytest warns about unknown mark `stress` (pytest.mark.stress not registered).
- Deprecation warnings in test data generator: `datetime.utcnow()` usage (2000 warnings).
- Scenario B latency is high (p50 ~13s), likely dominated by LLM response time.

## Follow-ups

- Register `stress` pytest marker to remove warnings.
- Update test data generator to use timezone-aware timestamps.
