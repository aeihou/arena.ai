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

## Folder growth

Create a named folder and its canonical README from the repository root:

```sh
python3 SRC/tools/new_folder.py path/to/NameOfFolder
python3 SRC/tools/new_folder.py path/to/NameOfFolder --summary "Short purpose."
python3 SRC/tools/new_folder.py NameOfFolder --approve-structure
```

The script makes the directory, writes `README.md` with the required
repository-absolute first line, and lists the child in the parent descriptor.
Top-level folders are structural and require `--approve-structure`. Exit status
is `0` for success and `2` for a rejected request.

## BeforeThinking prompts

Record the current developer prompt before any other work:

```sh
python3 SRC/tools/user_prompts.py before-thinking
python3 SRC/tools/user_prompts.py before-thinking "verbatim prompt"
python3 SRC/tools/user_prompts.py add "verbatim prompt"
```

`before-thinking` and `add` both implement `Add(new Prompt)` and append
[`AGENTS/.user/MyPrompts.md`](../../AGENTS/.user/MyPrompts.md). Stdin is required
when the prompt text is omitted. Exit status is `0` for success and `2` for a
rejected request.

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
