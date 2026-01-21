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
- Creates a new test data dir under `$HOME/.pkms-test/<run-id>`
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
RUN_STRESS_TESTS=1 STRESS_DATA_DIR=$HOME/.pkms-stress/manual \
  uv run pytest tests/stress/test_stress_ingestion.py -m stress -s
```

### Stress Test Scenarios

- **Scenario A (Ingestion throughput)**: High-volume `/api/inbox` ingestion with optional classification accuracy checks.
- **Scenario B (Concurrent load)**: Sustained mixed traffic (`/api/inbox`, `/api/browse`, `/api/ask`, `/api/refine`) with optional data-loss checks.
- **Scenario C (Large repo)**: Large atlas + git history, reconcile + search/refine + trigger flow with git/DB/memory metrics.

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

CI smoke mode sets smaller defaults for load-based scenarios and disables optional asserts:

```bash
CI_SMOKE=1
```

### Stress Test Outputs

- Per-scenario metrics: `$STRESS_METRICS_DIR/scenario-A.json`, `scenario-B.json`, `scenario-C.json`
- Aggregated metrics: `$STRESS_METRICS_DIR/summary.json`
- Gardener log (runner-started): `$STRESS_DATA_DIR/gardener.log`

## Environment Flags

Set these when you run the script:

```bash
# Keep test data directory after run
KEEP_DATA=1 ./scripts/test_e2e_full.sh

# Use a fixed test data directory
TEST_DATA_DIR=$HOME/.pkms-test/manual ./scripts/test_e2e_full.sh

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

## Cleanup

Remove test data:

```bash
rm -rf $HOME/.pkms-test
```
