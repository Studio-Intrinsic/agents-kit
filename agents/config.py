"""Configuration loading for agents-kit."""

from pathlib import Path
from typing import Any

import yaml


def find_agents_root() -> Path | None:
    """Find the .agents directory by walking up from current directory."""
    current = Path.cwd()
    while current != current.parent:
        agents_dir = current / ".agents"
        if agents_dir.is_dir():
            return current
        current = current.parent
    return None


def get_global_agents_home() -> Path | None:
    """Get ~/.agents if it exists."""
    global_dir = Path.home() / ".agents"
    return global_dir if global_dir.is_dir() else None


def get_default_config() -> dict[str, Any]:
    """Return default configuration."""
    return {
        "version": 1,
        "runtimes": ["claude-code"],
        "packs": ["ak-core"],
    }


def load_config() -> dict[str, Any]:
    """Load configuration from .agents/config.yaml.

    Returns default config if file doesn't exist.
    """
    root = find_agents_root()
    if not root:
        return get_default_config()

    config_path = root / ".agents" / "config.yaml"
    if not config_path.exists():
        return get_default_config()

    with open(config_path) as f:
        config = yaml.safe_load(f) or {}

    # Merge with defaults
    defaults = get_default_config()
    for key, value in defaults.items():
        if key not in config:
            config[key] = value

    return config


def get_agents_home() -> Path:
    """Get .agents directory - local first, then global fallback."""
    # Local takes precedence
    root = find_agents_root()
    if root:
        return root / ".agents"

    # Fall back to global
    global_home = get_global_agents_home()
    if global_home:
        return global_home

    # Last resort: current directory
    return Path.cwd() / ".agents"


def get_packs_dir() -> Path:
    """Get the packs directory path."""
    return get_agents_home() / "packs"


def get_adapters_dir() -> Path:
    """Get the adapters directory path."""
    return get_agents_home() / "adapters"


def get_schema_dir() -> Path:
    """Get the schema directory path."""
    return get_agents_home() / "schema"


def get_build_dir() -> Path:
    """Get the build directory path."""
    root = find_agents_root() or Path.cwd()
    return root / "build"
