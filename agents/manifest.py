"""Manifest system for tracking installed skills and detecting modifications."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

# Manifest stored globally since runtime install paths are global
MANIFEST_PATH = Path.home() / ".agents" / "manifest.json"


def hash_file(path: Path) -> str:
    """Compute SHA-256 hash of a file's contents.

    Args:
        path: Path to the file

    Returns:
        Hex digest of the file's SHA-256 hash
    """
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> dict[str, Any]:
    """Load the manifest file.

    Returns:
        Manifest dict with structure:
        {
            "version": 1,
            "installed": {
                "<runtime>": {
                    "<pack>/<skill>/<filename>": {
                        "source_hash": "...",
                        "installed_hash": "...",
                        "installed_at": "..."
                    }
                }
            }
        }
    """
    if not MANIFEST_PATH.exists():
        return {"version": 1, "installed": {}}

    try:
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "installed": {}}


def save_manifest(manifest: dict[str, Any]) -> None:
    """Save the manifest file.

    Args:
        manifest: Manifest dict to save
    """
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)


def get_installed_entry(
    manifest: dict[str, Any], runtime: str, key: str
) -> dict[str, Any] | None:
    """Get an installed entry from the manifest.

    Args:
        manifest: The manifest dict
        runtime: Runtime name (e.g., 'claude-code')
        key: Entry key (e.g., 'ak-core/plan/SKILL.md')

    Returns:
        Entry dict or None if not found
    """
    return manifest.get("installed", {}).get(runtime, {}).get(key)


def set_installed_entry(
    manifest: dict[str, Any],
    runtime: str,
    key: str,
    source_hash: str,
    installed_hash: str,
) -> None:
    """Set an installed entry in the manifest.

    Args:
        manifest: The manifest dict (modified in place)
        runtime: Runtime name
        key: Entry key
        source_hash: Hash of the source file (from build/)
        installed_hash: Hash of the installed file
    """
    if "installed" not in manifest:
        manifest["installed"] = {}
    if runtime not in manifest["installed"]:
        manifest["installed"][runtime] = {}

    manifest["installed"][runtime][key] = {
        "source_hash": source_hash,
        "installed_hash": installed_hash,
        "installed_at": datetime.now().isoformat(),
    }


class InstallResult:
    """Result of an installation attempt."""

    def __init__(self):
        self.installed: list[str] = []
        self.skipped: list[str] = []
        self.backed_up: list[str] = []
        self.would_install: list[str] = []
        self.would_skip: list[str] = []

    @property
    def total_installed(self) -> int:
        return len(self.installed)

    @property
    def total_skipped(self) -> int:
        return len(self.skipped)

    @property
    def has_skipped(self) -> bool:
        return len(self.skipped) > 0


def check_file_modified(
    manifest: dict[str, Any],
    runtime: str,
    key: str,
    installed_path: Path,
) -> bool:
    """Check if an installed file has been modified by the user.

    Args:
        manifest: The manifest dict
        runtime: Runtime name
        key: Entry key
        installed_path: Path to the installed file

    Returns:
        True if the file exists and has been modified since installation
    """
    if not installed_path.exists():
        return False

    entry = get_installed_entry(manifest, runtime, key)
    if not entry:
        # File exists but we didn't install it - treat as user-created
        return True

    current_hash = hash_file(installed_path)
    installed_hash = entry.get("installed_hash", "")

    # If current hash differs from what we installed, user modified it
    return current_hash != installed_hash
