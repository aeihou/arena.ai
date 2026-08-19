/DOCS/PLAN/SESSION_CONTEXT/README.md

# Session-context hand-off

- **Status:** Completed
- **Updated:** 2026-08-19
- **Outcome:** Rolling state supports immediate continuation while a compact log
  preserves selected historical outcomes.

## Developer-approved model

- **Tracking:** rolling context plus append-only compact log.
- **Detail:** semantic outcomes, validation, exceptions, and next direction.
- **Frequency:** update with every meaningful completed change.

## Canonical files

- Current state:
  [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](../../../AGENTS/HAND-OFF/SESSION_CONTEXT.md)
- Historical outcomes:
  [`AGENTS/HAND-OFF/SESSION_LOG.md`](../../../AGENTS/HAND-OFF/SESSION_LOG.md)
- Durable plan state: [`DOCS/PLAN/README.md`](../README.md)

Git history preserves prior rolling versions; the log retains only outcomes worth
finding without Git archaeology.

## Track

- latest semantic outcome;
- temporary constraints or exceptions;
- validation baseline;
- authoritative links; and
- next-agent direction.

## Derive or link instead

- runtime account, repository, branch, commit, and changed-file values;
- repository trees and file inventories;
- operating instructions;
- durable plan detail; and
- tool usage.

## Update rule

For meaningful work, validate first, rewrite current context, append one concise
log entry, and commit both with the implementation. Minor edits that do not alter
next-agent understanding need no log entry.

If context conflicts with the working copy or a detailed plan, derive reality,
treat the plan registry as authoritative for plan state, and repair context.

## Acceptance criteria

- A new agent can identify the latest outcome, validation state, and next
  direction without conversation history.
- Rolling context contains no obsolete history or duplicated plan state.
- Log entries remain short, semantic, and append-only.
- Runtime metadata is absent.
- Context and implementation ship together and pass repository verification.
