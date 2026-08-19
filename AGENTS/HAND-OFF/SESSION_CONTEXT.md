# Rolling session context

- **Updated:** 2026-08-19
- **Purpose:** Give the next agent the smallest complete semantic state needed to
  continue safely.

## Latest outcome

- Repository self-description now enumerates every relevant file in text and
  JSON output.
- The portable hand-off plan is an executable rebuild contract with task-driven
  file discovery.
- Session tracking now combines this rolling context with an append-only compact
  log.

## Decisions in force

- Rewrite this file after every meaningful completed repository change.
- Append one compact semantic entry to
  [`AGENTS/HAND-OFF/SESSION_LOG.md`](SESSION_LOG.md) in the same commit.
- Track outcomes, decisions, validation, blockers, and next actions.
- Do not persist resolved account, repository, branch, commit, or changed-file
  metadata; derive runtime state from Git and self-description.
- Keep durable plan detail in
  [`DOCS/PLAN/README.md`](../../DOCS/PLAN/README.md), not in this file.

## Validation baseline

- Self-consistency verification passes.
- The standard-library test suite has 12 passing tests.
- Python 3.9 grammar compatibility passes.
- Generated caches and local reports remain ignored.

## Blocked and deferred work

- **Blocked:** [`DOCS/PLAN/CONTINUOUS_VERIFICATION/README.md`](../../DOCS/PLAN/CONTINUOUS_VERIFICATION/README.md)
  awaits GitHub workflow permission.
- **Deferred:** [`DOCS/PLAN/PG01/README.md`](../../DOCS/PLAN/PG01/README.md)
  awaits a concrete developer-selected purpose.

## Next agent

1. Fetch `origin` and inspect the current `branch`.
2. Run `python3 SRC/tools/self_consistency.py --describe` and verification.
3. Read [`DOCS/PLAN/README.md`](../../DOCS/PLAN/README.md).
4. Continue from the latest developer request without repeating completed work.
5. Before committing meaningful work, refresh this context and append the
   matching compact log entry.
