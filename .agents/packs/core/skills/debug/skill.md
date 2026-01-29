---
id: debug
name: Debug
version: 1.0.0
description: |
  Systematic approach to finding and fixing bugs.
  Use when something isn't working as expected.
tags: [core, coding, troubleshooting]
inputs:
  - name: problem
    type: string
    required: true
    description: Description of the bug or unexpected behavior
  - name: context
    type: string
    required: false
    description: Relevant code, logs, or environment info
outputs:
  - name: diagnosis
    type: markdown
    description: Root cause analysis and fix
constraints:
  - Must reproduce before fixing
  - Must identify root cause, not just symptoms
  - Must verify fix doesn't break other things
  - Must document the solution
tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Debug

## Intent
Find the root cause of bugs systematically, not through guesswork.

## Procedure
1. **Reproduce**: Confirm you can trigger the bug
2. **Isolate**: Narrow down where it occurs
3. **Hypothesize**: Form theories about the cause
4. **Test**: Verify or eliminate each hypothesis
5. **Fix**: Address the root cause
6. **Verify**: Confirm fix works and doesn't break other things
7. **Document**: Record what was wrong and why

## Debugging Strategies
- **Binary search**: Comment out half the code, see if bug persists
- **Print debugging**: Add logs at key points to trace execution
- **Rubber duck**: Explain the code line by line
- **Fresh eyes**: Step away and return, or ask someone else
- **Revert**: Go back to working state, apply changes incrementally

## Common Bug Categories
- **State bugs**: Wrong value at wrong time
- **Race conditions**: Timing-dependent failures
- **Null/undefined**: Missing data handling
- **Off-by-one**: Loop/index errors
- **Type coercion**: Implicit conversions
- **Async issues**: Promises/callbacks not handled

## Questions to Ask
- When did it last work?
- What changed since then?
- Does it fail consistently or intermittently?
- Does it fail in all environments?
- What are the exact error messages?

## Failure Modes
- Fixing symptoms instead of root cause
- Not reproducing before attempting fix
- Making multiple changes at once
- Not testing the fix
- "It works on my machine"

## Examples

### Input
Bug: Users report "undefined" appearing in their dashboard greeting.

### Output
```markdown
## Debug: Undefined in Dashboard Greeting

### Reproduction
1. Create new user account
2. Skip profile setup
3. Navigate to dashboard
→ Confirmed: "Welcome, undefined!" appears

### Isolation
```javascript
// dashboard.js:15
const greeting = `Welcome, ${user.firstName}!`;
```

The `user.firstName` is undefined when profile isn't completed.

### Root Cause
New users who skip profile setup have no `firstName` in the database. The code assumes it always exists.

### Fix
```javascript
// Before
const greeting = `Welcome, ${user.firstName}!`;

// After
const greeting = `Welcome, ${user.firstName || 'there'}!`;
```

### Verification
- [x] New user without profile sees "Welcome, there!"
- [x] Existing users still see their name
- [x] Profile completion still updates greeting

### Prevention
Consider adding a migration to set default firstName, or make firstName required at signup.
```
