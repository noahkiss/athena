# CLI Gardeners Specification (Draft)

## Goals

- Allow Gardener automation to use CLI-based agents (Claude Code, OpenAI Codex) in unattended mode.
- Run on the same filewatcher/poller/cron trigger as existing automation.
- Support 1-n configured CLI agents with failover if one hits usage limits.
- Keep agents tightly scoped with explicit permissions and a local-only config file.
- Reuse existing AGENTS instructions to keep behavior consistent and deterministic.

## Non-Goals (For Now)

- Replace the existing API backends (OpenAI/Anthropic). CLI is an additional backend.
- Implement interactive flows or require user input.

## Integration Points

- **Automation**: use the existing `GARDENER_AUTO` and `GARDENER_MODE` watch/poll triggers.
- **Backend selection**: introduce a `cli` backend (e.g., `GARDENER_BACKEND=cli`).
- **Worker path**: `workers/gardener.py` delegates classification to the CLI backend when selected.

## Execution Contract

### Inputs

- Note content and filename.
- The combined instructions from:
  - `DATA_DIR/AGENTS.md`
  - `DATA_DIR/GARDENER.md`
- Context metadata (data paths, repo state, etc.).

### Output

The CLI agent must output a JSON object matching `GardenerAction`:

```json
{
  "action": "create|append|task",
  "path": "relative/path.md",
  "content": "string",
  "reasoning": "string"
}
```

The output is parsed using the existing `parse_gardener_action` logic.

### Failure Modes

- Invalid JSON or schema: classification failure, try next agent if configured.
- Exit code non-zero: determine retry/failover based on configured patterns.
- Any prompt for user input: treat as failure (agent is not compliant with unattended mode).

## Agent Configuration (Local, Not Committed)

### Location

- Default path: `DATA_DIR/.gardener/cli_agents.yaml`
- Optional override: `GARDENER_CLI_CONFIG=/path/to/cli_agents.yaml`
- This file should be local-only and excluded from git.

### Example

```yaml
version: 1
agents:
  - name: claude-code
    provider: claude
    mode: classify   # classify | edit (see below)
    command:
      - "claude"
      - "-p"
      - "{{prompt}}"
      - "--non-interactive"
    model_thinking: "claude-sonnet-4-20250514"
    model_fast: "claude-3-haiku-20240307"
    permissions_file: "~/.config/claude/permissions.yml"
    working_dir: "/data"
    timeout_s: 300
    env:
      CLAUDE_CODE_PROFILE: "pkms"
    retry_on:
      - allowance_exceeded
      - rate_limited

  - name: codex
    provider: codex
    mode: classify
    command:
      - "codex"
      - "--prompt"
      - "{{prompt}}"
      - "--non-interactive"
    model_thinking: "gpt-4.1"
    model_fast: "gpt-4.1-mini"
    permissions_file: "~/.config/codex/permissions.json"
    working_dir: "/data"
    timeout_s: 300
    env:
      CODEX_PROFILE: "pkms"
    retry_on:
      - allowance_exceeded
      - rate_limited
```

### Template Variables

- `{{prompt}}`: fully rendered prompt including AGENTS + note + schema.
- `{{model}}`: the model to use for the requested task (thinking or fast).

## Unattended Mode + Prompting

- **No interactive prompts**. If the CLI tool tries to ask for input, treat as failure.
- The prompt must explicitly say: "You are running unattended. Do not ask for user input."
- The prompt must require a JSON-only response (no extra text).

## AGENTS Instruction Loading

The CLI prompt must include, in order:

1. `AGENTS.md` (global and data dir).
2. `GARDENER.md` (data dir).
3. The note content and filename.
4. The required JSON schema.

The agent must be instructed to follow the AGENTS guidance exactly.

## Permissions and Edit Mode

Each agent has a **local permissions file**. This is required even in classify mode.

- **Classify mode**: agent must not modify files directly.
- **Edit mode** (optional): agent may edit files, but only within allowlisted paths.

### Edit Mode Contract (Optional)

If `mode=edit`, the agent:

- May edit files only under `DATA_DIR` (or an explicit allowlist).
- Must not create new files outside the allowlist.
- Must write a structured summary file (e.g., `DATA_DIR/.gardener/last_cli_result.json`)
  describing which files were edited, and a short summary of changes.
- Must still output a JSON action for the worker to record (even if it's a no-op).

## Failover Strategy

- Agents are tried in the order listed in the config.
- If an agent reports an allowance/limit error or a configured `retry_on` match, try the next.
- If all agents fail, the note remains in inbox and the run is marked failed.

## Observability

- Log agent name, provider, model, command exit code, and elapsed time.
- Capture stdout/stderr to `DATA_DIR/.gardener/cli_logs/<timestamp>-<agent>.log`.
- Record which agent handled each note in the result summary.

## Open Questions

- Confirm exact non-interactive flags and model arguments for each CLI tool.
- Define a stable, vendor-agnostic permissions schema for local config files.
- Decide whether edit mode is required for the MVP or a later phase.
