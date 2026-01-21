#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

RUN_ID=${RUN_ID:-"$(date +%Y%m%d-%H%M%S)-$RANDOM"}
REPORT_DATE=${REPORT_DATE:-"$(date +%Y-%m-%d)"}
STRESS_DATA_DIR=${STRESS_DATA_DIR:-"$ROOT_DIR/tests/TEST-RESULT-$REPORT_DATE"}
KEEP_DATA=${KEEP_DATA:-0}
START_GARDENER=${START_GARDENER:-1}
RUN_BOOTSTRAP=${RUN_BOOTSTRAP:-1}
CI_SMOKE=${CI_SMOKE:-0}
GARDENER_PORT=${GARDENER_PORT:-8000}
STRESS_BASE_URL=${STRESS_BASE_URL:-"http://127.0.0.1:${GARDENER_PORT}"}
STRESS_SCENARIOS=${STRESS_SCENARIOS:-""}
STRESS_METRICS_DIR=${STRESS_METRICS_DIR:-"$STRESS_DATA_DIR/metrics"}

export DATA_DIR="$STRESS_DATA_DIR"
export RUN_ID
export STRESS_DATA_DIR
export STRESS_BASE_URL
export STRESS_METRICS_DIR
export RUN_STRESS_TESTS=1

if [[ "$CI_SMOKE" == "1" ]]; then
  export STRESS_NOTE_COUNT=${STRESS_NOTE_COUNT:-100}
  export STRESS_CONCURRENCY=${STRESS_CONCURRENCY:-10}
  export STRESS_NOTES_PER_CLIENT=${STRESS_NOTES_PER_CLIENT:-10}
  export STRESS_DURATION_S=${STRESS_DURATION_S:-60}
  export STRESS_SUBMIT_THREADS=${STRESS_SUBMIT_THREADS:-5}
  export STRESS_BROWSE_THREADS=${STRESS_BROWSE_THREADS:-2}
  export STRESS_ASK_THREADS=${STRESS_ASK_THREADS:-2}
  export STRESS_REFINE_THREADS=${STRESS_REFINE_THREADS:-1}
  export STRESS_SUBMIT_RPS=${STRESS_SUBMIT_RPS:-2}
  export STRESS_EXPECT_ARCHIVE=${STRESS_EXPECT_ARCHIVE:-0}
  export STRESS_EXPECT_CLASSIFICATION=${STRESS_EXPECT_CLASSIFICATION:-0}
fi

if [[ -z "$STRESS_SCENARIOS" ]]; then
  if [[ "$CI_SMOKE" == "1" ]]; then
    STRESS_SCENARIOS="A,B"
  else
    STRESS_SCENARIOS="A"
  fi
fi

if [[ "$KEEP_DATA" != "1" ]]; then
  rm -rf "$STRESS_DATA_DIR"
fi
mkdir -p "$STRESS_DATA_DIR" "$STRESS_METRICS_DIR"

GARDENER_LOG="$STRESS_DATA_DIR/gardener.log"

cleanup() {
  local exit_code=$?
  if [[ -n "${gardener_pid:-}" ]]; then
    kill "$gardener_pid" 2>/dev/null || true
  fi
  wait 2>/dev/null || true
  exit "$exit_code"
}
trap cleanup EXIT

start_gardener() {
  pushd "$ROOT_DIR/gardener" >/dev/null
  uv run python -m uvicorn main:app --host 127.0.0.1 --port "$GARDENER_PORT" >"$GARDENER_LOG" 2>&1 &
  gardener_pid=$!
  popd >/dev/null

  for _ in {1..60}; do
    if curl -s -o /dev/null "http://127.0.0.1:${GARDENER_PORT}/api/status"; then
      return 0
    fi
    sleep 0.5
    if ! kill -0 "$gardener_pid" 2>/dev/null; then
      echo "Gardener failed to start. See $GARDENER_LOG"
      return 1
    fi
  done
  echo "Timed out waiting for Gardener. See $GARDENER_LOG"
  return 1
}

bootstrap_gardener() {
  curl -s -X POST "http://127.0.0.1:${GARDENER_PORT}/api/bootstrap" >/tmp/gardener-bootstrap.json
}

run_pytest() {
  local scenario=$1
  local test_file=$2
  export STRESS_METRICS_PATH="$STRESS_METRICS_DIR/scenario-${scenario}.json"
  if [[ -n "${gardener_pid:-}" ]]; then
    export STRESS_GARDENER_PID="$gardener_pid"
  fi
  pushd "$ROOT_DIR/gardener" >/dev/null
  uv run pytest "$test_file" -m stress -s
  popd >/dev/null
}

aggregate_metrics() {
  local output_path="$STRESS_METRICS_DIR/summary.json"
  pushd "$ROOT_DIR/gardener" >/dev/null
  uv run python - <<'PY'
import glob
import json
import os
from datetime import datetime, timezone

metrics_dir = os.environ["STRESS_METRICS_DIR"]
paths = sorted(glob.glob(os.path.join(metrics_dir, "scenario-*.json")))
scenarios = {}
for path in paths:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    scenario = payload.get("scenario") or os.path.splitext(os.path.basename(path))[0]
    scenarios[str(scenario)] = payload.get("summary", payload)

summary = {
    "run_id": os.environ.get("RUN_ID"),
    "data_dir": os.environ.get("STRESS_DATA_DIR"),
    "base_url": os.environ.get("STRESS_BASE_URL"),
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "scenarios": scenarios,
}

with open(os.path.join(metrics_dir, "summary.json"), "w", encoding="utf-8") as handle:
    json.dump(summary, handle, indent=2)
PY
  popd >/dev/null
  echo "Aggregated metrics: $output_path"
}

if [[ "$START_GARDENER" == "1" ]]; then
  start_gardener
fi

if [[ "$RUN_BOOTSTRAP" == "1" ]]; then
  bootstrap_gardener
fi

IFS="," read -r -a scenario_list <<<"$STRESS_SCENARIOS"
for scenario in "${scenario_list[@]}"; do
  case "$scenario" in
    A)
      run_pytest "A" "tests/stress/test_stress_ingestion.py"
      ;;
    B)
      run_pytest "B" "tests/stress/test_stress_concurrent.py"
      ;;
    C)
      run_pytest "C" "tests/stress/test_stress_large_repo.py"
      ;;
    D)
      run_pytest "D" "tests/stress/test_stress_db_contention.py"
      ;;
    E)
      run_pytest "E" "tests/stress/test_stress_chaos.py"
      ;;
    *)
      echo "Unknown scenario: $scenario"
      exit 1
      ;;
  esac
  echo "Scenario $scenario metrics: $STRESS_METRICS_DIR/scenario-${scenario}.json"
done

if compgen -G "$STRESS_METRICS_DIR/scenario-*.json" >/dev/null; then
  aggregate_metrics
fi

if [[ "$KEEP_DATA" != "1" ]]; then
  echo "Stress test complete. Data dir: $STRESS_DATA_DIR (will be removed on exit)"
else
  echo "Stress test complete. Data dir preserved at: $STRESS_DATA_DIR"
fi
