#!/usr/bin/env bash
set -euo pipefail

GARDNER_HOST=${GARDNER_HOST:-0.0.0.0}
GARDNER_PORT=${GARDNER_PORT:-8000}
SCRIBE_HOST=${SCRIBE_HOST:-0.0.0.0}
SCRIBE_PORT=${SCRIBE_PORT:-3000}

export GARDNER_URL=${GARDNER_URL:-http://127.0.0.1:${GARDNER_PORT}}

cleanup() {
  local exit_code=$?

  if [[ -n "${gardener_pid:-}" ]]; then
    kill "${gardener_pid}" 2>/dev/null || true
  fi

  if [[ -n "${scribe_pid:-}" ]]; then
    kill "${scribe_pid}" 2>/dev/null || true
  fi

  wait || true
  exit "${exit_code}"
}

trap cleanup SIGINT SIGTERM

cd /app/gardener
uv run uvicorn main:app --host "${GARDNER_HOST}" --port "${GARDNER_PORT}" &

gardener_pid=$!

cd /app/scribe
HOST="${SCRIBE_HOST}" PORT="${SCRIBE_PORT}" node ./dist/server/entry.mjs &

scribe_pid=$!

wait -n
exit_code=$?

kill "${gardener_pid}" "${scribe_pid}" 2>/dev/null || true
wait || true
exit "${exit_code}"
