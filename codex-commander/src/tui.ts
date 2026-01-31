import blessed from "blessed";
import type { Command } from "./commands";

export interface TuiHandle {
  screen: blessed.Widgets.Screen;
  output: blessed.Widgets.Log;
  input: blessed.Widgets.TextboxElement;
  showPicker: (
    commands: Command[],
    onSelect: (cmd: Command) => void,
    onCancel: () => void
  ) => void;
  hidePicker: () => void;
}

export function createScreen(): TuiHandle {
  const screen = blessed.screen({
    smartCSR: true,
    fastCSR: true,
    title: "codex-commander",
  });

  const output = blessed.log({
    parent: screen,
    top: 0,
    left: 0,
    width: "100%",
    height: "100%-3",
    scrollable: true,
    alwaysScroll: true,
    scrollbar: { ch: " ", style: { bg: "cyan" } },
    mouse: true,
  });

  const input = blessed.textbox({
    parent: screen,
    bottom: 0,
    left: 0,
    width: "100%",
    height: 3,
    border: { type: "line" },
    label: " > ",
    inputOnFocus: true,
  });

  let picker: blessed.Widgets.ListElement | null = null;
  let pickerCommands: Command[] = [];

  function showPicker(
    commands: Command[],
    onSelect: (cmd: Command) => void,
    onCancel: () => void
  ) {
    if (picker) picker.destroy();

    if (commands.length === 0) {
      // Show "no commands" message
      picker = blessed.list({
        parent: screen,
        bottom: 3,
        left: 0,
        width: "100%",
        height: 3,
        border: { type: "line" },
        items: ["  No commands found in ~/.codex/commands/"],
        style: { fg: "gray" },
      });
      picker.key("escape", () => {
        hidePicker();
        onCancel();
      });
      picker.focus();
      screen.render();
      return;
    }

    pickerCommands = commands;
    picker = blessed.list({
      parent: screen,
      bottom: 3,
      left: 0,
      width: "100%",
      height: Math.min(8, commands.length) + 2,
      border: { type: "line" },
      keys: true,
      vi: true,
      items: commands.map(
        (c) =>
          `${c.category.padEnd(12)} /${c.name.padEnd(15)} ${c.description}`
      ),
      style: { selected: { bg: "cyan", fg: "black" } },
    });

    picker.on("select", (_item: unknown, index: number) => {
      const cmd = pickerCommands[index];
      hidePicker();
      onSelect(cmd);
    });

    picker.key("escape", () => {
      hidePicker();
      onCancel();
    });

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
