import { readdir, readFile } from "fs/promises";
import { join, basename } from "path";
import matter from "gray-matter";

export interface Command {
  readonly name: string;
  readonly category: string;
  readonly description: string;
  readonly content: string;
  readonly path: string;
}

export async function loadCommands(): Promise<Map<string, Command>> {
  const commands = new Map<string, Command>();
  const dir = join(process.env.HOME || "", ".codex", "commands");

  let files: string[];
  try {
    files = await readdir(dir);
  } catch {
    return commands; // Directory doesn't exist
  }

  for (const file of files) {
    if (!file.endsWith(".md")) continue;

    const filePath = join(dir, file);
    try {
      const raw = await readFile(filePath, "utf-8");
      const { data, content } = matter(raw);

      const name = basename(file, ".md");
      const category =
        typeof data.category === "string" ? data.category : "general";
      const description =
        typeof data.description === "string" ? data.description : "";

      commands.set(name, {
        name,
        category,
        description,
        content: content.trim(),
        path: filePath,
      });
    } catch (err) {
      console.warn(`Skipping ${file}: ${err}`);
    }
  }

  return commands;
}

export function searchCommands(
  commands: Map<string, Command>,
  query: string
): Command[] {
  const q = query.toLowerCase();
  return [...commands.values()].filter(
    (c) => c.name.includes(q) || c.description.toLowerCase().includes(q)
  );
}
