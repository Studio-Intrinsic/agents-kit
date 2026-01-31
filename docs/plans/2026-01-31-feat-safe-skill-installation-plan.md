---
title: "feat: Namespace Packs to Avoid Conflicts"
type: feat
date: 2026-01-31
---

# Namespace Packs to Avoid Conflicts

## Overview

Prefix all agents-kit pack names with `ak-` to avoid conflicts with user-created packs.

## Problem Statement

The current installation uses pack names like `core/`, `ralph/`, `compound-product/` which could conflict with user-created packs of the same name. The `rm -rf` in the install script would destroy user content.

## Proposed Solution

**Rename packs to use a namespace prefix:**

| Current Name | New Name |
|--------------|----------|
| `core` | `ak-core` |
| `ralph` | `ak-ralph` |
| `compound-product` | `ak-compound-product` |

Install paths become:
```
~/.claude/skills/ak-core/plan/SKILL.md
~/.claude/skills/ak-ralph/...
~/.claude/skills/ak-compound-product/...
```

Users can safely create their own `core/` pack without conflict.

## Technical Approach

### Files to Modify

| File | Change |
|------|--------|
| `.agents/packs/core/pack.yaml` | Change `id: core` to `id: ak-core` |
| `.agents/packs/ralph/pack.yaml` | Change `id: ralph` to `id: ak-ralph` |
| `.agents/packs/compound-product/pack.yaml` | Change `id: compound-product` to `id: ak-compound-product` |
| Directory names | Rename `core/` → `ak-core/`, etc. |

### Implementation

**Tasks:**
- [x] Rename `.agents/packs/core/` to `.agents/packs/ak-core/`
- [x] Update `.agents/packs/ak-core/pack.yaml` with `id: ak-core`
- [x] Rename `.agents/packs/ralph/` to `.agents/packs/ak-ralph/`
- [x] Update `.agents/packs/ak-ralph/pack.yaml` with `id: ak-ralph`
- [x] Rename `.agents/packs/compound-product/` to `.agents/packs/ak-compound-product/`
- [x] Update `.agents/packs/ak-compound-product/pack.yaml` with `id: ak-compound-product`
- [x] Update any cross-references in skill files
- [x] Update documentation/README

## Acceptance Criteria

- [x] All pack directories use `ak-` prefix
- [x] Pack IDs in pack.yaml match directory names
- [x] `agents install` installs to `~/.claude/skills/ak-*/`
- [x] No conflicts possible with user-created pack names

## Why This Approach

**Rejected alternatives:**
- Marker files + manifest tracking: Overengineered for the problem
- Reserved name validation: Adds complexity and edge cases
- File-by-file installation: Unnecessary if names don't conflict

**This approach:**
- Zero runtime code changes
- Zero new concepts (marker files, manifests)
- Impossible for users to accidentally conflict
- Convention over configuration

## References

- Brainstorm: `docs/brainstorms/2026-01-31-skill-migration-strategy-brainstorm.md`
- Review feedback: DHH, Kieran, and Simplicity reviewers all recommended this approach
