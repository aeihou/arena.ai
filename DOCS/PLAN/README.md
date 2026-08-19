/DOCS/PLAN/README.md

# Plans

Canonical registry for repository plans and decision records.

Subfolders:
- [`DOCS/PLAN/FILE_STRUCTURE/README.md`](FILE_STRUCTURE/README.md) — completed repository-structure optimization.
- [`DOCS/PLAN/PORTABLE_HAND_OFF/README.md`](PORTABLE_HAND_OFF/README.md) — completed portable agent-context plan.
- [`DOCS/PLAN/INTERACTIVE_FIXER/README.md`](INTERACTIVE_FIXER/README.md) — completed grouped safe-fix interaction plan.
- [`DOCS/PLAN/CONTINUOUS_VERIFICATION/README.md`](CONTINUOUS_VERIFICATION/README.md) — blocked CI activation plan.
- [`DOCS/PLAN/PG01/README.md`](PG01/README.md) — deferred playground definition plan.

## Status model

| Status | Meaning |
|---|---|
| Proposed | An idea has been documented but not reviewed. |
| Pending approval | The developer must approve a decision before implementation. |
| Blocked | The plan is approved or actionable but an external dependency prevents progress. |
| Deferred | No action is expected until its trigger or purpose becomes clear. |
| Completed | Acceptance criteria were met and the result was validated. |
| Superseded | A linked plan replaced this plan. |

## Registry

| Plan | Status | Next action |
|---|---|---|
| [`DOCS/PLAN/FILE_STRUCTURE/README.md`](FILE_STRUCTURE/README.md) | Completed | Preserve the documented conventions. |
| [`DOCS/PLAN/PORTABLE_HAND_OFF/README.md`](PORTABLE_HAND_OFF/README.md) | Completed | Preserve derived identifiers and concise context. |
| [`DOCS/PLAN/INTERACTIVE_FIXER/README.md`](INTERACTIVE_FIXER/README.md) | Completed | Keep fixes deterministic and developer-approved. |
| [`DOCS/PLAN/CONTINUOUS_VERIFICATION/README.md`](CONTINUOUS_VERIFICATION/README.md) | Blocked | Restore GitHub workflow permission, then activate the template. |
| [`DOCS/PLAN/PG01/README.md`](PG01/README.md) | Deferred | Ask the developer for a concrete playground purpose. |

## Maintenance rules

1. Keep detailed scope, decisions, and acceptance criteria in each plan's own
   `README.md`; keep this file as a concise registry.
2. Update a plan and this registry together whenever its status changes.
3. Ask the developer before structural decisions or moving a plan into active
   implementation.
4. Record blockers explicitly instead of repeatedly attempting blocked work.
5. Move completed implementation guidance to the relevant product or tool docs;
   plans retain only the decision record and validation outcome.
