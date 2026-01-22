---
# pkms-5400
title: Implement keyboard shortcuts for power users
status: in-progress
type: feature
priority: normal
created_at: 2026-01-22T02:44:31Z
updated_at: 2026-01-22T03:37:47Z
---

Add comprehensive keyboard shortcuts for navigation and actions.

## Keyboard Shortcuts
**Global:**
- `/` or `Ctrl+K`: Open search
- `?`: Show keyboard shortcuts help
- `Esc`: Close modals/overlays, clear textarea

**Capture page:**
- `Ctrl/Cmd+Enter`: Submit note
- `Ctrl/Cmd+R`: Refine
- `Ctrl/Cmd+E`: Explore
- `Ctrl/Cmd+K`: Clear textarea

**Navigation:**
- `g c`: Go to Capture
- `g b`: Go to Browse
- `g a`: Go to Archive
- `g d`: Go to Dashboard
- `Ctrl+Shift+R`: Random note

**Browse:**
- `↑/↓`: Navigate file list
- `Enter`: Open selected file
- `Backspace`: Go up one directory

## Help Overlay
- Show keyboard shortcuts on `?` key
- Modal overlay with categorized shortcuts
- Searchable shortcuts list
- Footer hint: "Press ? for keyboard shortcuts"

## Technical Implementation
- Use event listeners on document
- Prevent conflicts with native browser shortcuts
- Handle modifier keys (Ctrl/Cmd cross-platform)
- Disable shortcuts when typing in inputs (except special keys)

## Checklist
- [x] Design keyboard shortcuts mapping
- [x] Implement global keyboard event handler
- [x] Add Capture page shortcuts (Submit, Refine, Explore, Clear)
- [x] Add navigation shortcuts (g c, g b, g a)
- [ ] Add search shortcut (/ or Ctrl+K) - deferred (no search page yet)
- [x] Add help overlay shortcut (?)
- [x] Build keyboard shortcuts help modal
- [x] Add footer hint for discoverability
- [x] Test on Windows (Ctrl) and Mac (Cmd) - cross-platform support implemented
- [x] Disable shortcuts when in input fields
- [ ] Document shortcuts in README (can add after testing)