#!/usr/bin/env python3
"""Unit tests for the folder-and-README growth script."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import new_folder
import self_consistency as verifier


class NewFolderTests(unittest.TestCase):
    def make_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "README.md").write_text(
            "/README.md\n\n# Test\n\nWorkspace entry.\n",
            encoding="utf-8",
        )
        section = root / "SRC"
        section.mkdir()
        (section / "README.md").write_text(
            "/SRC/README.md\n\n# SRC\n\nSource workspaces.\n",
            encoding="utf-8",
        )
        return temporary, root

    def test_creates_folder_and_canonical_readme(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        result = new_folder.new_folder(root, "SRC/demo", summary="Demo workspace.")

        self.assertTrue(result.directory.is_dir())
        self.assertEqual(
            "/SRC/demo/README.md\n\n# demo\n\nDemo workspace.\n",
            result.readme.read_text(encoding="utf-8"),
        )
        self.assertIn("demo/", (root / "SRC" / "README.md").read_text(encoding="utf-8"))
        self.assertTrue(result.parent_updated)
        self.assertEqual([], verifier.verify(root))

    def test_cli_writes_folder_and_updates_parent(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        status = new_folder.main(
            ["SRC/tools", "--root", str(root), "--summary", "Portable tools."]
        )

        self.assertEqual(0, status)
        self.assertTrue((root / "SRC" / "tools" / "README.md").is_file())
        parent = (root / "SRC" / "README.md").read_text(encoding="utf-8")
        self.assertIn("[`SRC/tools/README.md`](tools/README.md)", parent)
        self.assertEqual([], verifier.verify(root))

    def test_refuses_top_level_folder_without_approval(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        with self.assertRaises(new_folder.GrowthError):
            new_folder.new_folder(root, "PG02")
        self.assertFalse((root / "PG02").exists())

    def test_approved_top_level_folder_updates_root_readme(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        result = new_folder.new_folder(
            root, "PG02", summary="Playground 02 folder.", approve_structure=True
        )

        self.assertTrue(result.parent_updated)
        root_readme = (root / "README.md").read_text(encoding="utf-8")
        self.assertIn("[`PG02/README.md`](PG02/README.md)", root_readme)
        self.assertEqual([], verifier.verify(root))

    def test_refuses_existing_folder_and_invalid_names(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        (root / "SRC" / "demo").mkdir()

        with self.assertRaises(new_folder.GrowthError):
            new_folder.new_folder(root, "SRC/demo")
        with self.assertRaises(new_folder.GrowthError):
            new_folder.new_folder(root, "SRC/bad name")
        with self.assertRaises(new_folder.GrowthError):
            new_folder.new_folder(root, "../escape")
        with self.assertRaises(new_folder.GrowthError):
            new_folder.new_folder(root, "SRC/__pycache__")
        self.assertEqual(2, new_folder.main(["SRC/missing-parent/child", "--root", str(root)]))

    def test_does_not_duplicate_an_existing_parent_listing(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        (root / "SRC" / "README.md").write_text(
            "/SRC/README.md\n\n# SRC\n\nSource workspaces.\n\n"
            "Subfolders:\n- `demo/` — already noted.\n",
            encoding="utf-8",
        )

        result = new_folder.new_folder(root, "SRC/demo")

        self.assertFalse(result.parent_updated)
        parent = (root / "SRC" / "README.md").read_text(encoding="utf-8")
        self.assertEqual(1, parent.count("demo/"))
        self.assertEqual([], verifier.verify(root))


if __name__ == "__main__":
    unittest.main()
