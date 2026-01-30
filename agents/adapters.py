"""Adapter system for transforming skills to runtime-specific formats."""

import re
import shutil
from pathlib import Path
from typing import Any

import yaml

from agents.config import get_adapters_dir, get_build_dir, get_packs_dir


def load_adapter(runtime: str) -> dict[str, Any]:
    """Load adapter configuration for a runtime.

    Args:
        runtime: Name of the runtime (e.g., 'claude-code', 'codex')

    Returns:
        Adapter configuration dict

    Raises:
        FileNotFoundError: If adapter doesn't exist
    """
    adapters_dir = get_adapters_dir()
    adapter_path = adapters_dir / runtime / "adapter.yaml"

    if not adapter_path.exists():
        raise FileNotFoundError(f"Adapter not found: {adapter_path}")

    with open(adapter_path) as f:
        return yaml.safe_load(f)


def parse_skill_frontmatter(skill_path: Path) -> tuple[dict[str, Any], str]:
    """Parse a skill.md file into frontmatter and body.

    Args:
        skill_path: Path to skill.md file

    Returns:
        Tuple of (frontmatter dict, body string)
    """
    content = skill_path.read_text()

    # Match YAML frontmatter between --- markers
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content

    frontmatter_str, body = match.groups()
    frontmatter = yaml.safe_load(frontmatter_str) or {}

    return frontmatter, body


def transform_frontmatter(
    frontmatter: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Transform frontmatter: copy all → rename → omit → defaults.

    Args:
        frontmatter: Original frontmatter dict
        config: Frontmatter config with rename, omit, defaults keys

    Returns:
        Transformed frontmatter dict
    """
    # Start with all fields
    result = frontmatter.copy()

    # Apply renames
    for old, new in config.get("rename", {}).items():
        if old in result:
            result[new] = result.pop(old)

    # Remove omitted fields
    for field in config.get("omit", []):
        result.pop(field, None)

    # Apply defaults for missing fields
    for field, value in config.get("defaults", {}).items():
        if field not in result:
            result[field] = value

    return result


def transform_skill(skill_path: Path, adapter: dict[str, Any]) -> str:
    """Transform a skill file using an adapter.

    Args:
        skill_path: Path to skill.md file
        adapter: Adapter configuration

    Returns:
        Transformed skill content
    """
    frontmatter, body = parse_skill_frontmatter(skill_path)

    # Transform frontmatter using simplified config
    fm_config = adapter.get("frontmatter", {})
    new_frontmatter = transform_frontmatter(frontmatter, fm_config)

    # Reconstruct skill.md
    if new_frontmatter:
        frontmatter_str = yaml.dump(
            new_frontmatter, default_flow_style=False, sort_keys=False
        )
        return f"---\n{frontmatter_str}---\n{body}"
    else:
        return body


def get_skills_in_pack(pack_name: str) -> list[Path]:
    """Get all skill paths in a pack.

    Args:
        pack_name: Name of the pack

    Returns:
        List of paths to skill.md files
    """
    packs_dir = get_packs_dir()
    pack_dir = packs_dir / pack_name
    skills_dir = pack_dir / "skills"

    if not skills_dir.exists():
        return []

    skills = []
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "skill.md"
            if skill_file.exists():
                skills.append(skill_file)

    return skills


def render_all_skills(adapter: dict[str, Any], packs: list[str]) -> int:
    """Render all skills for an adapter.

    Args:
        adapter: Adapter configuration
        packs: List of pack names to render

    Returns:
        Number of skills rendered
    """
    runtime = adapter.get("runtime", "unknown")
    build_dir = get_build_dir() / runtime
    output_filename = adapter.get("filename", "skill.md")

    # Clean and recreate build directory for this runtime
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    count = 0
    for pack_name in packs:
        skills = get_skills_in_pack(pack_name)
        for skill_path in skills:
            skill_name = skill_path.parent.name

            # Create output directory
            output_dir = build_dir / pack_name / skill_name
            output_dir.mkdir(parents=True, exist_ok=True)

            # Transform and write
            transformed = transform_skill(skill_path, adapter)
            output_path = output_dir / output_filename
            output_path.write_text(transformed)
            count += 1

    return count


def install_to_runtime(adapter: dict[str, Any]) -> int:
    """Install rendered skills to runtime install path.

    Args:
        adapter: Adapter configuration

    Returns:
        Number of skills installed
    """
    runtime = adapter.get("runtime", "unknown")
    install_path_template = adapter.get("install_path", "")

    if not install_path_template:
        return 0

    build_dir = get_build_dir() / runtime
    if not build_dir.exists():
        return 0

    count = 0
    for pack_dir in build_dir.iterdir():
        if not pack_dir.is_dir():
            continue
        pack_name = pack_dir.name

        for skill_dir in pack_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_name = skill_dir.name

            # Expand install path template
            install_path = (
                install_path_template.replace("{pack}", pack_name).replace(
                    "{skill}", skill_name
                )
            )
            install_path = Path(install_path).expanduser()

            # Create install directory and copy files
            install_path.mkdir(parents=True, exist_ok=True)
            for file in skill_dir.iterdir():
                if file.is_file():
                    shutil.copy2(file, install_path / file.name)
                    count += 1

    return count
