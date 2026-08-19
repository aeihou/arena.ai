/AGENTS/HAND-OFF/README.md

# Agent hand-off

Portable index for cross-session continuity. Keep rules, current state, history,
and durable plans separate.

## Read in this order

1. [`AGENTS/README.md`](../README.md) — operating instructions.
2. [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](SESSION_CONTEXT.md) — current semantic
   state and next action.
3. [`DOCS/PLAN/README.md`](../../DOCS/PLAN/README.md) — authoritative plan status.
4. [`AGENTS/HAND-OFF/SESSION_LOG.md`](SESSION_LOG.md) — historical outcomes only
   when earlier context is needed.

## Portable identifiers

- `GitHub_User` — owner derived from `origin`.
- `repo` — repository derived from the working-copy root.
- `branch` — current branch derived from Git.

Never commit resolved identifier values to portable agent documents.

## Boundaries

- Instructions belong in [`AGENTS/README.md`](../README.md).
- Current state belongs in
  [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](SESSION_CONTEXT.md).
- Historical outcomes belong in
  [`AGENTS/HAND-OFF/SESSION_LOG.md`](SESSION_LOG.md).
- Durable decisions belong under [`DOCS/PLAN/README.md`](../../DOCS/PLAN/README.md).
- Tool behavior belongs in [`SRC/tools/README.md`](../../SRC/tools/README.md).

If documents conflict, derive repository reality with Git and self-description,
then repair the lower-authority context or history file.
