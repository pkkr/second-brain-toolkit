---
title: Example Project – Processes
description: Recurring workflows (deploy, local development)
type: guide
---

# Processes

## Deploy

1. Make sure `main` is green (CI passing)
2. `git checkout deploy && git merge main`
3. `fly deploy`

## Local development

1. Postgres runs on port 5433 locally — `psql -p 5433`
2. `npm run dev` starts backend + frontend together
