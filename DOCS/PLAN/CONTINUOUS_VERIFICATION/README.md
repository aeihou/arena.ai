/DOCS/PLAN/CONTINUOUS_VERIFICATION/README.md

# Continuous verification

- **Status:** Blocked
- **Updated:** 2026-08-19
- **Blocker:** The GitHub connection cannot create or update active workflow
  files without workflow permission.
- **Last confirmed:** 2026-08-19
- **Recheck trigger:** The repository connection explicitly grants workflow-file
  write permission.

## Goal

Run the portable self-consistency verifier and its tests automatically on pushes,
pull requests, and manual dispatches.

## Prepared implementation

The inactive workflow template is maintained at
[`GITHUB/self-consistency.yml`](../../../GITHUB/self-consistency.yml). It uses
Python 3.9 and has no third-party runtime dependencies.

## Recheck and execute

Do not probe the blocker by repeatedly pushing workflow changes. Recheck only
when the connection reports workflow-file write permission.

1. Confirm the repository connection grants workflow-file write permission.
2. Copy the template to `.github/workflows/self-consistency.yml`.
3. Push on the current `branch` and confirm the workflow starts.
4. Verify that unit tests and repository consistency both pass.
5. Mark this plan completed in this file and the parent registry.

## Acceptance criteria

- The active workflow exists under `.github/workflows/`.
- Push, pull-request, and manual triggers are available.
- The workflow invokes the same commands documented for local development.
- A successful run is visible on GitHub.

Do not retry activation while the permission blocker remains.
