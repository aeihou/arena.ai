/DOCS/PLAN/SELF_CONSTRUCTOR/README.md

# Self-constructing folders

- **Status:** Completed
- **Updated:** 2026-08-19
- **Outcome:** New folders are created with their canonical descriptor and
  validated by an immediate session reload.

Portable folder self-construction with descriptor, parent index, and session
reload.

## Goal

Turn the developer pseudocode
`selfConstructor(nameOfFolder().newFile("nameOfFolder.md")); newSession.Reload();`
into a parametrizable, repeatable command that grows the repository without
breaking any documented invariant.

## Decisions

1. Keep the tool at [`SRC/tools/script.sh`](../../../SRC/tools/script.sh) with
   the other portable maintenance tools; it depends only on Bash, coreutils,
   Git, and the existing verifier.
2. Support both canonical descriptor shapes: `NAME/NAME.md` by default and
   `NAME/README.md` when the folder needs a repository-absolute path line.
3. Update the parent descriptor's subfolder index automatically, because
   unlisted subfolders are a machine-checked defect.
4. Implement `newSession.Reload()` as re-derivation, not mutation: report the
   branch and working-tree state, name the files a next agent must re-read, and
   run [`SRC/tools/self_consistency.py`](../../../SRC/tools/self_consistency.py).
5. Never write session context, log entries, or plan status automatically; those
   remain developer-reviewed edits under [`AGENTS/README.md`](../../../AGENTS/README.md).
6. Fail closed: unknown options, unsafe names, and missing parents exit with
   status `2`, and reload findings exit with status `1`.

## Validation

- Focused fixtures in [`SRC/tools/test_script.py`](../../../SRC/tools/test_script.py)
  cover descriptor shapes, metadata, parent indexing, dry runs, idempotency,
  forced rewrites, reload findings, and usage errors.
- This plan folder was created by the first real execution of the tool, and the
  reload immediately reported the missing registry entry and subfolder index.
- Self-consistency verification and the complete standard-library suite pass.
