---
title: Project AGENTS.md Template
description: Template for the AGENTS.md stored in each project repository
type: template
---

# Project AGENTS.md Template

Copy this into `<project-repo>/AGENTS.md` and replace `<name>`:

    # Agent Instructions

    ## Second Brain

    Durable context for this project lives under `~/.second-brain/`:

    - Core facts and active tasks: `projects/<name>/project.md`
    - Recurring-workflow router: `projects/<name>/processes.md`
    - Detailed workflows: `projects/<name>/processes/`
    - Progress log: `projects/<name>/log.md`

    Read `~/.second-brain/AGENTS.md` at the start and follow its rules.
    Load only the project sections, linked notes, and process details
    relevant to the current task. For history, use only the newest ISO
    week, at most the latest five log entries, or targeted search results.
    If the Second Brain is unavailable on this machine, continue without it.
