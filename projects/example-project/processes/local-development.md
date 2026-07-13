---
title: Example Project – Local Development
description: How to run the example application locally
type: guide
---

# Local Development

## Preconditions

- Node.js and PostgreSQL are installed.
- The local PostgreSQL instance is available on port 5433.

## Steps

1. Verify the database connection with `psql -p 5433`.
2. Start the backend and frontend together with `npm run dev`.

## Verification

1. Open the local application.
2. Confirm that the booking calendar can read from the local database.
