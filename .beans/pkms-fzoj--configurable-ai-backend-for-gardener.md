---
# pkms-fzoj
title: Configurable AI Backend for Gardener
status: completed
type: feature
priority: normal
created_at: 2026-01-19T21:11:12Z
updated_at: 2026-01-19T21:22:37Z
parent: pkms-y140
---

Allow selecting which AI backend powers the gardener's classification engine.

## Supported Backends (Priority Order)

1. **OpenAI-compatible API** (current) - Works with OpenAI, LiteLLM, Azure, Ollama
2. **Anthropic Claude** (native SDK) - Direct Claude API with native features
3. **Claude Code / Codex style** - Agentic approach with tool use for classification

## Design

### Configuration
```bash
# Environment variables
GARDENER_BACKEND=openai|anthropic|agentic
AI_BASE_URL=...
AI_API_KEY=...
AI_MODEL=...
```

### Architecture
```
┌─────────────────────────────────┐
│     GardenerBackend (ABC)       │
├─────────────────────────────────┤
│ + classify_note(content) → Action│
│ + get_name() → str              │
└─────────────────────────────────┘
           ▲
     ┌─────┴─────┬─────────────┐
     │           │             │
┌────┴────┐ ┌────┴────┐ ┌──────┴──────┐
│ OpenAI  │ │Anthropic│ │   Agentic   │
│ Backend │ │ Backend │ │   Backend   │
└─────────┘ └─────────┘ └─────────────┘
```

### Backend Differences

| Backend | Auth | Features | Best For |
|---------|------|----------|----------|
| OpenAI | Bearer token | Standard chat | Compatibility |
| Anthropic | x-api-key | Native Claude, caching | Performance |
| Agentic | Varies | Tool use, multi-step | Complex classification |

## Checklist
- [x] Create GardenerBackend abstract base class
- [x] Implement OpenAIBackend (refactor existing code)
- [x] Implement AnthropicBackend with native SDK
- [ ] Implement AgenticBackend with tool use pattern (future)
- [x] Add GARDENER_BACKEND env var to config
- [x] Create factory function to instantiate correct backend
- [x] Update gardener worker to use backend abstraction
- [x] Add backend info to /api/status response
- [ ] Test with each backend type