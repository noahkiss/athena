# Testing Guide

This repo includes fast unit tests for the Gardener backend plus end-to-end testing with live LLM backends. The E2E scripts run repeatable flows that clean a test data directory, generate fresh content each run, and exercise multiple entrypoints.

## Prereqs

- LiteLLM or other OpenAI-compatible backend running.
- Local env file at `.env` with at least:
  - `GARDENER_BACKEND=openai`
  - `AI_BASE_URL=http://<host>:<port>/v1`
  - `AI_API_KEY=...`
  - `AI_MODEL_FAST=...`
  - `AI_MODEL_THINKING=...`
- Python deps installed via uv (include dev deps for tests/lint):
  - `cd gardener && uv sync --dev`
- Node deps for Scribe (only needed when `TEST_SCRIBE=1`):
  - `cd scribe && npm ci`

## Cost Management

**Default approach: Prefer low-cost test runs**

Tests that invoke AI backends (classification, ask, refine) incur API costs. Our default test parameters are tuned for **cost-conscious validation**:

- **Small data sets**: 100-200 notes instead of 1,000-10,000
- **Short durations**: 30-60s runs instead of 10+ minutes
- **AI call caps**: Scenario B stops after expected AI call count × multiplier (default 3x)
- **Minimal classification checks**: Only validate core functionality, not full accuracy

**When to run full-scale tests:**
- Before major releases (quarterly or as needed)
- When investigating performance regressions
- When validating LLM provider changes

**Cost control environment variables:**
```bash
# Scenario A: Limit note count
STRESS_NOTE_COUNT=100

# Scenario B: Cap AI calls and reduce duration
STRESS_DURATION_S=60
STRESS_AI_CALL_MULTIPLIER=3  # Stop after 3x expected calls
STRESS_ASK_THREADS=1
STRESS_REFINE_THREADS=1

# Scenario C: Smaller repository
STRESS_LARGE_FILE_COUNT=200
STRESS_LARGE_COMMIT_COUNT=1
```

**Recommended practice:** Run unit tests frequently (free), E2E tests regularly (low cost), and stress tests with reduced parameters. Reserve full-scale stress runs for validation milestones.

## Quick Start (Unit Tests + Lint)

Fast local checks that mirror CI:

```bash
cd gardener
uv run pytest
uv run ruff format --check .
uv run ruff check .
```

Scribe build (runs in CI too):

```bash
cd scribe
npm ci
npm run build
```

## Quick Start (Full E2E)

Runs Gardener API, MCP, retrieval, and (optionally) Scribe proxy checks.

```bash
./scripts/test_e2e_full.sh
```

Defaults:
- Creates a new test data dir under `tests/TEST-E2E-<timestamp>/`
- Boots Gardener on `127.0.0.1:8000`
- Builds and runs Scribe on `127.0.0.1:3000` (can be disabled)

## Stress Tests (Scenarios A-C)

Stress tests live under `gardener/tests/stress` and are driven by the runner script.

```bash
# Scenario A only (default)
./scripts/run_stress_tests.sh

# All scenarios
STRESS_SCENARIOS=A,B,C KEEP_DATA=1 ./scripts/run_stress_tests.sh

# CI smoke defaults (small sizes, no optional asserts)
CI_SMOKE=1 ./scripts/run_stress_tests.sh
```

If you need to invoke pytest directly:

```bash
cd gardener
RUN_STRESS_TESTS=1 STRESS_DATA_DIR=../tests/TEST-RESULT-manual \
  uv run pytest tests/stress/test_stress_ingestion.py -m stress -s
```

### Stress Test Scenarios

- **Scenario A (Ingestion throughput)**: High-volume `/api/inbox` ingestion with optional classification accuracy checks.
- **Scenario B (Concurrent load)**: Sustained mixed traffic (`/api/inbox`, `/api/browse`, `/api/ask`, `/api/refine`) with optional data-loss checks.
- **Scenario C (Large repo)**: Large atlas + git history, reconcile + search/refine + trigger flow with git/DB/memory metrics.
- **Scenario D (DB contention)**: Forces SQLite locks while hitting write-heavy endpoints and direct DB writes.
- **Scenario E (Chaos/manual)**: Opt-in failure injection to validate recovery and integrity (see `gardener/tests/stress/CHAOS.md`).

