---
id: workflow.triage
name: Triage Workflow
version: 1.0.0
description: Decide which skill or workflow to use and gather context
triggers:
  - /triage
  - "help me figure out"
  - "what should I do"
  - "how do I start"
skills:
  - plan
  - summarize
phases:
  - understand
  - classify
  - route
  - handoff
---

# Triage Workflow

## Intent
Match incoming requests to the right workflow/skill and gather necessary context.

## Phase 1: Understand
- Parse the request
- Ask clarifying questions if needed
- Identify the core intent
- Note any constraints mentioned

### Intent Categories
| Intent | Indicators |
|--------|------------|
| Planning | "how should I", "help me think through", "what's the approach" |
| Building | "implement", "create", "build", "add" |
| Fixing | "bug", "error", "broken", "doesn't work" |
| Reviewing | "check", "review", "is this good" |
| Understanding | "explain", "what does", "how does" |
| Writing | "document", "write", "draft" |

## Phase 2: Classify
Determine task characteristics:

### Complexity
- **Simple**: Single action, clear outcome, < 15 min
- **Medium**: Multiple steps, some ambiguity, 15-60 min
- **Complex**: Many steps, significant unknowns, > 1 hour

### Domain
- Code/Technical
- Documentation
- Planning
- Communication
- Analysis

### Urgency
- Blocking other work
- Time-sensitive
- Normal priority
- Background/improvement

## Phase 3: Route
Match to appropriate workflow/skill:

| Situation | Route To |
|-----------|----------|
| Complex task, unclear approach | `workflow.plan` |
| Approved plan, ready to execute | `workflow.work` |
| Work complete, needs quality check | `workflow.review` |
| Done, want to capture learnings | `workflow.compound` |
| Simple bug fix | `skill.debug` |
| Need to understand code | `skill.explain` |
| Need quick summary | `skill.summarize` |
| Reviewing PR | `skill.code-review` |

## Phase 4: Handoff
- Summarize context gathered
- State which workflow/skill applies
- Pass relevant information
- Begin the chosen workflow

## Handoff Format
```markdown
## Triage Result

**Request**: [Original request]
**Intent**: [Planning/Building/Fixing/etc.]
**Complexity**: [Simple/Medium/Complex]

**Routing to**: `workflow.plan` / `skill.debug` / etc.

**Context to pass**:
- [Key detail 1]
- [Key detail 2]

**Open questions for next phase**:
- [Question 1]
```

## Edge Cases
- **Multiple intents**: Break into separate tasks, prioritize
- **Unclear request**: Ask focused clarifying questions
- **No matching skill**: Propose creating a new one
- **Out of scope**: Explain what can't be helped with
