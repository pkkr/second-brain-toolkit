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
bash tests/test_install.sh
bash -n install.sh second-brain tests/test_install.sh
.venv/bin/python second_brain.py check . --strict --skip-generated --skip-config
.venv/bin/python second_brain.py check examples/second-brain --strict
.venv/bin/python second_brain.py generate examples/second-brain
.venv/bin/python second_brain.py generate examples/second-brain --check
```

Commit generated indexes when their source notes change. Never include
files from a personal Second Brain repository, real project data,
credentials, or secrets in an issue, test fixture, commit, or pull
request.

Changes to the data layout must update the schema version, migration
guide, changelog, examples, and tests together.
