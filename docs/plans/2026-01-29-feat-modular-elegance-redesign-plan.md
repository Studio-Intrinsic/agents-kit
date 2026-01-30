---
title: "feat: Modular Elegance Redesign"
type: feat
date: 2026-01-29
brainstorm: docs/brainstorms/2026-01-29-modular-elegance-brainstorm.md
revision: 2
revision_notes: Simplified based on reviewer feedback - single-file modules, cut lock files and wizard
---

# Modular Elegance Redesign (v2 - Simplified)

## Overview

A redesign of agents-kit to maximize simplicity and portability. The system centralizes skills in a canonical format and adapts them to any AI runtime (Claude Code, Codex, Cursor, etc.).

**Core Promise:** One source of truth, runnable everywhere.

## Problem Statement

The current bash scripts work but have limitations:
- Brittle YAML parsing
- Hardcoded adapter logic (adding a runtime requires code changes)
- No compounding workflow for knowledge extraction
- No validation beyond basic linting

## Proposed Solution

Build a Python CLI (`agents`) with:
1. **Declarative Adapter System** - Transform skills to any runtime via YAML config
2. **Simple Install Flow** - `agents install` does everything
3. **Multi-Agent Review** - Parallel reviewer evaluation for compounding
4. **Flat Module Structure** - Single files, not nested directories

## Technical Approach

### Architecture (Simplified)

```
agents-kit/
├── pyproject.toml                  # Package config (root level)
├── agents/                         # Python CLI source
│   ├── __init__.py                 # Version
│   ├── __main__.py                 # Entry point
│   ├── cli.py                      # All Click commands (~200 lines)
│   ├── adapters.py                 # Transform engine (~200 lines)
│   ├── compound.py                 # Compounding workflow (~250 lines)
│   ├── config.py                   # Config loading (~80 lines)
│   └── schemas.py                  # Schema validation (~100 lines)
├── .agents/
│   ├── packs/                      # Content (canonical pack storage)
│   │   ├── core/                   # Essential skills/workflows
│   │   └── reviewers/              # Meta-skills for compounding
│   ├── adapters/                   # Runtime transform configs
│   │   ├── claude-code/adapter.yaml
│   │   ├── codex/adapter.yaml
│   │   └── cursor/adapter.yaml
│   └── schema/                     # JSON schemas (existing)
├── tests/
│   ├── test_adapters.py
│   ├── test_commands.py
│   └── test_compound.py
└── README.md
```

**Key Simplifications:**
- No `cli/` subdirectory - package at root
- No `commands/` directory - all commands in `cli.py`
- No `adapters/` directory with multiple files - single `adapters.py`
- No `compound/` directory - single `compound.py`
- Adapters stay in `.agents/adapters/` (existing location)

---

### Implementation Phases

#### Phase 1: Foundation (CLI Structure)

**Objective:** Establish the CLI skeleton with basic commands.

**Files to create:**

| File | Lines (est.) | Purpose |
|------|--------------|---------|
| `pyproject.toml` | 30 | Package configuration |
| `agents/__init__.py` | 5 | Version |
| `agents/__main__.py` | 5 | Entry point |
| `agents/cli.py` | 50 | Click group + placeholder commands |
| `agents/config.py` | 80 | Config loading |

**pyproject.toml:**
```toml
[project]
name = "agents-kit"
version = "0.1.0"
description = "Model-agnostic skills library for AI coding assistants"
requires-python = ">=3.10"
dependencies = [
    "click>=8.0",
    "pyyaml>=6.0",
    "rich>=13.0",
]

[project.optional-dependencies]
compound = ["anthropic>=0.40"]

[project.scripts]
agents = "agents.cli:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**config.py schema:**
```yaml
# .agents/config.yaml
version: 1
runtimes:
  - claude-code
  - codex
packs:
  - core
