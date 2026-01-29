# agents-kit

A model-agnostic skills library for AI coding assistants. Write skills once, deploy to Claude Code, Codex, and beyond.

## Philosophy

### The Problem

Every team using AI coding assistants accumulates tribal knowledge: prompt patterns that work, workflows that produce quality output, conventions that prevent mistakes. This knowledge lives in individual heads, gets lost when people leave, and doesn't compound over time.

Meanwhile, each AI runtime (Claude Code, Codex, Cursor, etc.) has its own format for customization. Skills written for one tool don't transfer to another.

### The Solution

**agents-kit** treats AI skills as a *content product*:

1. **Canonical definitions** — Skills and workflows live in a portable, runtime-agnostic format
2. **Compile to runtimes** — A render pipeline transforms canonical skills into runtime-specific formats
3. **One-line install** — Teammates get the full library instantly
4. **Version and govern** — Semver, lock files, and review processes keep quality high
5. **Compound over time** — Every work session can contribute back to the library

```
┌─────────────────────────────────────────────────────────────┐
│                     Canonical Source                        │
│  .agents/packs/core/skills/plan/skill.md                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ agents render
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Build Artifacts                          │
│  build/claude-code/core/plan.md                            │
│  build/codex/core/plan.md                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │ agents install
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Runtime Locations                         │
│  ~/.claude/skills/core/plan.md                             │
│  ~/.codex/instructions/core/plan.md                        │
└─────────────────────────────────────────────────────────────┘
```

### Core Principles

**Portability over optimization.** A skill that works in one runtime should work in all of them. We accept some lowest-common-denominator constraints in exchange for write-once-deploy-everywhere.

**Quality over quantity.** Ten excellent skills beat a hundred mediocre ones. Every skill should be reviewed, tested, and refined.

**Compound knowledge.** The library should get better with use. After meaningful work, extract what you learned and contribute it back.

**Clear ownership.** Every pack has maintainers. Core is strict and stable; domain packs can iterate faster.

---

## Quick Start

### One-Line Install

```bash
curl -fsSL https://raw.githubusercontent.com/Studio-Intrinsic/agents-kit/main/install.sh | sh
```

This will:
1. Clone the repo to `~/.agents/repos/agents-kit`
2. Create the `~/.agents/` directory structure
3. Render skills for all supported runtimes
4. Install to Claude Code and Codex
5. Add `agents` CLI to your path

### Manual Installation

```bash
# Clone the repo
git clone https://github.com/Studio-Intrinsic/agents-kit.git
cd agents-kit

# Render skills for your runtime
./scripts/agents render --runtime claude-code

# Install to Claude Code
./scripts/agents install --runtime claude-code

# Or use symlinks for development (changes reflect immediately)
./scripts/agents link
```

### Verify Installation

```bash
# List installed skills
./scripts/agents list

# Validate all schemas
./scripts/agents validate

# Run full test suite
./scripts/agents test
```

---

## Repository Structure

```
agents-kit/
├── .agents/
│   ├── packs/                    # Skill packs
│   │   ├── core/                 # Essential skills for any team
│   │   │   ├── pack.yaml         # Pack metadata
│   │   │   ├── skills/           # Individual skills
│   │   │   │   ├── plan/
│   │   │   │   │   └── skill.md
│   │   │   │   ├── review/
│   │   │   │   └── ...
│   │   │   ├── workflows/        # Multi-phase processes
│   │   │   │   ├── plan.md
│   │   │   │   ├── work.md
│   │   │   │   └── ...
│   │   │   └── tests/
│   │   ├── coding/               # Code-focused skills
│   │   └── extraction/           # Data extraction skills
│   ├── schema/                   # JSON schemas for validation
│   │   ├── skill.schema.json
│   │   ├── workflow.schema.json
│   │   └── pack.schema.json
│   └── adapters/                 # Runtime-specific renderers
│       ├── claude-code/
│       │   └── adapter.yaml
│       └── codex/
│           └── adapter.yaml
├── build/                        # Generated (gitignored)
├── scripts/                      # CLI tools
│   ├── agents                    # Main CLI
│   ├── render                    # Render pipeline
│   ├── install                   # Installation script
│   ├── lint                      # Schema validation
│   └── test                      # Test runner
├── docs/
│   ├── authoring-guide.md        # How to write skills
│   └── governance.md             # Maintenance policies
├── install.sh                    # One-line installer
└── agents.lock                   # Version pinning
```

---

## Skill Format

Skills use YAML frontmatter plus markdown body:

```markdown
---
id: plan
name: Plan
version: 1.0.0
description: |
  Decompose a task into actionable steps with risks and assumptions.
  Use when starting any non-trivial work.
tags: [core, planning]
inputs:
  - name: task
    type: string
    required: true
outputs:
  - name: plan
    type: markdown
constraints:
  - Must identify assumptions
  - Must list risks
  - Must define done criteria
---

# Plan

## Intent
Transform ambiguous requests into structured, actionable plans.

## Procedure
1. Clarify the goal and success criteria
2. Identify assumptions and validate critical ones
3. Break into steps (max 7 top-level)
4. Flag risks and mitigations
5. Define "done" criteria

## Failure Modes
- Over-planning simple tasks
- Missing implicit requirements
- Not validating assumptions early

## Examples
[Input/output examples...]
```

