# Plans

Canonical registry for repository plans and decision records.

Subfolders:
- [`FILE_STRUCTURE/`](FILE_STRUCTURE/) — completed repository-structure optimization.
- [`PORTABLE_HAND_OFF/`](PORTABLE_HAND_OFF/) — completed portable agent-context plan.
- [`CONTINUOUS_VERIFICATION/`](CONTINUOUS_VERIFICATION/) — blocked CI activation plan.
- [`PG01/`](PG01/) — deferred playground definition plan.

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
| [File-structure optimization](FILE_STRUCTURE/) | Completed | Preserve the documented conventions. |
| [Portable agent hand-off](PORTABLE_HAND_OFF/) | Completed | Preserve derived identifiers and concise context. |
| [Continuous verification](CONTINUOUS_VERIFICATION/) | Blocked | Restore GitHub workflow permission, then activate the template. |
| [PG01 definition](PG01/) | Deferred | Ask the developer for a concrete playground purpose. |

## Maintenance rules

1. Keep detailed scope, decisions, and acceptance criteria in each plan's own
   `README.md`; keep this file as a concise registry.
2. Update a plan and this registry together whenever its status changes.
3. Ask the developer before structural decisions or moving a plan into active
   implementation.
4. Record blockers explicitly instead of repeatedly attempting blocked work.
5. Move completed implementation guidance to the relevant product or tool docs;
   plans retain only the decision record and validation outcome.
