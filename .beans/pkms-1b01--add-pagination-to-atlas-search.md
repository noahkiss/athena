---
# pkms-1b01
title: Add pagination to atlas search
status: draft
type: feature
priority: deferred
created_at: 2026-01-21T07:32:39Z
updated_at: 2026-01-21T07:32:39Z
---

Implement pagination for atlas browse and search endpoints to handle large repositories.

## Current Issues

- Full directory listings loaded into memory
- Linear scans for search operations
- Unbounded response sizes
- Performance degrades with repository size

## Proposed Changes

### /api/browse
- Add query params: `?limit=50&offset=0`
- Return total count and pagination metadata
- Client-side cursor tracking

### /api/ask (search)
- Limit number of results returned
- Add relevance ranking
- Return result count and pagination info

## Implementation

```python
{
  "results": [...],
  "pagination": {
    "total": 1234,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

## Frontend Changes

- Update scribe to handle paginated responses
- Add "Load more" or pagination controls
- Consider infinite scroll for browse view

## Acceptance Criteria

- Browse endpoint returns max 50 items by default
- Search limited to top 100 results
- Response times consistent regardless of repo size
- Frontend displays pagination controls