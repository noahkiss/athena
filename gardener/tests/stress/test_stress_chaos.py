"""Scenario E: Chaos testing (manual)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tests.stress.chaos_tools import (
    corrupt_state_db,
    delete_inbox_files,
    fill_disk_space,
    kill_process,
    rewrite_git_history,
)
from tests.stress.utils import IntegrityChecker, RequestSpec


pytestmark = pytest.mark.stress

if os.environ.get("RUN_STRESS_TESTS") != "1":
    pytest.skip("RUN_STRESS_TESTS=1 is required for stress tests.", allow_module_level=True)

if os.environ.get("STRESS_CHAOS") != "1":
    pytest.skip("STRESS_CHAOS=1 is required for chaos tests.", allow_module_level=True)


_ACTION_ORDER = {
    "corrupt-db": 10,
    "delete-inbox": 20,
    "rewrite-git": 30,
    "fill-disk": 40,
    "kill": 50,
}


def _split_actions(raw: str) -> list[str]:
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


def test_manual_chaos_scenarios(stress_client):
    data_dir_env = os.environ.get("STRESS_DATA_DIR")
    if not data_dir_env:
        pytest.skip("STRESS_DATA_DIR must be set for chaos stress test.")

    data_dir = Path(data_dir_env)
    actions = _split_actions(os.environ.get("STRESS_CHAOS_ACTIONS", ""))
    if not actions:
        pytest.skip("Set STRESS_CHAOS_ACTIONS to select chaos actions.")

    actions = sorted(actions, key=lambda item: _ACTION_ORDER.get(item, 100))
    summary = {
        "actions": [],
        "recovery_checks": {},
        "integrity": None,
        "db_integrity": None,
    }

    performed = 0

    def _record(action: str, status: str, **details: object) -> None:
        summary["actions"].append({"action": action, "status": status, **details})

    for action in actions:
        if action == "kill":
            if os.environ.get("STRESS_CHAOS_CONFIRM_KILL") != "1":
                _record(action, "skipped", reason="Set STRESS_CHAOS_CONFIRM_KILL=1")
                continue
            pid = os.environ.get("STRESS_GARDENER_PID")
            if not pid:
                _record(action, "skipped", reason="STRESS_GARDENER_PID not set")
                continue
            kill_process(int(pid))
            _record(action, "ok", pid=int(pid))
            performed += 1
        elif action == "corrupt-db":
            if os.environ.get("STRESS_CHAOS_CONFIRM_DB") != "1":
                _record(action, "skipped", reason="Set STRESS_CHAOS_CONFIRM_DB=1")
                continue
            table = os.environ.get("STRESS_CHAOS_DB_TABLE", "file_state")
            limit = int(os.environ.get("STRESS_CHAOS_DB_DELETE", "10"))
            deleted = corrupt_state_db(data_dir / ".gardener" / "state.db", table=table, limit=limit)
            _record(action, "ok", table=table, deleted=deleted)
            performed += 1
        elif action == "delete-inbox":
            if os.environ.get("STRESS_CHAOS_CONFIRM_INBOX") != "1":
                _record(action, "skipped", reason="Set STRESS_CHAOS_CONFIRM_INBOX=1")
                continue
            limit = int(os.environ.get("STRESS_CHAOS_INBOX_DELETE", "5"))
            backup = os.environ.get("STRESS_CHAOS_INBOX_BACKUP", "1") == "1"
            backup_dir = data_dir / "inbox" / "chaos-backup" if backup else None
            deleted = delete_inbox_files(data_dir / "inbox", limit=limit, backup_dir=backup_dir)
            _record(action, "ok", deleted=deleted, backup=str(backup_dir) if backup_dir else None)
            performed += 1
        elif action == "rewrite-git":
            if os.environ.get("STRESS_CHAOS_CONFIRM_GIT") != "1":
                _record(action, "skipped", reason="Set STRESS_CHAOS_CONFIRM_GIT=1")
                continue
            commits = int(os.environ.get("STRESS_CHAOS_GIT_COMMITS", "1"))
            success = rewrite_git_history(data_dir, commits=commits)
            _record(action, "ok" if success else "failed", commits=commits)
            performed += 1 if success else 0
        elif action == "fill-disk":
            if os.environ.get("STRESS_CHAOS_CONFIRM_DISK") != "1":
                _record(action, "skipped", reason="Set STRESS_CHAOS_CONFIRM_DISK=1")
                continue
            megabytes = int(os.environ.get("STRESS_CHAOS_FILL_MB", "256"))
            target = fill_disk_space(data_dir, megabytes=megabytes)
            _record(action, "ok", file=str(target), size_mb=megabytes)
            performed += 1
        else:
            _record(action, "skipped", reason="Unknown action")

    if performed == 0:
        pytest.skip("No chaos actions executed (all skipped or disabled).")

    if os.environ.get("STRESS_CHAOS_RECOVER") == "1":
        status = stress_client.request(RequestSpec("GET", "/api/status"))
        summary["recovery_checks"]["status"] = {
            "ok": status.ok,
            "status_code": status.status_code,
            "error": status.error,
        }
        reconcile = stress_client.request(RequestSpec("POST", "/api/reconcile"))
        summary["recovery_checks"]["reconcile"] = {
            "ok": reconcile.ok,
            "status_code": reconcile.status_code,
            "error": reconcile.error,
        }

    integrity = IntegrityChecker(data_dir)
    try:
        summary["integrity"] = integrity.report()
        summary["db_integrity"] = integrity.db_integrity_check(
            data_dir / ".gardener" / "state.db"
        )
    except Exception as exc:  # noqa: BLE001 - surface in metrics
        summary["integrity_error"] = str(exc)

    metrics_path = os.environ.get("STRESS_METRICS_PATH")
    if metrics_path:
        payload = {"scenario": "E", "summary": summary}
        Path(metrics_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
