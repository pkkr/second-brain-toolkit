#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEMP_ROOT"' EXIT

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

run_setup() {
    local home="$1"
    shift
    HOME="$home" XDG_BIN_HOME="$home/bin" \
        "$ROOT/setup.sh" --no-agent-links "$@" >/dev/null
}

SYMLINK_HOME="$TEMP_ROOT/symlink"
mkdir -p "$SYMLINK_HOME"
run_setup "$SYMLINK_HOME" --data-mode symlink
[ -L "$SYMLINK_HOME/.second-brain" ] || fail "symlink mode did not create the stable link"
[ "$(readlink "$SYMLINK_HOME/.second-brain")" = "$SYMLINK_HOME/second-brain" ] \
    || fail "stable link points to the wrong directory"
run_setup "$SYMLINK_HOME" --data-mode symlink
[ -L "$SYMLINK_HOME/.second-brain" ] || fail "symlink mode is not idempotent"

MOVE_HOME="$TEMP_ROOT/move"
mkdir -p "$MOVE_HOME/second-brain"
touch "$MOVE_HOME/second-brain/preserved-marker"
git -C "$MOVE_HOME/second-brain" init -q
run_setup "$MOVE_HOME" --data-mode move
[ ! -e "$MOVE_HOME/second-brain" ] || fail "move mode left the source directory behind"
[ -d "$MOVE_HOME/.second-brain" ] && [ ! -L "$MOVE_HOME/.second-brain" ] \
    || fail "move mode did not create a physical data directory"
[ -f "$MOVE_HOME/.second-brain/preserved-marker" ] || fail "move mode lost existing data"
git -C "$MOVE_HOME/.second-brain" rev-parse --is-inside-work-tree >/dev/null \
    || fail "move mode did not preserve the private Git repository"
run_setup "$MOVE_HOME" --data-mode move
[ -d "$MOVE_HOME/.second-brain" ] && [ ! -L "$MOVE_HOME/.second-brain" ] \
    || fail "move mode is not idempotent"

CONVERT_HOME="$TEMP_ROOT/convert"
mkdir -p "$CONVERT_HOME/second-brain"
touch "$CONVERT_HOME/second-brain/preserved-marker"
ln -s "$CONVERT_HOME/second-brain" "$CONVERT_HOME/.second-brain"
run_setup "$CONVERT_HOME" --data-mode move
[ ! -e "$CONVERT_HOME/second-brain" ] || fail "symlink conversion left the source behind"
[ -d "$CONVERT_HOME/.second-brain" ] && [ ! -L "$CONVERT_HOME/.second-brain" ] \
    || fail "symlink conversion did not produce a physical directory"
[ -f "$CONVERT_HOME/.second-brain/preserved-marker" ] \
    || fail "symlink conversion lost existing data"

CONFLICT_HOME="$TEMP_ROOT/conflict"
mkdir -p "$CONFLICT_HOME/second-brain" "$CONFLICT_HOME/.second-brain"
touch "$CONFLICT_HOME/second-brain/source-marker" "$CONFLICT_HOME/.second-brain/target-marker"
if run_setup "$CONFLICT_HOME" --data-mode move 2>/dev/null; then
    fail "move mode accepted two existing data directories"
fi
[ -f "$CONFLICT_HOME/second-brain/source-marker" ] \
    && [ -f "$CONFLICT_HOME/.second-brain/target-marker" ] \
    || fail "conflict handling changed existing data"

echo "setup.sh data-location tests passed"
