---
# pkms-gg6j
title: Fix auth header forwarding from Scribe to Gardener
status: completed
type: bug
priority: normal
created_at: 2026-01-21T05:46:01Z
updated_at: 2026-01-21T05:49:01Z
---

Scribe proxy endpoints don't include ATHENA_AUTH_TOKEN when calling Gardener, causing 401/403 when auth is enabled. Ensure the proxy forwards Authorization/X-Auth-Token (from env) on all Gardener API calls and document behavior.

## Checklist
- [x] Locate all Scribe->Gardener fetches that need auth
- [x] Add optional auth header forwarding from env
- [x] Update any related documentation or comments
- [x] Verify endpoints compile/build
