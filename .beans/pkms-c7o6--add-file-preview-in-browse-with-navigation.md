---
# pkms-c7o6
title: Add file preview in Browse with navigation
status: completed
type: feature
priority: normal
created_at: 2026-01-22T02:45:15Z
updated_at: 2026-01-23T22:02:03Z
---

Show rendered markdown preview when clicking files in Browse instead of raw markdown.

## Features
- Click file in Browse → preview modal or side panel
- Render markdown to HTML (with syntax highlighting)
- Previous/next file navigation
- Breadcrumb showing file location
- Edit button (future: inline editing)
- Quick actions: copy link, download, delete
- Keyboard navigation (←/→ for prev/next, Esc to close)

## Design Options
**Option 1: Modal Overlay**
- Full-screen or large modal
- Close button + keyboard shortcut (Esc)
- Good for focused reading

**Option 2: Side Panel**
- Split view: file list + preview
- Desktop-friendly
- Good for browsing multiple files

**Option 3: Inline Expansion**
- Expand file content below filename in list
- Mobile-friendly
- Good for quick previews

**Recommendation**: Modal for mobile, side panel for desktop (responsive)

## Technical Notes
- Reuse existing /api/browse endpoint
- Use marked.js or similar for markdown rendering
- Syntax highlighting with Prism or highlight.js
- Handle large files (lazy load, pagination)
- Cache rendered content

## Checklist
- [x] Choose preview layout (modal vs side panel) - Responsive: modal on mobile, side panel on desktop
- [x] Implement file preview modal component
- [x] Add markdown rendering
- [x] Add syntax highlighting for code blocks (highlight.js with theme-aware colors)
- [x] Add prev/next navigation
- [x] Add breadcrumb navigation
- [x] Add keyboard shortcuts (←/→, Esc)
- [x] Add quick actions (copy link, download)
- [x] Make responsive (modal on mobile, side panel on desktop)
- [x] Handle large files gracefully (truncate at ~100KB with notice)
- [x] Test with various markdown features
- [x] Add loading state while fetching