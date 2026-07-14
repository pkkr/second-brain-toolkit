#!/usr/bin/env bash
# Installs the public toolkit and connects a separate private data repository.
set -euo pipefail
cd "$(dirname "$0")"

DATA_DIR="$HOME/second-brain"
DATA_MODE=""
DRY_RUN=0
LINK_AGENTS=1
INIT_GIT=0
REPLACE_LINKS=0

usage() {
    cat <<'EOF'
Usage: ./setup.sh [options]

Options:
  --data-dir PATH    Private data repository (default: ~/second-brain)
  --data-mode MODE   Data location mode: symlink or move (prompts by default)
  --init-git         Initialize the private data directory as its own Git repo
  --no-agent-links   Do not configure Claude Code or GitHub Copilot links
  --replace-links    Replace existing symlinks that point elsewhere
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
        --data-mode)
            [ "$#" -ge 2 ] || { echo "ERROR: --data-mode needs symlink or move" >&2; exit 2; }
            DATA_MODE="$2"
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

case "$DATA_MODE" in
    ""|symlink|move) ;;
    *)
        echo "ERROR: --data-mode must be symlink or move" >&2
        exit 2
        ;;
esac

case "$DATA_DIR" in
    /*) ;;
    ~*) DATA_DIR="${DATA_DIR/#\~/$HOME}" ;;
    *) DATA_DIR="$PWD/$DATA_DIR" ;;
esac

ALIAS_PATH="$HOME/.second-brain"
SOURCE_DATA_DIR="$DATA_DIR"

if [ "$DRY_RUN" -eq 1 ]; then
    echo "Toolkit: $PWD"
    if [ -z "$DATA_MODE" ]; then
        echo "Data mode: interactive choice (non-interactive default: symlink)"
        echo "Symlink choice: $ALIAS_PATH -> $DATA_DIR"
        echo "Move choice: $DATA_DIR -> $ALIAS_PATH"
    elif [ "$DATA_MODE" = "symlink" ]; then
        echo "Data mode: symlink"
        echo "Private data: $DATA_DIR"
        echo "Stable data path: $ALIAS_PATH -> $DATA_DIR"
    else
        echo "Data mode: move"
        echo "Private data: $ALIAS_PATH"
        echo "Move source: $DATA_DIR"
    fi
    if [ "$LINK_AGENTS" -eq 1 ]; then
        echo "Agent links: enabled"
    else
        echo "Agent links: disabled"
    fi
    echo "Private Git repository: $([ "$INIT_GIT" -eq 1 ] && echo enabled || echo disabled)"
    exit 0
fi

if [ -z "$DATA_MODE" ]; then
    if [ -t 0 ]; then
        echo "Choose where the private Second Brain data should live:"
        echo "  1) Keep it at $DATA_DIR and create $ALIAS_PATH as a symlink (recommended)"
        echo "  2) Move or initialize it directly at $ALIAS_PATH"
        while :; do
            printf "Selection [1]: "
            if ! IFS= read -r SELECTION; then
                SELECTION=""
            fi
            case "$SELECTION" in
                ""|1|symlink)
                    DATA_MODE="symlink"
                    break
                    ;;
                2|move)
                    DATA_MODE="move"
                    break
                    ;;
                *) echo "Please enter 1 or 2." ;;
            esac
        done
    else
        DATA_MODE="symlink"
        echo "No interactive terminal detected; using the recommended symlink mode."
        echo "Use --data-mode move to store data directly at $ALIAS_PATH."
    fi
fi

resolved_path() {
    python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$1"
}

legacy_layout_at() {
    [ -d "$1/projekte" ] || [ -f "$1/workflow/vorgehen.md" ]
}

LEGACY_PATH=""
if legacy_layout_at "$SOURCE_DATA_DIR"; then
    LEGACY_PATH="$SOURCE_DATA_DIR"
elif [ -e "$ALIAS_PATH" ] && legacy_layout_at "$ALIAS_PATH"; then
    LEGACY_PATH="$ALIAS_PATH"
fi
if [ -n "$LEGACY_PATH" ]; then
    echo "ERROR: legacy German data layout detected at $LEGACY_PATH" >&2
    echo "Preview the migration before running setup:" >&2
    echo "  $PWD/second-brain migrate-legacy \"$LEGACY_PATH\" --remove-legacy-tools" >&2
    echo "After committing the data repo, apply it with --apply and re-run setup." >&2
    exit 1
fi

# Refuse every data-location conflict before creating the Python environment.
if [ "$DATA_MODE" = "symlink" ]; then
    if [ "$SOURCE_DATA_DIR" = "$ALIAS_PATH" ]; then
        echo "ERROR: symlink mode needs --data-dir to differ from $ALIAS_PATH" >&2
        exit 1
    fi
    if [ -e "$SOURCE_DATA_DIR" ] && [ ! -d "$SOURCE_DATA_DIR" ]; then
        echo "ERROR: the private data source is not a directory: $SOURCE_DATA_DIR" >&2
        exit 1
    fi
    if [ -L "$ALIAS_PATH" ]; then
        CURRENT_TARGET="$(readlink "$ALIAS_PATH")"
        if [ "$(resolved_path "$ALIAS_PATH")" != "$(resolved_path "$SOURCE_DATA_DIR")" ] \
            && [ "$REPLACE_LINKS" -ne 1 ]; then
            echo "ERROR: $ALIAS_PATH already points to $CURRENT_TARGET" >&2
            echo "Re-run with --replace-links only after verifying the old location." >&2
            exit 1
        fi
    elif [ -e "$ALIAS_PATH" ]; then
        echo "ERROR: $ALIAS_PATH already contains data and cannot become a symlink." >&2
        echo "Use --data-mode move if that directory is the intended data repository." >&2
        exit 1
    fi
else
    if [ -e "$SOURCE_DATA_DIR" ] && [ ! -d "$SOURCE_DATA_DIR" ]; then
        echo "ERROR: the private data source is not a directory: $SOURCE_DATA_DIR" >&2
        exit 1
    fi
    if [ -L "$SOURCE_DATA_DIR" ] && [ "$SOURCE_DATA_DIR" != "$ALIAS_PATH" ]; then
        echo "ERROR: move mode will not move a source that is itself a symlink: $SOURCE_DATA_DIR" >&2
        exit 1
    fi
    if [ -L "$ALIAS_PATH" ]; then
        if [ "$(resolved_path "$ALIAS_PATH")" != "$(resolved_path "$SOURCE_DATA_DIR")" ]; then
            echo "ERROR: $ALIAS_PATH points to a different data location." >&2
            echo "Setup will not replace or merge unrelated personal data." >&2
            exit 1
        fi
    elif [ -e "$ALIAS_PATH" ] && [ -e "$SOURCE_DATA_DIR" ] \
        && [ "$(resolved_path "$ALIAS_PATH")" != "$(resolved_path "$SOURCE_DATA_DIR")" ]; then
        echo "ERROR: both $SOURCE_DATA_DIR and $ALIAS_PATH contain data." >&2
        echo "Setup will not merge or overwrite private repositories." >&2
        exit 1
    fi
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

# 2. Apply the selected private-data location without merging or overwriting.
if [ "$DATA_MODE" = "move" ]; then
    MOVE_SOURCE="$(resolved_path "$SOURCE_DATA_DIR")"
    if [ -L "$ALIAS_PATH" ]; then
        unlink "$ALIAS_PATH"
    fi
    if [ -e "$ALIAS_PATH" ]; then
        DATA_DIR="$ALIAS_PATH"
    elif [ -e "$MOVE_SOURCE" ]; then
        mv "$MOVE_SOURCE" "$ALIAS_PATH"
        DATA_DIR="$ALIAS_PATH"
        echo "Moved private data: $MOVE_SOURCE -> $ALIAS_PATH"
    else
        DATA_DIR="$ALIAS_PATH"
    fi
else
    DATA_DIR="$SOURCE_DATA_DIR"
fi

# 3. Private data, kept in a separate repository by default
INIT_ARGS=(init "$DATA_DIR")
if [ "$INIT_GIT" -eq 1 ]; then
    INIT_ARGS+=(--git)
fi
"$PYTHON" second_brain.py "${INIT_ARGS[@]}"

# 4. Stable path used by agent instructions and project repositories
if [ "$DATA_MODE" = "symlink" ]; then
    ln -sfn "$DATA_DIR" "$ALIAS_PATH"
    echo "Stable data path: $ALIAS_PATH -> $DATA_DIR"
else
    echo "Private data stored directly at: $ALIAS_PATH"
fi

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
echo "Done. Personal data is in: $DATA_DIR"
echo "The public toolkit repository does not track that directory."
if [ "$INIT_GIT" -eq 1 ]; then
    echo "Only connect the private data repository to a private remote."
fi
