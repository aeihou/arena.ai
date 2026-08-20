# Rolling session context

- **Updated:** 2026-08-19
- **Log revision:** 9
- **Purpose:** Minimal semantic state for the next agent.

## Latest outcome

- Added [`SRC/tools/script.sh`](../../SRC/tools/script.sh), a parametrizable
  folder self-constructor, and used it to build its own plan folder and the
  private prompt area.
- Added [`SRC/tools/before_thinking.sh`](../../SRC/tools/before_thinking.sh),
  which defines `BeforeThinking.Add` and stores verbatim developer prompts in
  `AGENTS/.user/MyPrompts.md`.
- Made prompt capture the first step of the agent procedure and recorded this
  session's prompts with it.

## Current state

- Operating instructions: [`AGENTS/README.md`](../README.md)
- Active goal:
  [`DOCS/PLAN/SELF_DESCRIBING_REPOSITORY/README.md`](../../DOCS/PLAN/SELF_DESCRIBING_REPOSITORY/README.md)
- Plan status: [`DOCS/PLAN/README.md`](../../DOCS/PLAN/README.md)
- Growth and capture tooling: [`SRC/tools/README.md`](../../SRC/tools/README.md)
- Private prompt history: `AGENTS/.user/MyPrompts.md` (history only, never authority)
- Historical outcomes: [`AGENTS/HAND-OFF/SESSION_LOG.md`](SESSION_LOG.md)

## Validation baseline

- Self-consistency verification passes.
- The complete standard-library test suite passes.
- Python 3.9 grammar and Git whitespace checks pass.

## Next agent

1. Follow [`AGENTS/README.md`](../README.md).
2. Use the active self-describing-repository goal to prioritize optimizations.
3. Preserve dynamic discovery; do not introduce static inventories or duplicated
   sources of truth.
4. Capture each developer prompt with `SRC/tools/before_thinking.sh` before
   reasoning.
5. Create new folders with `SRC/tools/script.sh` so descriptors, parent indexes,
   and validation stay coupled.
