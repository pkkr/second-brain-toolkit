---
title: Migration Guide
description: How to move an existing Second Brain into the privacy-first layout
type: guide
---

# Migrating an Existing Second Brain

The privacy-first layout keeps the public toolkit and private data in
separate Git repositories. Commit or otherwise back up every existing
data change before applying a migration.

## Original German data layout

This migration converts structural conventions while preserving domain
prose, project logs, and exact process commands.

1. Clone or update the public toolkit in a dedicated directory:

   ```bash
   git clone https://github.com/pkkr/second-brain-toolkit.git ~/second-brain-toolkit
   cd ~/second-brain-toolkit
   python3 -m venv .venv
   .venv/bin/python -m pip install --editable .
   ```

2. Commit all current changes in the private data repository. The
   migration refuses a dirty Git worktree by default.

3. Preview the complete migration without writing anything:

   ```bash
   ./second-brain migrate-legacy ~/second-brain --remove-legacy-tools
   ```

4. Apply the reviewed plan:

   ```bash
   ./second-brain migrate-legacy ~/second-brain --apply --remove-legacy-tools
   ```

5. Install the stable alias, CLI command, and optional agent adapters:

   ```bash
   ./setup.sh --data-dir ~/second-brain
   ```

6. Update repository-level `AGENTS.md` references:

   - `~/second-brain/` → `~/.second-brain/`
   - `projekte/` → `projects/`
   - `projekt.md` → `project.md`
   - `prozesse.md` and `prozesse/` → `processes.md` and `processes/`

7. Validate both repositories and inspect the private migration diff:

   ```bash
   second-brain check --strict
   git -C ~/second-brain status --short
   git -C ~/second-brain diff --stat
   ```

8. Commit the migration in the private repository only after verifying
   its project count, logs, processes, links, and generated indexes.

The command converts standard names such as `projekte/`, `projekt.md`,
`prozesse/`, `pfad:`, and `Offene Themen` to their English toolkit
equivalents. Managed rules and templates become English. A customized
working style is preserved under `workflow/working-style.md`, regardless
of the language used inside it. Old data-repository tooling is backed up
before optional removal.

## Original single-repository layout

When toolkit code and personal data still share one repository:

1. Create a separate private repository, by default `~/second-brain`.
2. Copy personal projects, knowledge, inbox, customized workflow files,
   and project logs into it. Do not copy generated indexes or the
   generated global log directory.
3. Keep the public toolkit checkout at a different path such as
   `~/second-brain-toolkit`.
4. Follow the setup and validation steps above.
5. Remove personal files from the public repository only after the
   private copy and backup have been verified.

## Private Git history

If the data directory is not already a Git repository:

```bash
cd ~/second-brain
git init -b main
git add .
git commit -m "Initialize private Second Brain"
```

Verify that any remote repository is private before adding it. The
private data and public toolkit must remain separate histories.

## Process-router migration

For projects with a monolithic `processes.md`:

1. Keep `processes.md` as a short table containing trigger, process link,
   and last verification date.
2. Move each detailed recurring workflow into
   `projects/<name>/processes/<process>.md`.
3. Run `second-brain check` to find broken links.

Move checked tasks out of `Open items` into the project log or an
optional `completed-items.md` archive.
