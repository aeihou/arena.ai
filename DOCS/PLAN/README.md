# PLAN

Plans & roadmap folder.

Subfolders:
- `FILE_STRUCTURE/` — file structure optimization plans.

## Pending plans

Agents maintain this section as plans are proposed, approved, completed, or
superseded. Structural decisions require developer approval before changes are
applied.

1. **Continuous verification** — install `GITHUB/self-consistency.yml` as an
   active workflow when GitHub workflow permissions are available.

## Deferred decisions

- **PG01 definition** — keep the playground minimal until the developer chooses
  a concrete purpose. Do not add speculative subfolders.

## Completed plans

- **File-structure optimization** — consolidated maintenance tooling under
  `SRC/tools/` and replaced duplicated hand-off content with a slim hand-off.
  See [`FILE_STRUCTURE/`](FILE_STRUCTURE/).
- **Smart self-description** — added repository-derived branch, inventory, and
  top-level purpose output to the verifier; parent documentation now indexes
  each direct visible subfolder.
- **Hand-off normalization** — moved inter-session context to the self-describing
  `AGENTS/HAND-OFF/README.md` path and made its pending/deferred state consistent
  with this plan.

## Self-consistency report generation

The portable verifier checks local Markdown links, canonical names, directory
self-description and child indexes, stale `.gitkeep` files, current Arena branch
references, and text formatting. Derive a current repository description with:

```sh
python3 SRC/tools/self_consistency.py --describe
```

Use its interactive terminal flow when collaborating with a developer:

```sh
python3 SRC/tools/self_consistency.py --interactive
```

The prompt offers to create `self-consistency-report.md`, which is ignored by
Git because it is a local generated artifact. To generate a report without
prompts—for example in another automation job—provide the destination directly:

```sh
python3 SRC/tools/self_consistency.py --report self-consistency-report.md
```

A report contains a pass/fail summary and an actionable table of findings. The
verifier does not modify repository content; developers retain control over all
fixes. A portable GitHub Actions template is available at
`GITHUB/self-consistency.yml`; install it under `.github/workflows/` when CI is
needed.
