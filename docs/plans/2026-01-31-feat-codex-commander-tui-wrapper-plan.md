---
title: "feat: Codex Commander TUI Wrapper"
type: feat
date: 2026-01-31
---

# Codex Commander TUI Wrapper

## Overview

A terminal wrapper for Codex CLI that adds a slash command picker. User types `/`, picks a command from a fuzzy-filtered list, and the command's markdown content is injected into Codex.

**Stack:** Bun, Blessed, gray-matter, node-pty

## Problem Statement

Codex CLI lacks command discovery. Users copy-paste prompts or remember syntax. This tool adds a picker that appears on `/`, loads markdown commands from `~/.codex/commands/`, and injects them into Codex.

## Architecture

```
codex-commander/
├── src/
│   ├── index.ts      # Entry point + app orchestration
│   ├── tui.ts        # Blessed screen + picker overlay
│   ├── commands.ts   # Load commands from disk
│   └── codex.ts      # PTY wrapper for Codex
├── package.json
└── tsconfig.json
```

**4 files. ~400 lines total.**

## Command Format

```yaml
---
category: workflows
description: Decompose task into implementation steps
---

# Plan

[Markdown content injected as prompt...]
```

Command name from filename: `plan.md` → `/plan`

## Implementation

### Phase 1: PTY Passthrough

Create a working Codex wrapper with no features.

**src/codex.ts** (~70 lines)
```typescript
import * as pty from 'node-pty';

type ProcessState =
  | { status: 'idle'; pty: pty.IPty }
  | { status: 'spawning' }
  | { status: 'exited'; code: number };

export function spawnCodex(
  onData: (data: string) => void,
  onExit: (code: number) => void
): { write: (data: string) => void; resize: (cols: number, rows: number) => void } {
  const proc = pty.spawn('codex', [], {
    name: 'xterm-256color',
    cols: process.stdout.columns || 80,
    rows: process.stdout.rows || 24,
    cwd: process.cwd(),
    env: process.env as Record<string, string>,
  });

  proc.onData(onData);
  proc.onExit(({ exitCode }) => onExit(exitCode ?? 0));

  return {
    write: (data: string) => proc.write(data),
    resize: (cols: number, rows: number) => proc.resize(cols, rows),
  };
}
```

**src/index.ts** (~50 lines)
```typescript
import { createScreen } from './tui';
import { spawnCodex } from './codex';
import { loadCommands } from './commands';

async function main() {
  const commands = await loadCommands();
  const { screen, output, input, showPicker } = createScreen();

  const codex = spawnCodex(
    (data) => {
      output.pushLine(data);
      output.setScrollPerc(100);
      screen.render();
    },
    (code) => {
      output.pushLine(`\nCodex exited (code ${code}). Press Enter to restart.`);
      screen.render();
    }
  );

  // Handle resize
  process.stdout.on('resize', () => {
    codex.resize(process.stdout.columns, process.stdout.rows);
  });

  // Handle input
  input.on('submit', (value: string) => {
    if (value.startsWith('/')) {
      const [cmdName, ...rest] = value.slice(1).split(' ');
      const cmd = commands.get(cmdName);
      if (cmd) {
        const context = rest.join(' ').trim();
        const prompt = context ? `${cmd.content}\n\n---\n\nContext: ${context}` : cmd.content;
        codex.write(prompt + '\n');
      } else {
        codex.write(value + '\n');
      }
    } else {
      codex.write(value + '\n');
    }
    input.clearValue();
    screen.render();
  });

  screen.key(['C-c'], () => process.exit(0));
  screen.render();
}

main().catch(console.error);
```

### Phase 2: Command Loading

**src/commands.ts** (~80 lines)
```typescript
import { readdir, readFile } from 'fs/promises';
import { join, basename } from 'path';
import matter from 'gray-matter';

export interface Command {
  readonly name: string;
  readonly category: string;
  readonly description: string;
  readonly content: string;
  readonly path: string;
}

export async function loadCommands(): Promise<Map<string, Command>> {
  const commands = new Map<string, Command>();
  const dir = join(process.env.HOME || '', '.codex', 'commands');

  let files: string[];
  try {
    files = await readdir(dir);
  } catch {
    return commands; // Directory doesn't exist
  }

  for (const file of files) {
    if (!file.endsWith('.md')) continue;

    const path = join(dir, file);
    try {
      const raw = await readFile(path, 'utf-8');
      const { data, content } = matter(raw);

      const name = basename(file, '.md');
      const category = typeof data.category === 'string' ? data.category : 'general';
      const description = typeof data.description === 'string' ? data.description : '';

      commands.set(name, { name, category, description, content: content.trim(), path });
    } catch (err) {
      console.warn(`Skipping ${file}: ${err}`);
    }
  }

  return commands;
}

export function searchCommands(commands: Map<string, Command>, query: string): Command[] {
  const q = query.toLowerCase();
  return [...commands.values()].filter(
    (c) => c.name.includes(q) || c.description.toLowerCase().includes(q)
  );
}
```

