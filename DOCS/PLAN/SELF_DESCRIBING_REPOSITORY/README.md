/DOCS/PLAN/SELF_DESCRIBING_REPOSITORY/README.md

# Self-describing repository

- **Status:** Active
- **Updated:** 2026-08-19
- **Outcome:** The repository continuously describes its structure, preserves
  portable session continuity, and validates growth against shared conventions.

## Goal

Maintain a repository that is self-described, portable across supported
workspaces, dynamically extensible, session-aware, and self-consistent.

## Invariants

- Every relevant file and directory is discoverable at runtime.
- Every visible directory has a canonical descriptor.
- Parent descriptors index direct visible subfolders.
- Instructions, current context, historical outcomes, plans, and tool behavior
  each have one source of truth.
- Session context and compact history use synchronized monotonic revisions.
- Runtime identity and branch values are derived rather than committed.
- Growth updates descriptors, registries, context, tests, and validation together.

## Dynamic growth protocol

When adding a directory, plan, capability, or hand-off rule:

1. Add or update its canonical descriptor.
2. Link it from the immediate parent or registry.
3. Extend generic verification when the invariant is machine-checkable.
4. Add a focused fixture for new verifier behavior.
5. Refresh rolling context and append the next log revision.
6. Run the validation level defined in
   [`AGENTS/README.md`](../../../AGENTS/README.md).

Do not maintain copied static trees or manually curated file inventories;
self-description derives them from the working copy.

## Current capability

`python3 SRC/tools/self_consistency.py --describe` reports repository identity,
derived `GitHub_User` and branch sync, counts, top-level purposes, every
relevant directory with its descriptor, every relevant file, and consistency
findings. JSON exposes the same data for tools.

## Active direction

Keep this plan Active as the repository's north star. New optimizations should
strengthen one or more of these properties without duplicating canonical content:

- self-description;
- portable session hand-off;
- dynamic growth; or
- machine-enforced consistency.

## Acceptance criteria

- A first-time agent can discover what exists, where authoritative information
  lives, what changed, and what to do next.
- New structure is visible without editing a static inventory.
- Context remains portable and fresh across same-day sessions.
- Registry, descriptor, link, and validation guards pass after growth.
- The complete test suite and applicable runtime checks pass.
