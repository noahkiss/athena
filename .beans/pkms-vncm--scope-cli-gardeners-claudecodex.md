---
# pkms-vncm
title: Scope CLI gardeners (Claude/Codex)
status: todo
type: task
created_at: 2026-01-21T20:41:14Z
updated_at: 2026-01-21T20:41:14Z
---

Spec out CLI-based gardener agents (Claude Code + OpenAI Codex) that run unattended via the same filewatcher/cron as existing automation. Include per-agent local config for permissions + model selection, AGENTS instruction file consumption, failover across 1-n agents when one hits usage limits, and tight scoping to avoid interactive prompts.\n\n## Checklist\n- [ ] Review current gardener backend + scheduler config points for integration\n- [ ] Draft spec for CLI agent execution contract (inputs, outputs, environment, failure modes)\n- [ ] Define local per-agent permission/config file format + storage location\n- [ ] Specify agent selection + failover logic across configured CLI agents\n- [ ] Document how AGENTS instructions are loaded and enforced for unattended runs