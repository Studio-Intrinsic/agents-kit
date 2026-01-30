"""Schema validation for skills and packs."""

import json
import re
from pathlib import Path
from typing import Any

import yaml

from agents.config import get_packs_dir, get_schema_dir


def load_schema(schema_name: str) -> dict[str, Any]:
    """Load a JSON schema from the schema directory.

    Args:
        schema_name: Name of the schema file (e.g., 'skill.schema.json')

    Returns:
        Schema dict

    Raises:
        FileNotFoundError: If schema doesn't exist
    """
    schema_dir = get_schema_dir()
    schema_path = schema_dir / schema_name

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")

    with open(schema_path) as f:
        return json.load(f)


def parse_frontmatter(file_path: Path) -> dict[str, Any] | None:
    """Parse YAML frontmatter from a markdown file.

    Args:
        file_path: Path to markdown file

    Returns:
        Frontmatter dict or None if no frontmatter
    """
    content = file_path.read_text()

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return None


def validate_against_schema(
    data: dict[str, Any],
    schema: dict[str, Any],
    path: str = "",
) -> list[str]:
    """Validate data against a JSON schema (simple implementation).

    This is a simplified validator that checks:
    - Required fields
    - Type validation
    - Pattern matching for strings
    - Enum validation

    Args:
        data: Data to validate
        schema: JSON schema
        path: Current path for error messages

    Returns:
        List of validation errors
    """
    errors = []

    # Check required fields
    required = schema.get("required", [])
    for field in required:
        if field not in data:
            errors.append(f"{path}: Missing required field '{field}'")

    # Check properties
    properties = schema.get("properties", {})
    for field, value in data.items():
        if field not in properties:
            if schema.get("additionalProperties") is False:
                errors.append(f"{path}: Unknown field '{field}'")
            continue

        prop_schema = properties[field]
        field_path = f"{path}.{field}" if path else field

        # Type checking
        expected_type = prop_schema.get("type")
        if expected_type:
            type_map = {
                "string": str,
                "number": (int, float),
                "integer": int,
                "boolean": bool,
                "array": list,
                "object": dict,
            }
            expected_python_type = type_map.get(expected_type)
            if expected_python_type and not isinstance(value, expected_python_type):
                errors.append(
                    f"{field_path}: Expected {expected_type}, got {type(value).__name__}"
                )
                continue

        # Pattern matching for strings
        if expected_type == "string" and isinstance(value, str):
            pattern = prop_schema.get("pattern")
            if pattern and not re.match(pattern, value):
                errors.append(f"{field_path}: Value '{value}' doesn't match pattern")

            min_length = prop_schema.get("minLength")
            if min_length and len(value) < min_length:
                errors.append(
                    f"{field_path}: String too short (min {min_length} chars)"
                )

        # Enum validation
        enum_values = prop_schema.get("enum")
        if enum_values and value not in enum_values:
            errors.append(f"{field_path}: Value must be one of {enum_values}")

        # Array items validation
        if expected_type == "array" and isinstance(value, list):
            items_schema = prop_schema.get("items", {})
            for i, item in enumerate(value):
                item_path = f"{field_path}[{i}]"
                if items_schema.get("type") == "object":
                    errors.extend(
                        validate_against_schema(item, items_schema, item_path)
                    )
                elif items_schema.get("type") == "string":
                    if not isinstance(item, str):
                        errors.append(f"{item_path}: Expected string")
                    else:
                        pattern = items_schema.get("pattern")
                        if pattern and not re.match(pattern, item):
                            errors.append(
                                f"{item_path}: Value '{item}' doesn't match pattern"
                            )

    return errors


def validate_skill(skill_path: Path) -> list[str]:
    """Validate a skill.md file.

    Args:
        skill_path: Path to skill.md file

    Returns:
        List of validation errors
    """
    errors = []
    skill_name = skill_path.parent.name

    # Parse frontmatter
    frontmatter = parse_frontmatter(skill_path)
    if frontmatter is None:
        return [f"{skill_name}: No valid frontmatter found"]

    # Load and validate against schema
    try:
        schema = load_schema("skill.schema.json")
        schema_errors = validate_against_schema(frontmatter, schema, skill_name)
        errors.extend(schema_errors)
    except FileNotFoundError:
        # Schema doesn't exist, skip schema validation
        pass

    # Check that id matches directory name
    if frontmatter.get("id") != skill_name:
        errors.append(
            f"{skill_name}: Skill id '{frontmatter.get('id')}' doesn't match directory name"
        )

    return errors


def validate_pack(pack_path: Path) -> list[str]:
    """Validate a pack.yaml file.

    Args:
        pack_path: Path to pack.yaml file

    Returns:
        List of validation errors
    """
    errors = []
    pack_name = pack_path.parent.name

    # Load pack.yaml
    try:
        with open(pack_path) as f:
            pack_data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        return [f"{pack_name}: Invalid YAML - {e}"]

    # Load and validate against schema
    try:
        schema = load_schema("pack.schema.json")
        schema_errors = validate_against_schema(pack_data, schema, pack_name)
        errors.extend(schema_errors)
    except FileNotFoundError:
        # Schema doesn't exist, skip schema validation
        pass

    # Check that id matches directory name
    if pack_data.get("id") != pack_name:
        errors.append(
            f"{pack_name}: Pack id '{pack_data.get('id')}' doesn't match directory name"
        )

    # Check that listed skills exist
    skills_dir = pack_path.parent / "skills"
    listed_skills = pack_data.get("skills", [])
    for skill_id in listed_skills:
        skill_dir = skills_dir / skill_id
        if not skill_dir.exists():
            errors.append(f"{pack_name}: Listed skill '{skill_id}' not found")
        elif not (skill_dir / "skill.md").exists():
            errors.append(f"{pack_name}: Skill '{skill_id}' missing skill.md")

    # Check that listed workflows exist
    workflows_dir = pack_path.parent / "workflows"
    listed_workflows = pack_data.get("workflows", [])
    for workflow_id in listed_workflows:
        workflow_file = workflows_dir / f"{workflow_id}.md"
        if not workflow_file.exists():
            errors.append(f"{pack_name}: Listed workflow '{workflow_id}' not found")

    return errors


def validate_all() -> list[str]:
    """Validate all packs and skills.

    Returns:
        List of all validation errors
    """
    errors = []
    packs_dir = get_packs_dir()

    if not packs_dir.exists():
        return ["Packs directory not found"]

    for pack_dir in packs_dir.iterdir():
        if not pack_dir.is_dir():
            continue

        # Validate pack.yaml
        pack_yaml = pack_dir / "pack.yaml"
        if pack_yaml.exists():
            errors.extend(validate_pack(pack_yaml))
        else:
            errors.append(f"{pack_dir.name}: Missing pack.yaml")

        # Validate skills
        skills_dir = pack_dir / "skills"
        if skills_dir.exists():
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir():
                    skill_file = skill_dir / "skill.md"
                    if skill_file.exists():
                        errors.extend(validate_skill(skill_file))

    return errors
