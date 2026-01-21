---
# pkms-5oyn
title: Cache git operations
status: draft
type: feature
priority: deferred
created_at: 2026-01-21T07:32:50Z
updated_at: 2026-01-21T07:32:50Z
---

Implement caching for expensive git operations to improve performance.

## Operations to Cache

### git status
- Cache for 5-10 seconds
- Invalidate on known modifications
- Useful for frequent polling

### git diff
- Cache based on commit hash
- Immutable for historical diffs
- Store frequently accessed diffs

### git log
- Cache recent commit history
- Invalidate on new commits
- Paginate for large histories

## Implementation Options

### Option 1: In-Memory Cache
- Simple dict with TTL
- Fast but lost on restart
- Good for development

### Option 2: Redis Cache
- Persistent across restarts
- Distributed caching possible
- Adds dependency

### Option 3: Hybrid
- In-memory for hot data
- Database for cold data
- Best performance/persistence trade-off

## Invalidation Strategy

- Time-based expiration (TTL)
- Event-based invalidation (on commit)
- LRU eviction for memory management

## Considerations

- Cache invalidation is hard (classic problem)
- Need to balance freshness vs performance
- Monitor cache hit rate
- Add cache statistics endpoint

## Acceptance Criteria

- Git operations 10x faster for cached data
- Cache hit rate >80% under normal usage
- No stale data served to users
- Stress tests show improved performance