"""CLI commands for agents-kit."""

import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from agents import __version__
from agents.config import (
    find_agents_root,
    get_adapters_dir,
    get_build_dir,
    get_packs_dir,
    load_config,
)

console = Console()


@click.group()
@click.version_option(__version__, prog_name="agents-kit")
def cli():
    """agents-kit: Model-agnostic skills for AI coding assistants."""
    pass


@cli.command()
@click.option("--runtime", "-r", multiple=True, help="Target runtime(s)")
def render(runtime: tuple[str, ...]):
    """Render skills to build/ directory."""
    from agents.adapters import load_adapter, render_all_skills

    config = load_config()
    runtimes = list(runtime) if runtime else config.get("runtimes", [])
    packs = config.get("packs", [])

    if not runtimes:
        console.print("[red]No runtimes configured.[/red]")
        raise SystemExit(1)

    build_dir = get_build_dir()
    console.print(f"Rendering to [cyan]{build_dir}[/cyan]...")

    for rt in runtimes:
        try:
            adapter = load_adapter(rt)
        except FileNotFoundError:
            console.print(f"[red]Adapter not found for runtime: {rt}[/red]")
            continue

        rendered = render_all_skills(adapter, packs)
        console.print(f"  [green]{rt}[/green]: {rendered} skills rendered")

    console.print("[green]Done![/green]")


@cli.command()
@click.option("--runtime", "-r", multiple=True, help="Target runtime(s)")
def install(runtime: tuple[str, ...]):
    """Render and install skills to configured runtimes."""
    from agents.adapters import install_to_runtime, load_adapter, render_all_skills

    config = load_config()
    runtimes = list(runtime) if runtime else config.get("runtimes", [])
    packs = config.get("packs", [])

    if not runtimes:
        console.print("[red]No runtimes configured.[/red]")
        raise SystemExit(1)

    console.print("Rendering skills...")
    for rt in runtimes:
        try:
            adapter = load_adapter(rt)
        except FileNotFoundError:
            console.print(f"[red]Adapter not found for runtime: {rt}[/red]")
            continue

        rendered = render_all_skills(adapter, packs)
        console.print(f"  [green]{rt}[/green]: {rendered} skills rendered")

    console.print("\nInstalling to runtimes...")
    for rt in runtimes:
        try:
            adapter = load_adapter(rt)
        except FileNotFoundError:
            continue

        installed = install_to_runtime(adapter)
        install_path = adapter.get("install_path", "unknown")
        console.print(f"  [green]{rt}[/green]: {installed} skills -> {install_path}")

    console.print("[green]Done![/green]")


@cli.command()
def validate():
    """Validate all skills and packs against schemas."""
    from agents.schemas import validate_all

    console.print("Validating skills and packs...")
    errors = validate_all()

    if errors:
        console.print(f"\n[red]Found {len(errors)} validation errors:[/red]")
        for error in errors:
            console.print(f"  [red]•[/red] {error}")
        raise SystemExit(1)
    else:
        console.print("[green]All validations passed![/green]")


@cli.command("list")
def list_cmd():
    """List installed packs and skills."""
    config = load_config()
    packs_dir = get_packs_dir()

    if not packs_dir.exists():
        console.print("[yellow]No packs directory found.[/yellow]")
        return

    table = Table(title="Installed Packs & Skills")
    table.add_column("Pack", style="cyan")
    table.add_column("Skills", style="green")
    table.add_column("Workflows", style="blue")

    for pack_dir in sorted(packs_dir.iterdir()):
        if not pack_dir.is_dir():
            continue

        skills_dir = pack_dir / "skills"
        workflows_dir = pack_dir / "workflows"

        skills = []
        if skills_dir.exists():
            skills = [d.name for d in skills_dir.iterdir() if d.is_dir()]

        workflows = []
        if workflows_dir.exists():
            workflows = [f.stem for f in workflows_dir.glob("*.md")]

        table.add_row(
            pack_dir.name,
            ", ".join(skills[:5]) + ("..." if len(skills) > 5 else ""),
            ", ".join(workflows[:5]) + ("..." if len(workflows) > 5 else ""),
        )

    console.print(table)

    # Show configured runtimes
    runtimes = config.get("runtimes", [])
    if runtimes:
        console.print(f"\n[dim]Configured runtimes: {', '.join(runtimes)}[/dim]")


