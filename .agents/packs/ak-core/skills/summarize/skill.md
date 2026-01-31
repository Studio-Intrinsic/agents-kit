---
id: summarize
name: Summarize
version: 1.0.0
description: |
  Condense content while preserving key information.
  Use to create concise versions of documents, discussions, or code.
tags: [core, communication]
inputs:
  - name: content
    type: string
    required: true
    description: The content to summarize
  - name: length
    type: string
    required: false
    description: Target length (brief/standard/detailed)
outputs:
  - name: summary
    type: markdown
    description: Condensed version of the content
constraints:
  - Must preserve key information
  - Must not introduce new information
  - Must be shorter than original
  - Must maintain accuracy
---

# Summarize

## Intent
Create concise, accurate summaries that capture essential information.

## Procedure
1. Read and understand the full content
2. Identify the main purpose/thesis
3. Extract key points and supporting details
4. Remove redundancy and filler
5. Organize logically (most important first)
6. Verify nothing critical is lost

## Length Guidelines
- **Brief**: 1-3 sentences, core message only
- **Standard**: 1 paragraph, main points with key details
- **Detailed**: Multiple paragraphs, preserves structure and nuance

## Failure Modes
- Losing critical information
- Adding interpretation not in original
- Making it longer than necessary
- Burying the key point

## Examples

### Input
[Long technical document about API rate limiting implementation]

### Output (Standard)
```markdown
## Summary: API Rate Limiting

The system implements token bucket rate limiting at both user and IP levels. Users get 1000 requests/hour with burst allowance of 50. Rate limit headers (X-RateLimit-*) are included in all responses. When exceeded, the API returns 429 with retry-after header. Redis stores counters with automatic expiry. The implementation handles distributed deployments via consistent hashing.

**Key decisions**: Token bucket chosen over sliding window for burst tolerance. Redis selected for multi-node consistency.
```
