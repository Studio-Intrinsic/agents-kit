---
date: 2026-01-29
topic: modular-elegance-redesign
---

# Modular Elegance Redesign

## What We're Building

A full redesign of agents-kit to maximize simplicity and portability. The system centralizes skills (prompt patterns, workflows, conventions) in a canonical format and reliably adapts them to any AI runtime (Claude Code, Codex, Cursor, etc.).

Core promise: **One source of truth, runnable everywhere.**

## Product Intent vs Personal Workflow

This redesign focuses on providing durable tooling for teams and individuals to centralize, validate, and adapt skills across runtimes. Personal workflows (custom forks, bespoke update flows, or IDE-specific behaviors) should remain possible but are not the design driver.

## Why This Approach

We evaluated three approaches:
- **Incremental Enhancement** - Low risk but doesn't address structural issues
- **Modular Refactor** - Good balance but still carries legacy constraints
- **Full Redesign** (chosen) - Implements the vision without compromise

The full redesign was chosen because:
1. The current bash scripts are already straining (brittle YAML parsing, hardcoded adapter logic)
2. The compounding workflow doesn't exist yet - building it right from scratch is easier
3. Declarative adapters require a proper transform engine
4. Scaling from solo to enterprise needs a clean foundation

## Key Decisions

### 1. Python CLI with Wizard-Driven Setup
**Rationale:** Python offers robust YAML parsing, proper error handling, and maintainability. Acceptable dependency tradeoff for the capabilities gained. Interactive wizard (like `moltbot onboard`) guides users through: runtimes → packs → skills → installed.

### 2. Declarative Adapter System
**Rationale:** Core to the portability promise. Adapters must be pure YAML config, not hardcoded logic. The CLI interprets transform rules at runtime. Adding a new runtime = adding an adapter.yaml, not modifying code.

### 3. One-Step Install, Optional Render
**Rationale:** `agents install` does render+install as one logical operation. `agents render` exists for power users who want to inspect transforms before installation. Eliminates the mental overhead of a two-step process for normal use.

### 4. Zero-Friction Compounding with Multi-Agent Review
**Rationale:** Knowledge compounding is the differentiator. The workflow:
1. Session ends → agent proposes skill
2. Reviewer agents (from dedicated `reviewers` pack) evaluate in parallel
3. Results aggregated and presented to user in CLI
4. User decides: commit, edit, or reject
5. If committed → PR created for human merge

### 5. Separate Reviewers Pack
**Rationale:** Meta-level concerns (skill quality, code safety, novelty detection) live in their own pack. Teams can swap/extend reviewers without touching content packs. Clean separation of concerns.

### 6. Explicit Subcommands
**Rationale:** `agents render`, `agents install`, `agents compound` are clearer than magic auto-detection. Users know what's happening. Power users can compose commands; beginners use the wizard.

### 7. Keep Hierarchical Structure
**Rationale:** `.agents/packs/<pack>/skills/<skill>/skill.md` is explicit and scales for large libraries. The depth is justified by the organizational clarity it provides. Don't flatten just for fewer directories.

### 8. Floating vs Pinned Modes
**Rationale:**
- Floating mode (default for internal dev): `agents update` pulls main
- Pinned mode (for client/production): `agents update` respects lock file
- Lock file is optional - if absent, floats; if present, pins

## Open Questions

1. **Adapter transform DSL** - What operations should the declarative transform language support? (copy, rename, flatten, template, strip patterns, conditionals?)

2. **Pack dependencies** - Should packs declare dependencies on other packs with version constraints? Or keep it flat?

3. **Reviewer interface** - What's the contract between the compounding workflow and reviewer skills? (input schema, output schema, confidence scores?)

4. **Distribution** - PyPI package? brew? curl installer? All three?

5. **Testing framework** - How should skills be tested? Example-based? Assertion-based? LLM-evaluated?

## Non-Goals (For Now)

- Building runtime-specific editor UX or extension features
- Opinionated workflow enforcement beyond validation and installation
- Solving distribution strategy across every possible channel on day one

## Architecture Sketch

```
agents-kit/
├── .agents/
│   └── packs/                      # Content (canonical pack storage)
│       ├── core/                   # Essential skills/workflows
│       ├── reviewers/              # Meta-skills for compounding
│       └── <domain>/               # Team-specific packs
├── adapters/                       # Runtime transform configs
│   ├── claude-code/adapter.yaml
│   ├── codex/adapter.yaml
│   └── cursor/adapter.yaml
├── cli/                            # Python CLI source
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── commands/               # Subcommand implementations
│   │   ├── adapters/               # Transform engine
│   │   └── compound/               # Compounding workflow
│   └── pyproject.toml
├── schema/                         # JSON schemas for validation
├── docs/
└── README.md
```

## CLI Commands (Target)

```bash
# Setup
agents onboard              # Interactive wizard
agents doctor               # Validate installation

# Daily use
agents install              # Render + install to configured runtimes
agents update               # Pull + install
agents list                 # Show installed packs/skills

# Authoring
agents new skill <name>     # Create from template
agents new pack <name>      # Create pack structure
agents validate             # Schema + lint checks

# Power user
agents render               # Just transform, don't install
agents lock                 # Generate lock file

# Compounding
agents compound             # Interactive: propose → review → commit
```

## Next Steps

→ `/workflows:plan` to create implementation plan with file-by-file details

## Success Criteria

1. New user goes from zero to working skills in < 5 minutes
2. Adding a skill is editing one file and running one command
3. Adding a runtime is creating one YAML file
4. Skills live in one canonical place and render consistently across runtimes
5. System works identically for solo developer and 100-person team
