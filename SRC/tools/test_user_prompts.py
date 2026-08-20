#!/usr/bin/env python3
"""Unit tests for BeforeThinking.Add(new Prompt)."""

from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

import user_prompts


class UserPromptTests(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        return temporary, Path(temporary.name)

    def test_before_thinking_creates_store_and_numbers_entries(self) -> None:
        temporary, root = self.make_root()
        self.addCleanup(temporary.cleanup)
        day = date(2026, 8, 19)

        first = user_prompts.before_thinking(root, "first prompt", when=day)
        second = user_prompts.add_prompt(root, "second prompt", when=day)

        self.assertEqual(1, first)
        self.assertEqual(2, second)
        text = user_prompts.prompts_path(root).read_text(encoding="utf-8")
        self.assertIn("# MyPrompts\n", text)
        self.assertIn("## 1 — 2026-08-19\n", text)
        self.assertIn("```\nfirst prompt\n```\n", text)
        self.assertIn("```\nsecond prompt\n```\n", text)
        self.assertTrue(text.endswith("\n"))

    def test_cli_before_thinking_reads_argument(self) -> None:
        temporary, root = self.make_root()
        self.addCleanup(temporary.cleanup)

        status = user_prompts.main(
            ["before-thinking", "cli prompt", "--root", str(root)]
        )

        self.assertEqual(0, status)
        text = user_prompts.prompts_path(root).read_text(encoding="utf-8")
        self.assertIn("```\ncli prompt\n```\n", text)

    def test_rejects_empty_prompt_and_strips_trailing_space(self) -> None:
        temporary, root = self.make_root()
        self.addCleanup(temporary.cleanup)

        with self.assertRaises(user_prompts.PromptError):
            user_prompts.add_prompt(root, "   \n\t  ")
        user_prompts.add_prompt(root, "keep me  \n", when=date(2026, 8, 19))
        text = user_prompts.prompts_path(root).read_text(encoding="utf-8")
        self.assertIn("```\nkeep me\n```\n", text)
        self.assertNotIn("keep me  ", text)

    def test_lengthens_fence_when_prompt_contains_backticks(self) -> None:
        temporary, root = self.make_root()
        self.addCleanup(temporary.cleanup)

        user_prompts.add_prompt(root, "use ``` inside", when=date(2026, 8, 19))

        text = user_prompts.prompts_path(root).read_text(encoding="utf-8")
        self.assertIn("````\nuse ``` inside\n````\n", text)


if __name__ == "__main__":
    unittest.main()
