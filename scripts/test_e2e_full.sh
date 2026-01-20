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
TEST_AUTOMATION=${TEST_AUTOMATION:-0}
TEST_CLAUDE=${TEST_CLAUDE:-0}
GARDENER_PORT=${GARDENER_PORT:-8000}
SCRIBE_PORT=${SCRIBE_PORT:-3000}

export DATA_DIR="$TEST_DATA_DIR"
export GARDNER_URL="http://127.0.0.1:${GARDENER_PORT}"

if [[ "$TEST_AUTOMATION" == "1" ]]; then
  export GARDENER_AUTO=${GARDENER_AUTO:-true}
  export GARDENER_MODE=${GARDENER_MODE:-poll}
  export GARDENER_POLL_INTERVAL=${GARDENER_POLL_INTERVAL:-2}
  export GARDENER_DEBOUNCE=${GARDENER_DEBOUNCE:-0.5}
fi

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
  rebuild=0
  if [[ "$FORCE_BUILD" == "1" || ! -d dist ]]; then
    rebuild=1
  elif [[ ! -f dist/server/entry.mjs ]]; then
    rebuild=1
  elif find src -type f -newer dist/server/entry.mjs -print -quit | grep -q .; then
    rebuild=1
  fi
  if [[ "$rebuild" == "1" ]]; then
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

check_status() {
  local expect_bootstrapped=${1:-""}
  local expect_auto=${2:-""}
  local status_file
  status_file=$(mktemp)
  curl -s "http://127.0.0.1:${GARDENER_PORT}/api/status" >"$status_file"
  export EXPECT_BOOTSTRAPPED="$expect_bootstrapped"
  export EXPECT_AUTO="$expect_auto"
  export STATUS_FILE="$status_file"
  pushd "$ROOT_DIR/gardener" >/dev/null
  uv run python - <<'PY'
import json
import os
import sys
from pathlib import Path

status_path = os.environ["STATUS_FILE"]
with open(status_path, "r") as handle:
    data = json.load(handle)

if data.get("status") != "ok":
    sys.exit("Status endpoint did not return ok")

expected_inbox = str(Path(os.environ["DATA_DIR"]) / "inbox")
if data.get("inbox_path") != expected_inbox:
    sys.exit(f"inbox_path mismatch: {data.get('inbox_path')} != {expected_inbox}")

expected_backend = os.environ.get("GARDENER_BACKEND")
if expected_backend and data.get("gardener_backend") != expected_backend:
    sys.exit(f"gardener_backend mismatch: {data.get('gardener_backend')} != {expected_backend}")

expected_thinking = os.environ.get("AI_MODEL_THINKING")
if expected_thinking and data.get("gardener_model") != expected_thinking:
    sys.exit(f"gardener_model mismatch: {data.get('gardener_model')} != {expected_thinking}")

expected_fast = os.environ.get("AI_MODEL_FAST")
if expected_fast and data.get("gardener_model_fast") != expected_fast:
    sys.exit(f"gardener_model_fast mismatch: {data.get('gardener_model_fast')} != {expected_fast}")

expect_bootstrapped = os.environ.get("EXPECT_BOOTSTRAPPED")
if expect_bootstrapped in ("0", "1"):
    if bool(data.get("bootstrapped")) != (expect_bootstrapped == "1"):
        sys.exit(f"bootstrapped mismatch: {data.get('bootstrapped')} != {expect_bootstrapped}")

expect_auto = os.environ.get("EXPECT_AUTO")
if expect_auto in ("0", "1"):
    auto = data.get("automation") or {}
    if bool(auto.get("enabled")) != (expect_auto == "1"):
        sys.exit(f"automation.enabled mismatch: {auto.get('enabled')} != {expect_auto}")
    if expect_auto == "1":
        expected_mode = os.environ.get("GARDENER_MODE", "poll")
        if auto.get("mode") != expected_mode:
            sys.exit(f"automation.mode mismatch: {auto.get('mode')} != {expected_mode}")
PY
  popd >/dev/null
  rm -f "$status_file"
}

