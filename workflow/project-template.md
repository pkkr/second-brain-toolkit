---
title: Project Template
description: Template for a project's core note and supporting memory
type: template
---

# Project Template

The public toolkit repository contains a filled-in example. Copy this
template into `projects/<name>/project.md`:

    ---
    title: <Project Name>
    description: <One sentence describing the project>
    type: project
    repo: <git remote get-url origin, e.g. git@host:org/name.git>
    path: <local path, e.g. ~/code/name>
    status: active
    ---

    # <Project Name>

    ## Goal
    <Why does this project exist, and for whom?>

    ## Stack and architecture
    <Languages, frameworks, data stores, and notable constraints>

    ## Deployment
    <Where it runs; link to the detailed deployment process>

    ## Decisions
    <Key product or architecture decisions with concise rationale>

    ## Open items
    - [ ] <Active task>

    ## Archive
    - [Completed items](completed-items.md)
    - [Progress log](log.md)

Keep only active unchecked tasks in `Open items`. Move durable completed
work to `log.md`; use an optional `completed-items.md` when older task
history remains useful.

Each project also has a `log.md`. Add no more than one to three durable
entries for a noteworthy session:

    ## 2026-W27

    - 2026-07-02: <decision, released outcome, changed workflow, or unresolved risk>

Use `processes.md` as a short router:

    ---
    title: <Project Name> – Process Router
    description: Entry points for recurring project workflows
    type: guide
    ---

    # Process Router

    | Trigger | Process | Last verified |
    |---|---|---|
    | Deploy the service | [Deploy](processes/deploy.md) | YYYY-MM-DD |

Store each detailed recurring workflow under `processes/`, for example
`processes/deploy.md`:

    ---
    title: <Project Name> – Deploy
    description: How to deploy the service safely
    type: guide
    ---

    # Deploy

    ## Preconditions
    - <Required access, branch state, or checks>

    ## Steps
    1. <Step with the exact command>

    ## Verification
    1. <How to confirm success>
