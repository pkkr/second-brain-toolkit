# Second Brain – Project Memory

My Second Brain lives in `~/second-brain/`. It is the central,
cross-session knowledge base about my projects. Every agent keeps it
up to date so a new agent has context immediately.

## Identify the project

The key is the git remote URL (`git remote get-url origin`):

1. Find the matching project note:
   `grep -rl "repo: <remote-url>" ~/second-brain/projects/`
2. No match (or no remote): look up the local path in the `path:` field.
3. No note yet? Create `~/second-brain/projects/<repo-name>/project.md`
   from the template `~/second-brain/workflow/project-template.md`.
   This applies especially to brand-new projects: use `path:` as the
   key first, add `repo:` once a remote exists.

## At the start of a coding session

- Read the project's `project.md` and any notes it links to before working.
- Read `~/second-brain/workflow/working-style.md` for my general approach.

## Project-specific processes

- Recurring workflows for a project live in
  `~/second-brain/projects/<name>/processes.md` — e.g. how to deploy,
  run tests, run migrations, cut releases.
- Read them at session start and follow them.
- **Maintain automatically:** if you establish, discover, or notice a
  change to such a workflow during a session, record it there right
  away (one section per process, numbered steps with the exact
  commands). Don't ask for permission first.
- Boundary: anything that applies to ALL projects belongs in
  `workflow/working-style.md`, not in a project's processes.

## AGENTS.md in the project repo

- Make sure every project repo has an `AGENTS.md` at its root that
  points to its Second Brain notes — template:
  `~/second-brain/workflow/project-agents-template.md`.
  This lets tools without global wiring (Copilot, Cursor, Codex) find
  the project context too.
- If an `AGENTS.md` already exists, only add the Second Brain section
  if it's missing — never overwrite existing content.

## Process the inbox

- `~/second-brain/inbox.md` is my quick-capture space: unsorted
  thoughts and tasks, one bullet per entry.
- If I say "add this to the inbox", add it there — no need to ask.
- Whenever you're writing to the Second Brain anyway (session log,
  notes), check the inbox and process what you can confidently sort:
  - A task for a project → checkbox under "Open items" in `project.md`
  - A thought/piece of knowledge → extend an existing note or create a
    new one under `knowledge/`
  - Remove processed lines from the inbox; leave anything unclear.

## OKF conventions

All notes follow [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md),
Google Cloud's vendor-neutral Markdown+frontmatter spec — this toolkit
is stricter than the spec on required fields:

- YAML frontmatter with `title`, `description`, and `type` in every
  note (template: `.foam/templates/new-note.md`).
- One generated `index.md` per folder (`connect_neurons.py`) — never
  edit indexes or `log/` by hand.
- Link using standard Markdown links; no wikilinks (`[[...]]`) — Foam
  is configured so `[[` completion inserts Markdown links.

## Progress log & tasks

- At the end of any noteworthy session: 2–4 short bullets in the
  project's log `~/second-brain/projects/<name>/log.md` — what was
  built, decided, or learned. No commit-message repeats.
- Format: heading per ISO week (`## $(date +%G-W%V)`), newest week on
  top, bullets as `- YYYY-MM-DD: <summary>`.
- Tasks are checkboxes (`- [ ]`) under "Open items" in `project.md`:
  check off what's done, add what's newly discovered.
- The `log/` folder is generated from the project logs — never edit
  by hand.

## During & after the work

- Keep `project.md` current when something fundamental changes: goal,
  stack, architecture decisions, deployment, open items.
- Transient details (individual bug fixes, in-progress state) do NOT
  belong here — that's what git is for. The Second Brain holds what
  git doesn't show you.
- Follow the OKF conventions (see above).
- Never write secrets, tokens, or passwords into the Second Brain.
- After changes in the Second Brain, rebuild the indexes:
  `cd ~/second-brain && .venv/bin/python connect_neurons.py`
