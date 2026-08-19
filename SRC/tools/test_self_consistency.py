#!/usr/bin/env python3
"""Unit tests for the self-consistency verifier."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_safe_fix_groups_restore_consistency(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        docs = root / "DOCS"
        docs.mkdir()
        (docs / "README.md").write_text("# DOCS \n", encoding="utf-8")
        (root / "README.md").write_text("/README.md\n\nSee [docs](DOCS/).", encoding="utf-8")

        self.assertEqual(1, verifier.fix_readme_full_paths(root))
        self.assertEqual(1, verifier.fix_readme_links(root))
        self.assertEqual(2, verifier.fix_text_formatting(root))
        self.assertEqual([], verifier.verify(root))

    def test_interactive_safe_fixes_use_grouped_approval(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        docs = root / "DOCS"
        docs.mkdir()
        (docs / "README.md").write_text("# DOCS \n", encoding="utf-8")
        (root / "README.md").write_text("/README.md\n\nSee [docs](DOCS/).", encoding="utf-8")

        with patch("builtins.input", side_effect=["y", "y", "y"]) as prompt:
            findings = verifier.interactive_safe_fixes(root, verifier.verify(root))

        self.assertEqual(3, prompt.call_count)
        self.assertEqual([], findings)

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
        self.assertEqual(("README.md", "SRC/README.md"), description.file_paths)
        self.assertIn("Files:\n- README.md\n- SRC/README.md", verifier.description_text(description))
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

    def test_reports_plan_registry_status_mismatch(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        plan = root / "DOCS" / "PLAN"
        detail = plan / "ITEM"
        detail.mkdir(parents=True)
        (plan / "README.md").write_text(
            "/DOCS/PLAN/README.md\n\n# Plans\n\n"
            "## Status model\n\n| Status | Meaning |\n|---|---|\n"
            "| Proposed | Not approved. |\n| Completed | Done. |\n\n"
            "## Registry\n\n| Plan | Status | Next action |\n|---|---|---|\n"
            "| [`DOCS/PLAN/ITEM/README.md`](ITEM/README.md) | Completed | None. |\n",
            encoding="utf-8",
        )
        (detail / "README.md").write_text(
            "/DOCS/PLAN/ITEM/README.md\n\n# Item\n\n"
            "- **Status:** Proposed\n- **Updated:** 2026-08-19\n",
            encoding="utf-8",
        )

        findings = verifier.check_plan_registries(root)

        self.assertTrue(any(finding.code == "plan-status-mismatch" for finding in findings))

    def test_reports_stale_or_malformed_session_tracking(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        handoff = root / "AGENTS" / "HAND-OFF"
        handoff.mkdir(parents=True)
        (handoff / "SESSION_CONTEXT.md").write_text(
            "# Rolling session context\n\n- **Updated:** 2026-08-18\n\n"
            "## Latest outcome\n\nDone.\n\n"
            "## Validation baseline\n\nPassed.\n\n"
            "## Next agent\n\nContinue.\n",
            encoding="utf-8",
        )
        (handoff / "SESSION_LOG.md").write_text(
            "# Compact session log\n\n## 2026-08-19 — Test\n\n"
            "- **Outcome:** Done.\n- **Decisions:** Keep it.\n",
            encoding="utf-8",
        )

        codes = {finding.code for finding in verifier.check_session_tracking(root)}

        self.assertIn("missing-context-section", codes)
        self.assertIn("missing-log-field", codes)
        self.assertIn("stale-session-context", codes)

    def test_reports_same_day_context_revision_drift(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        handoff = root / "AGENTS" / "HAND-OFF"
        handoff.mkdir(parents=True)
        (handoff / "SESSION_CONTEXT.md").write_text(
            "# Rolling session context\n\n- **Updated:** 2026-08-19\n"
            "- **Log revision:** 1\n\n"
            "## Latest outcome\n\nDone.\n\n## Current state\n\nClean.\n\n"
            "## Validation baseline\n\nPassed.\n\n## Next agent\n\nContinue.\n",
            encoding="utf-8",
        )
        (handoff / "SESSION_LOG.md").write_text(
            "# Compact session log\n\n"
            "## 2026-08-19 — One\n\n- **Revision:** 1\n"
            "- **Outcome:** One.\n- **Decisions:** One.\n- **Validation:** One.\n\n"
            "## 2026-08-19 — Two\n\n- **Revision:** 2\n"
            "- **Outcome:** Two.\n- **Decisions:** Two.\n- **Validation:** Two.\n",
            encoding="utf-8",
        )

        codes = {finding.code for finding in verifier.check_session_tracking(root)}

        self.assertIn("context-log-revision-mismatch", codes)

    def test_reports_nonmonotonic_log_revisions(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        handoff = root / "AGENTS" / "HAND-OFF"
        handoff.mkdir(parents=True)
        (handoff / "SESSION_LOG.md").write_text(
            "# Compact session log\n\n"
            "## 2026-08-19 — Two\n\n- **Revision:** 2\n"
            "- **Outcome:** Two.\n- **Decisions:** Two.\n- **Validation:** Two.\n\n"
            "## 2026-08-19 — One\n\n- **Revision:** 1\n"
            "- **Outcome:** One.\n- **Decisions:** One.\n- **Validation:** One.\n",
            encoding="utf-8",
        )

        codes = {finding.code for finding in verifier.check_session_tracking(root)}

        self.assertIn("nonmonotonic-log-revision", codes)

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
