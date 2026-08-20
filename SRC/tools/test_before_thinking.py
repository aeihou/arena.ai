#!/usr/bin/env python3
"""Unit tests for the BeforeThinking prompt-capture tool."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SCRIPT = TOOLS / "before_thinking.sh"
STORE = "AGENTS/.user/MyPrompts.md"


class BeforeThinkingTests(unittest.TestCase):
    def make_root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        return Path(temporary.name)

    def add(self, root: Path, *arguments: str, stdin: str | None = None):
        return subprocess.run(
            ["bash", str(SCRIPT), "--root", str(root), *arguments],
            capture_output=True,
            text=True,
            input=stdin,
        )

    def store_text(self, root: Path) -> str:
        return (root / STORE).read_text(encoding="utf-8")

    def test_first_prompt_creates_store_with_header(self) -> None:
        root = self.make_root()

        result = self.add(root, "--session", "2026-01-01", "first prompt")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            "# My prompts\n\nVerbatim developer prompts kept for this workspace. "
            "Entries are appended by\n`SRC/tools/before_thinking.sh` before an agent "
            "starts reasoning, newest last.\n\n## Session 2026-01-01\n\n### Prompt 1\n\n"
            "```text\nfirst prompt\n```\n",
            self.store_text(root),
        )

    def test_prompts_are_numbered_and_grouped_by_session(self) -> None:
        root = self.make_root()
        self.add(root, "--session", "2026-01-01", "first prompt")
        self.add(root, "--session", "2026-01-01", "second prompt")

        self.add(root, "--session", "2026-01-02", "third prompt")
        text = self.store_text(root)

        self.assertEqual(1, text.count("## Session 2026-01-01"))
        self.assertEqual(1, text.count("## Session 2026-01-02"))
        self.assertIn("### Prompt 3", text)
        self.assertLess(text.index("first prompt"), text.index("third prompt"))

    def test_repeated_newest_prompt_is_ignored(self) -> None:
        root = self.make_root()
        self.add(root, "the same prompt")
        before = self.store_text(root)

        result = self.add(root, "the same prompt")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("already recorded", result.stdout)
        self.assertEqual(before, self.store_text(root))

    def test_stdin_keeps_multiline_text_verbatim(self) -> None:
        root = self.make_root()

        result = self.add(root, "--stdin", stdin="line one\nline two\t\n")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("```text\nline one\nline two\n```", self.store_text(root))

    def test_function_form_matches_the_pseudocode(self) -> None:
        root = self.make_root()

        result = subprocess.run(
            [
                "bash",
                "-c",
                'source "$1"; BeforeThinking.Add --root "$2" "sourced prompt"',
                "bash",
                str(SCRIPT),
                str(root),
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("sourced prompt", self.store_text(root))

    def test_custom_store_and_dry_run(self) -> None:
        root = self.make_root()

        result = self.add(root, "--file", "NOTES/prompts.md", "--dry-run", "prompt")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("would append prompt 1 to NOTES/prompts.md", result.stdout)
        self.assertFalse((root / "NOTES").exists())

        self.add(root, "--file", "NOTES/prompts.md", "prompt")
        self.assertTrue((root / "NOTES" / "prompts.md").is_file())

    def test_list_prints_the_store(self) -> None:
        root = self.make_root()
        self.add(root, "listed prompt")

        result = self.add(root, "--list")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("listed prompt", result.stdout)

    def test_invalid_usage_returns_environment_status(self) -> None:
        root = self.make_root()

        self.assertEqual(2, self.add(root).returncode)
        self.assertEqual(2, self.add(root, "   ").returncode)
        self.assertEqual(2, self.add(root, "--unknown", "prompt").returncode)
        self.assertEqual(2, self.add(root, "--list").returncode)


if __name__ == "__main__":
    unittest.main()