wait_for_inbox_empty() {
  local limit=${1:-80}
  for _ in $(seq 1 "$limit"); do
    if [[ -z "$(ls -1 "$DATA_DIR"/inbox/*.md 2>/dev/null || true)" ]]; then
      return 0
    fi
    sleep 0.5
  done
  return 1
}

wait_for_token_in_atlas() {
  local token=$1
  local limit=${2:-40}
  for _ in $(seq 1 "$limit"); do
    export SEARCH_TOKEN="$token"
    pushd "$ROOT_DIR/gardener" >/dev/null
    if output=$(uv run python - <<'PY'
import os
import sys
from pathlib import Path

token = os.environ["SEARCH_TOKEN"]
atlas_root = Path(os.environ["DATA_DIR"]) / "atlas"
for path in atlas_root.rglob("*.md"):
    try:
        if token in path.read_text():
            print(path)
            sys.exit(0)
    except Exception:
        continue
sys.exit(1)
PY
    ); then
      popd >/dev/null
      if [[ -n "$output" ]]; then
        echo "$output"
      fi
      return 0
    fi
    popd >/dev/null
    sleep 0.5
  done
  return 1
}

start_gardener
start_scribe

EXPECT_AUTO_FLAG=0
if [[ "$TEST_AUTOMATION" == "1" ]]; then
  EXPECT_AUTO_FLAG=1
fi
check_status "" "$EXPECT_AUTO_FLAG"

curl -s -X POST "http://127.0.0.1:${GARDENER_PORT}/api/bootstrap" >/tmp/gardener-bootstrap.json

check_status "1" "$EXPECT_AUTO_FLAG"
if [[ ! -f "$DATA_DIR/AGENTS.md" ]]; then
  echo "AGENTS.md missing after bootstrap"
  exit 1
fi
if [[ ! -d "$DATA_DIR/atlas" ]]; then
  echo "Atlas directory missing after bootstrap"
  exit 1
fi

TRAVERSAL_PATH=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import urllib.parse
print(urllib.parse.quote("../.."))
PY
popd >/dev/null)
BROWSE_FORBIDDEN_STATUS=$(curl -s -o /tmp/browse-forbidden.json -w "%{http_code}" \
  "http://127.0.0.1:${GARDENER_PORT}/api/browse/${TRAVERSAL_PATH}")
if [[ "$BROWSE_FORBIDDEN_STATUS" != "403" && "$BROWSE_FORBIDDEN_STATUS" != "404" ]]; then
  echo "Expected browse traversal to return 403 or 404, got $BROWSE_FORBIDDEN_STATUS"
  cat /tmp/browse-forbidden.json
  exit 1
fi

MISSING_PATH="missing-${RUN_ID}.md"
BROWSE_MISSING_STATUS=$(curl -s -o /tmp/browse-missing.json -w "%{http_code}" \
  "http://127.0.0.1:${GARDENER_PORT}/api/browse/${MISSING_PATH}")
if [[ "$BROWSE_MISSING_STATUS" != "404" ]]; then
  echo "Expected browse missing file to return 404, got $BROWSE_MISSING_STATUS"
  cat /tmp/browse-missing.json
  exit 1
fi

EMPTY_ASK=$(curl -s --max-time 30 -X POST "http://127.0.0.1:${GARDENER_PORT}/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": ""}')
if [[ "$EMPTY_ASK" != *"Enter a question"* ]]; then
  echo "Expected empty ask prompt message, got: $EMPTY_ASK"
  exit 1
fi

EMPTY_REFINE=$(curl -s --max-time 30 -X POST "http://127.0.0.1:${GARDENER_PORT}/api/refine" \
  -H "Content-Type: application/json" \
  -d '{"content": ""}')
if [[ "$EMPTY_REFINE" != *"Enter some content"* ]]; then
  echo "Expected empty refine prompt message, got: $EMPTY_REFINE"
  exit 1
fi

INVALID_ACTION_TARGET=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
from backends import GardenerAction
from workers.gardener import execute_action

