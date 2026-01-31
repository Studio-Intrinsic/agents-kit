---
id: code-review
name: Code Review
version: 1.0.0
description: |
  Review code changes for quality, correctness, and maintainability.
  Use when reviewing PRs, commits, or code snippets.
tags: [core, coding, quality]
inputs:
  - name: code
    type: code
    required: true
    description: The code to review
  - name: context
    type: string
    required: false
    description: What the code is supposed to do
outputs:
  - name: review
    type: markdown
    description: Code review with findings and suggestions
constraints:
  - Must check for bugs and logic errors
  - Must consider security implications
  - Must evaluate readability and maintainability
  - Must provide specific line references
tools:
  - Read
  - Glob
  - Grep
---

# Code Review

## Intent
Catch bugs, improve quality, and share knowledge through thorough code review.

## Procedure
1. Understand the change's purpose
2. Read through the full diff
3. Check for correctness and bugs
4. Evaluate security implications
5. Assess readability and style
6. Consider performance
7. Verify test coverage
8. Provide actionable feedback

## Review Checklist
### Correctness
- [ ] Logic handles all cases
- [ ] Edge cases considered
- [ ] Error handling appropriate
- [ ] Types are correct

### Security
- [ ] Input validation present
- [ ] No injection vulnerabilities
- [ ] Auth/authz checked
- [ ] Secrets not exposed

### Quality
- [ ] Code is readable
- [ ] Names are clear
- [ ] No unnecessary complexity
- [ ] DRY principles followed

### Testing
- [ ] Tests cover happy path
- [ ] Tests cover edge cases
- [ ] Tests cover error cases

## Feedback Guidelines
- Be specific (line numbers, concrete suggestions)
- Explain the "why" not just the "what"
- Distinguish blocking vs. non-blocking feedback
- Acknowledge good patterns

## Failure Modes
- Nitpicking style while missing bugs
- Not understanding the context
- Being unconstructive ("this is wrong")
- Missing security issues

## Examples

### Input
Review this authentication middleware:
```javascript
function authMiddleware(req, res, next) {
  const token = req.headers.authorization;
  if (token) {
    const user = jwt.decode(token);
    req.user = user;
    next();
  } else {
    res.status(401).send('Unauthorized');
  }
}
```

### Output
```markdown
## Code Review: Auth Middleware

### Critical Issues

**1. Token not verified (line 3)** 🔴
`jwt.decode()` only decodes without verification. Anyone can forge tokens.
```javascript
// Instead of:
const user = jwt.decode(token);
// Use:
const user = jwt.verify(token, process.env.JWT_SECRET);
```

**2. No error handling for invalid tokens** 🔴
If `jwt.verify()` fails, it throws. Wrap in try-catch:
```javascript
try {
  const user = jwt.verify(token, process.env.JWT_SECRET);
  req.user = user;
  next();
} catch (err) {
  res.status(401).send('Invalid token');
}
```

### Suggestions

**3. Strip 'Bearer ' prefix (line 2)** 🟡
Authorization headers typically include "Bearer ":
```javascript
const token = req.headers.authorization?.replace('Bearer ', '');
```

**4. Consider token expiry handling** 🟡
`jwt.verify()` checks expiry, but you may want custom handling for near-expiry tokens.

### What's Good
- Clean middleware pattern
- Appropriate 401 response
- Attaching user to request is idiomatic
```