@cli.command()
def doctor():
    """Check installation health."""
    from agents.adapters import load_adapter

    config = load_config()
    issues = []

    # Check .agents directory exists
    root = find_agents_root()
    if not root:
        issues.append("No .agents directory found in current path or parents")
    else:
        console.print(f"[green]✓[/green] Found .agents at {root}")

    # Check packs directory
    packs_dir = get_packs_dir()
    if packs_dir.exists():
        pack_count = len([d for d in packs_dir.iterdir() if d.is_dir()])
        console.print(f"[green]✓[/green] Packs directory: {pack_count} packs")
    else:
        issues.append("Packs directory not found")

    # Check adapters directory
    adapters_dir = get_adapters_dir()
    if adapters_dir.exists():
        adapter_count = len([d for d in adapters_dir.iterdir() if d.is_dir()])
        console.print(f"[green]✓[/green] Adapters directory: {adapter_count} adapters")
    else:
        issues.append("Adapters directory not found")

    # Check configured runtimes have adapters
    runtimes = config.get("runtimes", [])
    for rt in runtimes:
        try:
            adapter = load_adapter(rt)
            install_path = Path(adapter.get("install_path", "")).expanduser()
            if install_path.exists():
                console.print(f"[green]✓[/green] Runtime {rt}: install path exists")
            else:
                console.print(
                    f"[yellow]![/yellow] Runtime {rt}: install path does not exist (will be created)"
                )
        except FileNotFoundError:
            issues.append(f"No adapter found for configured runtime: {rt}")

    if issues:
        console.print(f"\n[red]Found {len(issues)} issues:[/red]")
        for issue in issues:
            console.print(f"  [red]✗[/red] {issue}")
        raise SystemExit(1)
    else:
        console.print("\n[green]All checks passed![/green]")


@cli.command()
def update():
    """Pull latest changes and reinstall."""
    root = find_agents_root()
    if not root:
        console.print("[red]No .agents directory found.[/red]")
        raise SystemExit(1)

    # Check if we're in a git repo
    git_dir = root / ".git"
    if not git_dir.exists() and not (root / ".git").is_file():
        console.print("[yellow]Not a git repository. Running install only.[/yellow]")
    else:
        console.print("Pulling latest changes...")
        result = subprocess.run(
            ["git", "pull"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            console.print(f"[red]Git pull failed:[/red] {result.stderr}")
            raise SystemExit(1)
        console.print(result.stdout.strip())

    # Run install
    console.print("\nReinstalling...")
    ctx = click.get_current_context()
    ctx.invoke(install)


@cli.command("new-skill")
@click.argument("name")
@click.option("--pack", "-p", required=True, help="Pack to add skill to")
def new_skill(name: str, pack: str):
    """Create a new skill from template."""
    import re

    # Validate name format
    if not re.match(r"^[a-z][a-z0-9-]*$", name):
        console.print(
            "[red]Skill name must be lowercase, start with a letter, and contain only letters, numbers, and hyphens.[/red]"
        )
        raise SystemExit(1)

    packs_dir = get_packs_dir()
    pack_dir = packs_dir / pack

    if not pack_dir.exists():
        console.print(f"[red]Pack '{pack}' not found.[/red]")
        raise SystemExit(1)

    skills_dir = pack_dir / "skills"
    skill_dir = skills_dir / name

    if skill_dir.exists():
        console.print(f"[red]Skill '{name}' already exists in pack '{pack}'.[/red]")
        raise SystemExit(1)

    # Create skill directory and file
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "skill.md"

    template = f'''---
id: {name}
name: {name.replace("-", " ").title()}
version: 1.0.0
description: |
  Describe what this skill does.
  When should it be used?
tags: []
inputs:
  - name: input_name
    type: string
    required: true
    description: Description of this input
outputs:
  - name: output_name
    type: markdown
    description: Description of this output
constraints: []
tools: []
---

# {name.replace("-", " ").title()}

## Intent

What this skill accomplishes and why it matters.

## Procedure

1. First step
2. Second step
3. Third step

## Failure Modes

- What can go wrong
- Common mistakes to avoid

## Examples

### Input

Example input here.

### Output

Example output here.
'''

    skill_file.write_text(template)
    console.print(f"[green]Created skill at {skill_file}[/green]")

    # Update pack.yaml
    pack_yaml = pack_dir / "pack.yaml"
    if pack_yaml.exists():
        import yaml

        with open(pack_yaml) as f:
            pack_config = yaml.safe_load(f) or {}

        skills = pack_config.get("skills", [])
        if name not in skills:
            skills.append(name)
            pack_config["skills"] = skills

            with open(pack_yaml, "w") as f:
                yaml.dump(pack_config, f, default_flow_style=False, sort_keys=False)
            console.print(f"[green]Added '{name}' to {pack_yaml}[/green]")


if __name__ == "__main__":
    cli()
