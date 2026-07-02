---
title: Example Project
description: A worked example showing the project-note format
type: project
repo: git@github.com:example-org/example-project.git
path: ~/code/example-project
status: active
---

# Example Project

This note demonstrates what a real `project.md` looks like once an
agent (or you) has filled it in. Delete this whole folder once you've
got the idea — it's not needed for the toolkit to work.

## Goal

A short web app that lets small teams track shared equipment
bookings. Built for a local makerspace that outgrew a shared
spreadsheet.

## Stack & architecture

- Backend: Node.js + PostgreSQL
- Frontend: React
- Local Postgres runs on port 5433 (5432 was already taken by another
  project on this machine)

## Deployment

Hosted on Fly.io, one app per environment (staging + production).
Deploy with `fly deploy` from the `deploy` branch.

## Decisions

- Chose Postgres over SQLite early on because concurrent bookings
  needed real row locking.
- No user accounts for v1 — a shared team link is enough at this scale.

## Open items

- [ ] Email reminders before a booking starts
- [ ] Recurring bookings
- [x] Basic booking calendar (2026-06-20)
