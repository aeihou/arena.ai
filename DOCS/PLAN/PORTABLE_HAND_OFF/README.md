/DOCS/PLAN/PORTABLE_HAND_OFF/README.md

# Portable agent hand-off

- **Status:** Completed
- **Revision:** 4
- **Updated:** 2026-08-19
- **Outcome:** Agent context can move between repositories and sessions without
  persisting account, repository, or branch values.

## Purpose

Define the contract, architecture, rebuild procedure, and validation criteria for
a concise hand-off that derives runtime state instead of copying stale state.

## Portability contract

Portable documentation uses three identifiers:

- `GitHub_User` — resolve the owner from the `origin` remote.
- `repo` — resolve the repository from the working-copy root.
- `branch` — resolve the current branch with `git branch --show-current`.

These are documentation identifiers, not values to replace and commit. Commands
may display resolved values at runtime, but portable Markdown must not persist
them.

## Sources of truth

Each concern has one canonical file:

- Operating instructions:
  [`AGENTS/README.md`](../../../AGENTS/README.md)
- Stable hand-off rules and learned constraints:
  [`AGENTS/HAND-OFF/README.md`](../../../AGENTS/HAND-OFF/README.md)
- Rolling next-agent state:
  [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](../../../AGENTS/HAND-OFF/SESSION_CONTEXT.md)
- Compact semantic history:
  [`AGENTS/HAND-OFF/SESSION_LOG.md`](../../../AGENTS/HAND-OFF/SESSION_LOG.md)
- Plan statuses and next actions:
  [`DOCS/PLAN/README.md`](../README.md)
- Verifier behavior and local usage:
  [`SRC/tools/README.md`](../../../SRC/tools/README.md)
- Prepared continuous-verification workflow:
  [`GITHUB/self-consistency.yml`](../../../GITHUB/self-consistency.yml)

Do not duplicate a source of truth. Link to it by repository-relative file name.

## Agent load sequence

1. Fetch `origin` without embedding a branch value in documentation.
2. Read [`AGENTS/README.md`](../../../AGENTS/README.md).
3. Run `python3 SRC/tools/self_consistency.py --describe` to discover every file
   as well as repository purpose and counts.
4. Read
   [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](../../../AGENTS/HAND-OFF/SESSION_CONTEXT.md)
   for the latest semantic continuation state.
5. Read other files relevant to the task. Include
   [`AGENTS/HAND-OFF/README.md`](../../../AGENTS/HAND-OFF/README.md) when stable
   hand-off constraints are needed.
6. Run `python3 SRC/tools/self_consistency.py` and resolve findings.
7. Read [`DOCS/PLAN/README.md`](../README.md) for blocked, deferred, and active
   decisions.
8. Use `askDev` before structural changes or when intent remains ambiguous.

## Rebuild procedure

Use this procedure when installing or repairing the hand-off system in another
repository.

### 1. Establish canonical documents

Create the operating instructions, hand-off, plan registry, and tool
documentation at the paths listed under Sources of truth. Every visible folder
must describe itself.

### 2. Normalize README contracts

For every README:

- put its repository-absolute full path on line 1;
- keep the human-readable heading after the path declaration;
- display repository-relative file names for internal links; and
- link directly to files rather than implicitly to directory README files.

### 3. Keep the hand-off minimal

Include only:

- commands that derive current state;
- capabilities that affect the next session;
- learned constraints not already expressed by operating instructions; and
- concise blocked and deferred decision state linked to detailed plans.

Exclude copied directory trees, resolved identifiers, session branch values,
implementation histories, and duplicated operating rules.

### 4. Restore verification

The portable verifier must check:

- valid local Markdown links;
- README full-path declarations;
- canonical internal README link names and direct file targets;
- folder descriptions and direct-child indexes;
- stale placeholders;
- hardcoded current branch values;
- generic canonical naming; and
- trailing whitespace and final newlines.

### 5. Restore developer interaction

Interactive verification uses grouped approval for deterministic safe fixes:

1. README full paths.
2. README internal links.
3. Text formatting.

Every prompt defaults to No. Structural changes, deletion, and ambiguous content
remain outside automatic fixes and require `askDev`.

### 6. Validate the rebuild

From the repository root, run:

```sh
python3 SRC/tools/self_consistency.py --describe
python3 SRC/tools/self_consistency.py
python3 -m unittest discover -s SRC/tools -p 'test_*.py'
git diff --check
git status --short
```

The rebuild is complete only when verification and tests pass and generated
artifacts do not dirty Git status.

## Acceptance criteria

- No portable agent document embeds an account, repository, or branch value.
- Every README declares its correct full path on line 1.
- Every internal README link displays the linked repository-relative file name
  and targets the file directly.
- Runtime state is derived from Git and the working copy.
- Self-description enumerates every relevant repository file instead of only
  reporting counts and top-level folders.
- The hand-off links to canonical instructions and detailed plans instead of
  duplicating them.
- Developer approval gates structural changes and grouped safe fixes.
- Repository self-description, verification, tests, and Git whitespace checks
  pass.

## Change protocol

When this contract changes:

1. Update this decision record.
2. Update the canonical implementation or instruction file.
3. Add or update verifier tests when the rule is machine-checkable.
4. Run the validation sequence.
5. Refresh
   [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](../../../AGENTS/HAND-OFF/SESSION_CONTEXT.md)
   and append the compact semantic outcome to
   [`AGENTS/HAND-OFF/SESSION_LOG.md`](../../../AGENTS/HAND-OFF/SESSION_LOG.md).
6. Update the parent plan registry if status or next action changes.
7. Commit and push only on the current `branch`.

## Decision history

- **Revision 1:** established portable identifiers, smart self-description,
  canonical hand-off location, README full paths, and linked-file naming.
- **Revision 2:** rebuilt the plan as an executable portability contract with a
  load sequence, source boundaries, rebuild procedure, interaction safeguards,
  validation sequence, and change protocol.
- **Revision 3:** made self-description enumerate the complete relevant file set
  and changed loading from a hardcoded hand-off step to task-driven discovery.
- **Revision 4:** added rolling semantic session context and a compact append-only
  outcome log, both updated with every meaningful change.
