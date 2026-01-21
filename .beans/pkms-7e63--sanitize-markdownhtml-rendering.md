---
# pkms-7e63
title: Sanitize markdown/HTML rendering
status: completed
type: bug
priority: normal
created_at: 2026-01-21T00:10:41Z
updated_at: 2026-01-21T00:27:00Z
---

Prevent XSS by sanitizing markdown and HTML outputs before rendering in the browser.

## Review Findings (2026-01-20)

### Critical: `format_refine_html()` in `gardener/main.py:561-582`
AI model output is directly embedded into HTML without escaping:
- Line 568: `tags` variable unescaped
- Line 571: `category` variable unescaped  
- Line 575: `related_text` variable unescaped
- Line 579: `missing` variable unescaped

**Risk**: If AI backend returns malicious content, HTML/JS injection is possible.
**Fix**: Apply `html.escape()` to all interpolated values.

### Also affects:
- `scribe/src/pages/browse/[...path].astro` - marked + set:html
- `gardener/main.py` - format_ask_html (already escapes answer, but verify)

## Checklist
- [x] Apply `html.escape()` to tags, category, related_text, missing in `format_refine_html()`
- [x] Verify `format_ask_html()` properly escapes all fields
- [x] Choose sanitization approach for browse markdown (marked sanitizer/DOMPurify or server-side)
- [x] Sanitize browse markdown before injecting into DOM
- [x] Add regression test or E2E check for script injection

## Changes Made
- Added `html.escape()` to all AI-generated fields in `format_refine_html()` (gardener/main.py:561-584)
- Verified `format_ask_html()` already escapes answer and paths correctly
- Added `html.escape()` to exception messages in /api/refine and /api/ask endpoints
- Installed `isomorphic-dompurify` in scribe for server-side HTML sanitization
- Added DOMPurify.sanitize() to browse page markdown rendering (scribe/src/pages/browse/[...path].astro)
- Created gardener/tests/test_xss_sanitization.py with 10 regression tests for XSS protection