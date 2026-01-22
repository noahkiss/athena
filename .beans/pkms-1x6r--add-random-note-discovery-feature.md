---
# pkms-1x6r
title: Add random note discovery feature
status: draft
type: feature
created_at: 2026-01-22T02:43:47Z
updated_at: 2026-01-22T02:43:47Z
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
- [ ] Design random note button UI
- [ ] Add API endpoint for random note selection
- [ ] Implement random file selection logic
- [ ] Add dice icon button to UI (dashboard or browse)
- [ ] Add keyboard shortcut (Ctrl+Shift+R)
- [ ] Show random note in modal or redirect to Browse
- [ ] Add "Next Random" button
- [ ] Add category exclusion (e.g., skip tasks)
- [ ] Consider age-weighted randomness
- [ ] Add animation/transition for surprise effect
- [ ] Test randomness distribution
- [ ] Document keyboard shortcut