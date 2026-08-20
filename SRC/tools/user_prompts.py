#!/usr/bin/env python3
"""Record developer prompts before thinking.

Implements:

    BeforeThinking.MyPrompts.md().Add(new Prompt)

The new prompt is appended to AGENTS/.user/MyPrompts.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Sequence

STORE = Path("AGENTS") / ".user"
PROMPTS = STORE / "MyPrompts.md"
HEADER = (
    "# MyPrompts\n"
    "\n"
    "Append-only developer prompts recorded by BeforeThinking.Add(new Prompt).\n"
    "Each entry is the verbatim request. Runtime Git identity is not recorded here.\n"
    "\n"
)
ENTRY_HEADING = re.compile(r"^## (\d+) — (\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


class PromptError(ValueError):
    """A rejected prompt-store request."""


def prompts_path(root: Path) -> Path:
    return root.expanduser().resolve() / PROMPTS


def _normalize_prompt(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [line.rstrip(" \t") for line in lines]
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    if not any(line.strip() for line in lines):
        raise PromptError("prompt is empty")
    return "\n".join(lines)


def _fence_for(text: str) -> str:
    longest = 0
    count = 0
    for char in text:
        if char == "`":
            count += 1
            if count > longest:
                longest = count
        else:
            count = 0
    return "`" * max(3, longest + 1)


def _next_number(text: str) -> int:
    numbers = [int(match.group(1)) for match in ENTRY_HEADING.finditer(text)]
    return max(numbers) + 1 if numbers else 1


def add_prompt(root: Path, text: str, when: date | None = None) -> int:
    """Append ``text`` to MyPrompts.md and return the new entry number."""
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise PromptError("repository root is not a directory: {}".format(root))
    cleaned = _normalize_prompt(text)
    path = prompts_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.is_file() else HEADER
    if existing and not existing.endswith("\n"):
        existing += "\n"
    if not existing.endswith("\n\n"):
        existing += "\n"
    number = _next_number(existing)
    fence = _fence_for(cleaned)
    entry = "## {} — {}\n\n{}\n{}\n{}\n".format(
        number,
        (when or date.today()).isoformat(),
        fence,
        cleaned,
        fence,
    )
    path.write_text(existing + entry, encoding="utf-8")
    return number


def before_thinking(root: Path, prompt: str, when: date | None = None) -> int:
    """Record a developer prompt before any other work."""
    return add_prompt(root, prompt, when=when)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=("add", "before-thinking"),
        help="Add(new Prompt); before-thinking is the named BeforeThinking hook",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="verbatim prompt; read stdin when omitted",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root (default: cwd)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    text = args.text
    if text is None:
        if sys.stdin.isatty():
            print("error: provide prompt text or pipe it on stdin", file=sys.stderr)
            return 2
        text = sys.stdin.read()
    try:
        number = before_thinking(args.root, text)
    except PromptError as error:
        print("error: {}".format(error), file=sys.stderr)
        return 2
    print("Added prompt {} to {}".format(number, PROMPTS.as_posix()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
