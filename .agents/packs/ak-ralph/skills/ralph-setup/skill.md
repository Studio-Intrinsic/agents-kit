---
id: ralph-setup
name: Ralph Setup
version: 1.0.0
description: |
  Install and configure Ralph autonomous agent loop in a project.
  Use when asked to set up ralph, install ralph automation, or configure PRD-driven development.
  Triggers on: install ralph, setup ralph, add ralph automation.
tags: [ralph, setup, automation]
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
  - Requires amp or claude CLI
---

# Ralph Setup

Install and configure the Ralph autonomous agent loop in a project.

## What is Ralph?

Ralph automates software development through repeated AI agent iterations:
1. Reads a `prd.json` file containing user stories
2. Picks the highest priority story where `passes: false`
3. Implements that single story
4. Runs quality checks and commits
5. Marks the story as complete
6. Repeats until all stories pass

Each iteration is a fresh instance with clean context. Memory persists via git history, `progress.txt`, and `prd.json`.

## Prerequisites

```bash
# Required
brew install jq  # JSON parsing

# One of these AI tools
npm install -g @anthropic-ai/claude-code  # Claude Code
# OR
npm install -g @anthropics/amp            # Amp CLI
```

## Installation Steps

### Step 1: Create Directory Structure

```bash
mkdir -p scripts/ralph
mkdir -p tasks
```

### Step 2: Create ralph.sh

Create `scripts/ralph/ralph.sh`:

```bash
#!/bin/bash
# Ralph - Long-running AI agent loop
# Usage: ./ralph.sh [--tool amp|claude] [max_iterations]

set -e

TOOL="claude"
MAX_ITERATIONS=10

while [[ $# -gt 0 ]]; do
  case $1 in
    --tool)
      TOOL="$2"
      shift 2
      ;;
    --tool=*)
      TOOL="${1#*=}"
      shift
      ;;
    *)
      if [[ "$1" =~ ^[0-9]+$ ]]; then
        MAX_ITERATIONS="$1"
      fi
      shift
      ;;
  esac
done

if [[ "$TOOL" != "amp" && "$TOOL" != "claude" ]]; then
  echo "Error: Invalid tool '$TOOL'. Must be 'amp' or 'claude'."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRD_FILE="$SCRIPT_DIR/prd.json"
PROGRESS_FILE="$SCRIPT_DIR/progress.txt"
ARCHIVE_DIR="$SCRIPT_DIR/archive"

# Initialize progress file
if [ ! -f "$PROGRESS_FILE" ]; then
  echo "# Ralph Progress Log" > "$PROGRESS_FILE"
  echo "Started: $(date)" >> "$PROGRESS_FILE"
  echo "---" >> "$PROGRESS_FILE"
fi

echo "Starting Ralph - Tool: $TOOL - Max iterations: $MAX_ITERATIONS"

for i in $(seq 1 $MAX_ITERATIONS); do
  echo ""
  echo "==============================================================="
  echo "  Ralph Iteration $i of $MAX_ITERATIONS ($TOOL)"
  echo "==============================================================="

  if [[ "$TOOL" == "amp" ]]; then
    OUTPUT=$(cat "$SCRIPT_DIR/prompt.md" | amp --dangerously-allow-all 2>&1 | tee /dev/stderr) || true
  else
    OUTPUT=$(claude --dangerously-skip-permissions --print < "$SCRIPT_DIR/CLAUDE.md" 2>&1 | tee /dev/stderr) || true
  fi

  if echo "$OUTPUT" | grep -q "<promise>COMPLETE</promise>"; then
    echo ""
    echo "Ralph completed all tasks!"
    exit 0
  fi

  echo "Iteration $i complete. Continuing..."
  sleep 2
done

echo ""
echo "Ralph reached max iterations ($MAX_ITERATIONS) without completing all tasks."
exit 1
```

Make it executable: `chmod +x scripts/ralph/ralph.sh`

### Step 3: Create Agent Instructions

Create `scripts/ralph/CLAUDE.md`:

```markdown
# Ralph Agent Instructions

You are an autonomous coding agent working on a software project.

## Your Task

1. Read the PRD at `scripts/ralph/prd.json`
2. Read the progress log at `scripts/ralph/progress.txt` (check Codebase Patterns section first)
3. Check you're on the correct branch from PRD `branchName`. If not, check it out or create from main.
4. Pick the **highest priority** user story where `passes: false`
5. Implement that single user story
6. Run quality checks (typecheck, lint, test)
7. If checks pass, commit ALL changes: `feat: [Story ID] - [Story Title]`
8. Update prd.json to set `passes: true` for the completed story
9. Append progress to `progress.txt`

## Progress Report Format

APPEND to progress.txt (never replace):
```
## [Date/Time] - [Story ID]
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

After completing a user story, check if ALL stories have `passes: true`.

If ALL stories are complete, reply with:
<promise>COMPLETE</promise>

If there are still stories with `passes: false`, end normally.

## Important

- Work on ONE story per iteration
- Commit frequently
- Keep CI green
- Read the Codebase Patterns section in progress.txt before starting
```

### Step 4: Create prd.json Template

Create `scripts/ralph/prd.json.example`:

```json
{
  "project": "MyProject",
  "branchName": "ralph/feature-name",
  "description": "Feature description",
  "userStories": [
    {
      "id": "US-001",
      "title": "First user story",
      "description": "As a user, I want X so that Y",
      "acceptanceCriteria": [
        "Criterion 1",
        "Criterion 2",
        "Typecheck passes"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

### Step 5: Update .gitignore

Add to `.gitignore`:

```
# Ralph
scripts/ralph/progress.txt
scripts/ralph/archive/
scripts/ralph/prd.json
```

## Running Ralph

### Basic Usage
```bash
# Run with Claude Code (default 10 iterations)
./scripts/ralph/ralph.sh

# Run with Amp
./scripts/ralph/ralph.sh --tool amp

# Specify max iterations
./scripts/ralph/ralph.sh --tool claude 20
```

### Workflow

1. **Create a PRD** using the `prd-generator` skill
2. **Convert to prd.json** using the `ralph-converter` skill
3. **Copy prd.json** to `scripts/ralph/prd.json`
4. **Run Ralph**: `./scripts/ralph/ralph.sh`

## Quick Install

Clone and copy from the reference repo:

```bash
git clone https://github.com/snarktank/ralph.git /tmp/ralph
mkdir -p scripts/ralph
cp /tmp/ralph/ralph.sh scripts/ralph/
cp /tmp/ralph/CLAUDE.md scripts/ralph/
cp /tmp/ralph/prompt.md scripts/ralph/
cp /tmp/ralph/prd.json.example scripts/ralph/
chmod +x scripts/ralph/ralph.sh
rm -rf /tmp/ralph
```

## Key Differences from Compound Product

| Aspect | Ralph | Compound Product |
|--------|-------|------------------|
| PRD Style | Asks user clarifying questions | Self-clarifies (autonomous) |
| Task naming | User Stories (US-001) | Tasks (T-001) |
| Focus | General feature development | Report-driven fixes |
| Report analysis | Manual | Automated |

## Checklist

After setup, verify:

- [ ] `scripts/ralph/` directory exists with scripts
- [ ] `ralph.sh` is executable
- [ ] `CLAUDE.md` or `prompt.md` exists
- [ ] `jq` and your AI tool are installed
- [ ] `.gitignore` updated
