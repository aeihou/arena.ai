# PLAN

Plans & roadmap folder.

Subfolders:
- `FILE_STRUCTURE/` — file structure optimization plans.

## Pending plans

Agents maintain this section as plans are proposed, approved, completed, or
superseded. Structural decisions require developer approval before changes are
applied.

1. **File-structure optimization** — document an actionable proposal in
   `FILE_STRUCTURE/` and request developer approval.
2. **Continuous verification** — install `GITHUB/self-consistency.yml` as an
   active workflow when GitHub workflow permissions are available.
3. **PG01 definition** — agree on the playground's purpose and whether it needs
   dedicated source and documentation subfolders.

## Self-consistency report generation

The portable verifier checks local Markdown links, canonical names, directory
self-description, stale `.gitkeep` files, current Arena branch references, and
text formatting.

Use its interactive terminal flow when collaborating with a developer:

```sh
python3 tools/self_consistency.py --interactive
```

The prompt offers to create `self-consistency-report.md`, which is ignored by
Git because it is a local generated artifact. To generate a report without
prompts—for example in another automation job—provide the destination directly:

```sh
python3 tools/self_consistency.py --report self-consistency-report.md
```

A report contains a pass/fail summary and an actionable table of findings. The
verifier does not modify repository content; developers retain control over all
fixes. A portable GitHub Actions template is available at
`GITHUB/self-consistency.yml`; install it under `.github/workflows/` when CI is
needed.
