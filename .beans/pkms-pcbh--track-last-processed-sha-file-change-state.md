---
# pkms-pcbh
title: Track last processed SHA + file change state
status: todo
type: feature
priority: normal
created_at: 2026-01-20T05:50:18Z
updated_at: 2026-01-20T15:12:21Z
parent: pkms-wsuj
---

Persist last-known git SHAs and file fingerprints in SQLite (preferred) or a state file to detect edits since last gardener run and avoid missing manual changes.\n\n## Checklist\n- [ ] Add SQLite table for processed commits (sha, timestamp, branch, note)\n- [ ] Store last seen vs last processed commit SHAs (db or state file fallback)\n- [ ] Track per-file hash/mtime and classify changes by location (inbox vs atlas vs meta)\n- [ ] Track repo identity/history rewrites; force rescan if HEAD diverges from last seen\n- [ ] Expose state via /api/status for visibility and automation\n- [ ] Decide retention/cleanup policy for state data