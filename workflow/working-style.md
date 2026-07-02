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

## Python

- venvs are always named `.venv` and live at the project root.
- CLI tools via pipx, libraries into the project venv — never install
  globally with `--break-system-packages`.
