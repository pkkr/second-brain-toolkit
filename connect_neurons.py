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

import re
import sys
from pathlib import Path

import yaml

RESERVED = {"index.md", "log.md", "README.md", "CLAUDE.md", "AGENTS.md", "inbox.md"}
IGNORE_DIRS = {".git", ".foam", ".vscode", ".venv", "node_modules", "attachments"}
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


def build_index(directory: Path, root: Path) -> bool:
    """Builds the index.md for a directory and recurses into subfolders.

    Returns whether the directory has an index.md, so the parent only
    links to indexes that actually exist.
    """
    entries = []

    # Subfolders first
    subdirs = sorted(
        d for d in directory.iterdir()
        if d.is_dir() and d.name not in IGNORE_DIRS
    )
    for sub in subdirs:
        if build_index(sub, root):
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
            index_path.unlink()
            print(f"Removed: {index_path.relative_to(root)}")
        return False

    rel_name = directory.relative_to(root).as_posix()
    heading = rel_name if rel_name != "." else root.name

    content = f"# {heading}\n\n" + "\n".join(entries) + "\n"

    # Only write if something changed (keeps git history clean)
    if index_path.exists() and index_path.read_text(encoding="utf-8") == content:
        return True
    index_path.write_text(content, encoding="utf-8")
    print(f"Updated: {index_path.relative_to(root)}")
    return True


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


def write_weekly_logs(root: Path) -> None:
    """Generates one global log per week from the project logs."""
    weeks = collect_weeks(root)
    log_dir = root / "log"
    if weeks:
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
        week_path.write_text(content, encoding="utf-8")
        print(f"Updated: {week_path.relative_to(root)}")

    # Remove generated weeks that no longer have any entries
    if log_dir.is_dir():
        for f in log_dir.glob("*.md"):
            if f.name == "index.md" or f.stem in weeks:
                continue
            if read_frontmatter(f).get("generated"):
                f.unlink()
                print(f"Removed: {f.relative_to(root)}")


if __name__ == "__main__":
    bundle_root = (Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()).resolve()
    write_weekly_logs(bundle_root)
    build_index(bundle_root, bundle_root)
    print("Done.")
