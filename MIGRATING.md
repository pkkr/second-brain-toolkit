---
title: Migration Guide
description: How to move an existing Second Brain into the privacy-first layout
type: guide
---

# Migrating an Existing Second Brain

The privacy-first layout separates the public toolkit from personal
data. Back up or commit the existing knowledge base before migrating.

## From the original single-repository layout

1. Clone or update the toolkit in a dedicated directory such as
   `~/second-brain-toolkit`.
2. Run `./setup.sh --dry-run` and review the paths.
3. Create or choose a separate private repository, by default
   `~/second-brain`.
4. Copy personal `projects/`, `knowledge/`, `inbox.md`, customized
   workflow files, and project logs into that private repository. Do not
   copy generated indexes or the generated global `log/` directory.
5. Run `./setup.sh --data-dir ~/second-brain` from the public toolkit.
6. Run `second-brain generate` followed by `second-brain check`.
7. Verify that `~/.second-brain` points to the private repository.
8. Remove personal files from the public repository only after the new
   copy and any private backup have been verified.

## Private Git history

Initialize the data directory independently if it is not already a Git
repository:

```bash
cd ~/second-brain
git init
git add .
git commit -m "Initialize private Second Brain"
```

If remote synchronization is required, create a private repository and
verify its visibility before adding it as a remote. The private data
repository and the public toolkit repository remain separate histories.

## Process-router migration

For projects with a monolithic `processes.md`:

1. Keep `processes.md` as a short table containing trigger, process link,
   and last verification date.
2. Move each detailed recurring workflow into
   `projects/<name>/processes/<process>.md`.
3. Run `second-brain check` to find broken links.

Move checked tasks out of `Open items` into the project log or an
optional `completed-items.md` archive.
