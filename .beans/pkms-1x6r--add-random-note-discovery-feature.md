---
# pkms-1x6r
title: Add random note discovery feature
status: completed
type: feature
priority: normal
created_at: 2026-01-22T02:43:47Z
updated_at: 2026-01-22T13:59:04Z
---

Implement serendipitous note discovery via random note button for rediscovering old notes.

## Features
- "Random Note" button (dice icon 🎲)
- Shows a random note from atlas
- Click to shuffle to another random note
- Keyboard shortcut (e.g., Ctrl+Shift+R)
- Exclude certain categories (e.g., tasks.md)
- Share random note link (optional)

## Design Ideas
- Floating button in corner
- Button in dashboard or browse page
- Keyboard shortcut overlay
- "Feeling lucky" style surprise

## Use Cases
- Rediscover forgotten notes
- Random inspiration/review
- Serendipitous connections
- Daily random note habit

## Technical Notes
- Get all atlas files from file_state DB
- Select random file using cryptographically secure random
- Consider weighting by age (older notes more likely to surface)
- Cache file list to avoid expensive queries

## Checklist
- [x] Design random note button UI (dice icon with hover title)
- [x] Add API endpoint for random note selection (GET /api/random)
- [x] Implement random file selection logic (using secrets.choice for crypto-secure randomness)
- [x] Add dice icon button to UI (browse page header)
- [x] Add keyboard shortcut (Ctrl+Shift+R or Cmd+Shift+R on Mac)
- [x] Show random note in modal or redirect to Browse (navigates to /browse/{path})
- [x] Add "Next Random" button (clicking Random again gets another note)

## Future Enhancements (Deferred)
- Add category exclusion (e.g., skip certain file patterns)
- Consider age-weighted randomness (bias toward older notes)
- Add animation/transition for surprise effect
- Test randomness distribution
- Add keyboard shortcut help UI or documentation