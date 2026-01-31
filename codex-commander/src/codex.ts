import * as pty from "node-pty";
import { existsSync } from "fs";
import { execSync } from "child_process";
import { join } from "path";

export interface CodexHandle {
  write: (data: string) => void;
  resize: (cols: number, rows: number) => void;
  kill: () => void;
}

function findCodex(): string {
  // Try `which codex` first
  try {
    const result = execSync("which codex", { encoding: "utf-8" }).trim();
    if (result && existsSync(result)) {
      return result;
    }
  } catch {
    // which failed, try known locations
  }

  // Check Conductor's bin directory
  const conductorPath = join(
    process.env.HOME || "",
    "Library/Application Support/com.conductor.app/bin/codex"
  );
  if (existsSync(conductorPath)) {
    return conductorPath;
  }

  // Check common paths
  const commonPaths = [
    "/usr/local/bin/codex",
    "/opt/homebrew/bin/codex",
    join(process.env.HOME || "", ".local/bin/codex"),
  ];
  for (const p of commonPaths) {
    if (existsSync(p)) {
      return p;
    }
  }

  // Fall back to just "codex" and let it fail with a clear error
  return "codex";
}

export function spawnCodex(
  onData: (data: string) => void,
  onExit: (code: number) => void
): CodexHandle {
  const codexPath = findCodex();
  const proc = pty.spawn(codexPath, [], {
    name: "xterm-256color",
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
    kill: () => proc.kill(),
  };
}