action = GardenerAction(
    action="create",
    path="../../escape.md",
    content="Invalid path test content",
    reasoning="test invalid path handling",
)
target = execute_action(action)
print(target)
PY
popd >/dev/null)
if [[ "$INVALID_ACTION_TARGET" != "$DATA_DIR/tasks.md" ]]; then
  echo "Invalid action path should route to tasks.md, got: $INVALID_ACTION_TARGET"
  exit 1
fi
if [[ ! -f "$DATA_DIR/tasks.md" ]] || ! grep -q "Invalid path" "$DATA_DIR/tasks.md"; then
  echo "tasks.md missing invalid path entry"
  exit 1
fi

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
export INBOX_RES
pushd "$ROOT_DIR/gardener" >/dev/null
uv run python - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["INBOX_RES"])
if not data.get("filename"):
    sys.exit("Inbox response missing filename")
if "Note saved" not in (data.get("message") or ""):
    sys.exit("Inbox response missing success message")
PY
popd >/dev/null

if [[ "$TEST_SCRIBE" == "1" ]]; then
  TOKEN_SCRIBE=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import uuid
print(f"scribe-{uuid.uuid4().hex[:8]}")
PY
popd >/dev/null)
  NOTE_SCRIBE="Scribe test ${TOKEN_SCRIBE}: add a note about backup strategy for the homelab."
  S_INBOX=$(curl -s -X POST "http://127.0.0.1:${SCRIBE_PORT}/api/inbox" \
    -H "Origin: http://127.0.0.1:${SCRIBE_PORT}" \
    -H "Referer: http://127.0.0.1:${SCRIBE_PORT}/" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "content=${NOTE_SCRIBE}")
  if [[ "$S_INBOX" != *"Saved to inbox"* ]]; then
    echo "Scribe inbox failed. Response: $S_INBOX"
    exit 1
  fi
  S_EMPTY_STATUS=$(curl -s -o /tmp/scribe-inbox-empty.json -w "%{http_code}" -X POST "http://127.0.0.1:${SCRIBE_PORT}/api/inbox" \
    -H "Origin: http://127.0.0.1:${SCRIBE_PORT}" \
    -H "Referer: http://127.0.0.1:${SCRIBE_PORT}/" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "content=")
  if [[ "$S_EMPTY_STATUS" != "400" ]]; then
    echo "Expected scribe empty inbox to return 400, got $S_EMPTY_STATUS"
    cat /tmp/scribe-inbox-empty.json
    exit 1
  fi
fi

curl -s -X POST "http://127.0.0.1:${GARDENER_PORT}/api/trigger-gardener" >/tmp/gardener-trigger.json

if ! wait_for_inbox_empty 80; then
  echo "Timed out waiting for inbox to clear. See $GARDENER_LOG"
  exit 1
fi

DIRECT_ATLAS=$(wait_for_token_in_atlas "$TOKEN_DIRECT" 40 || true)
if [[ -z "$DIRECT_ATLAS" ]]; then
  echo "Token from direct note not found in atlas"
  exit 1
fi
export DIRECT_ATLAS

if [[ "$TEST_SCRIBE" == "1" ]]; then
  SCRIBE_ATLAS=$(wait_for_token_in_atlas "$TOKEN_SCRIBE" 40 || true)
  if [[ -z "$SCRIBE_ATLAS" ]]; then
    echo "Token from scribe note not found in atlas"
    exit 1
  fi
  export SCRIBE_ATLAS
fi

LATEST_ATLAS=$(find "$DATA_DIR"/atlas -type f -name "*.md" -printf "%T@ %p\n" 2>/dev/null | sort -nr | head -n 1 | awk '{print $2}')
if [[ -z "$LATEST_ATLAS" ]]; then
  echo "No atlas files created. Check $GARDENER_LOG"
  exit 1
fi
export LATEST_ATLAS

REL_PATH=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import os
atlas_root = os.path.join(os.environ["DATA_DIR"], "atlas")
direct = os.environ["DIRECT_ATLAS"]
print(os.path.relpath(direct, atlas_root))
PY
popd >/dev/null)
export REL_PATH

ENCODED_PATH=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import os, urllib.parse
print(urllib.parse.quote(os.environ["REL_PATH"]))
PY
popd >/dev/null)