Classification accuracy checks require a configured AI backend (API key + model) and `STRESS_DATA_DIR` (the runner sets this automatically).

### Stress Test Environment Flags

General:

```bash
STRESS_SCENARIOS=A,B,C            # Comma-separated scenario list
STRESS_DATA_DIR=...               # Data dir (also sets DATA_DIR)
STRESS_METRICS_DIR=...            # Metrics output dir
KEEP_DATA=1                       # Preserve data dir after run
START_GARDENER=0                  # Skip starting Gardener (assumes running)
RUN_BOOTSTRAP=0                   # Skip /api/bootstrap
GARDENER_PORT=8010                # Port for runner when starting Gardener
STRESS_BASE_URL=http://...        # Override API base URL
```

Scenario A:

```bash
STRESS_CONCURRENCY=50
STRESS_NOTES_PER_CLIENT=20
STRESS_NOTE_COUNT=...             # Overrides concurrency * notes per client
STRESS_MIN_KB=1 STRESS_MAX_KB=50
STRESS_STAGGER_MAX=10
STRESS_EXPECT_CLASSIFICATION=1    # Adds Expected-Category header + accuracy checks
STRESS_MIN_CLASSIFICATION_ACCURACY=0.8
STRESS_EXPECT_ARCHIVE=1           # Assert archive count/no empties
```

Scenario B:

```bash
STRESS_DURATION_S=600
STRESS_SUBMIT_THREADS=20
STRESS_BROWSE_THREADS=10
STRESS_ASK_THREADS=10
STRESS_REFINE_THREADS=5
STRESS_SUBMIT_RPS=5
STRESS_AI_CALL_MULTIPLIER=3      # Stop ask/refine when total calls exceed expected * multiplier (0 disables)
STRESS_EXPECT_ARCHIVE=1           # Assert no data loss
```

Scenario C:

```bash
STRESS_LARGE_FILE_COUNT=10000
STRESS_LARGE_COMMIT_COUNT=20000
STRESS_LARGE_MIN_KB=1 STRESS_LARGE_MAX_KB=20
STRESS_RECONCILE_TIMEOUT=300
STRESS_SEARCH_TIMEOUT=60
```

Scenario D:

```bash
STRESS_DB_THREADS=100
STRESS_DB_DURATION_S=60
STRESS_DB_LOCK_HOLD_S=0.25
STRESS_DB_LOCK_IDLE_S=0.15          # Default: realistic breathing room
STRESS_DB_LOCK_CYCLES=200
STRESS_DB_TIMEOUT_S=5.0             # Default: allow waiting for locks (realistic)
STRESS_DB_RETRY_COUNT=10            # Default: sufficient retry attempts
STRESS_DB_RETRY_DELAY_S=0.1         # Default: reasonable backoff
STRESS_DB_EXPECT_RECOVERY=1         # Asserts zero deadlock-like failures
```

**Note:** Test defaults are tuned for **realistic contention** where retry logic should succeed. For extreme stress testing (documenting system limits), reduce timeout to 0 and retries to 3, and set `STRESS_DB_EXPECT_RECOVERY=0`.

Scenario E (manual):

```bash
STRESS_CHAOS=1
STRESS_CHAOS_ACTIONS=corrupt-db,delete-inbox,kill
STRESS_CHAOS_CONFIRM_DB=1
STRESS_CHAOS_CONFIRM_INBOX=1
STRESS_CHAOS_CONFIRM_KILL=1
STRESS_CHAOS_RECOVER=1
```

CI smoke mode sets smaller defaults for load-based scenarios and disables optional asserts:

```bash
CI_SMOKE=1
```

### Stress Test Outputs

- Per-scenario metrics: `$STRESS_METRICS_DIR/scenario-A.json`, `scenario-B.json`, `scenario-C.json`
- Aggregated metrics: `$STRESS_METRICS_DIR/summary.json`
- Gardener log (runner-started): `$STRESS_DATA_DIR/gardener.log`

### Stress Test Reporting Framework

Use a dated report file in `tests/` for each run. Start with the template:

- `tests/TEST-RESULT-YYYY-MM-DD.md`

Recommended sections:

