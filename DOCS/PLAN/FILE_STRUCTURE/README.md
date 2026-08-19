# File-structure optimization

Status: **implemented on 2026-08-19** after developer approval.

## Goal

Reduce root-level maintenance clutter without reorganizing domain folders before
their purposes are known. Keep agent context concise and derive repository state
from the working copy instead of maintaining a duplicated static tree.

## Decision

1. Consolidate repository-maintenance code under `SRC/tools/`.
2. Keep `GITHUB/` as the home of inactive GitHub templates.
3. Keep `PG01/` unchanged until its workspace requirements are approved.
4. Replace the detailed hand-off with a slim, self-describing hand-off that
   links to authoritative instructions and plans.
5. Ignore generated Python caches so verification never dirties Git status.

## Resulting structure

```text
arena.ai/
├── AEIHOU/                  owner context
├── AGENTS/                  authoritative instructions and slim hand-off
├── DOCS/PLAN/               plans and decision records
├── GITHUB/                  inactive GitHub templates
├── PG01/                    undefined playground; no premature scaffolding
└── SRC/
    └── tools/               maintenance verifier and tests
```

## Validation

The optimization is complete when:

- all verifier documentation and automation use `SRC/tools/` paths;
- every visible directory remains self-describing;
- the verifier and its tests pass from the repository root;
- no generated cache appears in `git status`; and
- the hand-off contains no hardcoded branch name or duplicated static tree.

## Deferred decision

The next structural decision is the purpose of `PG01`. Its subfolders should be
created only after the developer chooses its intended workflow.
