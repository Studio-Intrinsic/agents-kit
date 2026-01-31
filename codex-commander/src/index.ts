#!/usr/bin/env bun
import { createScreen } from "./tui";
import { spawnCodex } from "./codex";
import { loadCommands, searchCommands, type Command } from "./commands";

async function main() {
  const commands = await loadCommands();
  const { screen, output, input, showPicker, hidePicker } = createScreen();

  let codex = spawnCodex(
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
  process.stdout.on("resize", () => {
    codex.resize(process.stdout.columns, process.stdout.rows);
  });

  // Track picker state
  let pickerOpen = false;
  let currentFilter = "";

  // Handle slash key to open picker
  input.on("keypress", (ch: string) => {
    if (ch === "/" && input.getValue() === "") {
      pickerOpen = true;
      currentFilter = "";
      showPicker(
        [...commands.values()],
        (cmd: Command) => {
          pickerOpen = false;
          currentFilter = "";
          // Insert command into input
          input.setValue(`/${cmd.name} `);
          input.focus();
          screen.render();
        },
        () => {
          pickerOpen = false;
          currentFilter = "";
          input.clearValue();
          input.focus();
          screen.render();
        }
      );
    } else if (pickerOpen && ch && ch !== "\r" && ch !== "\n") {
      // Update filter as user types
      currentFilter += ch;
      const filtered = searchCommands(commands, currentFilter);
      showPicker(
        filtered,
        (cmd: Command) => {
          pickerOpen = false;
          currentFilter = "";
          input.setValue(`/${cmd.name} `);
          input.focus();
          screen.render();
        },
        () => {
          pickerOpen = false;
          currentFilter = "";
          input.clearValue();
          input.focus();
          screen.render();
        }
      );
    }
  });

  // Handle input submission
  input.on("submit", (value: string) => {
    if (!value.trim()) {
      input.clearValue();
      input.focus();
      screen.render();
      return;
    }

    if (value.startsWith("/")) {
      const [cmdName, ...rest] = value.slice(1).split(" ");
      const cmd = commands.get(cmdName);
      if (cmd) {
        const context = rest.join(" ").trim();
        const prompt = context
          ? `${cmd.content}\n\n---\n\nContext: ${context}`
          : cmd.content;
        output.pushLine(`> /${cmdName} ${context}`);
        codex.write(prompt + "\n");
      } else {
        // Command not found, send as-is
        output.pushLine(`> ${value}`);
        codex.write(value + "\n");
      }
    } else {
      output.pushLine(`> ${value}`);
      codex.write(value + "\n");
    }
    input.clearValue();
    input.focus();
    screen.render();
  });

  // Global key handlers
  screen.key(["C-c"], () => {
    codex.kill();
    process.exit(0);
  });

  // Initial render
  output.pushLine("codex-commander v0.1.0");
  output.pushLine('Type / to open command picker, Ctrl+C to exit.\n');
  screen.render();
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
