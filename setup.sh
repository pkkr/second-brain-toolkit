#!/usr/bin/env bash
# Installs the public toolkit and connects a separate private data repository.
set -euo pipefail
cd "$(dirname "$0")"

DATA_DIR="$HOME/second-brain"
DRY_RUN=0
LINK_AGENTS=1
INIT_GIT=0
REPLACE_LINKS=0

usage() {
    cat <<'EOF'
Usage: ./setup.sh [options]

Options:
  --data-dir PATH    Private data repository (default: ~/second-brain)
  --init-git         Initialize the private data directory as its own Git repo
  --no-agent-links   Do not configure Claude Code or GitHub Copilot links
  --replace-links    Replace existing agent symlinks that point elsewhere
  --dry-run          Show the planned locations without changing anything
  -h, --help         Show this help
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --data-dir)
            [ "$#" -ge 2 ] || { echo "ERROR: --data-dir needs a path" >&2; exit 2; }
            DATA_DIR="$2"
            shift 2
            ;;
        --init-git)
            INIT_GIT=1
            shift
            ;;
        --no-agent-links)
            LINK_AGENTS=0
            shift
            ;;
        --replace-links)
            REPLACE_LINKS=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "ERROR: unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

case "$DATA_DIR" in
    /*) ;;
    ~*) DATA_DIR="${DATA_DIR/#\~/$HOME}" ;;
    *) DATA_DIR="$PWD/$DATA_DIR" ;;
esac

ALIAS_PATH="$HOME/.second-brain"

if [ "$DRY_RUN" -eq 1 ]; then
    echo "Toolkit: $PWD"
    echo "Private data: $DATA_DIR"
    echo "Stable data path: $ALIAS_PATH -> $DATA_DIR"
    if [ "$LINK_AGENTS" -eq 1 ]; then
        echo "Agent links: enabled"
    else
        echo "Agent links: disabled"
    fi
    echo "Private Git repository: $([ "$INIT_GIT" -eq 1 ] && echo enabled || echo disabled)"
    exit 0
fi

# 1. Python environment
if [ ! -d .venv ]; then
    python3 -m venv .venv
    echo "Created Python environment."
fi
if [ -x .venv/bin/python ]; then
    PYTHON="$PWD/.venv/bin/python"
elif [ -x .venv/Scripts/python.exe ]; then
    PYTHON="$PWD/.venv/Scripts/python.exe"
else
    echo "ERROR: could not find the virtual-environment Python executable" >&2
    exit 1
fi
"$PYTHON" -m pip install --quiet --editable .
chmod +x second-brain

resolved_path() {
    "$PYTHON" -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$1"
}

# 2. Refuse conflicting data locations before creating any private files
if [ -L "$ALIAS_PATH" ]; then
    CURRENT_TARGET="$(readlink "$ALIAS_PATH")"
    if [ "$(resolved_path "$ALIAS_PATH")" != "$(resolved_path "$DATA_DIR")" ] \
        && [ "$REPLACE_LINKS" -ne 1 ]; then
        echo "ERROR: $ALIAS_PATH already points to $CURRENT_TARGET" >&2
        echo "Re-run with --replace-links only after verifying the old location." >&2
        exit 1
    fi
elif [ -e "$ALIAS_PATH" ]; then
    echo "ERROR: $ALIAS_PATH already exists and is not a symlink." >&2
    echo "Move or migrate it explicitly; setup will not replace personal data." >&2
    exit 1
fi

# 3. Private data, kept in a separate repository by default
INIT_ARGS=(init "$DATA_DIR")
if [ "$INIT_GIT" -eq 1 ]; then
    INIT_ARGS+=(--git)
fi
"$PYTHON" second_brain.py "${INIT_ARGS[@]}"

# 4. Stable path used by agent instructions and project repositories
ln -sfn "$DATA_DIR" "$ALIAS_PATH"
echo "Stable data path: $ALIAS_PATH -> $DATA_DIR"

link_agent_file() {
    local source="$1"
    local target="$2"
    local label="${3:-File}"
    mkdir -p "$(dirname "$target")"
    if [ -L "$target" ]; then
        local current
        current="$(readlink "$target")"
        if [ "$(resolved_path "$target")" != "$(resolved_path "$source")" ] \
            && [ "$REPLACE_LINKS" -ne 1 ]; then
            echo "Skipped existing symlink: $target -> $current"
            return
        fi
    elif [ -e "$target" ]; then
        if [ "$REPLACE_LINKS" -ne 1 ]; then
            echo "Skipped existing file: $target"
            return
        fi
        local backup="$target.backup-$(date +%Y%m%d%H%M%S)"
        cp "$target" "$backup"
        echo "Backed up existing file: $backup"
    fi
    ln -sfn "$source" "$target"
    echo "$label linked: $target"
}

link_agent_file \
    "$PWD/second-brain" \
    "${XDG_BIN_HOME:-$HOME/.local/bin}/second-brain" \
    "Command"

# 5. Optional tool adapters
if [ "$LINK_AGENTS" -eq 1 ]; then
    link_agent_file "$PWD/AGENTS.md" "$HOME/.claude/CLAUDE.md" "Claude instructions"

    VSCODE_USER=""
    case "$(uname -s)" in
        Darwin) VSCODE_USER="$HOME/Library/Application Support/Code/User" ;;
        Linux) VSCODE_USER="${XDG_CONFIG_HOME:-$HOME/.config}/Code/User" ;;
        MINGW*|MSYS*|CYGWIN*) VSCODE_USER="${APPDATA:-}/Code/User" ;;
    esac
    if [ -n "$VSCODE_USER" ] && [ -d "$VSCODE_USER" ]; then
        link_agent_file \
            "$PWD/workflow/copilot-instructions.md" \
            "$VSCODE_USER/prompts/second-brain.instructions.md" \
            "Copilot instructions"
    else
        echo "VS Code user directory not found; Copilot link skipped."
    fi
fi

"$PYTHON" second_brain.py doctor "$DATA_DIR"
if ! "$PYTHON" second_brain.py upgrade "$DATA_DIR" --check; then
    echo "Toolkit-managed files have updates available."
    echo "Review and apply them with: second-brain upgrade"
fi

echo
echo "Done. Personal data stays in: $DATA_DIR"
echo "The public toolkit repository does not track that directory."
if [ "$INIT_GIT" -eq 1 ]; then
    echo "Only connect the private data repository to a private remote."
fi
