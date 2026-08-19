/AGENTS/HAND-OFF/README.md

# Agent hand-off

Stable, portable hand-off rules for the next agent. Current semantic state lives
in [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](SESSION_CONTEXT.md), authoritative
operating rules remain in [`AGENTS/README.md`](../README.md), and plans remain in
[`DOCS/PLAN/README.md`](../../DOCS/PLAN/README.md).

## Portable identifiers

- `GitHub_User` means the owner derived from the `origin` remote.
- `repo` means the current repository derived from the working copy.
- `branch` means the current branch derived with `git branch --show-current`.

Never embed a specific account, repository name, or branch value in portable
agent instructions. Resolve them from Git and the current environment.

## Reload and self-describe

Do not trust a copied tree or branch name. Derive current state from the working
copy:

```sh
git fetch origin
git status --short --branch
python3 SRC/tools/self_consistency.py --describe
```

When asked to check broadly for updates, inspect other remote branches and infer
semantic intent. Do not copy malformed, stale, or branch-specific text.

## Current capabilities

- `SRC/tools/self_consistency.py` provides a complete relevant-file inventory,
  portable local verification, grouped developer-approved safe fixes, JSON
  output, and Markdown reports.
- `SRC/tools/test_self_consistency.py` covers the verifier with standard-library
  tests.
- `GITHUB/self-consistency.yml` is an inactive GitHub Actions template because
  the current GitHub connection cannot install workflow files.
- Plan status is indexed in [`DOCS/PLAN/README.md`](../../DOCS/PLAN/README.md);
  details and acceptance criteria live in each plan subfolder.

## Tracked session state

- Rewrite [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](SESSION_CONTEXT.md) with the
  latest semantic state after every meaningful completed change.
- Append one concise outcome to
  [`AGENTS/HAND-OFF/SESSION_LOG.md`](SESSION_LOG.md) in the same commit.
- Use Git history for old rolling-context versions; keep the log compact.
- Derive runtime metadata rather than recording it.

## Learned constraints

- Work, commit, and push only on the `branch` assigned to the session.
- User edits are authoritative; preserve their semantic intent during conflict
  resolution.
- Ask the developer before structural decisions. Once approved, implement and
  document them in the same turn.
- Keep `AGENTS/README.md` as the single source of operating instructions; do not
  duplicate its full workflow here.
- Every visible directory self-describes with `README.md` or `<NAME>.md`.
- Every `README.md` starts with its repository-absolute full path, such as
  `/AGENTS/HAND-OFF/README.md`.
- In every `README.md`, internal links display the repository-relative linked
  file name and target that file directly.
- Use canonical repository names, valid local Markdown links, clean text
  formatting, and no stale placeholders.

## Current decision state

- **Blocked:** [`DOCS/PLAN/CONTINUOUS_VERIFICATION/README.md`](../../DOCS/PLAN/CONTINUOUS_VERIFICATION/README.md)
  awaits GitHub workflow permission.
- **Deferred:** [`DOCS/PLAN/PG01/README.md`](../../DOCS/PLAN/PG01/README.md) awaits a concrete
  developer-selected purpose.
- **Continuous:** keep the plan registry, detailed plan status, and this hand-off
  short and consistent with repository reality.