```

**Tasks:**
- [x] Create `pyproject.toml` at repo root
- [x] Create `agents/__init__.py` with `__version__ = "0.1.0"`
- [x] Create `agents/__main__.py` with `from agents.cli import cli; cli()`
- [x] Create `agents/cli.py` with Click group
- [x] Create `agents/config.py` for config loading
- [x] Verify `pip install -e .` works
- [x] Verify `agents --version` works

---

#### Phase 2: Transform Engine

**Objective:** Build the adapter system in a single file.

**File:** `agents/adapters.py` (~80 lines)

**Simplified Adapter Schema:**

Adapters use a flat configuration instead of a transform DSL. Processing order: copy all → rename → omit → defaults.

| Key | Description | Example |
|-----|-------------|---------|
| `runtime` | Runtime identifier | `claude-code` |
| `filename` | Output filename | `SKILL.md` |
| `install_path` | Install location template | `~/.claude/skills/{pack}/{skill}/` |
| `frontmatter.rename` | Field renames (dict) | `{tools: allowed-tools}` |
| `frontmatter.omit` | Fields to remove (list) | `[constraints]` |
| `frontmatter.defaults` | Default values for missing fields | `{allowed-tools: [Read, Write]}` |

**adapter.yaml format:**
```yaml
# .agents/adapters/claude-code/adapter.yaml
runtime: claude-code
version: 1

filename: SKILL.md
install_path: ~/.claude/skills/{pack}/{skill}/

frontmatter:
  rename:
    tools: allowed-tools
  defaults:
    allowed-tools:
      - Read
      - Glob
      - Grep
      - Edit
      - Write
      - Bash
      - Task
```

```yaml
# .agents/adapters/codex/adapter.yaml
runtime: codex
version: 1

filename: instructions.md
install_path: ~/.codex/instructions/{pack}/{skill}/

frontmatter:
  omit: [tools, constraints]
```

**Tasks:**
- [x] Create `agents/adapters.py` with:
  - `load_adapter(runtime: str) -> dict`
  - `transform_skill(skill_path: Path, adapter: dict) -> str`
  - `transform_frontmatter(frontmatter: dict, config: dict) -> dict`
- [x] Update existing adapters in `.agents/adapters/` to simplified schema
- [x] Write tests in `tests/test_adapters.py`

---

#### Phase 3: Core Commands

**Objective:** Implement essential commands in `cli.py`.

All commands live in `agents/cli.py`. Extract to separate files only if `cli.py` exceeds ~400 lines.

##### `agents render`

Transform canonical skills to `build/` directory.

```python
@cli.command()
@click.option('--runtime', '-r', multiple=True, help='Target runtime(s)')
def render(runtime):
    """Render skills to build/ directory."""
    config = load_config()
    runtimes = runtime or config.get('runtimes', [])

    for rt in runtimes:
        adapter = load_adapter(rt)
        for pack in config.get('packs', []):
            for skill in get_skills(pack):
                output = transform_skill(skill, adapter)
                write_to_build(rt, pack, skill, output)
```

##### `agents install`

Render + copy to runtime install paths.

```python
@cli.command()
@click.option('--runtime', '-r', multiple=True)
def install(runtime):
    """Render and install skills to configured runtimes."""
    # 1. Run render
    # 2. Copy build/{runtime}/ to install_path from adapter
```

##### `agents validate`

Schema validation for skills and packs.

```python
@cli.command()
def validate():
    """Validate all skills and packs against schemas."""
    # - Validate pack.yaml files
    # - Validate skill.md frontmatter
    # - Check skills in pack.yaml match directories
```

##### `agents list`

Show installed inventory.

```python
@cli.command('list')
def list_cmd():
    """List installed packs and skills."""
    # Show packs, skills per pack, configured runtimes
```

##### `agents doctor`

Validate installation health.

```python
@cli.command()
def doctor():
    """Check installation health."""
    # - Config exists and valid
    # - Runtime paths exist and writable
    # - Packs have valid structure
```

##### `agents update`

Pull latest and install.

```python
@cli.command()
def update():
    """Pull latest changes and reinstall."""
    # 1. git pull (if in git repo)
    # 2. Run install
```

##### `agents new skill <name>`

Create skill from template.

```python
@cli.command()
@click.argument('name')
@click.option('--pack', '-p', required=True)
def new_skill(name, pack):
    """Create a new skill from template."""
    # - Validate name format
    # - Create .agents/packs/{pack}/skills/{name}/skill.md
    # - Update pack.yaml
