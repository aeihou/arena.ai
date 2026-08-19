/DOCS/PLAN/INTERACTIVE_FIXER/README.md

# Interactive verifier fixer

- **Status:** Completed
- **Updated:** 2026-08-19
- **Outcome:** Developers can preview and approve deterministic safe fixes by
  category from the verifier's interactive terminal flow.

## Goal

Turn verification findings into an efficient developer interaction without
removing developer control or enabling broad automatic rewrites.

## Approved interaction model

The developer selected grouped approval. The verifier previews finding counts and
asks once for each available category:

1. README full-path declarations.
2. README internal linked-file names and direct targets.
3. Trailing whitespace and final newlines.

Declined categories remain unchanged. Findings without a deterministic safe fix
remain report-only.

## Safeguards

- Interactive mode requires a terminal.
- Every category defaults to No.
- No file deletion, directory creation, or structural rewrite is included.
- Verification reruns after approved changes.
- Markdown report generation uses the post-fix findings.
- JSON mode remains non-interactive for automation.

## Acceptance criteria

- Each safe-fix category can be tested independently.
- Grouped fixes restore a representative malformed fixture to consistency.
- Existing report-only and automation behavior remains available.
- The verifier and complete unit test suite pass.
