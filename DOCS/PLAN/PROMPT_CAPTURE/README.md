/DOCS/PLAN/PROMPT_CAPTURE/README.md

# Prompt capture

- **Status:** Completed
- **Updated:** 2026-08-19
- **Outcome:** Developer prompts are captured verbatim in a private folder by a
  reusable `BeforeThinking.Add` function.

Private, verbatim developer prompt store maintained before each thinking cycle.

## Goal

Preserve exactly what the developer asked, in order, so that intent survives
session boundaries and can be re-read before any agent starts reasoning.

## Decisions

1. Store prompts in the hidden folder `AGENTS/.user/`, created with
   [`SRC/tools/script.sh`](../../../SRC/tools/script.sh). Hidden folders are
   exempt from descriptor and subfolder-index rules, so a private area does not
   distort repository self-description.
2. Keep the store at `AGENTS/.user/MyPrompts.md`: one `## Session <date>`
   heading per session, `### Prompt N` entries numbered across the whole file,
   and each prompt inside a fenced `text` block so punctuation, pseudocode, and
   links survive unchanged.
3. Implement the pseudocode `BeforeThinking.Add(new Prompt)` literally in
   [`SRC/tools/before_thinking.sh`](../../../SRC/tools/before_thinking.sh):
   sourcing the file defines the `BeforeThinking.Add` shell function, and the
   same file runs as a command.
4. Only trailing blanks are normalized, because trailing whitespace is a
   machine-checked defect; nothing else is rewritten.
5. Re-adding the newest prompt is a no-op, so replaying a session capture is
   safe and idempotent.
6. Prompts are history, not instructions: authority still follows
   [`AGENTS/README.md`](../../../AGENTS/README.md), and the store never replaces
   rolling context or the compact log.

## Validation

- Focused fixtures in
  [`SRC/tools/test_before_thinking.py`](../../../SRC/tools/test_before_thinking.py)
  cover store creation, numbering, session grouping, duplicate suppression,
  stdin capture, the sourced function form, custom stores, dry runs, listing,
  and usage errors.
- [`SRC/tools/test_script.py`](../../../SRC/tools/test_script.py) covers hidden
  folders and descriptor-free construction.
- Self-consistency verification and the complete standard-library suite pass.
