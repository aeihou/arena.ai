/AGENTS/README.md

## Instructions for agents

Authoritative operating procedure for the supported portable workspace.

Prioritize work against
[`DOCS/PLAN/SELF_DESCRIBING_REPOSITORY/README.md`](../DOCS/PLAN/SELF_DESCRIBING_REPOSITORY/README.md).

## Portability scope

This contract assumes Git, an `origin` remote hosted on GitHub, Python 3.9 or
newer, and the documented `AGENTS/`, `DOCS/PLAN/`, and `SRC/tools/` layout.
Equivalent paths may be installed elsewhere, but arbitrary hosts or layouts are
outside the current contract.

Portable identifiers are never committed as resolved values:

- `GitHub_User` — owner derived from `origin`.
- `repo` — repository derived from the working-copy root.
- `branch` — current branch derived from Git.

## Authority order

When information conflicts, use this order:

1. Current developer request and direct developer edits.
2. Repository and Git reality after fetching `origin`.
3. This file.
4. [`DOCS/PLAN/README.md`](../DOCS/PLAN/README.md) for plan status and each linked
   detail file for scope and acceptance criteria.
5. [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](HAND-OFF/SESSION_CONTEXT.md).
6. [`AGENTS/HAND-OFF/SESSION_LOG.md`](HAND-OFF/SESSION_LOG.md), which is history
   only.

Preserve the semantic intent of remote developer edits during conflict
resolution. Use `askDev` when intent is ambiguous; never silently overwrite it.

## Before work

### 1. Establish Git state

Run from the repository root:

```sh
git status --short --branch
branch=$(git branch --show-current)
test -n "$branch"
git fetch origin "$branch"
git rev-list --left-right --count HEAD...FETCH_HEAD
```

Interpret the counts as local-only then remote-only commits:

- `0 0` — synchronized.
- `0 N` — fast-forward with `git merge --ff-only FETCH_HEAD`.
- `N 0` — local work is ahead; continue without switching branches.
- `N M` — reconcile by rebasing local agent commits onto `FETCH_HEAD`, preserving
  remote developer intent. Stop for `askDev` if resolution is ambiguous.

Never switch from the assigned `branch`. Do not discard a dirty working tree. If
the branch is detached, `origin` is missing, fetch fails, or authentication is
unavailable, stop and report the blocker.

### 2. Derive repository state

```sh
python3 SRC/tools/self_consistency.py --describe
```

Then read [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](HAND-OFF/SESSION_CONTEXT.md) and
files relevant to the current request.

### 3. Verify and plan

```sh
python3 SRC/tools/self_consistency.py
```

Resolve findings. Use `--interactive` only for grouped developer-approved safe
fixes. Maintain [`DOCS/PLAN/README.md`](../DOCS/PLAN/README.md) and its linked
plan together when status or durable decisions change. Obtain developer approval
before structural changes.

## Validation levels

- **Documentation-only:** verifier and `git diff --check`.
- **Python or verifier:** documentation checks, full unit tests, and Python 3.9
  grammar compatibility.
- **Structural or workflow:** all checks plus developer approval and relevant
  runtime validation.
- **Blocked operation:** record the blocker and recheck procedure; do not claim
  completion.

The canonical commands and exit statuses live in
[`SRC/tools/README.md`](../SRC/tools/README.md).

## After meaningful work

A change is meaningful when it alters behavior, structure, instructions, plan
state, decisions, blockers, or next-agent understanding. Pure typo or formatting
corrections need no new log entry.

1. Run the applicable validation level.
2. Rewrite [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](HAND-OFF/SESSION_CONTEXT.md).
3. Append one entry with the next unique revision to
   [`AGENTS/HAND-OFF/SESSION_LOG.md`](HAND-OFF/SESSION_LOG.md); make the rolling
   `Log revision` match it.
4. Commit implementation and context together.
5. Fetch `branch` again, reconcile remote changes, and push only the assigned
   `branch` to `GitHub_User/repo`.

## Questions

Use `askDev` before guessing about intent, authority, structure, or destructive
changes.
