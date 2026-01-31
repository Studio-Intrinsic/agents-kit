#!/usr/bin/env bash
set -euo pipefail

# agents-kit installer
#
# PUBLIC REPO (default):
#   curl -fsSL https://raw.githubusercontent.com/Studio-Intrinsic/agents-kit/main/install.sh | sh
#
# PRIVATE FORK:
#   gh repo clone your-org/agents-kit ~/.agents/repos/agents-kit && ~/.agents/repos/agents-kit/install.sh
#
# Or set AGENTS_REPO_URL:
#   AGENTS_REPO_URL=git@github.com:your-org/agents-kit.git ./install.sh

AGENTS_HOME="${AGENTS_HOME:-$HOME/.agents}"
REPO_URL="${AGENTS_REPO_URL:-https://github.com/Studio-Intrinsic/agents-kit.git}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

main() {
    echo ""
    echo "╔═══════════════════════════════════════╗"
    echo "║     agents-kit installer              ║"
    echo "║     Model-Agnostic Skills Library     ║"
    echo "╚═══════════════════════════════════════╝"
    echo ""

    # Check prerequisites
    log_info "Checking prerequisites..."

    if ! command -v git &> /dev/null; then
        log_error "git is required but not installed"
        exit 1
    fi

    if ! command -v bash &> /dev/null; then
        log_error "bash is required but not installed"
        exit 1
    fi

    log_success "Prerequisites satisfied"

    # Create directory structure
    log_info "Creating directory structure..."
    mkdir -p "$AGENTS_HOME"/{config,repos,build/{claude-code,codex},bin}

    # Detect if running from a cloned repo (for private forks)
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Clone or update repo
    local repo_dir="$AGENTS_HOME/repos/agents-kit"

    # If running from a git repo that isn't the installed location, copy it
    if [[ -d "$script_dir/.git" ]] && [[ "$script_dir" != "$repo_dir" ]]; then
        log_info "Installing from local clone: $script_dir"
        if [[ -d "$repo_dir" ]]; then
            rm -rf "$repo_dir"
        fi
        cp -r "$script_dir" "$repo_dir"
        # Get the remote URL for config
        REPO_URL=$(git -C "$repo_dir" remote get-url origin 2>/dev/null || echo "$REPO_URL")
        log_success "Copied to $repo_dir"
    elif [[ -d "$repo_dir" ]]; then
        log_info "Updating existing installation..."
        git -C "$repo_dir" pull --ff-only || {
            log_warn "Could not update. Using existing version."
        }
    else
        log_info "Cloning agents-kit..."

        # Prefer gh CLI for better auth handling (especially private repos)
        if command -v gh &> /dev/null && [[ "$REPO_URL" == *"github.com"* ]]; then
            # Extract org/repo from URL
            local repo_slug
            repo_slug=$(echo "$REPO_URL" | sed -E 's|.*github.com[:/]||' | sed 's|\.git$||')

            if gh repo clone "$repo_slug" "$repo_dir" 2>/dev/null; then
                log_success "Cloned via GitHub CLI"
            else
                log_warn "gh clone failed, falling back to git..."
                if ! git clone "$REPO_URL" "$repo_dir"; then
                    log_error "Failed to clone repository"
                    log_info "For private repos, try: gh auth login"
                    exit 1
                fi
            fi
        else
            if ! git clone "$REPO_URL" "$repo_dir"; then
                log_error "Failed to clone repository"
                log_info "For private repos:"
                log_info "  1. Install GitHub CLI: brew install gh"
                log_info "  2. Authenticate: gh auth login"
                log_info "  3. Re-run this installer"
                exit 1
            fi
        fi
    fi

    log_success "Repository ready"

    # Create config file
    if [[ ! -f "$AGENTS_HOME/config.yaml" ]]; then
        cat > "$AGENTS_HOME/config.yaml" <<EOF
# agents configuration
version: 1
repos:
  - $repo_dir
default_runtime: claude-code
EOF
        log_success "Created config file"
    fi

    # Create symlink to CLI
    local cli_link="$AGENTS_HOME/bin/agents"
    rm -f "$cli_link"
    ln -s "$repo_dir/scripts/agents" "$cli_link"
    log_success "Created CLI symlink"

    # Render and install
    log_info "Rendering skills..."
    "$repo_dir/scripts/render"

    log_info "Installing skills..."
    "$repo_dir/scripts/install"

    # Add to PATH instructions
    echo ""
    log_success "Installation complete!"
    echo ""

    # Check if already in PATH
    if [[ ":$PATH:" != *":$AGENTS_HOME/bin:"* ]]; then
        echo "Add the following to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
        echo ""
        echo "  export PATH=\"\$PATH:$AGENTS_HOME/bin\""
        echo ""
        echo "Then restart your shell or run:"
        echo ""
        echo "  source ~/.bashrc  # or ~/.zshrc"
        echo ""
    fi

    echo "Available commands:"
    echo "  agents list       - List installed skills"
    echo "  agents render     - Render skills for runtimes"
    echo "  agents install    - Install to Claude Code / Codex"
    echo "  agents validate   - Check skill schemas"
    echo "  agents --help     - Full help"
    echo ""
}

main "$@"
