---
# pkms-ty7n
title: External tool edit attribution (Claude Code, scripts, MCP)
status: todo
type: feature
priority: normal
created_at: 2026-01-20T05:50:12Z
updated_at: 2026-01-20T05:50:37Z
parent: pkms-wsuj
---

Treat edits from Claude Code or other tooling like manual edits while preserving attribution/source metadata.\n\n## Checklist\n- [ ] Define how to record source attribution (commit author, frontmatter, or sidecar metadata)\n- [ ] Add a standard tag for external-tool edits in git commit messages\n- [ ] Ensure reconciliation workflow treats external edits identically to manual ones\n- [ ] Document recommended practices for external tooling