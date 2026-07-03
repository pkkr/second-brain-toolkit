---
title: General Working Style
description: How I work and how agents should collaborate with me
type: guide
---

# General Working Style

This is the one file you should actually rewrite for yourself — it's
where your personal preferences live. A few starting points:

## Approach

- Test locally and commit, but **do not push** without an explicit request.
- <add your communication/language preferences here>
- <add any confidentiality/compliance rules that apply to your work>

## Second Brain

- One [project template](project-template.md)-based note per project
  under `projects/<name>/`.
- Identify projects via the git remote URL in the `repo:` frontmatter field.
- Indexes are generated (`connect_neurons.py`), never edited by hand.

## Starting a new project

When I mention a new project/initiative (in chat or dropped in
`inbox.md`) that doesn't have a note yet, don't just create it
silently — ask clarifying questions first:

- **Name** — two names, not one:
  - internal folder slug under `projects/<name>/` (doesn't need to be
    pretty, just stable).
  - a human-readable **title** (frontmatter `title:`) recognizable to
    others (e.g. a manager) for use in summaries/progress notes.
  Suggest both instead of asking from scratch — I'll confirm or
  correct.
- **Goal** — what does "done" look like, for whom.
- **Repo or organizational-only** — does it live in a repo/path
  (normal `repo:`/`path:` frontmatter), or is it a cross-team /
  non-code initiative with no repo at all (omit those fields)?
- **Stakeholders** — other people involved (e.g. "work with X on Y").
- **Known next actions** — seed `Open items` with whatever's already
  known, including non-coding tasks (schedule a call, get an
  approval, wait on someone else's deliverable) alongside code tasks.
- **Related projects/notes** — link it from/to existing project or
  knowledge notes if it extends or depends on something that already
  exists.

Then create `project.md` (+ `log.md`, `processes.md` if useful) from
the template and, if the idea came from `inbox.md`, remove the
processed line.

## Python

- venvs are always named `.venv` and live at the project root.
- CLI tools via pipx, libraries into the project venv — never install
  globally with `--break-system-packages`.
