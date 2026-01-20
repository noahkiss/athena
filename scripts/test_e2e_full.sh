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
TEST_DATA_DIR=${TEST_DATA_DIR:-"$HOME/.pkms-test/$RUN_ID"}
KEEP_DATA=${KEEP_DATA:-0}
TEST_SCRIBE=${TEST_SCRIBE:-1}
FORCE_BUILD=${FORCE_BUILD:-0}
GARDENER_PORT=${GARDENER_PORT:-8000}
SCRIBE_PORT=${SCRIBE_PORT:-3000}

export DATA_DIR="$TEST_DATA_DIR"
export GARDNER_URL="http://127.0.0.1:${GARDENER_PORT}"

if [[ "$KEEP_DATA" != "1" ]]; then
  rm -rf "$TEST_DATA_DIR"
fi
mkdir -p "$TEST_DATA_DIR"

GARDENER_LOG="$TEST_DATA_DIR/gardener.log"
SCRIBE_LOG="$TEST_DATA_DIR/scribe.log"

cleanup() {
  local exit_code=$?
  if [[ -n "${scribe_pid:-}" ]]; then
    kill "$scribe_pid" 2>/dev/null || true
  fi
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

start_scribe() {
  if [[ "$TEST_SCRIBE" != "1" ]]; then
    return 0
  fi

  pushd "$ROOT_DIR/scribe" >/dev/null
  if [[ ! -d node_modules ]]; then
    npm ci
  fi
  if [[ "$FORCE_BUILD" == "1" || ! -d dist ]]; then
    npm run build
  fi

  HOST=127.0.0.1 PORT="$SCRIBE_PORT" node ./dist/server/entry.mjs >"$SCRIBE_LOG" 2>&1 &
  scribe_pid=$!
  popd >/dev/null

  for _ in {1..60}; do
    if curl -s -o /dev/null "http://127.0.0.1:${SCRIBE_PORT}/"; then
      return 0
    fi
    sleep 0.5
    if ! kill -0 "$scribe_pid" 2>/dev/null; then
      echo "Scribe failed to start. See $SCRIBE_LOG"
      return 1
    fi
  done
  echo "Timed out waiting for Scribe. See $SCRIBE_LOG"
  return 1
}

start_gardener
start_scribe

curl -s -X POST "http://127.0.0.1:${GARDENER_PORT}/api/bootstrap" >/tmp/gardener-bootstrap.json

TOKEN_DIRECT=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import uuid
print(f"direct-{uuid.uuid4().hex[:8]}")
PY
popd >/dev/null)
export TOKEN_DIRECT

NOTE_DIRECT="Project Athena test ${TOKEN_DIRECT}: Build a small homelab server. Document Proxmox setup and a network plan."
export NOTE_DIRECT
NOTE_DIRECT_JSON=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import json, os
print(json.dumps({"content": os.environ["NOTE_DIRECT"]}))
PY
popd >/dev/null)
INBOX_RES=$(curl -s -X POST "http://127.0.0.1:${GARDENER_PORT}/api/inbox" -H "Content-Type: application/json" -d "$NOTE_DIRECT_JSON")

if [[ "$TEST_SCRIBE" == "1" ]]; then
  TOKEN_SCRIBE=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import uuid
print(f"scribe-{uuid.uuid4().hex[:8]}")
PY
popd >/dev/null)
  NOTE_SCRIBE="Scribe test ${TOKEN_SCRIBE}: add a note about backup strategy for the homelab."
  curl -s -X POST "http://127.0.0.1:${SCRIBE_PORT}/api/inbox" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "content=${NOTE_SCRIBE}" >/tmp/scribe-inbox.json
fi

curl -s -X POST "http://127.0.0.1:${GARDENER_PORT}/api/trigger-gardener" >/tmp/gardener-trigger.json

for _ in {1..80}; do
  if [[ -z "$(ls -1 "$DATA_DIR"/inbox/*.md 2>/dev/null || true)" ]]; then
    break
  fi
  sleep 0.5
  done

LATEST_ATLAS=$(find "$DATA_DIR"/atlas -type f -name "*.md" -printf "%T@ %p\n" 2>/dev/null | sort -nr | head -n 1 | awk '{print $2}')
if [[ -z "$LATEST_ATLAS" ]]; then
  echo "No atlas files created. Check $GARDENER_LOG"
  exit 1
fi
export LATEST_ATLAS

REL_PATH=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import os
atlas_root = os.path.join(os.environ["DATA_DIR"], "atlas")
latest = os.environ["LATEST_ATLAS"]
print(os.path.relpath(latest, atlas_root))
PY
popd >/dev/null)
export REL_PATH

ENCODED_PATH=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import os, urllib.parse
print(urllib.parse.quote(os.environ["REL_PATH"]))
PY
popd >/dev/null)

BROWSE_FILE=$(curl -s "http://127.0.0.1:${GARDENER_PORT}/api/browse/${ENCODED_PATH}")

ASK_PAYLOAD=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import json, os
question = f"Where should I document the Proxmox homelab plan from {os.environ['TOKEN_DIRECT']}?"
print(json.dumps({"question": question}))
PY
popd >/dev/null)
ASK_ANSWER=$(curl -s --max-time 60 -X POST "http://127.0.0.1:${GARDENER_PORT}/api/ask" -H "Content-Type: application/json" -d "$ASK_PAYLOAD")

REFINE_PAYLOAD=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import json, os
content = f"Need to document Proxmox setup and network plan for {os.environ['TOKEN_DIRECT']}"
print(json.dumps({"content": content}))
PY
popd >/dev/null)
REFINE_RES=$(curl -s --max-time 60 -X POST "http://127.0.0.1:${GARDENER_PORT}/api/refine" -H "Content-Type: application/json" -d "$REFINE_PAYLOAD")

MCP_STATUS=$(curl -s -L -o /tmp/mcp-tools.json -w "%{http_code}" -X POST "http://127.0.0.1:${GARDENER_PORT}/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}')

if [[ "$MCP_STATUS" != "200" ]]; then
  echo "MCP tools/list failed with status $MCP_STATUS"
  cat /tmp/mcp-tools.json
  exit 1
fi

if ! grep -q "read_notes" /tmp/mcp-tools.json; then
  echo "MCP response missing read_notes. Response:"
  cat /tmp/mcp-tools.json
  exit 1
fi

if [[ "$TEST_SCRIBE" == "1" ]]; then
  S_REFINE=$(curl -s --max-time 60 -X POST "http://127.0.0.1:${SCRIBE_PORT}/api/refine" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "content=Refine test ${TOKEN_SCRIBE}")
  S_ASK=$(curl -s --max-time 60 -X POST "http://127.0.0.1:${SCRIBE_PORT}/api/ask" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "content=What did I say about backup strategy for ${TOKEN_SCRIBE}?" )
fi

printf "Gardener inbox response: %s\n" "$INBOX_RES"
printf "Latest atlas file: %s\n" "$LATEST_ATLAS"
printf "Browse response: %s\n" "$BROWSE_FILE"
printf "Ask response: %s\n" "$ASK_ANSWER"
printf "Refine response: %s\n" "$REFINE_RES"
if [[ "$TEST_SCRIBE" == "1" ]]; then
  printf "Scribe refine response: %s\n" "$S_REFINE"
  printf "Scribe ask response: %s\n" "$S_ASK"
fi

echo "Done. Logs: $GARDENER_LOG${TEST_SCRIBE:+, $SCRIBE_LOG}"
