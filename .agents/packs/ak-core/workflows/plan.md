---
id: workflow.plan
name: Plan Workflow
version: 1.0.0
description: Produce structured plans with risks, assumptions, and acceptance criteria
triggers:
  - /plan
  - "help me plan"
  - "break this down"
  - "how should I approach"
skills:
  - plan
  - critique
phases:
  - understand
  - research
  - structure
  - present
---

# Plan Workflow

## Phase 1: Understand
- Clarify the request (ask if ambiguous)
- Identify scope boundaries
- Note constraints mentioned
- Understand success criteria

## Phase 2: Research
- Explore relevant code/docs
- Identify existing patterns
- Find similar past work
- Note dependencies and blockers

## Phase 3: Structure
- Define success criteria
- List assumptions (validate critical ones)
- Break into steps (max 7 top-level)
- Identify risks and mitigations
- Estimate relative complexity

## Phase 4: Present
- Output structured plan
- Highlight open questions
- Note trade-offs considered
- Request approval before proceeding

## Checkpoints
- [ ] Goal is clear and bounded
- [ ] Assumptions are explicit
- [ ] Steps are actionable
- [ ] Risks have mitigations
- [ ] Done criteria are testable

## Output Format
```markdown
## Plan: [Title]

### Goal
[One sentence describing success]

### Assumptions
- [Assumption 1]
- [Assumption 2]

### Steps
1. [Step with clear outcome]
2. [Step with clear outcome]
...

### Risks
| Risk | Mitigation |
|------|------------|
| ... | ... |

### Done When
- [ ] [Testable criterion]
- [ ] [Testable criterion]

### Open Questions
- [Question needing resolution]
```
