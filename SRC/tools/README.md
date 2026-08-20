/SRC/tools/README.md

# tools

Portable, standard-library repository maintenance.

## Verifier commands

Run from the repository root:

```sh
# Verify
python3 SRC/tools/self_consistency.py

# Describe directories, descriptors, files, and top-level purposes, then verify
python3 SRC/tools/self_consistency.py --describe

# Preview grouped safe fixes for developer approval
python3 SRC/tools/self_consistency.py --interactive

# Automation and durable reports
python3 SRC/tools/self_consistency.py --format json
python3 SRC/tools/self_consistency.py --report self-consistency-report.md
```

Combine `--describe --format json` for structured description and findings,
including `directory_paths`, `directory_descriptors`, and `file_paths`.
Interactive prompts default to No and never delete files or alter directory
structure.

## Folder self-construction

`script.sh` creates a folder with its canonical descriptor, keeps the parent
descriptor's subfolder index truthful, and then reloads session state by
re-deriving Git and consistency reality.

```sh
# Create NAME/NAME.md, index it in the parent descriptor, and reload
SRC/tools/script.sh NAME

# Preview without touching the working copy
SRC/tools/script.sh --dry-run NAME

# Create a README-style descriptor with metadata inside another parent
SRC/tools/script.sh --parent DOCS/PLAN --descriptor readme \
  --title "Plan title" --summary "One-sentence purpose." \
  --metadata "Status: Proposed" --metadata "Updated: YYYY-MM-DD" NAME

# Construct several folders, keep the parent index manual, and skip the reload
SRC/tools/script.sh --index skip --no-reload NAME OTHER
```

Options: `--root`, `--parent`, `--descriptor {self,readme,none}`, `--title`,
`--summary`, `--metadata "Key: Value"` (repeatable), `--index {auto,skip}`,
`--force`, `--dry-run`, `--describe`, `--no-reload`, `--help`. Existing
descriptors are preserved unless `--force` is given, and the reload never
rewrites session context, logs, or plan status. Hidden names such as `.user` are
allowed and stay out of the parent index, because descriptor and index rules only
apply to visible folders. Exit status matches the verifier: `0` success, `1`
reload findings, `2` usage or environment errors.

## Prompt capture

`before_thinking.sh` implements `BeforeThinking.Add(new Prompt)`. It appends a
verbatim developer prompt to the private store `AGENTS/.user/MyPrompts.md` before
an agent starts reasoning.

```sh
# Command form
SRC/tools/before_thinking.sh "the developer prompt"

# Multi-line prompts
SRC/tools/before_thinking.sh --stdin <<'PROMPT'
first line
second line
PROMPT

# Function form
source SRC/tools/before_thinking.sh
BeforeThinking.Add "the developer prompt"

# Review the store
SRC/tools/before_thinking.sh --list
```

Options: `--root`, `--file`, `--session`, `--stdin`, `--list`, `--dry-run`,
`--verify`, `--help`. Prompts are grouped under a `## Session <date>` heading and
numbered across the file; only trailing blanks are normalized. Re-adding the
newest prompt is a no-op, so replaying a capture is safe.

## Enforced rules

The verifier checks local links, README contracts, folder indexes, placeholders,
portable branch references, plan registry/detail agreement, rolling context,
compact log entries, canonical naming, whitespace, and final newlines. Plan and
context rules are discovered from semantic Markdown headings rather than fixed
repository paths. Interactive mode can safely fix README paths, README links, and
text formatting.

Exit status is `0` for success, `1` for findings, and `2` for usage or environment
errors.

## Tests

```sh
python3 -m unittest discover -s SRC/tools -p 'test_*.py'
```

`test_self_consistency.py` covers the verifier, `test_script.py` covers folder
self-construction, and `test_before_thinking.py` covers prompt capture.
