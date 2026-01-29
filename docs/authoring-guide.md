# Skill Authoring Guide

This guide covers how to create and maintain skills for the agents-kit library.

## Quick Start

```bash
# Create a new skill
agents new skill my-skill

# Edit the generated file
# .agents/packs/core/skills/my-skill/skill.md

# Validate your changes
agents validate

# Test rendering
agents render --runtime claude-code
```

## Skill Structure

Every skill is a single `skill.md` file in its own directory:

```
.agents/packs/<pack>/skills/<skill-name>/
└── skill.md
```

## Skill Format

Skills use YAML frontmatter followed by markdown content:

```markdown
---
id: my-skill
name: My Skill
version: 1.0.0
description: |
  What this skill does.
  When to use it.
tags: [core, category]
inputs:
  - name: input_name
    type: string
    required: true
    description: What this input is
outputs:
  - name: output_name
    type: markdown
    description: What this output is
constraints:
  - Constraint 1
  - Constraint 2
---

# My Skill

## Intent
What this skill accomplishes and why it matters.

## Procedure
1. First step
2. Second step
3. Third step

## Failure Modes
- What can go wrong
- Common mistakes

## Examples

### Input
Example input

### Output
Example output
```

## Required Fields

### Frontmatter (Required)
- `id`: Unique identifier (lowercase, hyphens only)
- `name`: Human-readable name
- `version`: Semantic version (X.Y.Z)
- `description`: What the skill does and when to use it

### Frontmatter (Optional)
- `tags`: Array of categorization tags
- `inputs`: Array of input definitions
- `outputs`: Array of output definitions
- `constraints`: Array of rules the skill must follow
- `tools`: Array of tools the skill may use

### Body Sections (Recommended)
- `## Intent`: The purpose and value of the skill
- `## Procedure`: Step-by-step process
- `## Failure Modes`: What can go wrong
- `## Examples`: Input/output examples

## Naming Conventions

### Skill IDs
- Lowercase letters and hyphens only
- Descriptive but concise
- Examples: `plan`, `code-review`, `extract-structured`

### Skill Names
- Title case
- Match the ID conceptually
- Examples: `Plan`, `Code Review`, `Extract Structured`

## Version Guidelines

Use semantic versioning:
- **Major (X.0.0)**: Breaking changes to inputs/outputs
- **Minor (0.X.0)**: New capabilities, backward compatible
- **Patch (0.0.X)**: Bug fixes, clarifications

## Writing Good Skills

### Intent Section
- One paragraph explaining the "why"
- Who benefits from this skill
- What problem it solves

### Procedure Section
- Numbered steps (max 7 top-level)
- Each step should be actionable
- Include decision points where needed

### Failure Modes Section
- List common mistakes
- Explain what bad output looks like
- Help the model self-correct

### Examples Section
- Show realistic inputs
- Show complete, high-quality outputs
- Cover edge cases when helpful

## Testing Skills

```bash
# Run all validation
agents validate

# Run full test suite
agents test

# Test rendering for a specific runtime
agents render --runtime claude-code
agents render --runtime codex
```

## Workflow Structure

Workflows are similar to skills but define multi-phase processes:

```markdown
---
id: workflow.my-workflow
name: My Workflow
version: 1.0.0
description: What this workflow accomplishes
triggers:
  - /my-workflow
  - "trigger phrase"
skills:
  - skill-1
  - skill-2
phases:
  - phase-1
  - phase-2
---

# My Workflow

## Phase 1: Phase Name
- What happens in this phase
- Key activities

## Phase 2: Next Phase
...
```

## Pack Structure

Packs group related skills and workflows:

```yaml
# pack.yaml
id: my-pack
name: My Pack
version: 0.1.0
description: What this pack contains
author: your-team

skills:
  - skill-1
  - skill-2

workflows:
  - workflow-1

dependencies:
  - core  # Other packs this depends on
```

## Best Practices

1. **Start with Intent**: Know why the skill exists
2. **Be Specific**: Vague skills produce vague outputs
3. **Include Examples**: They teach better than rules
4. **List Failure Modes**: Help the model avoid mistakes
5. **Test Across Runtimes**: Ensure portability
6. **Keep It Focused**: One skill, one job
7. **Version Properly**: Breaking changes = major version

## Contributing

1. Create a new skill or update existing
2. Run `agents validate` and `agents test`
3. Submit PR with description of changes
4. Get review from pack maintainer
5. Merge after approval
