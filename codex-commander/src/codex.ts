import * as pty from "node-pty";

export interface CodexHandle {
  write: (data: string) => void;
  resize: (cols: number, rows: number) => void;
  kill: () => void;
}

export function spawnCodex(
  onData: (data: string) => void,
  onExit: (code: number) => void
): CodexHandle {
  const proc = pty.spawn("codex", [], {
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
