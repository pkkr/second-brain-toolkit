---
title: Example Project – Deploy
description: How to deploy the example application
type: guide
---

# Deploy

## Preconditions

- CI is passing on `main`.
- The deployment CLI is authenticated for the intended environment.

## Steps

1. Switch to the deployment branch: `git checkout deploy`.
2. Merge the verified release state: `git merge main`.
3. Deploy the application: `fly deploy`.

## Verification

1. Confirm the deployment command reports a healthy release.
2. Open the target environment and verify the booking calendar loads.
