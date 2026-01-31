---
id: critique
name: Critique
version: 1.0.0
description: |
  Find gaps, weaknesses, and areas for improvement.
  Use to stress-test ideas, plans, or implementations.
tags: [core, analysis]
inputs:
  - name: subject
    type: string
    required: true
    description: The idea, plan, or implementation to critique
  - name: perspective
    type: string
    required: false
    description: Specific angle to critique from (security, performance, UX, etc.)
outputs:
  - name: critique
    type: markdown
    description: Analysis of weaknesses and improvement opportunities
constraints:
  - Must be constructive, not just negative
  - Must provide specific examples
  - Must suggest alternatives where possible
  - Must acknowledge trade-offs
---

# Critique

## Intent
Identify weaknesses and blind spots to improve quality before problems occur.

## Procedure
1. Understand the subject and its goals
2. Identify assumptions being made
3. Consider failure modes and edge cases
4. Look for logical gaps or inconsistencies
5. Evaluate from multiple perspectives
6. Prioritize issues by impact
7. Suggest alternatives or mitigations

## Critique Lenses
- **Assumptions**: What must be true for this to work?
- **Edge cases**: What happens at boundaries?
- **Scalability**: Does this work at 10x/100x scale?
- **Dependencies**: What external factors could break this?
- **Alternatives**: What other approaches were possible?
- **Trade-offs**: What was sacrificed for this approach?

## Failure Modes
- Being destructive without constructive alternatives
- Missing the forest for the trees
- Not acknowledging valid trade-offs
- Critique paralysis (nothing is ever good enough)

## Examples

### Input
Critique this caching strategy: "Cache all database queries for 5 minutes"

### Output
```markdown
## Critique: Universal 5-Minute Cache

### Assumptions Challenged
1. **All data tolerates staleness** - User-specific data (balances, notifications) may need real-time accuracy
2. **5 minutes is optimal** - Some data changes rarely (configurations), some constantly (activity feeds)

### Gaps Identified
- **Cache invalidation**: No strategy for when underlying data changes
- **Memory bounds**: No limit on cache size; could exhaust memory
- **Cold start**: First request after deploy hits database for everything

### Edge Cases
- Race condition: User updates data, gets cached stale response
- Personalized queries: User A sees User B's cached data if query key isn't user-scoped

### Alternatives
1. **Tiered TTLs**: Static data (1hr), semi-static (5min), dynamic (30sec)
2. **Write-through invalidation**: Clear cache on writes
3. **Cache-aside with tags**: Invalidate by data type, not time

### Trade-off Acknowledgment
Simple universal caching is easy to implement and reason about. The suggested alternatives add complexity. For a low-traffic MVP, the original approach may be acceptable with monitoring.
```
