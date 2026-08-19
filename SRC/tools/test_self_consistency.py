#!/usr/bin/env python3
"""Unit tests for the self-consistency verifier."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import self_consistency as verifier


class VerifierTests(unittest.TestCase):
    def make_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "README.md").write_text("/README.md\n\n# Test\n", encoding="utf-8")
        return temporary, root

    def test_clean_repository_passes(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        section = root / "DOCS"
        section.mkdir()
        (section / "README.md").write_text(
            "/DOCS/README.md\n\n# DOCS\n\nSee [`README.md`](../README.md).\n",
            encoding="utf-8",
        )

        self.assertEqual([], verifier.verify(root))

    def test_reports_missing_readme_full_path(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        (root / "README.md").write_text("# Missing path\n", encoding="utf-8")

        findings = verifier.verify(root)

        self.assertTrue(
            any(finding.code == "missing-readme-full-path" for finding in findings)
        )

    def test_reports_broken_link_and_undescribed_folder(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        (root / "README.md").write_text("/README.md\n\n[missing](nowhere.md)\n", encoding="utf-8")
        (root / "EMPTY").mkdir()

        codes = {finding.code for finding in verifier.verify(root)}

        self.assertIn("broken-link", codes)
        self.assertIn("missing-folder-description", codes)

    def test_reports_noncanonical_readme_link_name_and_directory_target(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        docs = root / "DOCS"
        docs.mkdir()
        (docs / "README.md").write_text("/DOCS/README.md\n\n# DOCS\n", encoding="utf-8")
        (root / "README.md").write_text("/README.md\n\nSee [docs](DOCS/).\n", encoding="utf-8")

        codes = {finding.code for finding in verifier.verify(root)}

        self.assertIn("implicit-readme-link", codes)
        self.assertIn("noncanonical-link-name", codes)

    def test_reports_unlisted_direct_subfolder(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        docs = root / "DOCS"
        child = docs / "PLAN"
        child.mkdir(parents=True)
        (docs / "README.md").write_text("/DOCS/README.md\n\n# DOCS\n", encoding="utf-8")
        (child / "README.md").write_text("/DOCS/PLAN/README.md\n\n# PLAN\n", encoding="utf-8")

        findings = verifier.verify(root)

        self.assertTrue(any(finding.code == "unlisted-subfolder" for finding in findings))

    def test_describes_repository_from_working_copy(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        section = root / "SRC"
        section.mkdir()
        (section / "README.md").write_text(
            "/SRC/README.md\n\n# SRC\n\nSource workspaces.\n", encoding="utf-8"
        )

        description = verifier.describe_repository(root)

        self.assertEqual(root.name, description.name)
        self.assertIn(("SRC/", "Source workspaces."), description.sections)
        self.assertEqual(2, description.files)

    def test_reports_formatting_and_stale_placeholder(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        folder = root / "SRC"
        folder.mkdir()
        (folder / "README.md").write_text("/SRC/README.md\n\n# SRC \n", encoding="utf-8")
        (folder / ".gitkeep").touch()
        (root / "note.txt").write_text("no newline", encoding="utf-8")

        codes = {finding.code for finding in verifier.verify(root)}

        self.assertIn("trailing-whitespace", codes)
        self.assertIn("missing-final-newline", codes)
        self.assertIn("stale-gitkeep", codes)

    def test_reports_hardcoded_current_branch(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        subprocess.run(["git", "init", "-q"], cwd=str(root), check=True)
        subprocess.run(
            ["git", "checkout", "-q", "-b", "topic/portable"],
            cwd=str(root),
            check=True,
        )
        (root / "README.md").write_text(
            "/README.md\n\nDeploy topic/portable directly.\n", encoding="utf-8"
        )

        findings = verifier.verify(root)

        self.assertTrue(
            any(finding.code == "hardcoded-branch-reference" for finding in findings)
        )

    def test_reports_noncanonical_name(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        wrong_name = "GOT" + "HUB"
        (root / "README.md").write_text(
            "/README.md\n\n# " + wrong_name + "\n", encoding="utf-8"
        )

        findings = verifier.verify(root)

        self.assertTrue(any(finding.code == "noncanonical-name" for finding in findings))

    def test_markdown_report_contains_actionable_table(self) -> None:
        finding = verifier.Finding("broken-link", "README.md", 3, "missing destination")

        report = verifier.markdown_report([finding], Path("/repo"))

        self.assertIn("Result: **FAIL**", report)
        self.assertIn("`README.md:3`", report)
        self.assertIn("`broken-link`", report)


if __name__ == "__main__":
    unittest.main()
