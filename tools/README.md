# tools

Portable repository-maintenance tools.

## Self-consistency verifier

Run the zero-dependency verifier from the repository root:

```sh
python3 tools/self_consistency.py
```

For a guided developer prompt and Markdown report:

```sh
python3 tools/self_consistency.py --interactive
```

For automation, use `--format json` or `--report PATH`. The command exits with
status `0` when all checks pass, `1` when findings exist, and `2` for usage or
environment errors.

Run its test suite with:

```sh
python3 -m unittest discover -s tools -p 'test_*.py'
```
