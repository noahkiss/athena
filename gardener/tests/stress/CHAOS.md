# Chaos Scenario (E) - Manual Runbook

Scenario E is manual-only and intentionally destructive. Use it in a disposable stress data directory.

## Running the Chaos Scenario

Use the stress runner with explicit opt-in flags:

```bash
STRESS_SCENARIOS=E \
STRESS_CHAOS=1 \
STRESS_CHAOS_ACTIONS=corrupt-db,delete-inbox,kill \
STRESS_CHAOS_CONFIRM_DB=1 \
STRESS_CHAOS_CONFIRM_INBOX=1 \
STRESS_CHAOS_CONFIRM_KILL=1 \
./scripts/run_stress_tests.sh
```

Optional recovery checks:

```bash
STRESS_CHAOS_RECOVER=1
```

## Supported Actions + Flags

- `kill`
  - Requires: `STRESS_CHAOS_CONFIRM_KILL=1`
  - Needs: `STRESS_GARDENER_PID` (set by the runner when it starts Gardener)

- `corrupt-db`
  - Requires: `STRESS_CHAOS_CONFIRM_DB=1`
  - Optional: `STRESS_CHAOS_DB_TABLE=file_state`
  - Optional: `STRESS_CHAOS_DB_DELETE=10`

- `delete-inbox`
  - Requires: `STRESS_CHAOS_CONFIRM_INBOX=1`
  - Optional: `STRESS_CHAOS_INBOX_DELETE=5`
  - Optional: `STRESS_CHAOS_INBOX_BACKUP=1` (moves to `inbox/chaos-backup`)

- `rewrite-git`
  - Requires: `STRESS_CHAOS_CONFIRM_GIT=1`
  - Optional: `STRESS_CHAOS_GIT_COMMITS=1`

- `fill-disk`
  - Requires: `STRESS_CHAOS_CONFIRM_DISK=1`
  - Optional: `STRESS_CHAOS_FILL_MB=256`

## Recovery Procedures

- **Gardener killed**
  - Restart Gardener (rerun the stress runner or your service manager).
  - Verify `/api/status` responds and run `/api/reconcile`.

- **State DB corruption / row deletion**
  - Stop Gardener and back up `.gardener/state.db`.
  - If integrity checks fail or state is inconsistent, remove the DB and restart Gardener.
  - Run `/api/reconcile` to rebuild state from git history.

- **Inbox deletions**
  - If backups were enabled, restore from `inbox/chaos-backup`.
  - If not, re-submit source notes and re-run the gardener.

- **Git history rewrite**
  - Run `/api/reconcile` to refresh repo state.
  - Verify repo identity warnings and resolve any conflicts.

- **Disk filled**
  - Delete the fill file (default `chaos-fill.bin`).
  - Confirm free space, then re-run any failed operations.
