---
# pkms-wy0x
title: Implement async processing with worker pool
status: draft
type: feature
priority: deferred
created_at: 2026-01-21T07:32:30Z
updated_at: 2026-01-21T07:32:30Z
---

Replace threading.Lock with async queue-based processing for better scalability.

## Current Architecture Issues

- Single global lock blocks all processing
- Synchronous worker processing
- No parallelism for independent operations
- Threading overhead without true parallelism (GIL)

## Proposed Architecture

- AsyncIO-based worker pool
- Queue for inbox processing tasks
- Concurrent workers (configurable size)
- Async/await throughout gardener worker
- FastAPI background tasks integration

## Benefits

- True concurrent processing of independent notes
- Better resource utilization
- Scalable to larger workloads
- Modern Python async patterns
- Easier to add rate limiting and backpressure

## Implementation Phases

1. Convert gardener worker to async functions
2. Implement task queue (asyncio.Queue)
3. Create worker pool manager
4. Update API endpoints to enqueue tasks
5. Add monitoring and metrics

## Considerations

- Major refactoring required
- Need to test git operations with async (subprocess)
- LLM API calls already async-ready
- Database operations need async wrappers or run_in_executor

## Acceptance Criteria

- Multiple notes processed concurrently
- No degradation in classification accuracy
- Stress tests show improved throughput
- No race conditions or data corruption