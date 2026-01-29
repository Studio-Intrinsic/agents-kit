# Ralph Pack

Autonomous AI agent loop for PRD-driven development.

## Overview

Ralph automates software development through repeated AI agent iterations. Each fresh instance tackles one PRD (Product Requirements Document) item until completion. Memory persists via git history, `progress.txt`, and `prd.json`.

## Skills

### ralph-converter
Convert existing PRDs to the `prd.json` format that Ralph uses for autonomous execution.

### prd-generator
Generate detailed Product Requirements Documents with clarifying questions and structured output.

### ralph-setup
Install and configure Ralph in a project. Creates the directory structure, scripts, and configuration files needed to run the autonomous loop.

## Scripts

### ralph.sh
The main orchestration script that spawns AI instances in a loop.

```bash
# Run with Claude Code (default 10 iterations)
./ralph.sh --tool claude

# Run with Amp
./ralph.sh --tool amp

# Specify max iterations
./ralph.sh --tool claude 20
```

### agent-instructions.md
Instructions for Claude Code when running autonomously.

### amp-prompt.md
Instructions for Amp when running autonomously.

## Usage

1. Create a PRD using the `prd-generator` skill
2. Convert it to `prd.json` using the `ralph-converter` skill
3. Run `ralph.sh` to autonomously implement the stories

## How It Works

1. Ralph reads `prd.json` to find user stories
2. Picks the highest priority story where `passes: false`
3. Implements that single story
4. Runs quality checks (typecheck, lint, test)
5. Commits changes with message: `feat: [Story ID] - [Story Title]`
6. Updates `prd.json` to mark story as complete
7. Appends progress to `progress.txt`
8. Repeats until all stories pass or max iterations reached

## Files

- `prd.json` - Task list tracking story completion status
- `progress.txt` - Append-only learnings across iterations
- `archive/` - Previous run archives organized by date and branch

## Requirements

- `jq` for JSON parsing
- Claude Code or Amp CLI installed

## License

MIT - Originally from [snarktank/ralph](https://github.com/snarktank/ralph)
