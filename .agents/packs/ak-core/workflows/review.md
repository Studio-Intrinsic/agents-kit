---
id: workflow.review
name: Review Workflow
version: 1.0.0
description: Quality gates including regressions, style checks, and thorough review
triggers:
  - /review
  - "review this"
  - "check this code"
  - "is this ready"
skills:
  - review
  - code-review
  - critique
phases:
  - scope
  - analyze
  - report
  - iterate
---

# Review Workflow

## Phase 1: Scope
- Identify what's being reviewed
- Understand the context and goals
- Determine appropriate review criteria
- Set expectations for depth

## Phase 2: Analyze
Perform systematic review across dimensions:

### For Code
- [ ] Correctness: Logic handles all cases
- [ ] Security: No vulnerabilities introduced
- [ ] Performance: No obvious bottlenecks
- [ ] Readability: Code is clear
- [ ] Tests: Adequate coverage
- [ ] Style: Follows conventions

### For Documents
- [ ] Accuracy: Information is correct
- [ ] Completeness: Nothing important missing
- [ ] Clarity: Understandable by audience
- [ ] Structure: Logical organization
- [ ] Actionability: Clear next steps

### For Plans
- [ ] Feasibility: Can be executed
- [ ] Completeness: All steps present
- [ ] Risks: Identified and mitigated
- [ ] Assumptions: Explicit and valid

## Phase 3: Report
Structure findings by severity:

### Critical (Blocking)
Issues that must be fixed before proceeding.

### Major (Should Fix)
Issues that significantly impact quality.

### Minor (Nice to Have)
Improvements that would help but aren't essential.

### Positive
What's working well (important for morale and learning).

## Phase 4: Iterate
- Share findings with author
- Discuss any disagreements
- Re-review after fixes
- Approve when ready

## Review Output Format
```markdown
## Review: [Subject]

### Summary
[One paragraph overall assessment]

### Verdict
[ ] Approved
[ ] Approved with minor changes
[ ] Changes requested
[ ] Needs significant rework

### Critical Issues
1. **[Issue]** (location)
   - Problem: ...
   - Suggestion: ...

### Major Issues
...

### Minor Issues
...

### Positive Notes
- [What's good]
```

## Anti-Patterns
- Nitpicking style while missing bugs
- Being unconstructive ("just rewrite it")
- Not acknowledging good work
- Blocking on preference, not principle
