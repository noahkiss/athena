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
STRESS_DATA_DIR=${STRESS_DATA_DIR:-"$HOME/.pkms-stress/$RUN_ID"}
KEEP_DATA=${KEEP_DATA:-0}
START_GARDENER=${START_GARDENER:-1}
RUN_BOOTSTRAP=${RUN_BOOTSTRAP:-1}
GARDENER_PORT=${GARDENER_PORT:-8000}
STRESS_BASE_URL=${STRESS_BASE_URL:-"http://127.0.0.1:${GARDENER_PORT}"}
STRESS_SCENARIOS=${STRESS_SCENARIOS:-"A"}
STRESS_METRICS_DIR=${STRESS_METRICS_DIR:-"$STRESS_DATA_DIR/metrics"}

export DATA_DIR="$STRESS_DATA_DIR"
export STRESS_DATA_DIR
export STRESS_BASE_URL
export RUN_STRESS_TESTS=1

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
    *)
      echo "Unknown scenario: $scenario"
      exit 1
      ;;
  esac
  echo "Scenario $scenario metrics: $STRESS_METRICS_DIR/scenario-${scenario}.json"
done

if [[ "$KEEP_DATA" != "1" ]]; then
  echo "Stress test complete. Data dir: $STRESS_DATA_DIR (will be removed on exit)"
else
  echo "Stress test complete. Data dir preserved at: $STRESS_DATA_DIR"
fi
