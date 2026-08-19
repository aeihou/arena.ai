/AGENTS/README.md

## instructions for agents.

Authoritative, portable operating instructions for agents.

Subfolders:
- [`AGENTS/HAND-OFF/README.md`](HAND-OFF/README.md) — concise state and learned constraints for the next
  agent.

## EverytimeBeforeThink

### Update GitHub `GitHub_User/repo`

### `self.consistency.selfDescribe()`
Run `python3 SRC/tools/self_consistency.py --describe` to derive the current
branch, inventory counts, top-level purposes, and complete file list from the
working copy.

### Load tracked session context
Read [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](HAND-OFF/SESSION_CONTEXT.md) for the
latest semantic outcome, decisions, validation, blockers, and next actions.

### `self.consistency.verify()`
Run `python3 SRC/tools/self_consistency.py` and resolve every finding. Use
`--interactive` to preview grouped safe fixes for developer approval, or
`--report PATH` when a durable Markdown report is needed.

### Plan next optimization
Maintain the registry in [`DOCS/PLAN/README.md`](../DOCS/PLAN/README.md) and the
detailed document in the matching plan subfolder. Update both when status
changes, and ask the developer before applying structural decisions.

## EverytimeAfterThink

- For meaningful changes, refresh
  [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](HAND-OFF/SESSION_CONTEXT.md) and append
  one compact entry to
  [`AGENTS/HAND-OFF/SESSION_LOG.md`](HAND-OFF/SESSION_LOG.md).
- Commit implementation and context together.
- Push to GitHub `GitHub_User/repo` on the current `branch`.

## Any questions?

> `askDev`.
