# Compound Product Pack

Self-improving automation that analyzes reports, picks priorities, and autonomously implements fixes.

## Overview

Compound Product is a self-improving automation system that:
1. Analyzes daily reports about product performance
2. Identifies the highest-priority actionable item
3. Creates a detailed PRD and task list
4. Autonomously implements the fix (one task per iteration)
5. Creates a pull request for human review

## Skills

### prd (Autonomous PRD Generator)
Generate Product Requirements Documents autonomously. Unlike interactive PRD generators, this skill **self-clarifies** - it answers its own questions based on available context rather than asking the user.

### tasks (Tasks Converter)
Convert PRD markdown files to `prd.json` format for execution. Explodes high-level tasks into **8-15 granular, machine-verifiable sub-tasks**.

### compound-setup
Install and configure Compound Product automation in a project. Creates the directory structure, scripts, and configuration files needed to run the full automation pipeline.

## Scripts (Reference)

The `scripts/` directory contains the automation scripts that get installed into projects:

- **auto-compound.sh** - Full pipeline: analyze report → create PRD → generate tasks → execute → create PR
- **loop.sh** - Execute tasks from prd.json in a loop
- **analyze-report.sh** - Extract priority items from reports using AI
- **CLAUDE.md** - Agent instructions for autonomous execution
- **prompt.md** - Amp-specific agent instructions
- **config.example.json** - Example configuration file

## Usage

### Using Skills Standalone

The `prd` and `tasks` skills can be used in any project without the full automation:

```
# Generate a PRD
"Create a PRD for adding dark mode support"

# Convert to tasks
"Convert tasks/prd-dark-mode.md to prd.json"
```

### Installing Full Automation

Use the `compound-setup` skill to install the full automation pipeline:

```
"Install compound-product in this project"
```

Or install directly:

```bash
curl -fsSL https://raw.githubusercontent.com/snarktank/compound-product/main/install.sh | bash
```

### Running the Pipeline

After installation:

```bash
# Preview what would be done
./scripts/compound/auto-compound.sh --dry-run

# Run the full pipeline
./scripts/compound/auto-compound.sh

# Continue with existing tasks
./scripts/compound/loop.sh 10
```

## Key Concepts

### Self-Clarification
The PRD skill doesn't ask the user questions. Instead, it answers its own clarifying questions based on:
- The feature request
- AGENTS.md or CLAUDE.md context
- Existing code patterns
- Any provided reports or analysis

### Machine-Verifiable Tasks
Every task acceptance criterion must be a **boolean check** that an agent can definitively pass or fail:

**Good:** "Run `npm run typecheck` - exits with code 0"
**Bad:** "Works correctly"

### Task Granularity
PRDs should generate 8-15 granular tasks, not 3-5 large ones. Each task should:
- Do ONE thing
- Be completable in one context window
- Have boolean pass/fail criteria
- Separate investigation from implementation

## Requirements

- `jq` for JSON parsing
- `gh` CLI for GitHub operations
- `claude` or `amp` CLI for AI execution
- `agent-browser` (optional, for browser testing)

## License

MIT - Originally from [snarktank/compound-product](https://github.com/snarktank/compound-product)
