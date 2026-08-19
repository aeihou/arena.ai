# tools

Portable repository-maintenance tools.

## Self-consistency verifier

Run the zero-dependency verifier from the repository root:

```sh
python3 SRC/tools/self_consistency.py
```

Derive a smart repository inventory and verify it in one command:

```sh
python3 SRC/tools/self_consistency.py --describe
```

For a guided developer prompt and Markdown report:

```sh
python3 SRC/tools/self_consistency.py --interactive
```

For automation, use `--format json` or `--report PATH`. Combine JSON with
`--describe` to receive an object containing both `description` and `findings`.
The verifier also ensures visible direct subfolders are indexed by their parent
folder documentation. The command exits with
status `0` when all checks pass, `1` when findings exist, and `2` for usage or
environment errors.

Run its test suite with:

```sh
python3 -m unittest discover -s SRC/tools -p 'test_*.py'
```
