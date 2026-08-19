/DOCS/PLAN/CONSISTENCY_GUARDS/README.md

# Portable context and plan guards

- **Status:** Completed
- **Updated:** 2026-08-19
- **Outcome:** Generic Markdown conventions detect inconsistent plans and stale or
  malformed session tracking without repository-specific configuration.

## Goal

Protect next-agent context and plan status from silent drift while preserving the
verifier's portability.

## Discovery model

The verifier discovers documents by semantic headings rather than fixed paths:

- A plan registry contains `## Status model` and `## Registry`.
- Rolling state contains `# Rolling session context`.
- Compact history contains `# Compact session log`.

Repositories that do not use these conventions are unaffected.

## Plan guards

- Registry statuses must exist in the local status model.
- Linked detail status must match registry status.
- Detailed plans require valid `Status` and ISO `Updated` metadata.
- Every direct child plan README must be registered.

## Session guards

- Rolling context requires an ISO `Updated` date and non-empty outcome, state,
  validation, and next-agent sections.
- Rolling context requires a sibling compact log.
- Compact logs require at least one dated entry with Outcome, Decisions, and
  Validation fields.
- Rolling context cannot predate the newest sibling log entry.

## Acceptance criteria

- Rules are inferred from headings and links, not repository names.
- A valid repository passes without configuration.
- Status mismatch, malformed tracking, and stale context fixtures fail with
  actionable finding codes.
- Existing verifier and interaction behavior remains unchanged.
