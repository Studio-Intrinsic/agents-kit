---
id: plan
name: Plan
version: 1.0.0
description: |
  Decompose a task into actionable steps with risks and assumptions.
  Use when starting any non-trivial work.
tags: [core, planning]
inputs:
  - name: task
    type: string
    required: true
    description: The task or goal to plan
outputs:
  - name: plan
    type: markdown
    description: Structured plan with steps, risks, and done criteria
constraints:
  - Must identify assumptions
  - Must list risks
  - Must define done criteria
  - Steps should be max 7 top-level
---

# Plan

## Intent
Transform ambiguous requests into structured, actionable plans.

## Procedure
1. Clarify the goal and success criteria
2. Identify assumptions and validate critical ones
3. Break into steps (max 7 top-level)
4. Flag risks and mitigations
5. Define "done" criteria

## Failure Modes
- Over-planning simple tasks
- Missing implicit requirements
- Not validating assumptions early
- Creating steps that are too granular or too vague

## Examples

### Input
"Add user authentication to the app"

### Output
```markdown
## Plan: User Authentication

### Goal
Users can sign up, log in, and maintain sessions.

### Assumptions
- Using existing database (Postgres)
- Email/password auth (not OAuth initially)

### Steps
1. Add users table migration
2. Create auth routes (signup, login, logout)
3. Implement session middleware
4. Add protected route wrapper
5. Create login/signup UI

### Risks
- Password storage: Use bcrypt, not custom hashing
- Session hijacking: Use httpOnly cookies

### Done When
- User can sign up with email/password
- User can log in and stay logged in
- Protected routes redirect to login
```
