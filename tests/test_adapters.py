"""Tests for the adapter transform engine."""

from pathlib import Path

import pytest

from agents.adapters import (
    parse_skill_frontmatter,
    transform_frontmatter,
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


class TestTransformFrontmatter:
    """Tests for transform_frontmatter."""

    def test_rename_field(self):
        """Test renaming a field."""
        frontmatter = {"tools": ["Read", "Write"], "id": "test"}
        config = {"rename": {"tools": "allowed-tools"}}

        result = transform_frontmatter(frontmatter, config)

        assert result == {"allowed-tools": ["Read", "Write"], "id": "test"}

    def test_rename_missing_field(self):
        """Test renaming a field that doesn't exist."""
        frontmatter = {"id": "test"}
        config = {"rename": {"tools": "allowed-tools"}}

        result = transform_frontmatter(frontmatter, config)

        assert result == {"id": "test"}

    def test_omit_fields(self):
        """Test omitting fields."""
        frontmatter = {"id": "test", "name": "Test", "constraints": "remove me"}
        config = {"omit": ["constraints"]}

        result = transform_frontmatter(frontmatter, config)

        assert result == {"id": "test", "name": "Test"}

    def test_omit_multiple_fields(self):
        """Test omitting multiple fields."""
        frontmatter = {"id": "test", "tools": [], "constraints": []}
        config = {"omit": ["tools", "constraints"]}

        result = transform_frontmatter(frontmatter, config)

        assert result == {"id": "test"}

    def test_defaults_applied(self):
        """Test defaults are applied for missing fields."""
        frontmatter = {"id": "test"}
        config = {"defaults": {"allowed-tools": ["Read", "Write"]}}

        result = transform_frontmatter(frontmatter, config)

        assert result == {"id": "test", "allowed-tools": ["Read", "Write"]}

    def test_defaults_not_overwrite(self):
        """Test defaults don't overwrite existing fields."""
        frontmatter = {"id": "test", "allowed-tools": ["Bash"]}
        config = {"defaults": {"allowed-tools": ["Read", "Write"]}}

        result = transform_frontmatter(frontmatter, config)

        assert result == {"id": "test", "allowed-tools": ["Bash"]}

    def test_combined_transforms(self):
        """Test rename → omit → defaults in order."""
        frontmatter = {
            "id": "test",
            "tools": ["Read"],
            "constraints": "internal",
            "extra": "keep",
        }
        config = {
            "rename": {"tools": "allowed-tools"},
            "omit": ["constraints"],
            "defaults": {"version": "1.0.0"},
        }

        result = transform_frontmatter(frontmatter, config)

        assert result == {
            "id": "test",
            "allowed-tools": ["Read"],
            "extra": "keep",
            "version": "1.0.0",
        }

    def test_empty_config(self):
        """Test with empty config passes through all fields."""
        frontmatter = {"id": "test", "name": "Test"}
        config = {}

        result = transform_frontmatter(frontmatter, config)

        assert result == {"id": "test", "name": "Test"}


class TestTransformSkill:
    """Tests for transform_skill."""

    def test_claude_code_adapter(self, tmp_path: Path):
        """Test transformation with Claude Code adapter format."""
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
            "runtime": "claude-code",
            "filename": "SKILL.md",
            "frontmatter": {
                "rename": {"tools": "allowed-tools"},
                "defaults": {"allowed-tools": ["Glob"]},
            },
        }

        result = transform_skill(skill_file, adapter)

        # Check frontmatter was transformed
        assert "id: test-skill" in result
        assert "name: Test Skill" in result
        assert "allowed-tools:" in result
        assert "- Read" in result
        assert "- Write" in result
        # Check 'tools:' was renamed (not just present as substring of 'allowed-tools:')
        assert "\ntools:" not in result

        # Check body was preserved
        assert "# Test Skill" in result
        assert "## Intent" in result

    def test_codex_adapter(self, tmp_path: Path):
        """Test transformation with Codex adapter format."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""---
id: test-skill
name: Test Skill
version: 1.0.0
tools:
  - Read
constraints: internal
---

# Test Skill
""")

        adapter = {
            "runtime": "codex",
            "filename": "instructions.md",
            "frontmatter": {
                "omit": ["tools", "constraints"],
            },
        }

        result = transform_skill(skill_file, adapter)

        assert "id: test-skill" in result
        assert "name: Test Skill" in result
        assert "tools:" not in result
        assert "constraints" not in result
        assert "# Test Skill" in result

    def test_defaults_applied_when_missing(self, tmp_path: Path):
        """Test that defaults are applied when field is missing."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""---
id: test-skill
name: Test Skill
---

# Test Skill
""")

        adapter = {
            "runtime": "test-runtime",
            "frontmatter": {
                "defaults": {"allowed-tools": ["Read", "Write"]},
            },
        }

        result = transform_skill(skill_file, adapter)

        assert "allowed-tools:" in result
        assert "- Read" in result
        assert "- Write" in result

    def test_no_frontmatter_config(self, tmp_path: Path):
        """Test with no frontmatter config passes through unchanged."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""---
id: test-skill
name: Test Skill
---

# Body
""")

        adapter = {"runtime": "test", "filename": "skill.md"}

        result = transform_skill(skill_file, adapter)

        assert "id: test-skill" in result
        assert "name: Test Skill" in result
        assert "# Body" in result
