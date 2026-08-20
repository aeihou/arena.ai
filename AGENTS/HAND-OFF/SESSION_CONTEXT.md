# Rolling session context

- **Updated:** 2026-08-19
- **Log revision:** 9
- **Purpose:** Minimal semantic state for the next agent.

## Latest outcome

- Created `AGENTS/.user/` as the developer prompt store.
- Recorded every prompt from this session in
  [`AGENTS/.user/MyPrompts.md`](../.user/MyPrompts.md).
- Added `BeforeThinking.Add(new Prompt)` so new requests are appended before
  other work.

## Current state

- Operating instructions: [`AGENTS/README.md`](../README.md)
- Active goal:
  [`DOCS/PLAN/SELF_DESCRIBING_REPOSITORY/README.md`](../../DOCS/PLAN/SELF_DESCRIBING_REPOSITORY/README.md)
- Plan status: [`DOCS/PLAN/README.md`](../../DOCS/PLAN/README.md)
- Tool usage: [`SRC/tools/README.md`](../../SRC/tools/README.md)
- Developer prompts: [`AGENTS/.user/MyPrompts.md`](../.user/MyPrompts.md)
- Historical outcomes: [`AGENTS/HAND-OFF/SESSION_LOG.md`](SESSION_LOG.md)

## Validation baseline

- Self-consistency verification passes.
- The complete standard-library test suite passes.
- Python 3.9 grammar and Git whitespace checks pass.

## Next agent

1. Follow [`AGENTS/README.md`](../README.md), including Before thinking.
2. Append each new developer prompt with
   `python3 SRC/tools/user_prompts.py before-thinking` before other work.
3. Use the folder-growth script when adding visible directories.
4. Preserve dynamic discovery; do not introduce static inventories or duplicated
   sources of truth.
