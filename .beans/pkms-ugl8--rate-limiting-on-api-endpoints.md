---
# pkms-ugl8
title: Rate limiting on API endpoints
status: draft
type: feature
priority: deferred
created_at: 2026-01-21T07:33:14Z
updated_at: 2026-01-21T07:33:14Z
---

Implement rate limiting to protect system from overload and abuse.

## Endpoints to Protect

### High priority (expensive operations):
- POST /api/inbox (triggers processing)
- POST /api/refine (LLM call)
- POST /api/ask (search + LLM)
- GET /api/reconcile (expensive scan)

### Medium priority (moderate cost):
- GET /api/browse (filesystem operations)
- GET /api/status (git operations)

## Rate Limit Strategy

### Per-endpoint limits:
- /api/inbox: 10 req/min per client
- /api/refine: 5 req/min per client
- /api/ask: 20 req/min per client
- /api/reconcile: 1 req/5min per client

### Global limits:
- 100 req/min total across all endpoints
- Burst allowance: 20 requests

## Implementation Options

### Option 1: slowapi (FastAPI integration)
- Decorator-based rate limiting
- In-memory storage (default)
- Redis backend for distributed

### Option 2: middleware-based
- Custom FastAPI middleware
- Flexible rate limit rules
- Integration with existing auth

### Option 3: nginx/reverse proxy
- Rate limiting at reverse proxy layer
- Offload from application
- Requires infrastructure change

## Response Format

```json
{
  "error": "Rate limit exceeded",
  "retry_after": 45,
  "limit": 10,
  "remaining": 0
}
```

## Considerations

- Identify clients (IP, auth token, or session)
- Graceful degradation (soft vs hard limits)
- Admin/trusted clients bypass limits
- Monitor rate limit hit rate
- Adjust limits based on usage patterns

## Acceptance Criteria

- Rate limits enforced on all endpoints
- Clear error messages with retry-after
- Stress tests respect rate limits
- No impact on legitimate usage