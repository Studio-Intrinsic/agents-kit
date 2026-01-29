---
id: compound-setup
name: Compound Product Setup
version: 1.0.0
description: |
  Install and configure Compound Product automation in a project.
  Use when asked to set up compound-product, install compound automation, or configure self-improving automation.
  Triggers on: install compound-product, setup compound, add compound automation.
tags: [compound-product, setup, automation]
inputs:
  - name: project_path
    type: string
    required: false
    description: Path to the project (defaults to current directory)
  - name: tool
    type: string
    required: false
    description: AI tool to use (amp or claude, defaults to claude)
outputs:
  - name: setup_complete
    type: boolean
    description: Whether setup completed successfully
constraints:
  - Requires jq installed
  - Requires gh CLI for PR creation
  - Requires amp or claude CLI
---

# Compound Product Setup

Install and configure the Compound Product self-improving automation system in a project.

## What is Compound Product?

Compound Product is a self-improving automation system that:
1. Analyzes daily reports about product performance
2. Identifies the highest-priority issue
3. Creates a PRD and task list
4. Autonomously implements a fix
5. Creates a pull request for review

## Prerequisites

Before setup, ensure these are installed:

```bash
# Required
brew install jq           # JSON parsing
brew install gh           # GitHub CLI
gh auth login             # Authenticate with GitHub

# One of these AI tools
npm install -g @anthropic-ai/claude-code  # Claude Code
# OR
npm install -g @anthropics/amp            # Amp CLI

# Optional but recommended for browser testing
npm install -g agent-browser
```

## Installation Steps

### Step 1: Create Directory Structure

```bash
mkdir -p scripts/compound
mkdir -p reports
mkdir -p tasks
```

### Step 2: Create Configuration File

Create `compound.config.json` in the project root:

```json
{
  "tool": "claude",
  "reportsDir": "./reports",
  "outputDir": "./scripts/compound",
  "maxIterations": 25,
  "branchPrefix": "compound/",
  "qualityChecks": [
    "npm run typecheck",
    "npm run lint",
    "npm test"
  ]
}
```

Adjust `qualityChecks` for your project (e.g., use `bundle exec rubocop` for Ruby).

### Step 3: Create the Loop Script

Create `scripts/compound/loop.sh`:

```bash
#!/bin/bash
# Compound Product - Execution Loop
# Runs tasks from prd.json until complete or max iterations reached

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$PROJECT_ROOT/compound.config.json"

MAX_ITERATIONS="${1:-10}"
TOOL=$(jq -r '.tool // "claude"' "$CONFIG_FILE")
PRD_FILE="$SCRIPT_DIR/prd.json"
PROGRESS_FILE="$SCRIPT_DIR/progress.txt"
PROMPT_FILE="$SCRIPT_DIR/CLAUDE.md"

# Initialize progress file
if [ ! -f "$PROGRESS_FILE" ]; then
  echo "# Compound Progress Log" > "$PROGRESS_FILE"
  echo "Started: $(date)" >> "$PROGRESS_FILE"
  echo "---" >> "$PROGRESS_FILE"
fi

echo "Starting Compound loop - Tool: $TOOL - Max iterations: $MAX_ITERATIONS"

for i in $(seq 1 $MAX_ITERATIONS); do
  echo ""
  echo "==============================================================="
  echo "  Compound Iteration $i of $MAX_ITERATIONS ($TOOL)"
  echo "==============================================================="

  if [[ "$TOOL" == "amp" ]]; then
    OUTPUT=$(cat "$PROMPT_FILE" | amp --dangerously-allow-all 2>&1 | tee /dev/stderr) || true
  else
    OUTPUT=$(claude --dangerously-skip-permissions --print < "$PROMPT_FILE" 2>&1 | tee /dev/stderr) || true
  fi

  if echo "$OUTPUT" | grep -q "<promise>COMPLETE</promise>"; then
    echo ""
    echo "Compound completed all tasks!"
    exit 0
  fi

  echo "Iteration $i complete. Continuing..."
  sleep 2
done

echo ""
echo "Reached max iterations ($MAX_ITERATIONS) without completing all tasks."
exit 1
```

