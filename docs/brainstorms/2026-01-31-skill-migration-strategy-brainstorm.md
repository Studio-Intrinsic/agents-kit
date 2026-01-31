# Skill Migration Strategy Brainstorm

**Date:** 2026-01-31
**Status:** Decided

## What We're Building

A clear install/update strategy for agents-kit that handles pre-existing skills gracefully without complex migration logic.

## The Problem

Users may already have skills installed from:
1. The compound-engineering Claude Code plugin
2. Custom skills they wrote themselves
3. Other plugins or manual installations

When agents-kit installs, what happens to these existing skills?

## Key Decisions

### 1. Path-Based Identity

**Decision:** Skills are identified by their install path, not their source.

agents-kit installs to `~/.claude/skills/{pack}/{skill}/` - if compound-engineering already installed to that same path, that's fine. agents-kit is just a better distribution mechanism for the same skills.

### 2. No Migration Needed for Custom Skills

**Decision:** Users manage their own skills. agents-kit doesn't touch them.

Custom skills (flat directories like `~/.claude/skills/my-custom-skill/`) are in a different namespace than pack-based skills (`~/.claude/skills/core/plan/`). They coexist safely.

### 3. Reserved Pack Names

**Decision:** Error if a reserved pack name exists but wasn't installed by agents-kit.

If a user manually created `~/.claude/skills/core/` with their own content before installing agents-kit, installation should fail with a clear error asking them to rename their directory first.

Reserved names: `core`, `ralph`, `compound-product` (and any future official packs).

### 4. Overwrite Behavior

**Decision:** Only overwrite exact path matches. Preserve user additions.

- `agents install` writes to specific paths like `~/.claude/skills/core/plan/SKILL.md`
- If that exact file exists, overwrite it
- If user added extra files to `~/.claude/skills/core/plan/`, leave them alone
- If user added extra skills to `~/.claude/skills/core/my-custom/`, leave them alone

Future enhancement: make this configurable (always overwrite, never overwrite, prompt).

### 5. Updates

**Decision:** `agents install` and `agents update` both use the same overwrite logic.

No distinction between "first install" and "update" - both write agents-kit's files to their expected paths, overwriting what's there.

## What We're NOT Building

- Backup/restore system for skills
- Conflict detection UI
- Migration wizard from compound-engineering plugin
- Version checking to skip unchanged files
- Merge logic for modified skills

These are YAGNI for now. The simple path-based model handles the real-world cases.

## Open Questions

None - ready for implementation.

## Implementation Notes

1. Add reserved pack name validation in install script
2. Change from `rm -rf $pack_target` to file-by-file writes
3. Document the path-based identity model in README
