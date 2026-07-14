---
title: Changelog
description: Notable changes to Second Brain Toolkit
type: changelog
---

# Changelog

All notable changes to this project are documented here.

## 0.2.0 – 2026-07-14

- Separated the public toolkit from the private user-data repository.
- Added the `second-brain` CLI with initialization, generation,
  validation, diagnostics, project/process creation, task archiving, and
  managed upgrades.
- Added check-only generation for automated validation.
- Added schema versioning, migration guidance, tests, and CI.
- Made setup safer and more portable across supported shell platforms.
- Kept public context-loading rules aligned with the generic parts of the
  private rule set, including conflict handling and selective navigation.
- Added a dry-run-first migration command for the original German data
  layout, with collision checks, dirty-worktree protection, and backups.
- Added an interactive setup choice between a recommended stable
  symlink and physically storing the private repository at
  `~/.second-brain`, with deterministic flags and conflict protection.
- Renamed the bootstrap script to `install.sh` and moved the tracked
  sample data repository under `examples/second-brain/` so public
  toolkit code and demonstration content are easier to distinguish.
- Removed the redundant root `requirements.txt`; package dependencies
  are defined exclusively in `pyproject.toml`.

## 0.1.0 – 2026-07-13

- Published the initial Markdown, Foam, and OKF-based toolkit.
