#!/usr/bin/env python3
"""Unit tests for the self-constructing folder script."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SCRIPT = TOOLS / "script.sh"


class ScriptTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "README.md").write_text(
            "/README.md\n\n# Sandbox\n\nSandbox root.\n", encoding="utf-8"
        )
        tools = root / "SRC" / "tools"
        tools.mkdir(parents=True)
        (root / "SRC" / "README.md").write_text(
            "/SRC/README.md\n\n# SRC\n\nSources.\n\nSubfolders:\n"
            "- [`SRC/tools/README.md`](tools/README.md) — tools.\n",
            encoding="utf-8",
        )
        (tools / "README.md").write_text(
            "/SRC/tools/README.md\n\n# tools\n\nTools.\n", encoding="utf-8"
        )
        shutil.copy(TOOLS / "self_consistency.py", tools / "self_consistency.py")
        return root

    def run_script(self, root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(SCRIPT), "--root", str(root), *arguments],
            capture_output=True,
            text=True,
        )

    def test_self_named_descriptor_and_parent_index(self) -> None:
        root = self.make_repo()

        result = self.run_script(root, "DEMO")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            "# DEMO\n\nDEMO folder.\n",
            (root / "DEMO" / "DEMO.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "- [`DEMO/DEMO.md`](DEMO/DEMO.md) — DEMO folder.",
            (root / "README.md").read_text(encoding="utf-8"),
        )
        self.assertIn("newSession.Reload()", result.stdout)
        self.assertIn("verification passed", result.stdout)

    def test_readme_descriptor_carries_path_and_metadata(self) -> None:
        root = self.make_repo()

        result = self.run_script(
            root,
            "--parent",
            "SRC",
            "--descriptor",
            "readme",
            "--title",
            "Widgets",
            "--summary",
            "Widget helpers.",
            "--metadata",
            "Status: Proposed",
            "WIDGETS",
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            "/SRC/WIDGETS/README.md\n\n# Widgets\n\n- **Status:** Proposed\n\n"
            "Widget helpers.\n",
            (root / "SRC" / "WIDGETS" / "README.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "- [`SRC/WIDGETS/README.md`](WIDGETS/README.md) — Widget helpers.",
            (root / "SRC" / "README.md").read_text(encoding="utf-8"),
        )

    def test_dry_run_changes_nothing(self) -> None:
        root = self.make_repo()
        before = (root / "README.md").read_text(encoding="utf-8")

        result = self.run_script(root, "--dry-run", "DEMO")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertFalse((root / "DEMO").exists())
        self.assertEqual(before, (root / "README.md").read_text(encoding="utf-8"))

    def test_repeated_construction_is_idempotent(self) -> None:
        root = self.make_repo()
        self.run_script(root, "DEMO")
        first = (root / "README.md").read_text(encoding="utf-8")

        result = self.run_script(root, "DEMO")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("descriptor already exists", result.stdout)
        self.assertEqual(first, (root / "README.md").read_text(encoding="utf-8"))

    def test_force_rewrites_descriptor_without_duplicating_index(self) -> None:
        root = self.make_repo()
        self.run_script(root, "DEMO")

        result = self.run_script(root, "--force", "--summary", "Rebuilt.", "DEMO")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Rebuilt.", (root / "DEMO" / "DEMO.md").read_text(encoding="utf-8"))
        self.assertEqual(
            1, (root / "README.md").read_text(encoding="utf-8").count("](DEMO/DEMO.md)")
        )

    def test_skipping_the_index_leaves_the_parent_untouched(self) -> None:
        root = self.make_repo()
        before = (root / "README.md").read_text(encoding="utf-8")

        result = self.run_script(root, "--index", "skip", "--no-reload", "DEMO")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertTrue((root / "DEMO" / "DEMO.md").is_file())
        self.assertEqual(before, (root / "README.md").read_text(encoding="utf-8"))

    def test_reload_reports_verification_findings(self) -> None:
        root = self.make_repo()
        (root / "SRC" / "README.md").write_text(
            "/SRC/README.md\n\n# SRC\n\nSources.\n", encoding="utf-8"
        )

        result = self.run_script(root, "DEMO")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("unlisted-subfolder", result.stdout)

    def test_hidden_folder_is_created_without_index_or_descriptor(self) -> None:
        root = self.make_repo()
        before = (root / "README.md").read_text(encoding="utf-8")

        result = self.run_script(
            root, "--parent", "SRC", "--descriptor", "none", ".private"
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertTrue((root / "SRC" / ".private").is_dir())
        self.assertEqual([], list((root / "SRC" / ".private").iterdir()))
        self.assertEqual(before, (root / "README.md").read_text(encoding="utf-8"))
        self.assertNotIn(
            ".private/", (root / "SRC" / "README.md").read_text(encoding="utf-8")
        )

    def test_hidden_folder_keeps_a_descriptor_out_of_the_parent_index(self) -> None:
        root = self.make_repo()

        result = self.run_script(root, ".user")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertTrue((root / ".user" / ".user.md").is_file())
        self.assertNotIn(".user/", (root / "README.md").read_text(encoding="utf-8"))

    def test_invalid_usage_returns_environment_status(self) -> None:
        root = self.make_repo()

        self.assertEqual(2, self.run_script(root).returncode)
        self.assertEqual(2, self.run_script(root, "nested/name").returncode)
        self.assertEqual(2, self.run_script(root, "--descriptor", "other", "DEMO").returncode)
        self.assertEqual(2, self.run_script(root, "..").returncode)


if __name__ == "__main__":
    unittest.main()
