"""Tests for configuration loading."""

from pathlib import Path

import pytest

from agents.config import (
    find_agents_root,
    get_agents_home,
    get_global_agents_home,
)


class TestGetGlobalAgentsHome:
    """Tests for get_global_agents_home."""

    def test_returns_path_when_exists(self, tmp_path: Path, monkeypatch):
        """Test returns ~/.agents when directory exists."""
        global_agents = tmp_path / ".agents"
        global_agents.mkdir()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        result = get_global_agents_home()

        assert result == global_agents

    def test_returns_none_when_missing(self, tmp_path: Path, monkeypatch):
        """Test returns None when ~/.agents doesn't exist."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        result = get_global_agents_home()

        assert result is None


class TestGetAgentsHome:
    """Tests for get_agents_home with two-tier config."""

    def test_local_takes_precedence(self, tmp_path: Path, monkeypatch):
        """Test local .agents is used when both local and global exist."""
        # Setup local
        local_agents = tmp_path / "project" / ".agents"
        local_agents.mkdir(parents=True)

        # Setup global
        home = tmp_path / "home"
        global_agents = home / ".agents"
        global_agents.mkdir(parents=True)

        monkeypatch.setattr(Path, "home", lambda: home)
        monkeypatch.setattr(Path, "cwd", lambda: tmp_path / "project")

        result = get_agents_home()

        assert result == local_agents

    def test_global_fallback_when_no_local(self, tmp_path: Path, monkeypatch):
        """Test global ~/.agents is used when no local .agents exists."""
        # Setup global only
        home = tmp_path / "home"
        global_agents = home / ".agents"
        global_agents.mkdir(parents=True)

        # No local .agents - just an empty project dir
        project = tmp_path / "project"
        project.mkdir()

        monkeypatch.setattr(Path, "home", lambda: home)
        monkeypatch.setattr(Path, "cwd", lambda: project)

        result = get_agents_home()

        assert result == global_agents

    def test_cwd_fallback_when_neither_exists(self, tmp_path: Path, monkeypatch):
        """Test falls back to cwd/.agents when neither local nor global exist."""
        # Empty home (no global)
        home = tmp_path / "home"
        home.mkdir()

        # Empty project (no local)
        project = tmp_path / "project"
        project.mkdir()

        monkeypatch.setattr(Path, "home", lambda: home)
        monkeypatch.setattr(Path, "cwd", lambda: project)

        result = get_agents_home()

        assert result == project / ".agents"

    def test_existing_repos_work_unchanged(self, tmp_path: Path, monkeypatch):
        """Test repos with .agents work exactly as before."""
        # Setup local .agents (simulating existing repo)
        local_agents = tmp_path / ".agents"
        local_agents.mkdir()

        # Even with global, local should be used
        home = tmp_path / "home"
        global_agents = home / ".agents"
        global_agents.mkdir(parents=True)

        monkeypatch.setattr(Path, "home", lambda: home)
        monkeypatch.setattr(Path, "cwd", lambda: tmp_path)

        result = get_agents_home()

        assert result == local_agents
