# Second Brain Toolkit

A memory system for your coding agents. Every time you open a new
Claude Code, Copilot, or Cursor session, it has amnesia — it doesn't
know what your project is for, how you deploy it, what you decided
last week, or what's still open. This toolkit fixes that: a small
Markdown knowledge base that agents read *and write*, so context
survives across sessions, tools, and machines.

It's built on [Foam](https://foambubble.github.io/foam/) (VS Code +
plain Markdown, no server, no lock-in) and
[Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md),
Google Cloud's spec for storing knowledge as Markdown + YAML
frontmatter — together they keep the notes consistent enough for a
script to index them and for an agent to reliably find its way around.

## What it actually does

- **Agents identify your project automatically**, via its git remote
  URL, and know where to look for context — no copy-pasting a project
  brief into every new session.
- **Agents write back.** A short session log, updated task checkboxes,
  a newly-learned deploy command — captured in the moment, not
  reconstructed from memory three weeks later.
- **One rule file, every tool.** `AGENTS.md` is the emerging
  tool-neutral standard (read natively by Copilot, Cursor, Codex, and
  others). Claude Code gets the same file via a symlink to
  `~/.claude/CLAUDE.md`. No duplicated, drifting instructions.
- **A junk-drawer that empties itself.** Drop a thought or task into
  `inbox.md`; agents sort it into the right project or note the next
  time they're in there anyway.
- **Generated, not maintained.** `connect_neurons.py` builds an
  `index.md` per folder and rolls up all projects' weekly logs into a
  single global log — so you get an overview without keeping one by hand.

## Quick start

```bash
git clone https://github.com/pkkr/second-brain-toolkit.git ~/second-brain
cd ~/second-brain
./setup.sh
```

`setup.sh` creates a Python venv, links `AGENTS.md` to
`~/.claude/CLAUDE.md` (Claude Code) and into your VS Code profile
(Copilot), and builds the indexes. It's idempotent — safe to re-run
any time, including on a second machine.

Then open the folder in VS Code and accept the recommended-extensions
prompt (Foam, Python). Take a look at
[`projects/example-project/`](projects/example-project/project.md) and
[`knowledge/example-note.md`](knowledge/example-note.md) to see the
format in practice, then delete them once you've got the idea.

## Structure

| Location | Contents |
|---|---|
| `AGENTS.md` | The rules every agent follows — this is the actual engine |
| `inbox.md` | Quick capture: drop thoughts & tasks, agents sort them in |
| `workflow/` | Your general working style, plus templates |
| `projects/<name>/` | `project.md` (core facts + tasks), `processes.md`, `log.md` |
| `knowledge/` | Topic notes that don't belong to one project |
| `log/` | **Generated:** one weekly log per ISO week, across all projects |

## The OKF conventions

The [OKF spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
itself only requires a `type` field on each note; this toolkit is
stricter and also requires `title` and `description`:

- Every note carries YAML frontmatter with `title`, `description`, and
  `type`.
- Links are standard Markdown links (`[Title](path.md)`), not
  wikilinks — `connect_neurons.py` generates plain index pages, and
  keeping one link syntax means those pages render the same everywhere
  a Markdown renderer might show them (GitHub, a static site, etc.).
  Foam is configured (`foam.completion.linkFormat: "link"`) so typing
  `[[` still autocompletes, but inserts a Markdown link.
- One `index.md` per folder, generated — never hand-edited. Same for
  the `log/` roll-up.

Run the generator any time: it happens automatically when you open the
folder in VS Code, or manually with `⇧⌘B` / `Ctrl+Shift+B`, or:

```bash
.venv/bin/python connect_neurons.py
```

## Using it across your other repos

For tools that don't read a global config (or when you want context
to travel with the repo itself, e.g. for a teammate), add a small
`AGENTS.md` to each project pointing back at its Second Brain notes —
template in
[`workflow/project-agents-template.md`](workflow/project-agents-template.md).
Your main `AGENTS.md` already tells agents to set this up on their own
the first time they work in a new project.

## Multiple machines

`setup.sh` is the whole story: clone (or sync) the folder, run the
script, open in VS Code. It backs up any pre-existing
`~/.claude/CLAUDE.md` before linking, so it won't clobber unrelated
setups.

## A word on what to put in here

This is for durable context — the things a `git log` won't tell you:
why a decision was made, how deploys actually work, what's still
open. It is **not** a replacement for git history, and it should
**never** contain secrets, tokens, or credentials. If you're setting
this up on a work machine, check with your employer before pointing it
at anything beyond your own scratch notes, and keep it on
infrastructure they're comfortable with.

## License

MIT — see [LICENSE](LICENSE). Fork it, rename the reserved files if
you'd rather call it something else, make it yours.
