# PLAN

Plans & roadmap folder.

Subfolders:
- `FILE_STRUCTURE/` — file structure optimization plans.

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
