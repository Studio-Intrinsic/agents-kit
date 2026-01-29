---
id: write-prd
name: Write PRD
version: 1.0.0
description: |
  Create product requirements documents.
  Use when defining features, projects, or product changes.
tags: [core, product, documentation]
inputs:
  - name: feature
    type: string
    required: true
    description: The feature or project to document
  - name: context
    type: string
    required: false
    description: Background information and constraints
outputs:
  - name: prd
    type: markdown
    description: Complete product requirements document
constraints:
  - Must define clear success metrics
  - Must identify user stories
  - Must scope what's in and out
  - Must consider edge cases
---

# Write PRD

## Intent
Create clear, actionable product requirements that align stakeholders.

## Procedure
1. Clarify the problem being solved
2. Define target users and their needs
3. Specify success metrics
4. Detail functional requirements
5. Identify non-functional requirements
6. Scope boundaries (in/out)
7. Note dependencies and risks
8. Define milestones

## PRD Structure
```
1. Overview (problem, solution, success)
2. Background (context, research, competitors)
3. Users & Stories (who, what they need)
4. Requirements (functional, non-functional)
5. Scope (in, out, future)
6. Design (if applicable)
7. Metrics (how we measure success)
8. Timeline & Milestones
9. Risks & Mitigations
10. Open Questions
```

## Failure Modes
- Solution-first thinking (skipping problem definition)
- Vague requirements ("make it fast")
- Missing edge cases
- No success criteria
- Scope creep via ambiguity

## Examples

### Input
Write a PRD for adding dark mode to our web app.

### Output
```markdown
# PRD: Dark Mode

## Overview
### Problem
Users report eye strain when using our app in low-light environments. 23% of support tickets mention brightness/display issues.

### Solution
Add a dark color theme that users can toggle or set to follow system preferences.

### Success Metrics
- 40% adoption within 3 months
- 50% reduction in brightness-related support tickets
- No increase in accessibility complaints

## Users & Stories
**Primary**: Power users who use the app 4+ hours daily
- "I want to reduce eye strain during evening work sessions"

**Secondary**: All users in system dark mode
- "I want the app to match my system appearance automatically"

## Functional Requirements
1. Toggle in settings: Light / Dark / System
2. Persist preference across sessions
3. All UI components support both themes
4. Images/media maintain visibility in both modes

## Non-Functional Requirements
- Theme switch < 100ms, no flash
- WCAG AA contrast in both themes
- No layout shifts on toggle

## Scope
**In**: Web app, settings persistence, system detection
**Out**: Mobile apps (v2), scheduled switching, custom themes

## Timeline
1. Design system tokens: Week 1
2. Core components: Week 2-3
3. Page-by-page rollout: Week 4-5
4. QA & launch: Week 6

## Risks
- Inconsistent third-party components: Audit and wrap
- User content (images) unreadable: Add background protection

## Open Questions
- Should we default new users to system preference?
- Do we need a migration for existing users?
```
