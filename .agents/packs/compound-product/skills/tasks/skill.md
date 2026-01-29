---
id: tasks
name: Tasks Converter
version: 1.0.0
description: |
  Convert a PRD markdown file to prd.json for execution.
  Triggers on: convert prd, create tasks, prd to json, generate tasks from prd.
  Explodes tasks into granular, machine-verifiable sub-tasks.
tags: [compound-product, automation, tasks, autonomous]
inputs:
  - name: prd_path
    type: string
    required: true
    description: Path to the PRD markdown file
  - name: output_path
    type: string
    required: false
    description: Path for prd.json output (default: scripts/compound/prd.json)
  - name: branch_name
    type: string
    required: false
    description: Branch name for the feature
outputs:
  - name: prd_json
    type: json
    description: Executable task list in prd.json format
constraints:
  - Target 8-15 tasks per PRD
  - Each task does ONE thing
  - Every criterion is boolean pass/fail
  - No vague words like "review", "identify", "document"
---

# Tasks - Convert PRD to JSON Format

Converts a PRD markdown document into the prd.json format for the execution loop.

## Intent

1. Read the PRD markdown file
2. Extract tasks (from Tasks section or User Stories)
3. **Explode each task into granular, machine-verifiable sub-tasks**
4. Order by dependencies (schema → backend → UI → tests)
5. Output to the specified prd.json location

**Autonomous mode:** Do not ask questions. Use the PRD content and any provided context (branch name, output path) to generate prd.json immediately.

## Critical: Agent-Testable Tasks

Every task must be **autonomously verifiable** by an AI agent without human intervention.

### The Golden Rule

Each acceptance criterion must be a **boolean check** that an agent can definitively pass or fail:

**BAD - Vague/subjective:**
- "Works correctly"
- "Review the configuration"
- "Document the findings"
- "Identify the issue"
- "Verify it looks good"

**GOOD - Machine-verifiable:**
- "Run `npm run typecheck` - exits with code 0"
- "Navigate to /signup - page loads without console errors"
- "Click submit button - form submits and redirects to /dashboard"
- "File `src/auth/config.ts` contains `redirectUrl: '/onboarding'`"
- "API response status is 200 and body contains `{ success: true }`"

### Acceptance Criteria Patterns

Use these patterns for agent-testable criteria:

| Type | Pattern | Example |
|------|---------|---------|
| Command | "Run `[cmd]` - exits with code 0" | "Run `npm test` - exits with code 0" |
| File check | "File `[path]` contains `[string]`" | "File `middleware.ts` contains `clerkMiddleware`" |
| Browser nav | "agent-browser: open `[url]` - [expected result]" | "agent-browser: open /login - SignIn component renders" |
| Browser action | "agent-browser: click `[element]` - [expected result]" | "agent-browser: click 'Submit' button - redirects to /dashboard" |
| Console check | "agent-browser: console shows no errors" | |
| API check | "GET/POST `[url]` returns `[status]` with `[body]`" | "POST /api/signup returns 200" |
| Screenshot | "agent-browser: screenshot shows `[element]` visible" | "agent-browser: screenshot shows CTA button above fold" |

### Browser Testing with agent-browser

All browser-based acceptance criteria MUST use [agent-browser](https://github.com/vercel-labs/agent-browser).

**agent-browser commands:**
```bash
agent-browser open <url>              # Navigate to URL
agent-browser snapshot -i             # Get interactive elements with refs
agent-browser click @ref              # Click element by ref
agent-browser fill @ref "value"       # Fill input field
agent-browser screenshot <path>       # Save screenshot
agent-browser wait --load networkidle # Wait for page load
agent-browser console                 # Check console for errors
```

## Output Format

Create `prd.json`:

```json
{
  "project": "Project Name",
  "branchName": "compound/[feature-name]",
  "description": "[One-line description from PRD]",
  "tasks": [
    {
      "id": "T-001",
      "title": "[Specific action verb] [specific target]",
      "description": "[1-2 sentences: what to do and why]",
      "acceptanceCriteria": [
        "Specific machine-verifiable criterion with expected outcome",
        "Another criterion with pass/fail condition",
        "Run `npm run typecheck` - exits with code 0"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

## Task Granularity Rules

### Target: 8-15 tasks per PRD

PRDs should typically generate 8-15 granular tasks. If you have fewer than 6, you probably need to split tasks further.

### Split Multi-Step Tasks

**TOO BIG:**
```json
{
  "title": "Test signup flow and fix issues",
  "acceptanceCriteria": [
    "Test the signup flow",
    "Identify any issues",
    "Fix the issues",
    "Verify the fix works"
  ]
}
```

**PROPERLY SPLIT:**
```json
[
  {
    "id": "T-001",
    "title": "Navigate to signup page and capture baseline",
    "acceptanceCriteria": [
      "Navigate to /signup - page loads successfully",
      "Screenshot saved to tmp/signup-baseline.png",
      "Browser console errors logged to tmp/signup-console.log"
    ]
  },
  {
    "id": "T-002",
    "title": "Test email input field validation",
    "acceptanceCriteria": [
      "Enter 'invalid-email' in email field - error message appears",
      "Enter 'valid@example.com' - error message disappears",
      "Field has aria-invalid='true' when invalid"
    ]
  },
  {
    "id": "T-003",
    "title": "Test form submission with valid data",
    "acceptanceCriteria": [
      "Fill email: 'test@example.com', password: 'TestPass123!'",
      "Click submit button - loading state appears",
      "After submit - redirects to /onboarding OR error message appears"
    ]
  }
]
```

### One Concern Per Task

Each task should do ONE thing:

| Concern | Separate Task |
|---------|---------------|
| Navigate to page | T-001 |
| Check for errors | T-002 |
| Test input validation | T-003 |
| Test form submission | T-004 |
| Verify redirect | T-005 |
| Test mobile viewport | T-006 |
| Implement fix | T-007 |
| Verify fix on desktop | T-008 |
| Verify fix on mobile | T-009 |

### Investigation vs Implementation

**Never combine "find the problem" with "fix the problem"** in one task.

## Task Sizing

Each task must be completable in ONE iteration (~one context window).

**Right-sized tasks:**
- Check one configuration file for specific values
- Test one user interaction (click, type, submit)
- Verify one redirect or navigation
- Change one prop or configuration value
- Add one CSS rule or style change
- Test one viewport size

**Too big (split these):**
- "Test the entire signup flow" → Split into: load page, test inputs, test submit, test redirect, test mobile
- "Fix the bug" → Split into: identify file, make change, verify change, test regression
- "Add authentication" → Split into: schema, middleware, login UI, session handling

## Priority Ordering

Set priority based on dependencies:

1. **Investigation tasks** - priority 1-3 (understand before changing)
2. **Schema/database changes** - priority 4-5
3. **Backend logic changes** - priority 6-7
4. **UI component changes** - priority 8-9
5. **Verification tasks** - priority 10+

Lower priority number = executed first.

## Checklist

Before saving prd.json:

- [ ] **8-15 tasks** generated (not 3-5)
- [ ] Each task does **ONE thing**
- [ ] Investigation separated from implementation
- [ ] Every criterion is **boolean pass/fail**
- [ ] No vague words: "review", "identify", "document", "verify it works"
- [ ] Commands specify expected exit code
- [ ] Browser actions specify expected result
- [ ] All tasks have `passes: false`
- [ ] Priority order reflects dependencies
