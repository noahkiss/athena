---
# pkms-0xj8
title: Investigate and prevent runaway API usage
status: completed
type: task
priority: normal
created_at: 2026-01-22T02:57:26Z
updated_at: 2026-01-22T03:22:23Z
---

Investigate why 250 API requests were made when tests only documented ~14 calls, and implement safeguards.

## The Mystery
- Documented test AI calls today: ~14 (Scenario B: 9, Scenario C: ~5)
- Actual Gemini Pro usage: 250 requests (hit daily cap)
- Gap: 236 unaccounted requests

## Likely Culprit
Two gardener processes found running since Jan 19:
- Port 8765: 10h39m CPU time
- Port 8766: 9h55m CPU time

These could have made 236+ API calls over 20 hours if:
- Automation was enabled
- Inbox had files to process
- Ask/refine endpoints were being hit

## Investigation Tasks
1. Check logs from those processes (if available)
2. Check their data directories for activity
3. Review git history in their atlas dirs
4. Count commits (each = 1 classification call)
5. Determine what triggered so many calls

## Prevention Measures
1. **Add API call counter to status endpoint**
   - Track calls per session
   - Show in /api/status response
   - Warn when approaching limits

2. **Add API rate limiting config**
   - MAX_API_CALLS_PER_HOUR env var
   - Stop processing when limit hit
   - Log warning and sleep until reset

3. **Add process cleanup to test scripts**
   - Kill gardener after test completion
   - Use trap/atexit handlers
   - Document cleanup steps

4. **Add API usage monitoring**
   - Log each API call with timestamp
   - Daily usage report in logs
   - Alert when >80% of quota used

5. **Improve test documentation**
   - Document expected API call counts for each scenario
   - Add warnings about background processes
   - Document how to check for running instances

## Checklist
- [x] Check logs from old processes (if available)
- [x] Check data dirs for activity (inbox, atlas, git history)
- [x] Count commits to estimate API usage
- [x] Add API call counter to gardener state
- [x] Add API counter to /api/status response
- [x] Add MAX_API_CALLS_PER_HOUR config
- [x] Implement rate limiting with graceful stop
- [x] Add cleanup handlers to test scripts
- [x] Add API usage logging
- [x] Update TESTS.md with warnings about background processes
- [x] Document how to check for runaway processes