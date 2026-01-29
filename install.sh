#!/usr/bin/env bash
set -euo pipefail

# One-line install script for agents-kit
# curl -fsSL https://your-domain/install.sh | sh

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

    # Clone or update repo
    local repo_dir="$AGENTS_HOME/repos/agents-kit"

    if [[ -d "$repo_dir" ]]; then
        log_info "Updating existing installation..."
        git -C "$repo_dir" pull --ff-only || {
            log_warn "Could not update. Using existing version."
        }
    else
        log_info "Cloning agents-kit..."

        # Try to clone (will prompt for auth if private)
        if ! git clone "$REPO_URL" "$repo_dir"; then
            log_error "Failed to clone repository"
            log_info "If this is a private repo, ensure you have access"
            exit 1
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
