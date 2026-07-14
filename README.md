# Second Brain Toolkit

A privacy-first, tool-neutral memory system for coding agents. It keeps
durable project context in plain Markdown so decisions, recurring
workflows, active tasks, and lessons survive across sessions, tools, and
machines.

The toolkit is local-first: there is no server, account, proprietary
database, or required cloud service. It works with any editor, uses
[Foam](https://foambubble.github.io/foam/) as an optional editing layer,
and follows [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
conventions for Markdown and YAML frontmatter.

## Contents

- [Features](#features)
- [How the pieces fit together](#how-the-pieces-fit-together)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Installer options](#installer-options)
- [Create the first project memory](#create-the-first-project-memory)
- [Record a recurring workflow](#record-a-recurring-workflow)
- [Recommended daily workflow](#recommended-daily-workflow)
- [Private data layout](#private-data-layout)
- [Note and metadata conventions](#note-and-metadata-conventions)
- [Command-line reference](#command-line-reference)
- [What validation checks](#what-validation-checks)
- [Managed upgrades](#managed-upgrades)
- [Migrating existing data](#migrating-existing-data)
- [Agent integrations](#agent-integrations)
- [Multiple machines](#multiple-machines)
- [Privacy and security](#privacy-and-security)
- [Development](#development)

## Features

- **Durable project memory:** one compact source of truth for project
  goals, architecture, decisions, deployment context, and active work.
- **Automatic project lookup:** agents identify the current project by
  its Git remote, with its local path as a fallback.
- **Progressive context loading:** routine sessions load only the
  relevant project summary and process router, not the complete archive.
- **Recurring workflow routing:** short process indexes lead to detailed,
  independently maintained instructions for deploys, releases, backups,
  migrations, and similar operations.
- **Selective write-back:** noteworthy decisions, released outcomes,
  changed workflows, and unresolved risks are retained without copying
  ordinary Git history into the knowledge base.
- **Inbox capture:** unsorted thoughts and tasks can be recorded quickly
  and assigned to the right project later.
- **Generated navigation:** folder indexes and cross-project weekly logs
  are built from the source notes.
- **Structural validation:** the CLI checks metadata, links, project
  identity, task placement, log dates, schema compatibility, generated
  output, and common secret-like values.
- **Safe task archiving:** checked tasks leave the active project context
  while remaining searchable in a completed-items archive.
- **Managed upgrades:** shared rules and templates can be updated from
  the public toolkit with timestamped backups; personal working-style
  customizations are preserved.
- **Legacy migration:** the original German data layout can be previewed
  and migrated without translating or discarding domain prose.
- **Agent adapters:** optional bridges are included for Claude Code and
  GitHub Copilot; repository-level `AGENTS.md` files support Codex,
  Cursor, and other instruction-aware agents.
- **Privacy by architecture:** public tooling and private memory remain
  separate Git repositories.

## How the pieces fit together

The installation has three independent parts:

| Part | Purpose | Typical location |
|---|---|---|
| Public toolkit | CLI, installer, rules, templates, examples, tests | `~/second-brain-toolkit` |
| Private data repository | Personal projects, knowledge, inbox, and logs | `~/second-brain` or `~/.second-brain` |
| Stable data path | Location used by agent and project instructions | Always `~/.second-brain` |

The private repository can remain at a visible path such as
`~/second-brain`, with `~/.second-brain` pointing to it, or it can live
physically at `~/.second-brain`. Both modes expose the same stable path
to agents. Personal data is never added to the public toolkit history.

## Requirements

- Python 3.10 or newer
- Bash and a POSIX-style environment
- macOS or Linux; WSL is recommended on Windows
- Git, strongly recommended for private history and multi-machine sync

The Python CLI itself can also be installed manually on Windows, but the
Bash installer targets macOS, Linux, and WSL.

## Quick start

```bash
git clone https://github.com/pkkr/second-brain-toolkit.git ~/second-brain-toolkit
cd ~/second-brain-toolkit
./install.sh
```

The interactive installer:

1. Asks where the private data should live.
2. Creates a local `.venv` and installs the toolkit in editable mode.
3. Initializes or reuses the private data repository without replacing
   existing notes.
4. Exposes it through the stable `~/.second-brain` path.
5. Links the `second-brain` command under
   `${XDG_BIN_HOME:-$HOME/.local/bin}`.
6. Optionally installs agent-tool bridges.
7. Runs installation diagnostics and checks for managed-file updates.

Choose one of the two data-location modes:

```text
1) Keep the data at ~/second-brain and create ~/.second-brain as a symlink
2) Move or initialize the data repository directly at ~/.second-brain
```

Symlink mode is recommended because the physical repository location
remains obvious. Direct mode is useful when `~/.second-brain` should be
the actual repository. The installer never merges two existing data
directories or overwrites an unrelated data target.

Verify the result:

```bash
second-brain doctor
second-brain check --strict
```

If the command is not found, add its directory to `PATH`:

```bash
export PATH="${XDG_BIN_HOME:-$HOME/.local/bin}:$PATH"
```

### Manual CLI installation

Use `pipx` when only the CLI and managed assets are needed:

```bash
git clone https://github.com/pkkr/second-brain-toolkit.git ~/second-brain-toolkit
pipx install ~/second-brain-toolkit
second-brain init ~/.second-brain --git
second-brain doctor
```

Alternatively, install into a dedicated virtual environment with
`python -m pip install .`. Manual installation does not create the
stable data symlink or agent-tool adapters provided by `install.sh`;
`pipx` exposes the CLI through its own bin directory. The example above
stores data directly at the stable path.

## Installer options

Preview everything without changing the filesystem:

```bash
./install.sh --dry-run
```

For unattended installs, select the location mode explicitly:

```bash
./install.sh --data-mode symlink
./install.sh --data-mode move
```

All installer options:

| Option | Effect |
|---|---|
| `--data-dir PATH` | Select the source/private repository; defaults to `~/second-brain` |
| `--data-mode symlink` | Keep the source directory and link `~/.second-brain` to it |
| `--data-mode move` | Move or initialize the physical repository at `~/.second-brain` |
| `--init-git` | Initialize the private data directory as a separate Git repository |
| `--no-agent-links` | Leave Claude Code and Copilot user configuration untouched |
| `--replace-links` | Replace conflicting tool symlinks; regular adapter files are backed up first |
| `--dry-run` | Show paths and choices without installing or moving anything |

Examples:

```bash
# Recommended installation with a separate private Git history
./install.sh --data-mode symlink --init-git

# Use a custom physical data location
./install.sh --data-dir ~/Documents/agent-memory --data-mode symlink

# Keep every agent-tool integration manual
./install.sh --no-agent-links

# Local-only fallback inside the toolkit checkout; /private is Git-ignored
./install.sh --data-dir ./private --data-mode symlink
```

`--replace-links` does not authorize data-directory merging. If both the
selected source and `~/.second-brain` contain data, installation stops before
creating the Python environment or changing either directory.

## Create the first project memory

Project and process names are slugs containing lowercase letters,
numbers, and hyphens.

Create a project from its Git identity and local path:

```bash
second-brain new-project example-app \
  --title "Example App" \
  --description "Durable context for the Example App" \
  --repo git@github.com:example-org/example-app.git \
  --local-path ~/code/example-app
```

At least `--repo` or `--local-path` is required. Supplying both makes
lookup reliable when the repository is moved or checked out differently
on another machine.

The command creates:

```text
projects/example-app/
├── project.md
├── processes.md
├── processes/
└── log.md
```

Fill in the placeholders in `project.md`, especially:

- Goal
- Stack and architecture
- Deployment destination
- Durable decisions and their rationale
- Active, unchecked tasks under `Open items`

Then add a small `AGENTS.md` to the source repository using
[`workflow/project-agents-template.md`](workflow/project-agents-template.md).
Replace `<name>` with `example-app`. This gives repository-aware agents a
stable pointer to the private context without copying that context into
the project repository.

The filled-in
[`examples/second-brain/projects/example-project/`](examples/second-brain/projects/example-project/)
directory demonstrates the complete format inside a self-contained
sample data repository.

## Record a recurring workflow

Create a detailed workflow and register it in the project's process
router:

```bash
second-brain new-process example-app deploy \
  --trigger "Deploy the application" \
  --title "Deploy" \
  --description "How to deploy Example App safely"
```

This creates `projects/example-app/processes/deploy.md` with sections
for preconditions, exact steps, and verification. It also adds a dated
row to `processes.md`.

Keep `processes.md` short. Its job is to tell an agent which detailed
file to load for a specific trigger. Update the process and its
`Last verified` date when the real procedure changes.

## Recommended daily workflow

### Start work

An instruction-aware agent should:

1. Read the general working style.
2. Identify the active project from its Git remote or local path.
3. Load the project's frontmatter, goal, architecture, decisions, and
   open items.
4. Read the compact process router.
5. Open only the process, linked note, or recent history relevant to the
   current task.

This progressive-loading rule is the core context optimization: full
logs, completed-item archives, unrelated projects, generated indexes,
and every linked note are not loaded preemptively.

### Capture an idea quickly

Add one bullet to `~/.second-brain/inbox.md`:

```markdown
- Check whether the release process should include a rollback test.
```

When the item can be assigned confidently, move a task into the
project's `Open items` or durable knowledge into an appropriate note,
then remove only the processed inbox line.

### Maintain active tasks

Keep only active tasks in the project summary:

```markdown
## Open items

- [ ] Add rollback verification to the release workflow
```

If tasks were checked manually, archive them with:

```bash
second-brain archive-tasks example-app
```

The command removes checked items from active context and appends them,
with the current date, to `completed-items.md`.

### Record durable progress

For a noteworthy session, add at most one to three concise entries to
the project `log.md`:

```markdown
## 2026-W29

- 2026-07-14: Release verification now includes an explicit rollback test.
```

Log decisions and rationale, user-visible released outcomes, incidents
and lessons, changed recurring workflows, or risks that matter to a
future session. Do not duplicate routine commit messages, test output,
or transient implementation details.

### Regenerate and validate

After structural changes or log edits:

```bash
second-brain generate
second-brain check --strict
```

Commit the private repository independently from the source project and
the public toolkit.

## Private data layout

`second-brain init` and `install.sh` create only missing files and preserve
existing notes.

| Location | Contents |
|---|---|
| `AGENTS.md` | Shared context-loading and write-back rules for agents |
| `README.md` | Short privacy notice for the private repository |
| `inbox.md` | Quick capture for unsorted thoughts and tasks |
| `second-brain.yml` | Data schema version |
| `workflow/working-style.md` | Personal preferences that apply across projects |
| `workflow/project-template.md` | Core project-note template |
| `workflow/project-agents-template.md` | Pointer template for source repositories |
| `workflow/copilot-instructions.md` | Copilot bridge to the shared rules |
| `projects/<name>/project.md` | Goal, architecture, decisions, deployment, and active work |
| `projects/<name>/processes.md` | Compact trigger-to-process router |
| `projects/<name>/processes/*.md` | Detailed recurring workflows |
| `projects/<name>/log.md` | Durable, manually maintained project progress |
| `projects/<name>/completed-items.md` | Optional archived task history |
| `knowledge/` | Notes that apply across projects |
| `index.md` files | Generated navigation for each non-empty folder |
| `log/YYYY-Www.md` | Generated weekly roll-up across all project logs |
| `.foam/templates/new-note.md` | Foam-compatible OKF note template |
| `.backups/` | Ignored backups created by upgrades and migrations |

Generated `index.md` files and the top-level `log/` roll-up are derived
artifacts. Edit the project notes and project logs instead, then run
`second-brain generate`.

## Note and metadata conventions

Every indexed content note requires YAML frontmatter with non-empty
`title`, `description`, and `type` values:

```markdown
---
title: Deployment Lessons
description: Reusable findings from production deployments
type: note
---

# Deployment Lessons
```

Additional conventions:

- Use standard Markdown links, not wikilinks.
- Give every project at least one identity field: `repo:` or `path:`.
- Do not reuse the same project identity in multiple project notes.
- Use `status: active` for active projects.
- Keep completed checkboxes out of `Open items`.
- Format log headings as ISO weeks (`YYYY-Www`).
- Format log bullets as `- YYYY-MM-DD: Summary`.
- Keep process details in individual files and use the router only for
  discovery.
- Keep personal prose in any language; the standardized structural names
  remain English for portability.

Foam is optional. To use it, open `~/.second-brain` in VS Code, install
the Foam extension, and use the included new-note template. The data
remains ordinary Markdown and works without Foam.

## Command-line reference

All commands default to `~/.second-brain`. Set `SECOND_BRAIN_HOME` to
change the default for the current environment, or pass a path directly.

```bash
export SECOND_BRAIN_HOME=~/Documents/agent-memory
```

| Command | Purpose and important options |
|---|---|
| `second-brain init [PATH] [--git]` | Create missing private-data structure; preserve existing files; optionally initialize a private Git repository |
| `second-brain generate [PATH]` | Generate folder indexes and cross-project weekly logs |
| `second-brain generate [PATH] --check` | Report generated drift without writing files; suitable for CI |
| `second-brain check [PATH] [--strict] [--skip-generated] [--skip-config]` | Validate a data repository or standalone content; strict mode treats warnings as failures |
| `second-brain doctor [PATH]` | Check Python, Git, directory existence/writability, stable-path resolution, and repository validity |
| `second-brain new-project NAME [options]` | Create a project summary, process router, process directory, and log |
| `second-brain new-process PROJECT NAME --trigger TEXT [options]` | Create a detailed workflow and add it to the process router |
| `second-brain archive-tasks PROJECT [--path PATH]` | Move checked `Open items` into the dated completed-items archive |
| `second-brain upgrade [PATH] [--check]` | Check or apply updates to toolkit-managed rules, templates, and schema |
| `second-brain migrate-legacy [PATH] [options]` | Preview or apply migration from the original German layout |
| `second-brain --version` | Show the installed toolkit version |

Project creation options:

```text
--title TITLE
--description DESCRIPTION
--repo REMOTE
--local-path PATH
--path SECOND_BRAIN_DIRECTORY
```

Process creation options:

```text
--trigger DESCRIPTION   required router trigger
--title TITLE
--description DESCRIPTION
--path SECOND_BRAIN_DIRECTORY
```

Run `second-brain COMMAND --help` for the exact syntax of any command.

Commands use conventional automation-friendly exit statuses:

| Status | Meaning |
|---|---|
| `0` | Operation completed or validation passed |
| `1` | Validation failed, generated/managed files are stale, or a safe operation was refused |
| `2` | Invalid input or a required data directory is unavailable |

## What validation checks

`second-brain check` reports actionable file paths and checks:

- Supported `second-brain.yml` schema version
- Parseable YAML frontmatter and required OKF fields
- Broken relative Markdown links
- Missing or duplicate project `repo:` and `path:` identities
- Checked tasks left under `Open items`
- Invalid ISO-week headings and impossible log dates
- Stale folder indexes and weekly roll-ups
- Common private-key, GitHub-token, AWS-key, and API-key patterns

The secret scan is a safety net, not a complete secret-management or
data-loss-prevention system. Never intentionally store production
credentials, private keys, tokens, or reusable passwords.

Useful validation modes:

```bash
# Normal local validation
second-brain check

# Fail on warnings as well as errors
second-brain check --strict

# Validate source content without checking generated drift
second-brain check --skip-generated

# Validate standalone content that is not a complete data repository
second-brain check PATH --skip-generated --skip-config

# CI-safe generated-file check with no writes
second-brain generate --check
```

## Managed upgrades

After updating the public toolkit checkout, inspect private managed-file
changes before applying them:

```bash
git -C ~/second-brain-toolkit pull
second-brain upgrade --check
second-brain upgrade
second-brain check --strict
```

Managed files include shared `AGENTS.md`, the Foam note template, the
Copilot bridge, and the project/project-agent templates. Changed private
copies are backed up under `.backups/<timestamp>/` before replacement.
`workflow/working-style.md` is deliberately not managed and is always
preserved.

If a private data schema is newer than the installed toolkit supports,
upgrade stops instead of attempting a downgrade.

## Migrating existing data

The legacy migration is dry-run-first:

```bash
second-brain migrate-legacy ~/second-brain --remove-legacy-tools
second-brain migrate-legacy ~/second-brain --apply --remove-legacy-tools
```

It standardizes structural names such as `projekte/`, `projekt.md`,
`prozesse.md`, `pfad:`, and `Offene Themen`; refreshes managed English
rules and templates; regenerates derived files; and preserves domain
prose, project logs, exact process commands, and the customized working
style.

Migration refuses collisions and, by default, a dirty Git worktree.
`--allow-dirty` exists for exceptional cases but is not recommended.
Files replaced or removed during migration are backed up first.

See [MIGRATING.md](MIGRATING.md) for the complete checklist, including
the original single-repository layout.

## Agent integrations

Agent products discover instructions differently. The toolkit keeps the
memory model independent and treats product-specific integration as a
small adapter layer.

| Tool | Integration |
|---|---|
| Claude Code | The installer can link the public `AGENTS.md` rules to `~/.claude/CLAUDE.md` |
| GitHub Copilot in VS Code | The installer can install the Copilot bridge in the detected user profile |
| Codex, Cursor, and repository-aware agents | Add a repository-level `AGENTS.md` based on the provided template |
| Other agents | Point their instruction mechanism to `~/.second-brain/AGENTS.md` and the active project's notes |

Existing unrelated tool files and symlinks are skipped unless
`--replace-links` is explicitly supplied. A replaced regular adapter
file receives a timestamped backup beside the original.

Use `./install.sh --no-agent-links` when all tool configuration should
remain manual.

## Multiple machines

Keep two independent histories:

1. Pull public code and templates from the toolkit repository.
2. Synchronize private memory through a private Git remote or another
   approved private storage system.

Example installation on an additional machine:

```bash
git clone https://github.com/pkkr/second-brain-toolkit.git ~/second-brain-toolkit
git clone <private-remote> ~/second-brain
cd ~/second-brain-toolkit
./install.sh --data-dir ~/second-brain --data-mode symlink
second-brain upgrade --check
second-brain doctor
```

Project instructions continue to use `~/.second-brain`, regardless of
where the physical private checkout lives on each machine.

## Privacy and security

- Keep the private data repository and every remote private.
- Never commit personal memory to the public toolkit repository.
- Store only context that is appropriate for the machine and account
  where the repository is synchronized.
- Do not store production secrets, tokens, private keys, or reusable
  passwords.
- Use fictional names and synthetic examples in public documentation,
  issues, fixtures, screenshots, and pull requests.
- Review generated and migrated diffs before committing them.
- Follow organizational data-handling rules on managed devices and
  company projects.

A hidden directory is not an encryption or access-control mechanism.
Choosing direct mode at `~/.second-brain` changes the physical location,
not the confidentiality guarantees.

## Development

Create the development environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --editable .
```

Run the complete local checks:

```bash
.venv/bin/python -m unittest discover -s tests
bash tests/test_install.sh
bash -n install.sh second-brain tests/test_install.sh
.venv/bin/python second_brain.py check . --strict --skip-generated --skip-config
.venv/bin/python second_brain.py check examples/second-brain --strict
.venv/bin/python second_brain.py generate examples/second-brain --check
.venv/bin/python -m pip wheel --no-deps --wheel-dir dist .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes. Changes
to the data layout must update the schema version, migration guide,
changelog, examples, and tests together.

## License

MIT — see [LICENSE](LICENSE).