```

**Tasks:**
- [x] Implement `render` command
- [x] Implement `install` command
- [x] Implement `validate` command
- [x] Implement `list` command
- [x] Implement `doctor` command
- [x] Implement `update` command
- [x] Implement `new skill` command
- [x] Create `agents/schemas.py` for validation logic
- [ ] Write tests in `tests/test_commands.py`

---

#### Phase 4: Compounding Workflow

**Objective:** Multi-agent review for skill proposals in a single file.

**File:** `agents/compound.py` (~250 lines)

This phase has three parts:
1. Create the reviewers pack (content)
2. Implement the compound logic (code)
3. Wire up the CLI command

##### 4a: Create Reviewers Pack

```
.agents/packs/reviewers/
├── pack.yaml
└── skills/
    ├── skill-quality/skill.md      # Is the skill well-formed?
    ├── novelty-detector/skill.md   # Is this truly new knowledge?
    └── clarity-checker/skill.md    # Is the skill understandable?
```

**Note:** Start with 3 reviewers, not 4. Add `code-safety` reviewer later if needed.

**Reviewer Contract:**

```yaml
# Input to reviewer (passed as context)
inputs:
  - name: proposed_skill
    type: markdown
  - name: existing_skills
    type: array

# Output from reviewer (parsed from response)
outputs:
  - name: verdict
    type: string  # approve | reject | revise
  - name: confidence
    type: number  # 0.0 - 1.0
  - name: feedback
    type: markdown
```

##### 4b: Implement Compound Logic

**agents/compound.py:**

```python
"""Compounding workflow - multi-agent skill review."""

import asyncio
from pathlib import Path
from typing import Literal

# Only import anthropic if compound features are used
def get_client():
    try:
        from anthropic import Anthropic
        return Anthropic()
    except ImportError:
        raise click.ClickException(
            "Compound features require: pip install agents-kit[compound]"
        )

async def run_reviewer(client, reviewer_skill: str, proposal: str, existing: list[str]) -> dict:
    """Run a single reviewer and parse its verdict."""
    # 1. Load reviewer skill content
    # 2. Call LLM with skill as system prompt, proposal as user message
    # 3. Parse response for verdict, confidence, feedback
    # Return: {"verdict": "approve", "confidence": 0.85, "feedback": "..."}

async def run_all_reviewers(proposal: str) -> list[dict]:
    """Run all reviewers in parallel."""
    client = get_client()
    reviewers = get_reviewer_skills()
    existing = get_existing_skill_ids()

    tasks = [run_reviewer(client, r, proposal, existing) for r in reviewers]
    return await asyncio.gather(*tasks)

def aggregate_results(results: list[dict]) -> dict:
    """Aggregate reviewer results into final verdict."""
    approvals = [r for r in results if r['verdict'] == 'approve']
    rejections = [r for r in results if r['verdict'] == 'reject']

    # Majority approval required
    if len(approvals) > len(results) / 2:
        return {"verdict": "approve", "results": results}
    return {"verdict": "reject", "results": results}

def present_results(aggregated: dict):
    """Present results to user with rich formatting."""
    # Show each reviewer's verdict, confidence, feedback
    # Show final aggregated verdict
    # Prompt: commit, edit, or reject
```

##### 4c: CLI Command

```python
@cli.command()
@click.argument('skill_file', type=click.Path(exists=True))
def compound(skill_file):
    """Review a proposed skill with multi-agent evaluation."""
    proposal = Path(skill_file).read_text()

    # Run reviewers
    results = asyncio.run(run_all_reviewers(proposal))
    aggregated = aggregate_results(results)

    # Present to user
    present_results(aggregated)

    # Get user decision
    action = click.prompt('Action', type=click.Choice(['commit', 'edit', 'reject']))

    if action == 'commit':
        # Move skill to pack, update pack.yaml, create PR
        pass
