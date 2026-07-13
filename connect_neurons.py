#!/usr/bin/env python3
"""
Generates OKF-compliant index.md files for a Second Brain bundle.

Walks all folders recursively, reads title/description/type from each
note's YAML frontmatter, and writes one index.md per folder with
standard Markdown links. Also rolls up per-project weekly logs into a
global log/ folder.

Usage:
    pip install pyyaml
    python connect_neurons.py [path-to-bundle]   # default: current directory
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

RESERVED = {"index.md", "log.md", "README.md", "CLAUDE.md", "AGENTS.md", "inbox.md"}
IGNORE_DIRS = {
    ".git",
    ".backups",
    ".foam",
    ".vscode",
    ".venv",
    "node_modules",
    "attachments",
}
WEEK_RE = re.compile(r"^\d{4}-W\d{2}$")


def read_frontmatter(path: Path) -> dict:
    """Reads the YAML frontmatter block of a Markdown file."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def build_index(directory: Path, root: Path, check: bool = False) -> tuple[bool, bool]:
    """Builds the index.md for a directory and recurses into subfolders.

    Returns whether the directory has an index and whether generated
    output is stale, so callers can use the same logic for write and
    check-only modes.
    """
    entries = []

    # Subfolders first
    subdirs = sorted(
        d for d in directory.iterdir()
        if d.is_dir()
        and d.name not in IGNORE_DIRS
        and not (directory == root and d.name == "private")
    )
    changed = False
    for sub in subdirs:
        has_index, sub_changed = build_index(sub, root, check=check)
        changed = changed or sub_changed
        if has_index:
            entries.append(f"- [{sub.name}/]({sub.name}/index.md)")

    # Content files
    files = sorted(
        f for f in directory.glob("*.md")
        if f.name not in RESERVED
    )
    for f in files:
        fm = read_frontmatter(f)
        title = fm.get("title") or f.stem
        desc = fm.get("description") or ""
        ctype = fm.get("type")
        label = f"- [{title}]({f.name})"
        if ctype:
            label += f" *({ctype})*"
        if desc:
            label += f" — {desc}"
        entries.append(label)

        if not fm.get("type"):
            rel = f.relative_to(root)
            print(f"WARNING: {rel} has no 'type' field (not OKF-compliant)")

    index_path = directory / "index.md"

    # No content left: clean up a stale index.md
    if not entries:
        if index_path.exists():
            changed = True
            if check:
                print(f"STALE: remove {index_path.relative_to(root)}")
            else:
                index_path.unlink()
                print(f"Removed: {index_path.relative_to(root)}")
        return False, changed

    rel_name = directory.relative_to(root).as_posix()
    heading = rel_name if rel_name != "." else root.name

    content = f"# {heading}\n\n" + "\n".join(entries) + "\n"

    # Only write if something changed (keeps git history clean)
    if index_path.exists() and index_path.read_text(encoding="utf-8") == content:
        return True, changed
    changed = True
    if check:
        print(f"STALE: update {index_path.relative_to(root)}")
    else:
        index_path.write_text(content, encoding="utf-8")
        print(f"Updated: {index_path.relative_to(root)}")
    return True, changed


def collect_weeks(root: Path) -> dict:
    """Collects bullets from all project logs, grouped by week and project."""
    weeks: dict[str, dict[str, list[str]]] = {}
    for log_path in sorted((root / "projects").glob("*/log.md")):
        fm = read_frontmatter(log_path.parent / "project.md")
        project = fm.get("title") or log_path.parent.name
        week = None
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                heading = line[3:].strip()
                week = heading if WEEK_RE.match(heading) else None
            elif week and line.lstrip().startswith("-"):
                weeks.setdefault(week, {}).setdefault(project, []).append(line.rstrip())
    return weeks


def write_weekly_logs(root: Path, check: bool = False) -> bool:
    """Generates one global log per week from the project logs."""
    changed = False
    weeks = collect_weeks(root)
    log_dir = root / "log"
    if weeks and not check:
        log_dir.mkdir(exist_ok=True)

    for week, projects in weeks.items():
        sections = []
        for project in sorted(projects):
            sections.append(f"## {project}\n\n" + "\n".join(projects[project]))
        content = (
            "---\n"
            f"title: {week}\n"
            "description: Weekly log – auto-generated from project logs\n"
            "type: log\n"
            "generated: true\n"
            "---\n\n"
            f"# {week}\n\n" + "\n\n".join(sections) + "\n"
        )
        week_path = log_dir / f"{week}.md"
        if week_path.exists() and week_path.read_text(encoding="utf-8") == content:
            continue
        changed = True
        if check:
            print(f"STALE: update {week_path.relative_to(root)}")
        else:
            week_path.write_text(content, encoding="utf-8")
            print(f"Updated: {week_path.relative_to(root)}")

    # Remove generated weeks that no longer have any entries
    if log_dir.is_dir():
        for f in log_dir.glob("*.md"):
            if f.name == "index.md" or f.stem in weeks:
                continue
            if read_frontmatter(f).get("generated"):
                changed = True
                if check:
                    print(f"STALE: remove {f.relative_to(root)}")
                else:
                    f.unlink()
                    print(f"Removed: {f.relative_to(root)}")
    return changed


def generate(root: Path, check: bool = False) -> bool:
    """Generates derived files and returns whether changes were needed."""
    logs_changed = write_weekly_logs(root, check=check)
    _, indexes_changed = build_index(root, root, check=check)
    return logs_changed or indexes_changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate indexes and weekly logs for a Second Brain."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Second Brain data directory (default: current directory)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report stale generated files without modifying them",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    bundle_root = Path(args.path).expanduser().resolve()
    if not bundle_root.is_dir():
        print(f"ERROR: data directory does not exist: {bundle_root}", file=sys.stderr)
        raise SystemExit(2)
    changed = generate(bundle_root, check=args.check)
    if args.check and changed:
        print("Generated files are stale.", file=sys.stderr)
        raise SystemExit(1)
    print("Generated files are current." if args.check else "Done.")
