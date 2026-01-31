---
id: workflow.work
name: Work Workflow
version: 1.0.0
description: Execute plans with checkpoints, logging, and intermediate outputs
triggers:
  - /work
  - "implement this"
  - "execute the plan"
  - "let's build"
skills:
  - debug
  - refactor
  - code-review
phases:
  - setup
  - execute
  - verify
  - checkpoint
---

# Work Workflow

## Phase 1: Setup
- Confirm plan exists and is approved
- Identify first actionable step
- Set up environment if needed
- Create branch if working on code

## Phase 2: Execute
For each step in the plan:
1. State what you're about to do
2. Do the work
3. Show the result
4. Confirm step is complete before moving on

### Execution Principles
- One step at a time
- Show intermediate results
- Ask before making assumptions
- Stop on unexpected errors

## Phase 3: Verify
- Review completed work against plan
- Run tests if applicable
- Check for regressions
- Validate done criteria

## Phase 4: Checkpoint
- Summarize what was accomplished
- Note any deviations from plan
- Identify follow-up work
- Update any documentation

## Progress Tracking
```markdown
## Progress: [Task Name]

### Completed
- [x] Step 1: [Description]
- [x] Step 2: [Description]

### In Progress
- [ ] Step 3: [Description]
  - Status: [Current state]

### Remaining
- [ ] Step 4: [Description]
```

## Error Handling
When encountering an error:
1. Stop and report the error
2. Diagnose using debug skill
3. Propose fix or workaround
4. Get approval before continuing

## Quality Gates
Before marking done:
- [ ] All plan steps completed
- [ ] Tests pass (if applicable)
- [ ] No regressions introduced
- [ ] Done criteria verified
- [ ] Code reviewed (if significant)