```

**Tasks:**
- [ ] Create `.agents/packs/reviewers/pack.yaml`
- [ ] Create `skill-quality` reviewer skill
- [ ] Create `novelty-detector` reviewer skill
- [ ] Create `clarity-checker` reviewer skill
- [ ] Create `agents/compound.py` with:
  - `run_reviewer()` - single reviewer execution
  - `run_all_reviewers()` - parallel execution
  - `aggregate_results()` - combine verdicts
  - `present_results()` - rich output
- [ ] Add `compound` command to `cli.py`
- [ ] Write tests in `tests/test_compound.py`

---

## Acceptance Criteria

### Functional Requirements

- [ ] `agents install` renders and installs skills to configured runtimes
- [ ] `agents validate` catches schema errors before installation
- [ ] `agents list` shows installed packs and skills
- [ ] `agents compound` runs reviewers in parallel and presents results
- [ ] Adding a runtime is creating one adapter.yaml file

### Non-Functional Requirements

- [ ] CLI responds in < 2s for all non-network operations
- [ ] Clear error messages with remediation suggestions
- [ ] Works on macOS and Linux (Windows is stretch goal)
- [ ] Python 3.10+ compatibility

### Quality Gates

- [ ] Core commands have unit tests
- [ ] Transform operations have golden output tests
- [ ] `agents validate` passes on all existing packs

---

## What We Cut (vs. Original Plan)

| Feature | Status | Rationale |
|---------|--------|-----------|
| Lock files (`agents lock`) | Cut | Git provides versioning; use `git checkout <sha>` |
| Onboarding wizard (`agents onboard`) | Cut | `agents install` is simple enough |
| `commands/` directory | Cut | All commands fit in `cli.py` |
| `adapters/` directory (3 files) | Cut | Single `adapters.py` is sufficient |
| `compound/` directory (3 files) | Cut | Single `compound.py` is sufficient |
| `code-safety` reviewer | Deferred | Start with 3 reviewers |
| `agents new pack` | Deferred | Rarely needed; manual creation is fine |
| JSON Schema for config | Deferred | Simple YAML validation is enough for MVP |

---

## File Change Summary

### New Files

| File | Lines (est.) | Purpose |
|------|--------------|---------|
| `pyproject.toml` | 30 | Package configuration |
| `agents/__init__.py` | 5 | Version |
| `agents/__main__.py` | 5 | Entry point |
| `agents/cli.py` | 200 | All CLI commands |
| `agents/config.py` | 80 | Config loading |
| `agents/adapters.py` | 200 | Transform engine |
| `agents/compound.py` | 250 | Compounding workflow |
| `agents/schemas.py` | 100 | Schema validation |
| `tests/test_adapters.py` | 100 | Adapter tests |
| `tests/test_commands.py` | 150 | Command tests |
| `tests/test_compound.py` | 100 | Compound tests |
| `.agents/packs/reviewers/pack.yaml` | 15 | Reviewers pack |
| `.agents/packs/reviewers/skills/skill-quality/skill.md` | 80 | Quality reviewer |
| `.agents/packs/reviewers/skills/novelty-detector/skill.md` | 80 | Novelty reviewer |
| `.agents/packs/reviewers/skills/clarity-checker/skill.md` | 80 | Clarity reviewer |

**Total estimated new code: ~1,475 lines** (down from ~2,500+ in original plan)

### Modified Files

| File | Change |
|------|--------|
| `README.md` | Add CLI installation and usage |
| `.gitignore` | Add `build/`, `*.egg-info`, `__pycache__`, `.venv/` |

---

## Dependencies

- Python 3.10+
- Git (for `agents update`)
- `gh` CLI (optional, for PR creation in compound)
- Anthropic API key (for compound workflow only)

---

## Success Metrics

1. **Install time** - `agents install` completes in < 5s
2. **Validation coverage** - Catch 100% of schema violations
3. **Compound flow** - Reviewers complete in < 30s total

---

## References

- Brainstorm: `docs/brainstorms/2026-01-29-modular-elegance-brainstorm.md`
- Authoring guide: `docs/authoring-guide.md`
- Existing adapters: `.agents/adapters/`
- Existing schemas: `.agents/schema/`
