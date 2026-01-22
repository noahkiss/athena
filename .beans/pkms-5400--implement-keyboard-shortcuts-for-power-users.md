---
# pkms-5400
title: Implement keyboard shortcuts for power users
status: draft
type: feature
created_at: 2026-01-22T02:44:31Z
updated_at: 2026-01-22T02:44:31Z
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
- [ ] Design keyboard shortcuts mapping
- [ ] Implement global keyboard event handler
- [ ] Add Capture page shortcuts (Submit, Refine, Explore, Clear)
- [ ] Add navigation shortcuts (g c, g b, g a, g d)
- [ ] Add search shortcut (/ or Ctrl+K)
- [ ] Add help overlay shortcut (?)
- [ ] Build keyboard shortcuts help modal
- [ ] Add footer hint for discoverability
- [ ] Test on Windows (Ctrl) and Mac (Cmd)
- [ ] Disable shortcuts when in input fields
- [ ] Document shortcuts in README