---
title: General Working Style
description: Default collaboration rules shared across projects
type: guide
---

# General Working Style

Customize this file with preferences that genuinely apply across all
projects. Project-specific commands and exceptions belong in the
corresponding project notes.

## Instruction priority

- Follow the user's current explicit request first.
- Then follow the nearest repository instructions, project-specific
  Second Brain guidance, this file, and finally general agent defaults.
- At the same level, prefer the more specific and more recently verified
  instruction.
- Do not attempt to resolve conflicting instructions by performing both
  alternatives. State the conflict and its practical consequence.
- Security, privacy, legal, and compliance constraints always remain in
  force.

## Approach

- Test locally and commit, but **do not push** without an explicit request.
- Make reasonable, reversible assumptions when they keep work moving;
  surface assumptions that materially affect the outcome.
- Preserve unrelated local changes and avoid destructive version-control
  operations unless explicitly requested.
- Use fictional names and synthetic data in public repositories, demos,
  screenshots, and mockups unless real data is explicitly authorized.
- <add communication or language preferences here>
- <add confidentiality or compliance requirements here>

## Context discipline

- Start with the smallest useful context: the active project summary,
  open items, and the process router.
- Load detailed process notes, historical log entries, archives, and
  linked knowledge only when the task needs them.
- Treat a link as navigation, not as an instruction to load its target.
- Prefer targeted searches and recent log entries over reading an entire
  history.
- Keep notes concise and durable. Git already records implementation
  detail; the Second Brain should explain intent, decisions, workflows,
  and unresolved risks.

## Second Brain

- Keep one `project-template.md`-based note per project under
  `projects/<name>/`.
- Identify projects by the `repo:` frontmatter field, with `path:` as a
  fallback.
- Keep `processes.md` as a router and detailed recurring workflows under
  `processes/`.
- Generate indexes with `second-brain generate`; never edit them manually.

## Python

- Name project virtual environments `.venv` and keep them at the project
  root.
- Install CLI tools with pipx and libraries in the project virtual
  environment; do not bypass the system package manager globally.
