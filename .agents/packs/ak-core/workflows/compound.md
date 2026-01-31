---
id: workflow.compound
name: Compound Workflow
version: 1.0.0
description: Extract reusable patterns and propose skill updates
triggers:
  - /compound
  - "extract learnings"
  - "what did we learn"
  - "document this pattern"
skills:
  - summarize
  - extract-structured
phases:
  - reflect
  - extract
  - propose
  - integrate
---

# Compound Workflow

## Intent
Turn individual work sessions into reusable knowledge that benefits future work.

## Phase 1: Reflect
- Review what was accomplished
- Identify challenges faced
- Note solutions that worked
- Recognize patterns that emerged

### Reflection Questions
- What took longer than expected? Why?
- What would you do differently next time?
- What did you learn that could help others?
- What was reusable vs. one-off?

## Phase 2: Extract
Identify compoundable artifacts:

### Types of Learnings
1. **New Skill**: A reusable procedure for a task type
2. **Skill Update**: Improvement to existing skill
3. **Pattern**: Reusable solution approach
4. **Anti-Pattern**: What to avoid
5. **Checklist**: Quality gates for specific task type
6. **Template**: Reusable document structure

### Extraction Criteria
- Would this help in future similar situations?
- Is it general enough to apply beyond this case?
- Is it specific enough to be actionable?

## Phase 3: Propose
Create structured proposal:

```markdown
## Compound Proposal

### Type
[ ] New Skill
[ ] Skill Update
[ ] Pattern
[ ] Anti-Pattern
[ ] Checklist
[ ] Template

### Summary
[One paragraph describing the learning]

### Context
[When does this apply?]

### Content
[The actual skill/pattern/checklist]

### Evidence
[Where this was validated]
```

## Phase 4: Integrate
- Review proposal for quality
- Check for duplicates
- Categorize appropriately
- Submit for team review
- Update library after approval

## Compounding Cadence
- **During work**: Note interesting patterns
- **After task**: Quick reflection (5 min)
- **Weekly**: Review notes, extract 1-2 learnings
- **Monthly**: Consolidate, propose skill updates

## Quality Bar
A learning is worth compounding if:
- [ ] It would save 15+ minutes in future
- [ ] It applies to more than one project/task
- [ ] It's not already documented elsewhere
- [ ] It's concrete and actionable