1. **Run metadata**
   - Date/time, run ID, operator, commit SHA, branch
2. **Environment**
   - Host/OS, Python/uv versions, backend provider + model(s), auth enabled, hardware notes
3. **Run configuration**
   - Scenario list, key env vars, data dir, base URL, CI smoke mode, timeouts
4. **Scenario results**
   - Summaries from `scenario-*.json` (latency, errors, throughput, integrity, DB checks)
5. **Anomalies / regressions**
   - Errors, non-linear slowdowns, data loss, lock spikes, unexpected behavior
6. **Follow-ups**
   - Issues to file, tuning ideas, rerun notes

Attach links or pasted summaries of the metrics JSONs as needed.

## Environment Flags

Set these when you run the script:

```bash
# Keep test data directory after run
KEEP_DATA=1 ./scripts/test_e2e_full.sh

# Use a custom test data directory
TEST_DATA_DIR=./tests/TEST-E2E-custom ./scripts/test_e2e_full.sh

# Skip Scribe proxy checks
TEST_SCRIBE=0 ./scripts/test_e2e_full.sh

# Force rebuild of Scribe dist/
FORCE_BUILD=1 ./scripts/test_e2e_full.sh

# Enable gardener automation (poll mode) and validate it processes MCP notes
TEST_AUTOMATION=1 ./scripts/test_e2e_full.sh

# Run optional Claude CLI MCP check (requires claude CLI configured).
# Optionally set CLAUDE_MODEL if your default model isn't available.
TEST_CLAUDE=1 CLAUDE_MODEL=claude-3-5-sonnet ./scripts/test_e2e_full.sh

# Custom ports
GARDENER_PORT=8010 SCRIBE_PORT=3010 ./scripts/test_e2e_full.sh
```

## What the E2E Script Does

1. Cleans `TEST_DATA_DIR` unless `KEEP_DATA=1`.
2. Starts Gardener (uvicorn) with `DATA_DIR` overridden.
3. Verifies `/api/status` and bootstrap state.
4. Bootstraps `/data` structure and validates `AGENTS.md` + atlas presence.
5. Runs negative checks (browse traversal + missing file, empty ask/refine).
6. Validates invalid action paths are routed to `tasks.md`.
7. Submits a note via `/api/inbox` with a random token (asserts response shape).
8. Optionally submits a second note through Scribe `/api/inbox` (and checks empty input handling).
9. Triggers the gardener and waits for the inbox to clear.
10. Verifies atlas content for both tokens and fetches it with `/api/browse`.
11. Calls `/api/ask` and `/api/refine` using the generated token (asserts no errors + expected fields).
12. Calls MCP `tools/list`, then `tools/call` for `read_notes` and `add_note`.
13. Processes the MCP-added note (or lets automation handle it when enabled).
14. If enabled, tests Scribe `/api/refine` and `/api/ask` proxies.
15. If enabled, runs a Claude CLI MCP prompt check.

If any critical step fails, the script exits non-zero and prints the log path.

## MCP Test Notes

The script uses a simple JSON-RPC call:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list"}
```

Expected response includes `read_notes` and `add_note`. If your MCP client expects a different method name, adjust the script accordingly.

## Claude CLI (Optional)

To test the MCP server via Claude Code CLI:

1) Add the MCP server:
```bash
claude mcp add --transport http athena-pkms http://127.0.0.1:8000/mcp
```

2) Run a prompt that forces tool use:
```bash
claude -p "Use read_notes to list atlas root, then summarize the relevant files about Proxmox." \
  --model "claude-3-5-sonnet" \
  --temperature 0
