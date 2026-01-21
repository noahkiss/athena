---
# pkms-15v4
title: Add connection pooling or queue for database writes
status: draft
type: feature
priority: deferred
created_at: 2026-01-21T07:32:19Z
updated_at: 2026-01-21T07:32:19Z
---

Implement connection pooling or a write queue to serialize database operations and reduce lock contention.

## Options

### Option 1: Connection Pooling
- Use a pool of DB connections (e.g., SQLAlchemy pool)
- Configure appropriate pool size and timeouts
- Handle connection lifecycle automatically

### Option 2: Write Queue
- Single writer thread consuming from queue
- API endpoints enqueue operations
- Async/await for operation completion
- Backpressure handling for queue overflow

### Option 3: Hybrid
- Connection pool for reads
- Single writer queue for writes
- Best of both worlds

## Considerations

- SQLite still single-writer, so queue may be simpler
- Connection pooling helps with connection overhead
- Write queue provides natural backpressure
- Need to handle queue overflow gracefully

## Acceptance Criteria

- Database lock errors reduced significantly (>90%)
- Write throughput improved or unchanged
- API latency not significantly increased
- Stress tests show improved concurrency handling