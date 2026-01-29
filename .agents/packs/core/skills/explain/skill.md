---
id: explain
name: Explain
version: 1.0.0
description: |
  Explain code or concepts clearly at the appropriate level.
  Use when someone needs to understand how something works.
tags: [core, education, communication]
inputs:
  - name: subject
    type: string
    required: true
    description: The code or concept to explain
  - name: audience
    type: string
    required: false
    description: Who the explanation is for (beginner/intermediate/expert)
outputs:
  - name: explanation
    type: markdown
    description: Clear explanation of the subject
constraints:
  - Must match audience level
  - Must use concrete examples
  - Must build from known to unknown
  - Must not oversimplify to incorrectness
---

# Explain

## Intent
Make complex things understandable without sacrificing accuracy.

## Procedure
1. Identify the audience's level
2. Understand what they already know
3. Find the core concept to convey
4. Build a mental model with analogies
5. Use concrete examples
6. Address common misconceptions
7. Provide next steps for deeper learning

## Explanation Levels
- **Beginner**: Analogies, no jargon, focus on "what" and "why"
- **Intermediate**: Technical terms with definitions, focus on "how"
- **Expert**: Assume fundamentals, focus on nuance and trade-offs

## Teaching Techniques
- **Analogy**: Compare to something familiar
- **Example**: Show concrete instances
- **Contrast**: Compare with alternatives
- **Progression**: Simple case → complex case
- **Visual**: Diagrams or ASCII art when helpful

## Failure Modes
- Talking down to experts
- Over-complicating for beginners
- Using jargon without definition
- Analogies that don't quite fit
- Explaining "what" without "why"

## Examples

### Input
Explain database indexing to a junior developer.

### Output
```markdown
## Database Indexing Explained

### The Problem
Imagine a library with 1 million books, but no organization system. To find a specific book, you'd check every single shelf. That's what a database does without indexes—it scans every row.

### What an Index Is
An index is like a library's card catalog. Instead of searching every book, you look up "Python" in the catalog, which tells you exactly where Python books are located.

In database terms: an index is a sorted data structure that points to rows in your table.

### How It Works
```
Table: users
| id | name    | email              |
|----|---------|-------------------|
| 1  | Alice   | alice@example.com |
| 2  | Bob     | bob@example.com   |
| 3  | Charlie | charlie@test.com  |

Index on email:
alice@example.com    → row 1
bob@example.com      → row 2
charlie@test.com     → row 3
(sorted alphabetically)
```

When you query `WHERE email = 'bob@example.com'`:
- **Without index**: Check all 3 rows (or millions in production)
- **With index**: Binary search finds it in ~20 comparisons even with 1M rows

### Trade-offs
- ✅ Reads are much faster
- ❌ Writes are slower (index must be updated)
- ❌ Uses extra disk space

### When to Index
- Columns you frequently search/filter on
- Columns used in JOIN conditions
- Columns used in ORDER BY

### Next Steps
- Try `EXPLAIN` to see if your queries use indexes
- Learn about composite indexes (multiple columns)
- Understand index types (B-tree vs. hash vs. full-text)
```