See [docs/authoring-guide.md](docs/authoring-guide.md) for complete documentation.

---

## Core Pack (v0.10.0)

### Skills

| Skill | Purpose |
|-------|---------|
| `plan` | Decompose tasks into actionable steps |
| `review` | Quality check any artifact |
| `summarize` | Condense content preserving key info |
| `critique` | Find gaps and weaknesses |
| `extract-structured` | Pull structured data from unstructured content |
| `write-prd` | Create product requirements documents |
| `code-review` | Review code for bugs, security, quality |
| `explain` | Explain code or concepts clearly |
| `debug` | Systematic approach to finding bugs |
| `refactor` | Improve code structure without changing behavior |

### Workflows

| Workflow | Purpose |
|----------|---------|
| `plan` | Produce structured plans with risks and acceptance criteria |
| `work` | Execute plans with checkpoints and verification |
| `review` | Quality gates with systematic review |
| `compound` | Extract reusable patterns from work sessions |
| `triage` | Route requests to appropriate skills/workflows |

---

## CLI Reference

```bash
# Setup
agents init                          # Create ~/.agents/ structure
agents init --from <git-url>         # Clone repo + configure

# Rendering
agents render                        # Render all packs for all runtimes
agents render --pack core            # Render specific pack
agents render --runtime claude-code  # Render for specific runtime

# Installation
agents install                       # Install to all runtimes
agents install --runtime codex       # Install for specific runtime
agents link                          # Symlink mode (for development)

# Pack management
agents list                          # List installed packs and skills
agents update                        # Pull latest from repos
agents lock                          # Generate agents.lock

# Development
agents new skill <name>              # Create skill from template
agents new pack <name>               # Create pack from template
agents validate                      # Check all schemas
agents test                          # Run all tests

# Compounding
agents compound                      # Review session, propose updates
```

---

## Supported Runtimes

### Claude Code (Primary)

Skills render to `~/.claude/skills/` as markdown files compatible with Claude Code's skill system.

### Codex/OpenAI

Skills render to `~/.codex/instructions/` with transformations for OpenAI's instruction-following patterns:
- Frontmatter flattened to prose
- Constraints converted to "You must..." statements
- Claude-specific references removed

### Adding New Runtimes

Create an adapter in `.agents/adapters/<runtime>/`:

```yaml
# adapter.yaml
runtime: new-runtime
output_format: skill.md
install_path: ~/.new-runtime/skills/

transforms:
  frontmatter:
    - from: id
      to: skill_id
  body:
    - copy: true
```

---

## Versioning

### Skill Versions

Individual skills follow semantic versioning:
- **Major**: Breaking changes to inputs/outputs
- **Minor**: New capabilities, backward compatible
- **Patch**: Bug fixes, clarifications

### Pack Versions

Packs version independently:
- Bump when skills are added/removed
- Bump when major skill updates occur

### Lock File

`agents.lock` pins exact versions:

```yaml
schema_version: 1
locked_at: 2026-01-28T12:00:00Z
commit: abc123def456

packs:
  core:
    version: 0.10.0
    commit: abc123
```

Regenerate with `agents lock` after updates.

---

## Contributing

### Adding a Skill

```bash
# Create from template
agents new skill my-skill

# Edit the skill
# .agents/packs/core/skills/my-skill/skill.md

# Validate
agents validate

# Test rendering
agents render
agents test

# Submit PR
```

### Skill Quality Bar

All skills must:
- [ ] Pass schema validation
- [ ] Have unique ID
- [ ] Include Intent section
- [ ] Include Procedure section
- [ ] Include at least one example
- [ ] Render for all target runtimes

Core pack skills additionally require:
- [ ] Comprehensive examples
- [ ] Failure Modes section
- [ ] Two reviewer approvals

See [docs/governance.md](docs/governance.md) for full policies.

---

## Compounding Loop

The library improves through use. After meaningful work:

```bash
agents compound
```

This workflow:
1. Reviews what you accomplished
2. Identifies reusable patterns
3. Proposes new skills or updates
4. Generates PR-ready changes

**Types of contributions:**
- New skill for a recurring task type
- Update to existing skill (better examples, new failure modes)
- Pattern or anti-pattern documentation
- Checklist for quality gates

---

## Local Development

```bash
# Clone and enter repo
git clone https://github.com/Studio-Intrinsic/agents-kit.git
cd agents-kit

# Use symlinks so changes reflect immediately
./scripts/agents link

# Make changes to skills...

# Validate your changes
./scripts/agents validate

# Test rendering
./scripts/agents test

# Commit and push
git add -A
git commit -m "Add new skill: my-skill"
git push
```

---

## Machine Layout

The installer creates this structure:

```
~/.agents/
├── config.yaml          # Points to repos, preferences
├── repos/               # Cloned skill repos
│   └── agents-kit/
├── build/               # Rendered outputs by runtime
│   ├── claude-code/
│   └── codex/
└── bin/                 # CLI symlink
    └── agents -> ~/.agents/repos/agents-kit/scripts/agents
```

**Rule:** Canonical content lives in repos. Machine state lives in `~/.agents/`.

---

## License

MIT

---

## Credits

Built with Claude Code.
