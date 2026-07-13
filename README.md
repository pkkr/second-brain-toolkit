# Second Brain Toolkit

A privacy-first memory system for coding agents. It keeps durable project
context in plain Markdown so decisions, recurring workflows, and active
tasks survive across sessions, tools, and machines.

The toolkit uses [Foam](https://foambubble.github.io/foam/) for editing
and follows [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
conventions for Markdown and YAML frontmatter. No server or proprietary
database is required.

## What it does

- **Identifies projects automatically** from a git remote or local path.
- **Loads context progressively:** agents start with a compact project
  summary and open detailed processes or history only when needed.
- **Writes back selectively:** durable decisions, released outcomes,
  changed workflows, and unresolved risks are recorded without copying
  git history into the notes.
- **Keeps public code and private memory separate:** personal data lives
  in an ignored `private/` directory, exposed through the stable
  `~/.second-brain` path.
- **Validates the knowledge base:** the CLI detects malformed metadata,
  broken links, duplicate project identities, misplaced completed tasks,
  invalid logs, and stale generated files.
- **Generates navigation:** folder indexes and cross-project weekly logs
  are derived automatically.

## Quick start

```bash
git clone https://github.com/pkkr/second-brain-toolkit.git ~/second-brain-toolkit
cd ~/second-brain-toolkit
./setup.sh
```

The setup script:

1. Creates a local Python environment.
2. Initializes personal data in `private/`, which the public repository
   ignores.
3. Links that directory to `~/.second-brain` so project instructions do
   not depend on the toolkit's installation path.
4. Installs a `second-brain` command under `~/.local/bin` when that path
   is available.
5. Adds optional agent-tool links without overwriting unrelated files.

Preview all locations without changing anything:

```bash
./setup.sh --dry-run
```

To give the private data its own local Git history:

```bash
./setup.sh --init-git
```

Only connect that nested repository to a **private** remote. The outer
toolkit repository will continue to ignore it.

## Public toolkit versus private data

| Location | Purpose | Public repository |
|---|---|---|
| Toolkit root | CLI, rules, templates, examples, tests | Tracked |
| `private/` | Personal projects, knowledge, inbox, and logs | Ignored |
| `~/.second-brain` | Stable link to the selected private directory | Outside the repository |

Inside the private data directory:

| Location | Contents |
|---|---|
| `AGENTS.md` | Shared rules for agents |
| `inbox.md` | Quick capture for unsorted thoughts and tasks |
| `workflow/` | General working style and reusable templates |
| `projects/<name>/` | Project summary, active tasks, process router, detailed processes, and log |
| `knowledge/` | Durable notes that apply across projects |
| `log/` | Generated weekly roll-up across projects |
| `second-brain.yml` | Data schema version |

The tracked [`projects/example-project/`](projects/example-project/project.md)
and [`knowledge/example-note.md`](knowledge/example-note.md) demonstrate
the format; they are not copied into private data.

## Command line interface

```bash
second-brain init [PATH] [--git]
second-brain generate [PATH]
second-brain generate [PATH] --check
second-brain check [PATH] [--strict]
second-brain doctor [PATH]
second-brain new-project NAME --repo REMOTE
second-brain new-process PROJECT NAME --trigger DESCRIPTION
second-brain archive-tasks PROJECT
second-brain upgrade [PATH] [--check]
```

The default path is `~/.second-brain`, or the value of
`SECOND_BRAIN_HOME` when set.

- `init` creates missing private-data files and preserves existing ones.
- `generate` updates folder indexes and weekly log roll-ups.
- `generate --check` reports generated drift without writing files.
- `check` validates structure, metadata, links, project identities,
  task placement, logs, generated output, and common secret-like values.
- `doctor` checks the local installation before running the validator.
- `new-project` creates a project summary, process router, log, and
  process directory with valid metadata.
- `new-process` creates a detailed workflow and adds it to the router.
- `archive-tasks` moves checked tasks out of `Open items` into a durable
  archive.
- `upgrade` refreshes toolkit-managed rules and templates, backing up
  changed copies while preserving the customized working style.

The original generator remains available for scripting:

```bash
.venv/bin/python connect_neurons.py ~/.second-brain
.venv/bin/python connect_neurons.py --check ~/.second-brain
```

## Context model

The default reading path is intentionally small:

1. General working style
2. Project frontmatter, goal, architecture, decisions, and active tasks
3. The process router
4. Only the detailed process, recent log entries, or linked notes needed
   for the current task

Completed-task archives, full logs, unrelated projects, and generated
indexes are not loaded "just in case." This keeps routine work fast
without discarding deeper context.

## OKF conventions

The toolkit requires every indexed note to contain `title`,
`description`, and `type` in YAML frontmatter. It also uses:

- Standard Markdown links instead of wikilinks
- Generated `index.md` files per folder
- Generated cross-project weekly logs
- Active unchecked tasks only under `Open items`
- One detailed file per recurring process, reached through a compact
  `processes.md` router

Run `second-brain check` after structural changes.

## Agent-tool adapters

Agent products discover instructions differently. The toolkit keeps the
memory format independent and treats integrations as adapters:

| Tool | Toolkit integration |
|---|---|
| Claude Code | Optional link from `AGENTS.md` to `~/.claude/CLAUDE.md` |
| GitHub Copilot in VS Code | Optional user-instructions link when the VS Code profile is detected |
| Codex, Cursor, and other repository-aware tools | Add the small repository-level `AGENTS.md` from the provided template |

Use `./setup.sh --no-agent-links` when tool configuration should remain
untouched. Existing files and unrelated symlinks are skipped unless
`--replace-links` is explicitly supplied.

`setup.sh` targets macOS and Linux. On Windows, WSL is the recommended
path; the Python CLI itself also works from PowerShell after creating a
virtual environment and installing the project with `pip install -e .`.

## Multiple machines

There are two independent histories:

1. Pull toolkit updates from the public toolkit repository.
2. Synchronize `private/` through a separate private repository or an
   approved private storage system.

After pulling toolkit updates, run `second-brain upgrade --check` and
then `second-brain upgrade` to apply reviewed rule and template changes.
Customized `workflow/working-style.md` is never replaced.

Run `./setup.sh --data-dir PATH` on each machine to recreate the stable
`~/.second-brain` link. Never add `private/` to the public toolkit
repository.

Existing installations can follow [MIGRATING.md](MIGRATING.md).

## Privacy and scope

Store only durable context that source control and issue trackers do not
explain well: rationale, operating knowledge, current priorities, and
unresolved risks.

Never store production or personal secrets, tokens, private keys, or
reusable passwords. Clearly labeled throwaway credentials for a
local-only environment are acceptable only when they contain no real
data and are never reused. Follow organizational data-handling policies
on managed devices and company projects.

## Development

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python second_brain.py check .
.venv/bin/python connect_neurons.py --check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes.

## License

MIT — see [LICENSE](LICENSE).
