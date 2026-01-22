---
# pkms-5rc5
title: Add global fuzzy search across atlas and archive
status: draft
type: feature
created_at: 2026-01-22T02:42:03Z
updated_at: 2026-01-22T02:42:03Z
---

Implement fast, fuzzy search across all notes with keyboard shortcut and instant results.

## Features
- Global search bar in header (or keyboard shortcut overlay)
- Fuzzy matching (typo-tolerant)
- Search across atlas + archive simultaneously
- Instant results as you type (debounced)
- Keyboard navigation through results
- Click result to open in Browse or view inline
- Show search excerpts with highlights
- Keyboard shortcut: / or Ctrl+K to open

## Search Scope
- Note titles/filenames
- Note content
- Tags/categories
- Archive notes

## Technical Approach
**Option 1: Fuse.js (Client-side)**
- Pros: Fast, no backend needed, fuzzy by default
- Cons: Need to load index, limited to smaller datasets

**Option 2: Backend with SQLite FTS5**
- Pros: Handles large datasets, server-side
- Cons: Need to maintain search index

**Option 3: Simple grep-based (current ask endpoint)**
- Pros: No dependencies, works now
- Cons: Not fuzzy, slower

**Recommendation**: Start with Fuse.js client-side for MVP, migrate to FTS5 if needed.

## Checklist
- [ ] Choose search implementation (Fuse.js recommended)
- [ ] Add search index building (client or server)
- [ ] Design search UI (modal overlay or header bar)
- [ ] Implement search input with debouncing
- [ ] Add keyboard shortcut (/ or Ctrl+K)
- [ ] Build search results list with highlights
- [ ] Add keyboard navigation (up/down/enter)
- [ ] Link results to Browse or inline preview
- [ ] Add search scope filters (atlas, archive, all)
- [ ] Test fuzzy matching quality
- [ ] Test with large note counts
- [ ] Optimize performance (lazy loading, virtualization)