#!/usr/bin/env python3
"""Privacy-first command line tools for Second Brain Toolkit."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

import yaml

from connect_neurons import IGNORE_DIRS, generate


SCHEMA_VERSION = 1
TOOLKIT_VERSION = "0.2.0"
MODULE_ROOT = Path(__file__).resolve().parent
INSTALLED_ASSET_ROOT = Path(sys.prefix) / "share" / "second-brain-toolkit"
TOOLKIT_ROOT = MODULE_ROOT if (MODULE_ROOT / "AGENTS.md").exists() else INSTALLED_ASSET_ROOT
DEFAULT_HOME = Path(os.environ.get("SECOND_BRAIN_HOME", "~/.second-brain")).expanduser()
REQUIRED_FIELDS = ("title", "description", "type")
RESERVED_MARKDOWN = {
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "index.md",
    "inbox.md",
    "log.md",
}
ISO_WEEK_RE = re.compile(r"^## (\d{4}-W\d{2})$")
LOG_ENTRY_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}): .+")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SECRET_PATTERNS = (
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key block"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "GitHub token-like value"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access-key-like value"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "API-key-like value"),
)
MANAGED_FILES = (
    "AGENTS.md",
    ".foam/templates/new-note.md",
    "workflow/copilot-instructions.md",
    "workflow/project-agents-template.md",
    "workflow/project-template.md",
)


@dataclass(frozen=True)
class Finding:
    level: str
    path: Path
    message: str

    def render(self, root: Path) -> str:
        try:
            location = self.path.relative_to(root)
        except ValueError:
            location = self.path
        return f"{self.level}: {location}: {self.message}"


def iter_markdown(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if any(part in IGNORE_DIRS for part in relative.parts):
            continue
        if relative.parts and relative.parts[0] == "private":
            continue
        yield path


def parse_frontmatter(path: Path) -> tuple[dict | None, str | None]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, "missing YAML frontmatter"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "unclosed YAML frontmatter"
    try:
        parsed = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        return None, f"invalid YAML frontmatter ({exc.problem or 'parse error'})"
    if not isinstance(parsed, dict):
        return None, "frontmatter must be a mapping"
    return parsed, None


def strip_code(line: str) -> str:
    return re.sub(r"`[^`]*`", "", line)


def validate_frontmatter(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_markdown(root):
        if path.name in RESERVED_MARKDOWN:
            continue
        frontmatter, error = parse_frontmatter(path)
        if error:
            findings.append(Finding("ERROR", path, error))
            continue
        for field in REQUIRED_FIELDS:
            value = frontmatter.get(field)
            if not isinstance(value, str) or not value.strip():
                findings.append(Finding("ERROR", path, f"missing required '{field}' value"))
    return findings


def validate_links(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_markdown(root):
        in_fence = False
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence or line.startswith("    "):
                continue
            for raw_target in LINK_RE.findall(strip_code(line)):
                target = raw_target.strip().strip("<>")
                if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                    continue
                target_path = target.split("#", 1)[0]
                if target_path and not (path.parent / target_path).resolve().exists():
                    findings.append(
                        Finding("ERROR", path, f"line {line_number}: broken link to '{target}'")
                    )
    return findings


def section_lines(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return []
    end = next(
        (index for index in range(start, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return lines[start:end]


def validate_projects(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    seen: dict[tuple[str, str], Path] = {}
    projects_dir = root / "projects"
    if not projects_dir.exists():
        return findings

    for project_file in sorted(projects_dir.glob("*/project.md")):
        frontmatter, error = parse_frontmatter(project_file)
        if error:
            findings.append(Finding("ERROR", project_file, error))
            continue
        if not frontmatter.get("repo") and not frontmatter.get("path"):
            findings.append(Finding("ERROR", project_file, "requires a 'repo' or 'path' key"))
        for key in ("repo", "path"):
            value = frontmatter.get(key)
            if not value:
                continue
            identity = (key, str(value))
            if identity in seen:
                findings.append(
                    Finding(
                        "ERROR",
                        project_file,
                        f"duplicate {key} also used by {seen[identity].relative_to(root)}",
                    )
                )
            else:
                seen[identity] = project_file

        for line in section_lines(project_file.read_text(encoding="utf-8"), "## Open items"):
            if re.match(r"^- \[[xX]\]", line):
                findings.append(
                    Finding("ERROR", project_file, "completed task found under 'Open items'")
                )

    for log_file in sorted(projects_dir.glob("*/log.md")):
        for line_number, line in enumerate(log_file.read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith("## "):
                match = ISO_WEEK_RE.fullmatch(line)
                try:
                    if not match:
                        raise ValueError
                    datetime.strptime(f"{match.group(1)}-1", "%G-W%V-%u")
                except ValueError:
                    findings.append(
                        Finding("ERROR", log_file, f"line {line_number}: invalid ISO-week heading")
                    )
            if line.startswith("- "):
                match = LOG_ENTRY_RE.fullmatch(line)
                try:
                    if not match:
                        raise ValueError
                    date.fromisoformat(match.group(1))
                except ValueError:
                    findings.append(
                        Finding("ERROR", log_file, f"line {line_number}: invalid dated log entry")
                    )
    return findings


def validate_config(root: Path) -> list[Finding]:
    config = root / "second-brain.yml"
    if not config.exists():
        return [Finding("WARNING", config, "missing schema configuration")]
    try:
        data = yaml.safe_load(config.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        return [Finding("ERROR", config, f"invalid YAML ({exc.problem or 'parse error'})")]
    if not isinstance(data, dict):
        return [Finding("ERROR", config, "schema configuration must be a mapping")]
    version = data.get("schema_version")
    if version != SCHEMA_VERSION:
        return [
            Finding(
                "ERROR",
                config,
                f"schema_version is {version!r}; toolkit expects {SCHEMA_VERSION}",
            )
        ]
    return []


def validate_secrets(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".yml", ".yaml", ".txt"}:
            continue
        relative = path.relative_to(root)
        if any(part in IGNORE_DIRS for part in relative.parts):
            continue
        if relative.parts and relative.parts[0] == "private":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(Finding("ERROR", path, f"possible secret detected ({label})"))
    return findings


def check_brain(root: Path, include_generated: bool = True) -> list[Finding]:
    findings = (
        validate_config(root)
        + validate_frontmatter(root)
        + validate_links(root)
        + validate_projects(root)
        + validate_secrets(root)
    )
    if include_generated and generate(root, check=True):
        findings.append(Finding("ERROR", root, "generated indexes or weekly logs are stale"))
    return findings


def copy_if_missing(source: Path, destination: Path) -> bool:
    if destination.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True


def frontmatter(data: dict) -> str:
    return "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True) + "---\n"


def require_slug(value: str, label: str) -> str:
    if not SLUG_RE.fullmatch(value):
        raise ValueError(f"{label} must contain lowercase letters, numbers, and hyphens only")
    return value


def project_title(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def initialize_brain(root: Path, initialize_git: bool = False) -> list[Path]:
    root.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for directory in ("projects", "knowledge", "log", "workflow"):
        path = root / directory
        if not path.exists():
            path.mkdir(parents=True)
            created.append(path)

    sources = [
        (TOOLKIT_ROOT / "AGENTS.md", root / "AGENTS.md"),
        (TOOLKIT_ROOT / "inbox.md", root / "inbox.md"),
        (TOOLKIT_ROOT / ".foam/templates/new-note.md", root / ".foam/templates/new-note.md"),
    ]
    sources.extend(
        (source, root / "workflow" / source.name)
        for source in (TOOLKIT_ROOT / "workflow").glob("*.md")
        if source.name != "index.md"
    )
    for source, destination in sources:
        if copy_if_missing(source, destination):
            created.append(destination)

    files = {
        root / "second-brain.yml": (
            "schema_version: 1\n"
            "# This directory contains private user data. Keep its remote private.\n"
        ),
        root / ".gitignore": ".DS_Store\n__pycache__/\n.backups/\n",
        root / "README.md": (
            "# Private Second Brain\n\n"
            "This directory contains personal project memory created by Second Brain Toolkit.\n"
            "Keep any Git remote for this directory private. The surrounding toolkit repository\n"
            "ignores this directory.\n"
        ),
    }
    for destination, content in files.items():
        if not destination.exists():
            destination.write_text(content, encoding="utf-8")
            created.append(destination)

    generate(root)
    if initialize_git and not (root / ".git").exists():
        result = subprocess.run(
            ["git", "init", "-b", "main", str(root)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            subprocess.run(
                ["git", "init", str(root)], check=True, stdout=subprocess.DEVNULL
            )
            subprocess.run(
                ["git", "-C", str(root), "branch", "-M", "main"], check=True
            )
        print("Initialized a separate Git repository for private data.")
    return created


def command_init(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    created = initialize_brain(root, initialize_git=args.git)
    print(f"Second Brain initialized at {root}")
    print(f"Created {len(created)} item(s); existing files were preserved.")
    if args.git:
        print("Before adding a remote, verify that the remote repository is private.")
    return 0


def command_generate(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: data directory does not exist: {root}", file=sys.stderr)
        return 2
    changed = generate(root, check=args.check)
    if args.check and changed:
        print("Generated files are stale.", file=sys.stderr)
        return 1
    print("Generated files are current." if args.check else "Done.")
    return 0


def command_check(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: data directory does not exist: {root}", file=sys.stderr)
        return 2
    findings = check_brain(root, include_generated=not args.skip_generated)
    for finding in findings:
        print(finding.render(root))
    errors = sum(finding.level == "ERROR" for finding in findings)
    warnings = sum(finding.level == "WARNING" for finding in findings)
    if errors or (args.strict and warnings):
        print(f"Check failed: {errors} error(s), {warnings} warning(s).", file=sys.stderr)
        return 1
    print(f"Check passed: {warnings} warning(s).")
    return 0


def command_doctor(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    checks: list[tuple[str, bool, str]] = [
        ("Python 3.10+", sys.version_info >= (3, 10), sys.version.split()[0]),
        ("Git available", shutil.which("git") is not None, shutil.which("git") or "not found"),
        ("Data directory", root.is_dir(), str(root)),
        ("Data directory writable", root.is_dir() and os.access(root, os.W_OK), str(root)),
    ]
    alias = Path("~/.second-brain").expanduser()
    alias_ok = alias.exists() and alias.resolve() == root
    checks.append(("Stable ~/.second-brain path", alias_ok, str(alias)))
    for label, passed, detail in checks:
        print(f"{'OK' if passed else 'WARN'}: {label} ({detail})")
    if not root.is_dir():
        return 1
    return command_check(
        argparse.Namespace(path=str(root), strict=False, skip_generated=False)
    )


def command_new_project(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    if not (root / "second-brain.yml").exists():
        print(f"ERROR: initialize the Second Brain first: {root}", file=sys.stderr)
        return 2
    try:
        slug = require_slug(args.name, "project name")
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not args.repo and not args.local_path:
        print("ERROR: provide --repo or --local-path", file=sys.stderr)
        return 2
    project_dir = root / "projects" / slug
    project_file = project_dir / "project.md"
    if project_file.exists():
        print(f"ERROR: project already exists: {project_file}", file=sys.stderr)
        return 1

    title = args.title or project_title(slug)
    metadata = {
        "title": title,
        "description": args.description or f"Project memory for {title}",
        "type": "project",
    }
    if args.repo:
        metadata["repo"] = args.repo
    if args.local_path:
        metadata["path"] = args.local_path
    metadata["status"] = "active"

    project_dir.mkdir(parents=True)
    (project_dir / "processes").mkdir()
    project_file.write_text(
        frontmatter(metadata)
        + f"\n# {title}\n\n"
        + "## Goal\n\n<Describe why this project exists and for whom.>\n\n"
        + "## Stack and architecture\n\n<Describe the durable technical structure.>\n\n"
        + "## Deployment\n\n<Describe the destination and link to a process when available.>\n\n"
        + "## Decisions\n\n<Add durable decisions with concise rationale.>\n\n"
        + "## Open items\n\n",
        encoding="utf-8",
    )
    (project_dir / "processes.md").write_text(
        frontmatter(
            {
                "title": f"{title} – Process Router",
                "description": f"Entry points for recurring {title} workflows",
                "type": "guide",
            }
        )
        + "\n# Process Router\n\n"
        + "| Trigger | Process | Last verified |\n"
        + "|---|---|---|\n",
        encoding="utf-8",
    )
    (project_dir / "log.md").write_text("", encoding="utf-8")
    generate(root)
    print(f"Created project: {project_file}")
    return 0


def command_new_process(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    if not (root / "second-brain.yml").exists():
        print(f"ERROR: initialize the Second Brain first: {root}", file=sys.stderr)
        return 2
    try:
        project = require_slug(args.project, "project name")
        process = require_slug(args.name, "process name")
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    project_dir = root / "projects" / project
    project_file = project_dir / "project.md"
    if not project_file.exists():
        print(f"ERROR: unknown project: {project}", file=sys.stderr)
        return 1
    project_metadata, error = parse_frontmatter(project_file)
    if error:
        print(f"ERROR: cannot read project metadata: {error}", file=sys.stderr)
        return 1
    if not project_metadata.get("title"):
        print("ERROR: project metadata has no title", file=sys.stderr)
        return 1
    title = args.title or project_title(process)
    process_file = project_dir / "processes" / f"{process}.md"
    if process_file.exists():
        print(f"ERROR: process already exists: {process_file}", file=sys.stderr)
        return 1
    router = project_dir / "processes.md"
    if not router.exists():
        print(f"ERROR: process router does not exist: {router}", file=sys.stderr)
        return 1
    router_text = router.read_text(encoding="utf-8")
    if "|---|---|---|" not in router_text:
        print(f"ERROR: process router has no supported table: {router}", file=sys.stderr)
        return 1
    process_file.parent.mkdir(exist_ok=True)
    process_file.write_text(
        frontmatter(
            {
                "title": f"{project_metadata['title']} – {title}",
                "description": args.description or f"How to perform {title.lower()}",
                "type": "guide",
            }
        )
        + f"\n# {title}\n\n"
        + "## Preconditions\n\n- <Add required access, state, or checks.>\n\n"
        + "## Steps\n\n1. <Add the first exact step.>\n\n"
        + "## Verification\n\n1. <Describe how to confirm success.>\n",
        encoding="utf-8",
    )

    trigger = args.trigger.replace("|", "\\|")
    safe_title = title.replace("|", "\\|")
    row = f"| {trigger} | [{safe_title}](processes/{process}.md) | {date.today().isoformat()} |"
    lines = router_text.rstrip().splitlines()
    insert_at = len(lines)
    for index, line in enumerate(lines):
        if line.startswith("|---"):
            insert_at = index + 1
            while insert_at < len(lines) and lines[insert_at].startswith("|"):
                insert_at += 1
            break
    lines.insert(insert_at, row)
    router.write_text("\n".join(lines) + "\n", encoding="utf-8")
    generate(root)
    print(f"Created process: {process_file}")
    return 0


def command_archive_tasks(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    if not (root / "second-brain.yml").exists():
        print(f"ERROR: initialize the Second Brain first: {root}", file=sys.stderr)
        return 2
    try:
        project = require_slug(args.project, "project name")
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    project_dir = root / "projects" / project
    project_file = project_dir / "project.md"
    if not project_file.exists():
        print(f"ERROR: unknown project: {project}", file=sys.stderr)
        return 1
    metadata, error = parse_frontmatter(project_file)
    if error or not metadata.get("title"):
        print("ERROR: project metadata has no valid title", file=sys.stderr)
        return 1

    lines = project_file.read_text(encoding="utf-8").splitlines()
    in_open_items = False
    completed: list[str] = []
    kept: list[str] = []
    for line in lines:
        if line == "## Open items":
            in_open_items = True
        elif in_open_items and line.startswith("## "):
            in_open_items = False
        if in_open_items and re.match(r"^- \[[xX]\] ", line):
            completed.append(re.sub(r"^- \[[xX]\] ", "", line).strip())
        else:
            kept.append(line)
    if not completed:
        print("No completed tasks found under Open items.")
        return 0

    project_file.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
    archive = project_dir / "completed-items.md"
    if not archive.exists():
        archive.write_text(
            frontmatter(
                {
                    "title": f"{metadata['title']} – Completed Items",
                    "description": "Archived tasks that no longer belong in the active summary",
                    "type": "archive",
                }
            )
            + "\n# Completed Items\n",
            encoding="utf-8",
        )
    project_text = project_file.read_text(encoding="utf-8")
    if "completed-items.md" not in project_text:
        project_file.write_text(
            project_text.rstrip()
            + "\n\n## Archive\n\n- [Completed items](completed-items.md)\n",
            encoding="utf-8",
        )
    with archive.open("a", encoding="utf-8") as handle:
        handle.write("\n" + "\n".join(
            f"- {date.today().isoformat()}: {task}" for task in completed
        ) + "\n")
    generate(root)
    print(f"Archived {len(completed)} completed task(s) in {archive}")
    return 0


def command_upgrade(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: data directory does not exist: {root}", file=sys.stderr)
        return 2
    outdated = []
    for relative in MANAGED_FILES:
        source = TOOLKIT_ROOT / relative
        destination = root / relative
        if not destination.exists() or destination.read_bytes() != source.read_bytes():
            outdated.append((source, destination, Path(relative)))
    config = root / "second-brain.yml"
    config_data: dict = {}
    if config.exists():
        try:
            parsed_config = yaml.safe_load(config.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            print(
                f"ERROR: invalid schema configuration ({exc.problem or 'parse error'})",
                file=sys.stderr,
            )
            return 1
        if not isinstance(parsed_config, dict):
            print("ERROR: schema configuration must be a mapping", file=sys.stderr)
            return 1
        config_data = parsed_config
        current_version = config_data.get("schema_version", 0)
        if isinstance(current_version, int) and current_version > SCHEMA_VERSION:
            print(
                f"ERROR: data schema {current_version} is newer than this toolkit supports",
                file=sys.stderr,
            )
            return 1
    config_findings = validate_config(root)
    if args.check:
        for _, _, relative in outdated:
            print(f"OUTDATED: {relative}")
        for finding in config_findings:
            print(finding.render(root))
        if outdated or config_findings:
            return 1
        print("Managed files and schema are current.")
        return 0

    backup_root = root / ".backups" / datetime.now().strftime("%Y%m%dT%H%M%S%f")
    for source, destination, relative in outdated:
        if destination.exists():
            backup = backup_root / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, backup)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        print(f"Updated managed file: {relative}")
    config_data["schema_version"] = SCHEMA_VERSION
    new_config = yaml.safe_dump(config_data, sort_keys=False)
    if not config.exists() or config.read_text(encoding="utf-8") != new_config:
        if config.exists():
            backup = backup_root / "second-brain.yml"
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(config, backup)
        config.write_text(new_config, encoding="utf-8")
    generate(root)
    if backup_root.exists():
        print(f"Previous managed files were backed up under {backup_root}")
    print("Upgrade complete. Customized working-style.md was preserved.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="second-brain")
    parser.add_argument("--version", action="version", version=f"%(prog)s {TOOLKIT_VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a private Second Brain")
    init_parser.add_argument("path", nargs="?", default=str(DEFAULT_HOME))
    init_parser.add_argument(
        "--git",
        action="store_true",
        help="initialize the data directory as a separate private Git repository",
    )
    init_parser.set_defaults(func=command_init)

    generate_parser = subparsers.add_parser("generate", help="build indexes and weekly logs")
    generate_parser.add_argument("path", nargs="?", default=str(DEFAULT_HOME))
    generate_parser.add_argument("--check", action="store_true")
    generate_parser.set_defaults(func=command_generate)

    check_parser = subparsers.add_parser("check", help="validate a Second Brain")
    check_parser.add_argument("path", nargs="?", default=str(DEFAULT_HOME))
    check_parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    check_parser.add_argument("--skip-generated", action="store_true")
    check_parser.set_defaults(func=command_check)

    doctor_parser = subparsers.add_parser("doctor", help="diagnose installation and data issues")
    doctor_parser.add_argument("path", nargs="?", default=str(DEFAULT_HOME))
    doctor_parser.set_defaults(func=command_doctor)

    project_parser = subparsers.add_parser("new-project", help="create a project memory")
    project_parser.add_argument("name")
    project_parser.add_argument("--title")
    project_parser.add_argument("--description")
    project_parser.add_argument("--repo")
    project_parser.add_argument("--local-path")
    project_parser.add_argument(
        "--path", default=str(DEFAULT_HOME), help="Second Brain data directory"
    )
    project_parser.set_defaults(func=command_new_project)

    process_parser = subparsers.add_parser("new-process", help="add a detailed recurring process")
    process_parser.add_argument("project")
    process_parser.add_argument("name")
    process_parser.add_argument("--trigger", required=True)
    process_parser.add_argument("--title")
    process_parser.add_argument("--description")
    process_parser.add_argument(
        "--path", default=str(DEFAULT_HOME), help="Second Brain data directory"
    )
    process_parser.set_defaults(func=command_new_process)

    archive_parser = subparsers.add_parser(
        "archive-tasks", help="move checked Open items into the completed archive"
    )
    archive_parser.add_argument("project")
    archive_parser.add_argument(
        "--path", default=str(DEFAULT_HOME), help="Second Brain data directory"
    )
    archive_parser.set_defaults(func=command_archive_tasks)

    upgrade_parser = subparsers.add_parser(
        "upgrade", help="update toolkit-managed rules and templates safely"
    )
    upgrade_parser.add_argument("path", nargs="?", default=str(DEFAULT_HOME))
    upgrade_parser.add_argument("--check", action="store_true")
    upgrade_parser.set_defaults(func=command_upgrade)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
