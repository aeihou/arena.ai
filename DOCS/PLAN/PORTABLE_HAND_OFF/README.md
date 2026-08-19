# Portable agent hand-off

- **Status:** Completed
- **Updated:** 2026-08-19
- **Outcome:** Agent context is concise, self-describing, and free of embedded
  account, repository, and branch values.

## Goal

Make agent instructions transferable between repositories and sessions without
copying stale identity or branch state.

## Decisions

1. Store inter-session context at
   [`AGENTS/HAND-OFF/README.md`](../../../AGENTS/HAND-OFF/README.md).
2. Keep authoritative operating rules in
   [`AGENTS/README.md`](../../../AGENTS/README.md) rather than duplicating them.
3. Use `GitHub_User`, `repo`, and `branch` as portable identifiers.
4. Resolve actual values from the `origin` remote, current working copy, and Git.
5. Generate repository inventory with
   `python3 SRC/tools/self_consistency.py --describe` instead of maintaining a
   static tree in the hand-off.
6. Treat hardcoded current branch values in Markdown as consistency findings.

## Acceptance criteria

- Agent documentation contains no embedded account, repository, or branch value.
- The hand-off links to authoritative instructions and the plan registry.
- Repository self-description and verification pass from the root.
- The hand-off distinguishes blocked and deferred work without duplicating full
  plan details.

## Ongoing constraint

Future agent-documentation changes must preserve portable identifiers and derive
runtime state rather than committing it.
