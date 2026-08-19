/DOCS/PLAN/PORTABLE_HAND_OFF/README.md

# Portable agent hand-off

- **Status:** Completed
- **Revision:** 6
- **Updated:** 2026-08-19
- **Outcome:** Agent continuity is portable, derived from repository reality, and
  split across canonical documents.

## Goal

Transfer useful agent context between repositories and sessions without copying
stale runtime state or duplicating instructions, plans, history, and tool docs.

## Contract

Portability covers GitHub repositories with Git, Python 3.9 or newer, and the
canonical workspace layout. Other hosts and arbitrary layouts require an adapted
installation.

- Use `GitHub_User`, `repo`, and `branch` as unresolved portable identifiers.
- Derive actual values from `origin`, the working-copy root, and Git.
- Start every README with its repository-absolute path.
- Name internal README links by repository-relative target file and link directly
  to that file.
- Discover current files with `python3 SRC/tools/self_consistency.py --describe`.

## Canonical documents

- Instructions: [`AGENTS/README.md`](../../../AGENTS/README.md)
- Hand-off index: [`AGENTS/HAND-OFF/README.md`](../../../AGENTS/HAND-OFF/README.md)
- Current context:
  [`AGENTS/HAND-OFF/SESSION_CONTEXT.md`](../../../AGENTS/HAND-OFF/SESSION_CONTEXT.md)
- Historical outcomes:
  [`AGENTS/HAND-OFF/SESSION_LOG.md`](../../../AGENTS/HAND-OFF/SESSION_LOG.md)
- Plan registry: [`DOCS/PLAN/README.md`](../README.md)
- Tool usage: [`SRC/tools/README.md`](../../../SRC/tools/README.md)

Each concern has one source of truth. Other documents link to it instead of
restating it.

## Transfer checklist

1. Install the canonical documents at equivalent repository-relative paths.
2. Replace resolved identity and branch values with portable identifiers.
3. Normalize README path declarations and internal links.
4. Run self-description to discover the actual file set.
5. Read current context and the plan registry.
6. Run the verifier and tests documented in
   [`SRC/tools/README.md`](../../../SRC/tools/README.md).
7. Ask the developer before ambiguous or structural changes.

## Content boundaries

Keep in hand-off context:

- latest semantic outcome;
- current constraints or exceptions;
- validation state; and
- next-agent direction.

Do not keep there:

- copied repository trees or file lists;
- resolved account, repository, branch, or commit values;
- duplicated instructions or plan detail;
- implementation history; or
- tool usage already documented elsewhere.

## Acceptance criteria

- Runtime state is derived rather than committed.
- The next agent can find instructions, current context, plans, history, and tool
  usage from the hand-off index.
- No canonical concern is maintained in multiple documents.
- README and link contracts pass automated verification.
- Session context and history follow
  [`DOCS/PLAN/SESSION_CONTEXT/README.md`](../SESSION_CONTEXT/README.md).

## Decision history

- **Revisions 1–3:** established portable identifiers, README contracts, smart
  self-description, and a rebuild procedure.
- **Revision 4:** added rolling context and compact semantic history.
- **Revision 5:** removed repeated procedures and made canonical ownership and
  content boundaries explicit.
- **Revision 6:** clarified portability scope and delegated authority, Git
  reconciliation, validation levels, and completion rules to agent instructions.
