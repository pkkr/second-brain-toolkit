#!/usr/bin/env bash
# Sets up the Second Brain on a new machine. Idempotent.
set -euo pipefail
cd "$(dirname "$0")"

# 1. Python venv
if [ ! -d .venv ]; then
    python3 -m venv .venv
    echo "venv created."
fi
.venv/bin/pip install --quiet -r requirements.txt

# 2. Agent rules: source of truth is AGENTS.md (tool-neutral standard,
#    read natively by Copilot/Cursor/Codex in the repo). Claude Code
#    gets it globally via the symlink ~/.claude/CLAUDE.md.
mkdir -p "$HOME/.claude"
TARGET="$HOME/.claude/CLAUDE.md"
if [ -e "$TARGET" ] && [ ! -L "$TARGET" ]; then
    cp "$TARGET" "$TARGET.backup-$(date +%Y%m%d%H%M%S)"
    echo "Existing $TARGET backed up."
fi
ln -sf "$PWD/AGENTS.md" "$TARGET"
echo "Agent rules linked: $TARGET -> $PWD/AGENTS.md"

# 3. GitHub Copilot: link user instructions into the VS Code profile.
#    macOS path shown; on Linux use "$HOME/.config/Code/User", on
#    Windows (Git Bash) use "$APPDATA/Code/User".
VSCODE_USER="$HOME/Library/Application Support/Code/User"
if [ -d "$VSCODE_USER" ]; then
    mkdir -p "$VSCODE_USER/prompts"
    ln -sf "$PWD/workflow/copilot-instructions.md" \
        "$VSCODE_USER/prompts/second-brain.instructions.md"
    echo "Copilot instructions linked."
fi

# 4. Build indexes & weekly logs
.venv/bin/python connect_neurons.py

echo ""
echo "Done. Open the folder in VS Code and install the recommended"
echo "extensions (Foam, Python) when prompted."