```

3) Confirm the tool call and verify the summary references the new atlas file.

## Test Data Organization

Test data is stored in repo-tracked `tests/` subdirectories:

**Stress tests:**
- Directory: `tests/TEST-RESULT-YYYY-MM-DD/`
- Contains: metrics JSON files and test data (inbox, atlas, .gardener DB, etc.)
- Report: `tests/TEST-RESULT-YYYY-MM-DD.md` (adjacent to data directory)

**E2E tests:**
- Directory: `tests/TEST-E2E-YYYY-MM-DD-HHMMSS/`
- Contains: test data (not typically documented in reports)

**Version control:**
- Test report `.md` files and `metrics/*.json` are tracked in git
- Large data subdirectories (inbox/, atlas/, .gardener/) are ignored via `tests/.gitignore`
- This allows validating test results alongside test data without bloating the repo

## API Usage Monitoring and Rate Limiting

**IMPORTANT:** Gardener now tracks all AI backend API calls to prevent runaway usage and enforce quotas.

### Features

The API usage tracking system provides:
- Per-operation call counters (classify, refine, ask)
- Hourly and daily rate limits with configurable thresholds
- Warning logs when approaching limits (default: 80% of quota)
- Automatic rate limit enforcement with graceful errors
- Usage statistics in `/api/status` endpoint

### Configuration

Set these environment variables to control API usage limits:

```bash
# Maximum API calls per hour (default: 100)
MAX_API_CALLS_PER_HOUR=100

# Maximum API calls per day (default: 500)
MAX_API_CALLS_PER_DAY=500

# Warning threshold percentage (default: 80)
API_WARN_THRESHOLD_PERCENT=80
```

### Checking API Usage

View current API usage via the status endpoint:

```bash
curl http://localhost:8000/api/status | jq '.api_usage'
```

Response includes:
- `total_calls`: Total API calls since database creation
- `calls_last_hour`: Calls in the last 60 minutes
- `calls_last_day`: Calls in the last 24 hours
- `hourly_limit` / `daily_limit`: Configured limits
- `hourly_usage_percent` / `daily_usage_percent`: Usage as percentage
- `is_near_hourly_limit` / `is_near_daily_limit`: Warning flags

### Checking for Runaway Processes

After running tests, verify no gardener processes are still running:

```bash
# Check for gardener processes
ps aux | grep -i gardener | grep -v grep

# Or check specifically for uvicorn/python processes on gardener port
lsof -i :8000  # Replace 8000 with your GARDENER_PORT

# Kill any lingering processes
pkill -f "uvicorn main:app"
```

**Note:** The test scripts (`test_e2e_full.sh`, `run_stress_tests.sh`) include automatic cleanup handlers (`trap cleanup EXIT`) that kill gardener processes when the script exits. However, if a script is interrupted with `SIGKILL` or system crash, processes may survive.

### Expected API Call Counts

Reference counts for common test scenarios:

**E2E Test (`test_e2e_full.sh`):**
- 1-2 classify calls (inbox notes)
- 1 ask call
- 1 refine call
- 1 MCP add_note call (if enabled)
- **Total: ~4-5 API calls**

**Stress Test Scenario A** (ingestion, 100 notes):
- 100 classify calls (if classification enabled)
- **Total: ~100 API calls**

**Stress Test Scenario B** (concurrent, 60s):
- Variable classify calls (depends on submit threads and duration)
- Configurable ask/refine calls (capped by `STRESS_AI_CALL_MULTIPLIER`)
- **Total: 10-200+ API calls** (depends on configuration)

**Stress Test Scenario C** (large repo):
- Minimal classify calls (tests search/refine on existing data)
- ~5 ask/refine calls
- **Total: ~5-10 API calls**

### Debugging High API Usage

If you see unexpectedly high API usage:

1. Check recent API calls in the database:
   ```bash
   sqlite3 /path/to/data/.gardener/state.db "SELECT backend, operation, timestamp, success FROM api_calls ORDER BY timestamp DESC LIMIT 50;"
   ```

2. Count calls by operation type:
   ```bash
   sqlite3 /path/to/data/.gardener/state.db "SELECT operation, COUNT(*) as count FROM api_calls WHERE success = 1 GROUP BY operation;"
   ```

3. Look for automation running in background:
   ```bash
   curl http://localhost:8000/api/status | jq '.automation'
   ```

4. Check gardener logs for rate limit warnings:
   ```bash
   grep -i "API usage at" /path/to/gardener.log
   ```

## Cleanup

Remove old test data (preserves reports):

```bash
# Remove all test data subdirectories but keep .md reports
find tests/ -type d \( -name "TEST-RESULT-*" -o -name "TEST-E2E-*" \) -exec rm -rf {} +

# Or remove everything including reports
rm -rf tests/TEST-RESULT-* tests/TEST-E2E-*
```