Make it executable: `chmod +x scripts/compound/loop.sh`

### Step 4: Create the Agent Instructions

Create `scripts/compound/CLAUDE.md`:

```markdown
# Compound Agent Instructions

You are an autonomous coding agent working on a software project.

## Your Task

1. Read the PRD at `scripts/compound/prd.json`
2. Read the progress log at `scripts/compound/progress.txt`
3. Check you're on the correct branch from PRD `branchName`
4. Pick the **highest priority** task where `passes: false`
5. Implement that single task
6. Run quality checks (typecheck, lint, test)
7. If checks pass, commit ALL changes: `feat: [Task ID] - [Task Title]`
8. Update prd.json to set `passes: true` for the completed task
9. Append progress to `progress.txt`

## Progress Report Format

APPEND to progress.txt (never replace):
```
## [Date/Time] - [Task ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
---
```

## Quality Requirements

- ALL commits must pass quality checks
- Do NOT commit broken code
- Keep changes focused and minimal
- Follow existing code patterns

## Stop Condition

After completing a task, check if ALL tasks have `passes: true`.

If ALL tasks are complete, reply with:
<promise>COMPLETE</promise>

If there are still tasks with `passes: false`, end normally.

## Important

- Work on ONE task per iteration
- Commit frequently
- Keep CI green
```

### Step 5: Add a Sample Report

Create a sample report in `reports/` to test:

```markdown
# Weekly Performance Report - 2024-01-15

## Metrics
- Signup conversion: 2.3% (down from 3.1%)
- Page load time: 2.1s (target: <1.5s)
- Error rate: 0.5%

## Issues Identified

### 1. Signup Page Performance (HIGH PRIORITY)
The signup page is loading slowly due to unoptimized images.
- Impact: 25% drop in conversions
- Suggested fix: Compress hero image, lazy load below-fold content

### 2. Mobile Navigation Bug (MEDIUM)
Menu doesn't close after selecting an item on mobile.
- Impact: Poor mobile UX
- Suggested fix: Add click handler to close menu on navigation

### 3. Dashboard Widget Alignment (LOW)
Stats widgets are misaligned on tablet viewports.
- Impact: Minor visual issue
- Suggested fix: Adjust grid breakpoints
```

### Step 6: Update .gitignore

Add to `.gitignore`:

```
# Compound Product
scripts/compound/progress.txt
scripts/compound/archive/
scripts/compound/*.log
tmp/
```

## Running Compound Product

### Dry Run (Preview)
```bash
./scripts/compound/auto-compound.sh --dry-run
```

### Full Execution
```bash
./scripts/compound/auto-compound.sh
```

### Continue Existing Plan
```bash
./scripts/compound/loop.sh 10
```

## How It Works

1. **Analyze Report**: Reads the latest report in `reports/`, uses AI to pick the #1 priority
2. **Create Branch**: Creates a feature branch like `compound/fix-signup-performance`
3. **Generate PRD**: Uses the `prd` skill to create a detailed PRD
4. **Convert to Tasks**: Uses the `tasks` skill to create granular prd.json
5. **Execute Loop**: Runs the agent in a loop, one task per iteration
6. **Create PR**: Pushes changes and creates a pull request

## Quick Install via curl

For projects that want the full automation:

```bash
curl -fsSL https://raw.githubusercontent.com/snarktank/compound-product/main/install.sh | bash
```

Or clone and run:

```bash
git clone https://github.com/snarktank/compound-product.git /tmp/compound-product
/tmp/compound-product/install.sh /path/to/your/project
rm -rf /tmp/compound-product
```

## Checklist

After setup, verify:

- [ ] `scripts/compound/` directory exists with scripts
- [ ] `compound.config.json` configured for your project
- [ ] `reports/` directory exists
- [ ] `tasks/` directory exists
- [ ] `.gitignore` updated
- [ ] `jq`, `gh`, and your AI tool are installed
- [ ] `gh auth status` shows you're authenticated
