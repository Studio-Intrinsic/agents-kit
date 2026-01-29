---
id: review
name: Review
version: 1.0.0
description: |
  Quality check any artifact against criteria.
  Use to validate code, documents, plans, or any work product.
tags: [core, quality]
inputs:
  - name: artifact
    type: string
    required: true
    description: The artifact to review (code, document, plan, etc.)
  - name: criteria
    type: array
    required: false
    description: Specific criteria to check against
outputs:
  - name: review
    type: markdown
    description: Structured review with findings and recommendations
constraints:
  - Must be specific about issues found
  - Must provide actionable recommendations
  - Must note what is working well
  - Must prioritize findings by severity
---

# Review

## Intent
Provide thorough, actionable feedback on any work product.

## Procedure
1. Understand the artifact's purpose and context
2. Identify relevant quality criteria
3. Systematically check against each criterion
4. Note strengths (what's working)
5. List issues with severity (critical/major/minor)
6. Provide specific, actionable recommendations

## Quality Criteria Categories
- **Correctness**: Does it do what it's supposed to?
- **Completeness**: Is anything missing?
- **Clarity**: Is it understandable?
- **Consistency**: Does it follow established patterns?
- **Maintainability**: Can it be easily modified?
- **Performance**: Are there obvious bottlenecks?
- **Security**: Are there vulnerabilities?

## Failure Modes
- Being too harsh without acknowledging positives
- Vague feedback ("this could be better")
- Missing critical issues while noting minor ones
- Not considering context/constraints

## Examples

### Input
Review this API endpoint code for a user registration flow.

### Output
```markdown
## Review: User Registration Endpoint

### Summary
Functional implementation with security concerns to address.

### Strengths
- Clear separation of validation and persistence
- Good error messages for users
- Follows REST conventions

### Issues

#### Critical
1. **Password stored in plain text** (line 45)
   - Use bcrypt.hash() before saving
   - Add password complexity validation

#### Major
2. **No rate limiting**
   - Add rate limiter middleware to prevent brute force
   - Recommend: 5 attempts per minute per IP

#### Minor
3. **Inconsistent error response format** (lines 32, 58)
   - Standardize to { error: { code, message } }

### Recommendations
1. Add password hashing immediately (security critical)
2. Implement rate limiting before production
3. Consider adding email verification flow
```
