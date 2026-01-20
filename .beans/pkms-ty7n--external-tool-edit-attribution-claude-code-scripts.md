---
# pkms-ty7n
title: External tool edit attribution (Claude Code, scripts, MCP)
status: todo
type: feature
priority: normal
created_at: 2026-01-20T05:50:12Z
updated_at: 2026-01-20T15:12:34Z
parent: pkms-wsuj
---

Treat edits from Claude Code or other tooling like manual edits while preserving attribution/source metadata, and record optional provenance in SQLite when possible.\n\n## Checklist\n- [ ] Define how to record source attribution (commit author, frontmatter, or sidecar metadata)\n- [ ] Decide default provenance location to avoid touching curated notes (prefer sidecar/DB)\n- [ ] Add a standard tag for external-tool edits in git commit messages\n- [ ] Record external tool provenance in SQLite state when enabled\n- [ ] Ensure reconciliation workflow treats external edits identically to manual ones\n- [ ] Document recommended practices for external tooling