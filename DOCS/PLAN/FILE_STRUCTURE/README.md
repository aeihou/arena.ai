/DOCS/PLAN/FILE_STRUCTURE/README.md

# File-structure optimization

- **Status:** Completed
- **Updated:** 2026-08-19
- **Outcome:** Maintenance code and documentation have clear canonical homes.

## Goal

Reduce root clutter and prevent speculative structure while keeping repository
state discoverable from the working copy.

## Decisions

1. Keep maintenance code and tests under `SRC/tools/`.
2. Keep inactive GitHub templates under `GITHUB/`.
3. Keep plans and decision records under `DOCS/PLAN/`.
4. Keep portable hand-off files under `AGENTS/HAND-OFF/`.
5. Keep `PG01/` minimal until
   [`DOCS/PLAN/PG01/README.md`](../PG01/README.md) becomes active.
6. Ignore generated Python caches and local reports.
7. Derive structure with self-description; do not maintain a static tree.

## Validation

- Every visible directory has a descriptor.
- Parent descriptors index direct visible subfolders.
- Tool paths consistently use `SRC/tools/`.
- Generated artifacts do not dirty Git status.
- Self-description, verification, and tests pass from the repository root.