BROWSE_FILE_PATH=/tmp/gardener-browse.json
curl -s "http://127.0.0.1:${GARDENER_PORT}/api/browse/${ENCODED_PATH}" >"$BROWSE_FILE_PATH"
BROWSE_FILE=$(cat "$BROWSE_FILE_PATH")

export BROWSE_FILE_PATH
pushd "$ROOT_DIR/gardener" >/dev/null
uv run python - <<'PY'
import json
import os
import sys

with open(os.environ["BROWSE_FILE_PATH"], "r") as handle:
    data = json.load(handle)

if data.get("path") != os.environ["REL_PATH"]:
    sys.exit(f"Browse path mismatch: {data.get('path')} != {os.environ['REL_PATH']}")

if not data.get("is_file"):
    sys.exit("Browse response did not mark item as file")

content = data.get("content") or ""
if os.environ["TOKEN_DIRECT"] not in content:
    sys.exit("Browse content missing direct token")
PY
popd >/dev/null

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

if [[ -z "$ASK_ANSWER" || "$ASK_ANSWER" == *"AI not configured"* || "$ASK_ANSWER" == *"Ask failed"* ]]; then
  echo "Ask endpoint returned error or empty response: $ASK_ANSWER"
  exit 1
fi
if [[ -z "$REFINE_RES" || "$REFINE_RES" == *"AI not configured"* || "$REFINE_RES" == *"Refinement failed"* ]]; then
  echo "Refine endpoint returned error or empty response: $REFINE_RES"
  exit 1
fi
if [[ "$REFINE_RES" != *"Tags:"* || "$REFINE_RES" != *"Category:"* ]]; then
  echo "Refine response missing expected fields: $REFINE_RES"
  exit 1
fi

MCP_STATUS=$(curl -s -L -o /tmp/mcp-tools.json -w "%{http_code}" -X POST "http://127.0.0.1:${GARDENER_PORT}/mcp" \
  -H "Accept: application/json" \
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
if ! grep -q "add_note" /tmp/mcp-tools.json; then
  echo "MCP response missing add_note. Response:"
  cat /tmp/mcp-tools.json
  exit 1
fi

MCP_READ_PAYLOAD=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import json, os
payload = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {"name": "read_notes", "arguments": {"path": os.environ["REL_PATH"]}},
}
print(json.dumps(payload))
PY
popd >/dev/null)
MCP_READ_STATUS=$(curl -s -L -o /tmp/mcp-read.json -w "%{http_code}" -X POST "http://127.0.0.1:${GARDENER_PORT}/mcp" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d "$MCP_READ_PAYLOAD")
if [[ "$MCP_READ_STATUS" != "200" ]]; then
  echo "MCP read_notes failed with status $MCP_READ_STATUS"
  cat /tmp/mcp-read.json
  exit 1
fi
if ! grep -Fq "$TOKEN_DIRECT" /tmp/mcp-read.json; then
  echo "MCP read_notes response missing direct token. Response:"
  cat /tmp/mcp-read.json
  exit 1
fi

MCP_TOKEN=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import uuid
print(f"mcp-{uuid.uuid4().hex[:8]}")
PY
popd >/dev/null)
export MCP_TOKEN
MCP_ADD_PAYLOAD=$(pushd "$ROOT_DIR/gardener" >/dev/null && uv run python - <<'PY'
import json, os
payload = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "add_note",
        "arguments": {"content": f"MCP note {os.environ['MCP_TOKEN']}: capture backup plan and retention."},
    },
}
print(json.dumps(payload))
PY
popd >/dev/null)
MCP_ADD_STATUS=$(curl -s -L -o /tmp/mcp-add.json -w "%{http_code}" -X POST "http://127.0.0.1:${GARDENER_PORT}/mcp" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d "$MCP_ADD_PAYLOAD")
if [[ "$MCP_ADD_STATUS" != "200" ]]; then
  echo "MCP add_note failed with status $MCP_ADD_STATUS"
  cat /tmp/mcp-add.json
  exit 1
fi
if ! grep -q "Note saved to inbox" /tmp/mcp-add.json; then
  echo "MCP add_note response missing success message:"
  cat /tmp/mcp-add.json
  exit 1
