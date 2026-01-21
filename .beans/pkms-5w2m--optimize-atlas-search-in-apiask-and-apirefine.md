---
# pkms-5w2m
title: Optimize atlas search in /api/ask and /api/refine
status: completed
type: task
priority: normal
created_at: 2026-01-21T00:10:49Z
updated_at: 2026-01-21T02:14:07Z
---

Reduce full-tree scans and duplicate file reads when searching the atlas for related content.

Refs: gardener/main.py (search_atlas)

## Checklist
- [x] Avoid double read of each file
- [x] Consider caching or indexing for repeated queries
- [x] Add tests/benchmarks for large atlas sizes

## Changes Made

### gardener/main.py
- Fixed double-read: content is now read once and reused for both scoring and preview
- Pre-computed lowercase keywords outside the loop to avoid redundant `.lower()` calls
- Added `FileContentCache` class with mtime validation and TTL-based expiration
- Cache holds up to 500 entries with 60-second TTL
- Automatic cache invalidation when files are modified (mtime check)
- LRU-style eviction when cache is full

### gardener/tests/test_search_atlas.py (new)
- 16 tests for search functionality:
  - `TestSearchAtlas`: 8 tests for search behavior (matching, scoring, previews, nested files, case-insensitivity)
  - `TestFileContentCache`: 4 tests for cache behavior (storage, mtime invalidation, eviction)
  - `TestExtractKeywords`: 4 tests for keyword extraction