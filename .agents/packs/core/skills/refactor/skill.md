---
id: refactor
name: Refactor
version: 1.0.0
description: |
  Improve code structure without changing behavior.
  Use to reduce complexity, improve readability, or prepare for new features.
tags: [core, coding, quality]
inputs:
  - name: code
    type: code
    required: true
    description: The code to refactor
  - name: goal
    type: string
    required: false
    description: Specific refactoring goal (readability, performance, etc.)
outputs:
  - name: refactored
    type: code
    description: Improved code with explanation
constraints:
  - Must not change external behavior
  - Must have tests before refactoring
  - Must make small, incremental changes
  - Must justify each change
tools:
  - Read
  - Edit
  - Bash
---

# Refactor

## Intent
Improve internal code quality while maintaining identical external behavior.

## Procedure
1. Ensure tests exist (or write them first)
2. Identify the specific issue to address
3. Plan small, incremental changes
4. Make one change at a time
5. Run tests after each change
6. Commit working states frequently

## Common Refactorings
- **Extract function**: Pull out reusable logic
- **Inline**: Remove unnecessary indirection
- **Rename**: Improve clarity of names
- **Extract variable**: Name complex expressions
- **Split loop**: Separate concerns
- **Replace conditional with polymorphism**
- **Introduce parameter object**: Group related params

## Code Smells to Address
- **Long functions**: > 20 lines, hard to understand
- **Deep nesting**: > 3 levels, hard to follow
- **Duplicate code**: Same logic in multiple places
- **Long parameter lists**: > 3-4 parameters
- **Feature envy**: Method uses another class's data extensively
- **Primitive obsession**: Using primitives instead of small objects
- **Comments explaining bad code**: Code should be self-explanatory

## Failure Modes
- Refactoring without tests
- Making too many changes at once
- Changing behavior accidentally
- Over-engineering simple code
- Refactoring for its own sake

## Examples

### Input
Refactor this function for readability:
```javascript
function p(u) {
  if (u.a > 18 && u.s === 'active' && u.b > 0 && !u.d) {
    return u.b * 0.1;
  } else if (u.a > 18 && u.s === 'active' && u.b > 0 && u.d) {
    return u.b * 0.15;
  }
  return 0;
}
```

### Output
```markdown
## Refactoring: Discount Calculator

### Issues Identified
1. Cryptic function and parameter names
2. Repeated eligibility check
3. Magic numbers
4. Unclear business logic

### Refactored Code
```javascript
const STANDARD_DISCOUNT_RATE = 0.10;
const PREMIUM_DISCOUNT_RATE = 0.15;

function calculateDiscount(user) {
  if (!isEligibleForDiscount(user)) {
    return 0;
  }

  const rate = user.isPremium ? PREMIUM_DISCOUNT_RATE : STANDARD_DISCOUNT_RATE;
  return user.balance * rate;
}

function isEligibleForDiscount(user) {
  return user.age > 18
    && user.status === 'active'
    && user.balance > 0;
}
```

### Changes Made
1. **Renamed function**: `p` → `calculateDiscount`
2. **Renamed parameter**: `u` → `user`
3. **Expanded abbreviations**: `a`→`age`, `s`→`status`, `b`→`balance`, `d`→`isPremium`
4. **Extracted function**: `isEligibleForDiscount` removes duplication
5. **Named constants**: Discount rates are now self-documenting
6. **Simplified conditional**: Single eligibility check, rate determined separately

### Behavior Verification
- All original test cases pass
- Edge cases still handled identically
```
