"""Tests for the adapter transform engine."""

import tempfile
from pathlib import Path

import pytest

from agents.adapters import (
    apply_body_transforms,
    apply_frontmatter_transforms,
    get_output_filename,
    parse_skill_frontmatter,
    transform_skill,
)


class TestParseFrontmatter:
    """Tests for parse_skill_frontmatter."""

    def test_parse_valid_frontmatter(self, tmp_path: Path):
        """Test parsing a skill with valid frontmatter."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""---
id: test-skill
name: Test Skill
version: 1.0.0
description: A test skill
---

# Test Skill

This is the body.
""")
        frontmatter, body = parse_skill_frontmatter(skill_file)

        assert frontmatter["id"] == "test-skill"
        assert frontmatter["name"] == "Test Skill"
        assert frontmatter["version"] == "1.0.0"
        assert "# Test Skill" in body

    def test_parse_no_frontmatter(self, tmp_path: Path):
        """Test parsing a skill without frontmatter."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("# Just a heading\n\nNo frontmatter here.")

        frontmatter, body = parse_skill_frontmatter(skill_file)

        assert frontmatter == {}
        assert "# Just a heading" in body


class TestApplyFrontmatterTransforms:
    """Tests for apply_frontmatter_transforms."""

    def test_copy_single_field(self):
        """Test copying a single field."""
        frontmatter = {"id": "test", "name": "Test", "extra": "ignore"}
        transforms = [{"copy": "id"}]

        result = apply_frontmatter_transforms(frontmatter, transforms)

        assert result == {"id": "test"}

    def test_copy_multiple_fields(self):
        """Test copying multiple fields."""
        frontmatter = {"id": "test", "name": "Test", "version": "1.0.0"}
        transforms = [{"copy": ["id", "name", "version"]}]

        result = apply_frontmatter_transforms(frontmatter, transforms)

        assert result == {"id": "test", "name": "Test", "version": "1.0.0"}

    def test_copy_missing_field(self):
        """Test copying a field that doesn't exist."""
        frontmatter = {"id": "test"}
        transforms = [{"copy": ["id", "missing"]}]

        result = apply_frontmatter_transforms(frontmatter, transforms)

        assert result == {"id": "test"}

    def test_rename_field(self):
        """Test renaming a field."""
        frontmatter = {"tools": ["Read", "Write"]}
        transforms = [{"rename": {"from": "tools", "to": "allowed-tools"}}]

        result = apply_frontmatter_transforms(frontmatter, transforms)

        assert result == {"allowed-tools": ["Read", "Write"]}

    def test_rename_missing_field(self):
        """Test renaming a field that doesn't exist."""
        frontmatter = {"id": "test"}
        transforms = [{"rename": {"from": "tools", "to": "allowed-tools"}}]

        result = apply_frontmatter_transforms(frontmatter, transforms)

        assert result == {}

    def test_omit_field(self):
        """Test omitting fields."""
        frontmatter = {"id": "test", "name": "Test"}
        transforms = [
            {"copy": ["id", "name"]},
            {"omit": "name"},
        ]

        result = apply_frontmatter_transforms(frontmatter, transforms)

        assert result == {"id": "test"}

    def test_combined_transforms(self):
        """Test combining copy and rename."""
        frontmatter = {
            "id": "test",
            "name": "Test Skill",
            "version": "1.0.0",
            "tools": ["Read"],
            "extra": "ignored",
        }
        transforms = [
            {"copy": ["id", "name", "version"]},
            {"rename": {"from": "tools", "to": "allowed-tools"}},
        ]

        result = apply_frontmatter_transforms(frontmatter, transforms)

        assert result == {
            "id": "test",
            "name": "Test Skill",
            "version": "1.0.0",
            "allowed-tools": ["Read"],
        }


class TestApplyBodyTransforms:
    """Tests for apply_body_transforms."""

    def test_copy_body(self):
        """Test copying body as-is."""
        body = "# Heading\n\nSome content."
        transforms = [{"copy": True}]

        result = apply_body_transforms(body, transforms)

        assert result == body

    def test_no_copy(self):
        """Test when copy is not true."""
        body = "# Heading\n\nSome content."
        transforms = [{"copy": False}]

        result = apply_body_transforms(body, transforms)

        assert result == body  # Falls through


class TestGetOutputFilename:
    """Tests for get_output_filename."""

    def test_template_filename(self):
        """Test filename from template."""
        transforms = [{"template": "SKILL.md"}]

        result = get_output_filename("my-skill", transforms)

        assert result == "SKILL.md"

    def test_template_with_skill_var(self):
        """Test filename template with {skill} variable."""
        transforms = [{"template": "{skill}.md"}]

        result = get_output_filename("my-skill", transforms)

        assert result == "my-skill.md"

    def test_default_filename(self):
        """Test default filename when no template."""
        transforms = []

        result = get_output_filename("my-skill", transforms)

        assert result == "skill.md"


class TestTransformSkill:
    """Tests for transform_skill."""

    def test_full_transform(self, tmp_path: Path):
        """Test a complete skill transformation."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""---
id: test-skill
name: Test Skill
version: 1.0.0
description: A test skill for testing.
tools:
  - Read
  - Write
---

# Test Skill

## Intent

Test the transform engine.
""")

        adapter = {
            "runtime": "test-runtime",
            "transforms": {
                "frontmatter": [
                    {"copy": ["id", "name", "version", "description"]},
                    {"rename": {"from": "tools", "to": "allowed-tools"}},
                ],
                "body": [{"copy": True}],
                "defaults": {
                    "allowed-tools": ["Glob"],
                },
            },
        }

        result = transform_skill(skill_file, adapter)

        # Check frontmatter was transformed
        assert "id: test-skill" in result
        assert "name: Test Skill" in result
        assert "allowed-tools:" in result
        assert "- Read" in result
        assert "- Write" in result

        # Check body was preserved
        assert "# Test Skill" in result
        assert "## Intent" in result

    def test_defaults_applied(self, tmp_path: Path):
        """Test that defaults are applied when field is missing."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""---
id: test-skill
name: Test Skill
version: 1.0.0
description: No tools defined.
---

# Test Skill
""")

        adapter = {
            "runtime": "test-runtime",
            "transforms": {
                "frontmatter": [
                    {"copy": ["id", "name", "version", "description"]},
                ],
                "body": [{"copy": True}],
                "defaults": {
                    "allowed-tools": ["Read", "Write"],
                },
            },
        }

        result = transform_skill(skill_file, adapter)

        assert "allowed-tools:" in result
        assert "- Read" in result
        assert "- Write" in result
