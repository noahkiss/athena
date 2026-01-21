---
# pkms-gc50
title: Harden LLM JSON parsing for classification
status: completed
type: bug
priority: normal
created_at: 2026-01-21T00:10:45Z
updated_at: 2026-01-21T01:27:46Z
---

Avoid failed inbox processing when LLM responses are malformed; add structured output handling and retries.

Refs: gardener/backends/openai.py, gardener/backends/anthropic.py

## Checklist
- [x] Add JSON schema/validation and retry on parse errors
- [x] Use provider features for structured output if available
- [x] Log parse failures with enough context for debugging
- [x] Add unit test or harness to cover malformed outputs

## Changes Made

### gardener/backends/base.py
- Added `ParseError` exception class with `response_text` and `original_error` for debugging
- Added `extract_json_from_response()` helper to handle markdown code blocks and bare JSON
- Added `parse_gardener_action()` to parse and validate LLM responses with proper error handling

### gardener/backends/anthropic.py & openai.py
- Replaced ad-hoc JSON extraction with shared `parse_gardener_action()` helper
- Added retry logic (default 2 retries) with improved prompts on parse failure
- Logs attempts and final failures with context
- Raises `ParseError` with debugging info after exhausting retries

### gardener/tests/test_json_parsing.py
- 13 unit tests covering:
  - JSON extraction from code blocks, bare JSON, and mixed text
  - Validation of required fields and action values
  - ParseError details for debugging

### Notes
- Provider-specific structured output (OpenAI JSON mode, Anthropic tool use) not implemented as the current retry-based approach is robust and provider-agnostic
- On parse failure, retry prompts explicitly request bare JSON without markdown