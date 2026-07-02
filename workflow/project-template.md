---
title: Project Template
description: Template for a project's core note (project.md)
type: template
---

# Project Template

See [`projects/example-project/`](../projects/example-project/project.md)
for a filled-in example. Copy this into `projects/<name>/project.md`:

    ---
    title: <Project Name>
    description: <One sentence – what is this project?>
    type: project
    repo: <git remote get-url origin, e.g. git@host:org/name.git>
    path: <local path, e.g. ~/code/name>
    status: active
    ---

    # <Project Name>

    ## Goal
    <Why does this project exist? For whom?>

    ## Stack & architecture
    <Languages, frameworks, database, notable quirks>

    ## Deployment
    <Where does it run, how do you deploy?>

    ## Decisions
    <Key architecture/product decisions with a short rationale>

    ## Open items
    - [ ] <Task – check off when done>

Each project also keeps a `log.md` (not indexed):

    ## 2026-W27
    - 2026-07-02: <short bullet of what happened>

And a `processes.md` for recurring workflows (agents maintain this automatically):

    ---
    title: <Project Name> – Processes
    description: Recurring workflows (deploy, tests, migrations …)
    type: guide
    ---

    # Processes

    ## Deploy
    1. <Step with the exact command>
