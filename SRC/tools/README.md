/SRC/tools/README.md

# tools

Portable, standard-library repository maintenance.

## Verifier commands

Run from the repository root:

```sh
# Verify
python3 SRC/tools/self_consistency.py

# Describe identity, sync, directories, descriptors, files, and purposes, then verify
python3 SRC/tools/self_consistency.py --describe

# Preview grouped safe fixes for developer approval
python3 SRC/tools/self_consistency.py --interactive

# Automation and durable reports
python3 SRC/tools/self_consistency.py --format json
python3 SRC/tools/self_consistency.py --report self-consistency-report.md
```

Combine `--describe --format json` for structured description and findings,
including `github_user`, `sync`, `ahead`, `behind`, `directory_paths`,
`directory_descriptors`, and `file_paths`. `sync` is derived from local Git
state and is one of `no-git`, `detached`, `no-origin`, `remote-branch-absent`,
`synchronized`, `ahead`, `behind`, `diverged`, or `unknown`. Interactive
prompts default to No and never delete files or alter directory structure.

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
python3 -m py_compile SRC/tools/self_consistency.py SRC/tools/test_self_consistency.py
git diff --check
```