### Phase 3: Picker Overlay

**src/tui.ts** (~150 lines)
```typescript
import blessed from 'blessed';

export function createScreen() {
  const screen = blessed.screen({
    smartCSR: true,
    fastCSR: true,
    title: 'codex-commander',
  });

  const output = blessed.log({
    parent: screen,
    top: 0,
    left: 0,
    width: '100%',
    height: '100%-3',
    scrollable: true,
    alwaysScroll: true,
    scrollbar: { ch: ' ', style: { bg: 'cyan' } },
    mouse: true,
  });

  const input = blessed.textbox({
    parent: screen,
    bottom: 0,
    left: 0,
    width: '100%',
    height: 3,
    border: { type: 'line' },
    label: ' > ',
    inputOnFocus: true,
  });

  let picker: blessed.Widgets.ListElement | null = null;
  let pickerCommands: Command[] = [];

  function showPicker(commands: Command[], onSelect: (cmd: Command) => void) {
    if (picker) picker.destroy();

    pickerCommands = commands;
    picker = blessed.list({
      parent: screen,
      bottom: 3,
      left: 0,
      width: '100%',
      height: Math.min(8, commands.length) + 2,
      border: { type: 'line' },
      keys: true,
      vi: true,
      items: commands.map((c) => `${c.category.padEnd(12)} /${c.name.padEnd(15)} ${c.description}`),
      style: { selected: { bg: 'cyan', fg: 'black' } },
    });

    picker.on('select', (item, index) => {
      onSelect(pickerCommands[index]);
      hidePicker();
    });

    picker.key('escape', hidePicker);
    picker.focus();
    screen.render();
  }

  function hidePicker() {
    if (picker) {
      picker.destroy();
      picker = null;
    }
    input.focus();
    screen.render();
  }

  input.focus();
  return { screen, output, input, showPicker, hidePicker };
}
```

## Key Bindings

| Context | Key | Action |
|---------|-----|--------|
| Input | Enter | Submit to Codex |
| Input | `/` at pos 0 | Open picker |
| Input | Ctrl+C | Exit |
| Picker | Up/Down | Navigate |
| Picker | Enter | Select command |
| Picker | Escape | Close picker |

## Error Handling

| Error | Handling |
|-------|----------|
| Command file read error | Log warning, skip file |
| Malformed frontmatter | Log warning, skip file |
| Codex not installed | Show error, exit 1 |
| Codex crashes | Show "Press Enter to restart" |
| No commands found | Picker shows "No commands" |

## Dependencies

```json
{
  "dependencies": {
    "blessed": "^0.1.81",
    "gray-matter": "^4.0.3",
    "node-pty": "^1.1.0"
  },
  "devDependencies": {
    "@types/blessed": "^0.1.25",
    "bun-types": "latest"
  }
}
```

## Acceptance Criteria

- [x] `codex-commander` launches and shows Codex output
- [x] Typing `/` opens picker with commands from `~/.codex/commands/`
- [x] Typing filters the picker list
- [x] Enter selects and injects command content
- [x] Escape closes picker
- [x] Ctrl+C exits cleanly

## Milestones

| # | Deliverable |
|---|-------------|
| 1 | PTY passthrough works (type, see Codex output) |
| 2 | `/` shows picker, selection injects content |
| 3 | Polish (error messages, edge cases) |

## What's NOT in v1

These were considered and explicitly deferred:

- Hot-reload of commands (restart to reload)
- Input history (up/down arrows)
- Plugin directories (`~/.codex/plugins/*/commands/`)
- Response completion detection (just stream passthrough)
- Conversation state tracking (let Codex handle it)
- Exponential backoff restart (simple "Press Enter")
- Configuration file (all hardcoded)
- Mouse support in picker

Add these in v2 based on user feedback.

## References

- [Blessed GitHub](https://github.com/chjj/blessed)
- [node-pty GitHub](https://github.com/microsoft/node-pty)
- [gray-matter](https://www.npmjs.com/package/gray-matter)
