---
title: "feat: Two-Tier Config/Skills Architecture"
type: feat
date: 2026-01-31
---

# Two-Tier Config/Skills Architecture

## Overview

Enable global skills at `~/.agents/` with local repo override at `repo/.agents/`. Local wins completely — no merge logic, no new abstractions.

## Problem Statement

**Current:** `find_agents_root()` walks up from cwd, stops at first `.agents/`. No global installation support.

**Wanted:** Skills installed once at `~/.agents/packs/` available everywhere. Local `.agents/` overrides when present.

## Solution

Modify `get_agents_home()` to check local first, fall back to global. That's it.

```python
# config.py - the entire change

def get_global_agents_home() -> Path | None:
    """Get ~/.agents if it exists."""
    global_dir = Path.home() / ".agents"
    return global_dir if global_dir.is_dir() else None

def get_agents_home() -> Path:
    """Get .agents directory - local first, then global fallback."""
    # Local takes precedence
    root = find_agents_root()
    if root:
        return root / ".agents"

    # Fall back to global
    global_home = get_global_agents_home()
    if global_home:
        return global_home

    # Last resort: current directory
    return Path.cwd() / ".agents"
```

## What This Enables

```
~/.agents/                    # Install skills here once
├── packs/
│   └── core/
│       └── skills/
│           ├── commit/
│           └── review/

~/work/client-repo/           # cd here, run agents
(no .agents/ needed)          # Uses global skills

~/work/special-repo/          # Has local .agents/
└── .agents/                  # Completely overrides global
    └── packs/
        └── custom/
```

## Acceptance Criteria

- [x] `agents install` in repo without `.agents/` uses `~/.agents/`
- [x] `agents install` in repo with `.agents/` ignores global
- [x] Missing both → clear error message
- [x] Existing repos with `.agents/` work unchanged

## What We're NOT Building

Per reviewer feedback, these are deferred until real demand:

| Feature | Why Deferred |
|---------|--------------|
| Memory module | No use case yet. Put context in `config.yaml` if needed. |
| Config merge | Complexity for imaginary problems. Local wins. |
| Shadow warnings | Noise. Document the behavior instead. |
| `--global` flag | Premature. Users can cd to ~/.agents/. |
| Source indicators | Gold-plating. Add `--verbose` if requested. |

## Implementation

**Files to modify:** `agents/config.py` only

**Lines of code:** ~15

**Time estimate:** 1 hour including tests

### Changes

1. Add `get_global_agents_home()` function
2. Modify `get_agents_home()` to check both locations
3. Add test cases for: local-only, global-only, both (local wins), neither (error)

## Future Considerations

If users request repo-specific context that skills can read:

```yaml
# repo/.agents/config.yaml
context:
  stack: [next.js, postgres]
  conventions:
    commits: conventional
```

Skills can read `config.context.whatever`. No new module needed — just structured data in existing config.

## References

- Current config: `agents/config.py:9-17` (`find_agents_root`)
- Current home: `agents/config.py:54-61` (`get_agents_home`)
- Reviewer feedback: DHH, Kieran, Simplicity reviewers all recommended this minimal approach
