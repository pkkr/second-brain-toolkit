---
title: Copilot Bridge
description: Copilot user instructions that bridge to AGENTS.md
type: guide
applyTo: '**'
---

# Second Brain (applies to every project)

At the start of work, read `~/.second-brain/AGENTS.md` and follow it. If
that file is unavailable, use this compact fallback:

- Identify the current project through `git remote get-url origin`, then
  find or create its `projects/<name>/project.md` using the `repo:` or
  `path:` frontmatter field.
- Read the general working style and the project's summary, decisions,
  and open items. Follow linked context only when relevant.
- Treat `processes.md` as a router and load only the detailed recurring
  process needed for the current task.
- Do not read the complete project log by default; use the newest ISO
  week, at most the latest five entries, or a targeted search.
- For noteworthy sessions, write at most one to three durable log
  bullets. Keep only active tasks in `Open items`; archive completed work.
- Never store real secrets, tokens, private keys, or reusable passwords
  in the Second Brain.
