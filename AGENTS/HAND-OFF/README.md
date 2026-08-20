/AGENTS/HAND-OFF/README.md

# Agent hand-off

Index for cross-session continuity. Operating procedure and authority are defined
only in [`AGENTS/README.md`](../README.md).

## Read in this order

1. [`AGENTS/README.md`](../README.md) — procedure, portability, and authority.
2. [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](SESSION_CONTEXT.md) — current semantic
   state and next direction.
3. [`DOCS/PLAN/README.md`](../../DOCS/PLAN/README.md) — registered plan status.
4. [`AGENTS/HAND-OFF/SESSION_LOG.md`](SESSION_LOG.md) — historical outcomes only
   when earlier context is needed.

## Content boundaries

- Current state belongs in
  [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](SESSION_CONTEXT.md).
- Historical outcomes belong in
  [`AGENTS/HAND-OFF/SESSION_LOG.md`](SESSION_LOG.md).
- Durable decisions belong under [`DOCS/PLAN/README.md`](../../DOCS/PLAN/README.md).
- Tool behavior belongs in [`SRC/tools/README.md`](../../SRC/tools/README.md).
- Developer prompts belong in [`AGENTS/.user/MyPrompts.md`](../.user/MyPrompts.md).

If context or history conflicts with higher-authority sources, derive reality and
repair the lower-authority file.
