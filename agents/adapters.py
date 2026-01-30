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


def apply_frontmatter_transforms(
    frontmatter: dict[str, Any],
    transforms: list[dict[str, Any]],
) -> dict[str, Any]:
    """Apply transformation operations to frontmatter.

    Supported operations:
    - copy: Copy field(s) as-is. Can be a single field or list of fields.
    - rename: Rename a field. Format: {from: old_name, to: new_name}
    - omit: Remove field(s). Can be a single field or list of fields.

    Args:
        frontmatter: Original frontmatter dict
        transforms: List of transform operations

    Returns:
        Transformed frontmatter dict
    """
    result = {}

    for op in transforms:
        if "copy" in op:
            fields = op["copy"]
            if isinstance(fields, str):
                fields = [fields]
            for field in fields:
                if field in frontmatter:
                    result[field] = frontmatter[field]

        elif "rename" in op:
            rename = op["rename"]
            from_field = rename.get("from")
            to_field = rename.get("to")
            if from_field and to_field and from_field in frontmatter:
                result[to_field] = frontmatter[from_field]

        elif "omit" in op:
            # Omit removes fields from result
            fields = op["omit"]
            if isinstance(fields, str):
                fields = [fields]
            for field in fields:
                result.pop(field, None)

    return result


def apply_body_transforms(body: str, transforms: list[dict[str, Any]]) -> str:
    """Apply transformation operations to body.

    Supported operations:
    - copy: If true, copy body as-is

    Args:
        body: Original body string
        transforms: List of transform operations

    Returns:
        Transformed body string
    """
    for op in transforms:
        if op.get("copy") is True:
            return body
    return body


def get_output_filename(
    skill_name: str,
    transforms: list[dict[str, Any]],
) -> str:
    """Determine output filename based on transforms.

    Args:
        skill_name: Name of the skill
        transforms: Filename transform operations

    Returns:
        Output filename
    """
    for op in transforms:
        if "template" in op:
            template = op["template"]
            return template.replace("{skill}", skill_name)
    return "skill.md"


def transform_skill(skill_path: Path, adapter: dict[str, Any]) -> str:
    """Transform a skill file using an adapter.

    Args:
        skill_path: Path to skill.md file
        adapter: Adapter configuration

    Returns:
        Transformed skill content
    """
    frontmatter, body = parse_skill_frontmatter(skill_path)
    transforms = adapter.get("transforms", {})

    # Transform frontmatter
    fm_transforms = transforms.get("frontmatter", [])
    new_frontmatter = apply_frontmatter_transforms(frontmatter, fm_transforms)

    # Apply defaults if specified
    defaults = transforms.get("defaults", {})
    for key, value in defaults.items():
        if key not in new_frontmatter:
            new_frontmatter[key] = value

    # Transform body
    body_transforms = transforms.get("body", [])
    new_body = apply_body_transforms(body, body_transforms)

    # Reconstruct skill.md
    if new_frontmatter:
        frontmatter_str = yaml.dump(
            new_frontmatter, default_flow_style=False, sort_keys=False
        )
        return f"---\n{frontmatter_str}---\n{new_body}"
    else:
        return new_body


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
    transforms = adapter.get("transforms", {})
    filename_transforms = transforms.get("filename", [])

    # Clean and recreate build directory for this runtime
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    count = 0
    for pack_name in packs:
        skills = get_skills_in_pack(pack_name)
        for skill_path in skills:
            skill_name = skill_path.parent.name
            output_filename = get_output_filename(skill_name, filename_transforms)

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
                install_path_template.replace("{pack}", pack_name)
                .replace("{skill}", skill_name)
            )
            install_path = Path(install_path).expanduser()

            # Create install directory and copy files
            install_path.mkdir(parents=True, exist_ok=True)
            for file in skill_dir.iterdir():
                if file.is_file():
                    shutil.copy2(file, install_path / file.name)
                    count += 1

    return count