fi

if [[ "$TEST_AUTOMATION" != "1" ]]; then
  curl -s -X POST "http://127.0.0.1:${GARDENER_PORT}/api/trigger-gardener" >/tmp/gardener-trigger-mcp.json
fi
MCP_ATLAS=$(wait_for_token_in_atlas "$MCP_TOKEN" 60 || true)
if [[ -z "$MCP_ATLAS" ]]; then
  echo "Token from MCP add_note not found in atlas"
  exit 1
fi
export MCP_ATLAS

if [[ "$TEST_SCRIBE" == "1" ]]; then
  S_REFINE=$(curl -s --max-time 60 -X POST "http://127.0.0.1:${SCRIBE_PORT}/api/refine" \
    -H "Origin: http://127.0.0.1:${SCRIBE_PORT}" \
    -H "Referer: http://127.0.0.1:${SCRIBE_PORT}/" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "content=Refine test ${TOKEN_SCRIBE}")
  S_ASK=$(curl -s --max-time 60 -X POST "http://127.0.0.1:${SCRIBE_PORT}/api/ask" \
    -H "Origin: http://127.0.0.1:${SCRIBE_PORT}" \
    -H "Referer: http://127.0.0.1:${SCRIBE_PORT}/" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "content=What did I say about backup strategy for ${TOKEN_SCRIBE}?" )
  if [[ "$S_REFINE" == *"Cross-site POST form submissions are forbidden"* ]]; then
    echo "Scribe refine failed CSRF check. Response: $S_REFINE"
    exit 1
  fi
  if [[ "$S_ASK" == *"Cross-site POST form submissions are forbidden"* ]]; then
    echo "Scribe ask failed CSRF check. Response: $S_ASK"
    exit 1
  fi
  if [[ "$S_REFINE" == *"Refinement failed"* ]]; then
    echo "Scribe refine returned error. Response: $S_REFINE"
    exit 1
  fi
  if [[ "$S_ASK" == *"Ask failed"* ]]; then
    echo "Scribe ask returned error. Response: $S_ASK"
    exit 1
  fi
  if [[ "$S_ASK" == *"<title>404"* || "$S_ASK" == *"Path: /api/ask"* ]]; then
    echo "Scribe ask returned 404. Response: $S_ASK"
    exit 1
  fi
fi

if [[ "$TEST_CLAUDE" == "1" ]]; then
  if ! command -v claude >/dev/null 2>&1; then
    echo "Claude CLI not found (TEST_CLAUDE=1). Install it or disable TEST_CLAUDE."
    exit 1
  fi
  if ! claude mcp list | grep -q "athena-pkms"; then
    claude mcp add --transport http athena-pkms "http://127.0.0.1:${GARDENER_PORT}/mcp"
  fi
  CLAUDE_MODEL=${CLAUDE_MODEL:-}
  CLAUDE_OUTPUT=$(mktemp)
  CLAUDE_PROMPT="Use read_notes to find the file that mentions ${TOKEN_DIRECT}, then summarize it."
  CLAUDE_TEMP_ARGS=()
  if claude --help 2>&1 | grep -q -- "--temperature"; then
    CLAUDE_TEMP_ARGS=(--temperature 0)
  fi
  CLAUDE_CMD=(claude -p "$CLAUDE_PROMPT")
  if [[ -n "$CLAUDE_MODEL" ]]; then
    CLAUDE_CMD+=(--model "$CLAUDE_MODEL")
  fi
  CLAUDE_CMD+=("${CLAUDE_TEMP_ARGS[@]}")
  if ! "${CLAUDE_CMD[@]}" >"$CLAUDE_OUTPUT" 2>&1; then
    echo "Claude CLI failed. Output:"
    cat "$CLAUDE_OUTPUT"
    exit 1
  fi
  if ! grep -Fq "$TOKEN_DIRECT" "$CLAUDE_OUTPUT"; then
    echo "Claude output did not reference the direct token. Output:"
    cat "$CLAUDE_OUTPUT"
    exit 1
  fi
  rm -f "$CLAUDE_OUTPUT"
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
