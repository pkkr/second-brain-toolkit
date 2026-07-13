---
title: Contributing
description: How to propose and validate changes to Second Brain Toolkit
type: guide
---

# Contributing

Contributions should keep the memory format tool-neutral, privacy-first,
and usable as plain Markdown without a hosted service.

## Development setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --editable .
```

## Before opening a pull request

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python second_brain.py check . --strict
.venv/bin/python connect_neurons.py .
.venv/bin/python connect_neurons.py --check .
```

Commit generated indexes when their source notes change. Never include
personal files from `private/`, real project data, credentials, or
secrets in an issue, test fixture, commit, or pull request.

Changes to the data layout must update the schema version, migration
guide, changelog, examples, and tests together.
