---
title: Copilot Bridge
description: Copilot user instructions – bridge to AGENTS.md
type: guide
applyTo: '**'
---

# Second Brain (applies to every project)

At the start of your work, read `~/second-brain/AGENTS.md` (e.g. via
terminal: `cat ~/second-brain/AGENTS.md`) and follow the rules there
in full. Short version if that file isn't readable:

- My Second Brain lives in `~/second-brain/`.
- Identify the current project via `git remote get-url origin` and
  find/create its note `projects/<name>/project.md` (frontmatter field
  `repo:` = remote URL).
- Read the project's `project.md` and `processes.md` before working.
- At the end of noteworthy sessions: 2–4 bullets in the project's
  `log.md` (`## <ISO week>`, bullets `- YYYY-MM-DD: …`), check off
  tasks in `project.md`.
- Never write secrets into the Second Brain.
