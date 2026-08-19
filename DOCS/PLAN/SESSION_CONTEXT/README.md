/DOCS/PLAN/SESSION_CONTEXT/README.md

# Session-context hand-off

- **Status:** Completed
- **Updated:** 2026-08-19
- **Outcome:** The next agent receives current semantic state while a compact
  append-only log preserves cross-session outcomes.

## Goal

Keep enough context to continue work without replaying the conversation,
duplicating durable plans, or committing runtime-specific Git state.

## Developer-approved model

- **Tracking:** rolling context plus compact append-only ledger.
- **Detail:** semantic outcomes, decisions, validation, blockers, and next steps.
- **Update policy:** update after every meaningful completed repository change.

## Architecture

- Rolling current state:
  [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](../../../AGENTS/HAND-OFF/SESSION_CONTEXT.md)
- Compact historical outcomes:
  [`AGENTS/HAND-OFF/SESSION_LOG.md`](../../../AGENTS/HAND-OFF/SESSION_LOG.md)
- Stable hand-off rules:
  [`AGENTS/HAND-OFF/README.md`](../../../AGENTS/HAND-OFF/README.md)
- Durable plan status:
  [`DOCS/PLAN/README.md`](../README.md)

Git history preserves prior rolling-context versions, while the compact log makes
important outcomes discoverable without reading commit history.

## Rolling-context schema

The rolling file contains:

1. Latest outcome.
2. Decisions in force.
3. Validation baseline.
4. Blocked and deferred work.
5. Explicit next-agent actions.

Rewrite stale entries instead of accumulating history.

## Compact-log schema

Each appended entry contains:

- a date and semantic title;
- outcome;
- decisions; and
- validation.

Keep entries short. Do not restate detailed implementation, plans, or file diffs.

## Data boundaries

Track:

- what changed semantically;
- why the decision matters;
- what validation passed;
- unresolved blockers; and
- what the next agent should do.

Derive instead of tracking:

- account and repository values;
- current branch value;
- commit hashes;
- changed-file lists;
- full repository trees; and
- generated reports or caches.

## Update lifecycle

For every meaningful completed change:

1. Implement and validate the work.
2. Rewrite
   [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](../../../AGENTS/HAND-OFF/SESSION_CONTEXT.md)
   with the new current state.
3. Append one concise entry to
   [`AGENTS/HAND-OFF/SESSION_LOG.md`](../../../AGENTS/HAND-OFF/SESSION_LOG.md).
4. Update [`DOCS/PLAN/README.md`](../README.md) and a detailed plan only when plan
   status or decisions changed.
5. Commit context and implementation together.
6. Push only after fetching and reconciling the current `branch`.

Minor typo-only edits that do not affect next-agent understanding may reuse the
existing context without a new log entry.

## Acceptance criteria

- A new agent can identify the latest outcome, constraints, validation state,
  blockers, and next actions without conversation history.
- Rolling context contains no obsolete session history.
- The compact log is append-only and concise.
- Runtime-specific account, repository, branch, commit, and file-diff values are
  absent.
- Context changes ship in the same commit as meaningful work.
- All internal links and repository consistency checks pass.

## Failure prevention

- If rolling context conflicts with a detailed plan, the detailed plan and plan
  registry are authoritative.
- If context conflicts with the working copy, derive reality with Git and
  self-description, then repair context.
- Never use the compact log as an instruction source; it is historical evidence
  only.
