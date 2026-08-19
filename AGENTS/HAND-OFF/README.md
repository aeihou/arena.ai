# Agent hand-off

Smart, minimal session context for the next agent. Authoritative operating rules
remain in [`AGENTS/README.md`](../README.md); plans remain in
[`DOCS/PLAN/README.md`](../../DOCS/PLAN/README.md).

## Portable identifiers

- `GitHub_User` means the owner derived from the `origin` remote.
- `repo` means the current repository derived from the working copy.

Never embed a specific account, repository name, or session branch in portable
agent instructions. Resolve them from Git and the current environment.

## Reload and self-describe

Do not trust a copied tree or branch name. Derive current state from the working
copy:

```sh
git fetch origin
git status --short --branch
python3 SRC/tools/self_consistency.py --describe
```

When asked to check broadly for updates, inspect other remote Arena branches and
infer semantic intent. Do not copy malformed, stale, or branch-specific text.

## Current capabilities

- `SRC/tools/self_consistency.py` provides portable local verification,
  interactive developer prompts, JSON output, and Markdown reports.
- `SRC/tools/test_self_consistency.py` covers the verifier with standard-library
  tests.
- `GITHUB/self-consistency.yml` is an inactive GitHub Actions template because
  the current GitHub connection cannot install workflow files.
- Repository structure and pending work are documented under `DOCS/PLAN/`.

## Learned constraints

- Work, commit, and push only on the Arena branch assigned to the session.
- User edits are authoritative; preserve their semantic intent during conflict
  resolution.
- Ask the developer before structural decisions. Once approved, implement and
  document them in the same turn.
- Keep `AGENTS/README.md` as the single source of operating instructions; do not
  duplicate its full workflow here.
- Every visible directory self-describes with `README.md` or `<NAME>.md`.
- Use canonical repository names, valid local Markdown links, clean text
  formatting, and no stale placeholders.

## Current decision state

- **Pending:** activate the GitHub Actions template when workflow permissions
  are available.
- **Deferred:** keep `PG01` minimal until the developer chooses a concrete
  purpose.
- **Continuous:** keep plans and this hand-off short, current, and derived from
  repository reality.
