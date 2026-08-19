#!/usr/bin/env python3
"""Verify repository documentation and structural consistency.

The checker intentionally uses only Python's standard library so the same command
can run on a developer workstation and in GitHub Actions.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import unquote

IGNORED_DIRECTORIES = {
    ".git",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
}
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
README_LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)]+)\)")
# Keep generic typo policy data out of documentation so describing the checker
# does not make the checker report itself. Repository-specific identity belongs
# to the working copy, not this portable verifier.
DISALLOWED_NAMES = {
    "GOT" + "HUB": "GitHub",
}


@dataclass(frozen=True, order=True)
class Finding:
    """One actionable consistency problem."""

    code: str
    path: str
    line: int
    message: str


@dataclass(frozen=True)
class RepositoryDescription:
    """A concise inventory derived from the current working copy."""

    name: str
    branch: str | None
    directories: int
    files: int
    sections: tuple[tuple[str, str], ...]


def _is_ignored(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return any(part in IGNORED_DIRECTORIES for part in relative.parts)


def iter_files(root: Path) -> Iterable[Path]:
    """Yield relevant files in deterministic order."""
    for path in sorted(root.rglob("*")):
        if path.is_file() and not _is_ignored(path, root):
            yield path


def _read_text(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
        ".gitignore",
        "Dockerfile",
        "Makefile",
    }:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _current_branch(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(root),
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def _folder_summary(directory: Path) -> str:
    candidates = (directory / "README.md", directory / (directory.name + ".md"))
    for candidate in candidates:
        if not candidate.is_file():
            continue
        text = _read_text(candidate) or ""
        paragraph: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not paragraph:
                if not stripped or stripped.startswith(("#", "```", ">")):
                    continue
                paragraph.append(stripped)
            elif not stripped or stripped.startswith(("#", "```")):
                break
            else:
                paragraph.append(stripped)
        if paragraph:
            return " ".join(paragraph)
    return "No summary available."


def describe_repository(root: Path) -> RepositoryDescription:
    """Derive a compact repository inventory without a maintained static tree."""
    files = list(iter_files(root))
    directories = [
        path
        for path in root.rglob("*")
        if path.is_dir() and not _is_ignored(path, root)
    ]
    sections = tuple(
        (path.name + "/", _folder_summary(path))
        for path in sorted(root.iterdir())
        if path.is_dir() and not path.name.startswith(".") and not _is_ignored(path, root)
    )
    return RepositoryDescription(
        name=root.name,
        branch=_current_branch(root),
        directories=len(directories),
        files=len(files),
        sections=sections,
    )


def description_text(description: RepositoryDescription) -> str:
    lines = [
        "Repository: {}".format(description.name),
        "Branch: {}".format(description.branch or "not detected"),
        "Inventory: {} directories, {} files".format(
            description.directories, description.files
        ),
        "Top-level sections:",
    ]
    lines.extend("- {} {}".format(name, summary) for name, summary in description.sections)
    return "\n".join(lines)


def check_formatting(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files(root):
        text = _read_text(path)
        if text is None:
            continue
        relative = path.relative_to(root).as_posix()
        for number, line in enumerate(text.splitlines(), 1):
            if line.endswith((" ", "\t")):
                findings.append(
                    Finding("trailing-whitespace", relative, number, "remove trailing whitespace")
                )
        if text and not text.endswith("\n"):
            findings.append(
                Finding("missing-final-newline", relative, max(1, len(text.splitlines())), "add a final newline")
            )
    return findings


def _link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    # Optional Markdown title: `(target "title")`.
    return target.split(maxsplit=1)[0]


def check_markdown_links(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files(root):
        if path.suffix.lower() != ".md":
            continue
        text = _read_text(path) or ""
        for number, line in enumerate(text.splitlines(), 1):
            for match in MARKDOWN_LINK.finditer(line):
                target = _link_target(match.group(1))
                if not target or target.startswith(("#", "/", "mailto:")) or "://" in target:
                    continue
                clean_target = unquote(target.split("#", 1)[0].split("?", 1)[0])
                destination = (path.parent / clean_target).resolve()
                try:
                    destination.relative_to(root)
                except ValueError:
                    exists = False
                else:
                    exists = destination.exists()
                if not exists:
                    findings.append(
                        Finding(
                            "broken-link",
                            path.relative_to(root).as_posix(),
                            number,
                            "local link does not exist: {}".format(target),
                        )
                    )
    return findings


def check_readme_link_names(root: Path) -> list[Finding]:
    """Require internal README links to display and target the linked file."""
    findings: list[Finding] = []
    for path in iter_files(root):
        if path.name != "README.md":
            continue
        text = _read_text(path) or ""
        for number, line in enumerate(text.splitlines(), 1):
            for match in README_LINK.finditer(line):
                label = match.group(1).strip().strip("`")
                target = _link_target(match.group(2))
                if not target or target.startswith(("#", "/", "mailto:")) or "://" in target:
                    continue
                clean_target = unquote(target.split("#", 1)[0].split("?", 1)[0])
                destination = (path.parent / clean_target).resolve()
                try:
                    destination.relative_to(root)
                except ValueError:
                    continue
                linked_file = destination
                if destination.is_dir() and (destination / "README.md").is_file():
                    linked_file = destination / "README.md"
                    findings.append(
                        Finding(
                            "implicit-readme-link",
                            path.relative_to(root).as_posix(),
                            number,
                            "link directly to {}".format(
                                linked_file.relative_to(root).as_posix()
                            ),
                        )
                    )
                if not linked_file.is_file():
                    continue
                expected = linked_file.relative_to(root).as_posix()
                if label != expected:
                    findings.append(
                        Finding(
                            "noncanonical-link-name",
                            path.relative_to(root).as_posix(),
                            number,
                            "use linked file name {!r} as link text".format(expected),
                        )
                    )
    return findings


def check_folder_descriptions(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    directories = [root]
    directories.extend(
        path
        for path in sorted(root.rglob("*"))
        if path.is_dir()
        and not _is_ignored(path, root)
        and not any(part.startswith(".") for part in path.relative_to(root).parts)
    )
    for directory in directories:
        relative = directory.relative_to(root)
        candidates = [directory / "README.md"]
        if directory != root:
            candidates.append(directory / (directory.name + ".md"))
        if not any(candidate.is_file() for candidate in candidates):
            display = relative.as_posix() if relative.parts else "."
            findings.append(
                Finding(
                    "missing-folder-description",
                    display,
                    0,
                    "add README.md or {}.md".format(directory.name),
                )
            )
    return findings


def check_folder_indexes(root: Path) -> list[Finding]:
    """Ensure a folder descriptor names each direct visible subfolder."""
    findings: list[Finding] = []
    directories = [
        path
        for path in sorted(root.rglob("*"))
        if path.is_dir()
        and not _is_ignored(path, root)
        and not any(part.startswith(".") for part in path.relative_to(root).parts)
    ]
    for directory in directories:
        children = [
            child
            for child in sorted(directory.iterdir())
            if child.is_dir()
            and not child.name.startswith(".")
            and not _is_ignored(child, root)
        ]
        if not children:
            continue
        candidates = (directory / "README.md", directory / (directory.name + ".md"))
        descriptor = next((path for path in candidates if path.is_file()), None)
        if descriptor is None:
            continue  # check_folder_descriptions reports the primary problem.
        text = _read_text(descriptor) or ""
        for child in children:
            marker = child.name + "/"
            if marker not in text:
                findings.append(
                    Finding(
                        "unlisted-subfolder",
                        descriptor.relative_to(root).as_posix(),
                        0,
                        "list direct subfolder {!r}".format(marker),
                    )
                )
    return findings


def check_stale_placeholders(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files(root):
        if path.name != ".gitkeep":
            continue
        siblings = [item for item in path.parent.iterdir() if item.name != ".gitkeep"]
        if siblings:
            findings.append(
                Finding(
                    "stale-gitkeep",
                    path.relative_to(root).as_posix(),
                    0,
                    "remove .gitkeep because the directory is no longer empty",
                )
            )
    return findings


def check_canonical_names(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files(root):
        if path.suffix.lower() != ".md":
            continue
        text = _read_text(path) or ""
        for number, line in enumerate(text.splitlines(), 1):
            for wrong, replacement in DISALLOWED_NAMES.items():
                if wrong.lower() in line.lower():
                    findings.append(
                        Finding(
                            "noncanonical-name",
                            path.relative_to(root).as_posix(),
                            number,
                            "replace {!r} with {!r}".format(wrong, replacement),
                        )
                    )
    return findings


def check_branch_references(root: Path) -> list[Finding]:
    """Prevent the current branch value from leaking into portable Markdown."""
    branch = _current_branch(root)
    if not branch:
        return []

    findings: list[Finding] = []
    for path in iter_files(root):
        if path.suffix.lower() != ".md":
            continue
        text = _read_text(path) or ""
        for number, line in enumerate(text.splitlines(), 1):
            if branch in line:
                findings.append(
                    Finding(
                        "hardcoded-branch-reference",
                        path.relative_to(root).as_posix(),
                        number,
                        "replace the current branch value with portable placeholder 'branch'",
                    )
                )
    return findings


def verify(root: Path) -> list[Finding]:
    checks = (
        check_markdown_links,
        check_readme_link_names,
        check_folder_descriptions,
        check_folder_indexes,
        check_stale_placeholders,
        check_canonical_names,
        check_branch_references,
        check_formatting,
    )
    findings: list[Finding] = []
    for check in checks:
        findings.extend(check(root))
    return sorted(set(findings), key=lambda finding: (finding.path, finding.line, finding.code))


def text_report(findings: Sequence[Finding], root: Path) -> str:
    if not findings:
        return "Self-consistency verification passed: no findings."
    lines = ["Self-consistency verification found {} issue(s):".format(len(findings))]
    for finding in findings:
        location = finding.path + (":" + str(finding.line) if finding.line else "")
        lines.append("- {} [{}] {}".format(location, finding.code, finding.message))
    return "\n".join(lines)


def markdown_report(findings: Sequence[Finding], root: Path) -> str:
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "# Self-consistency report",
        "",
        "- Generated: `{}`".format(generated),
        "- Repository: `{}`".format(root),
        "- Result: **{}**".format("PASS" if not findings else "FAIL"),
        "- Findings: **{}**".format(len(findings)),
        "",
    ]
    if findings:
        lines.extend(["| Location | Rule | Recommendation |", "|---|---|---|"])
        for finding in findings:
            location = finding.path + (":" + str(finding.line) if finding.line else "")
            message = finding.message.replace("|", "\\|")
            lines.append("| `{}` | `{}` | {} |".format(location, finding.code, message))
    else:
        lines.append("No consistency problems were detected.")
    lines.append("")
    return "\n".join(lines)


def _prompt_report_path(default: str) -> str | None:
    print("Developer interaction mode")
    answer = input("Write a Markdown report? [Y/n] ").strip().lower()
    if answer in {"n", "no"}:
        return None
    selected = input("Report path [{}]: ".format(default)).strip()
    return selected or default


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root (default: cwd)")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="stdout format")
    parser.add_argument("--report", type=Path, help="write a Markdown report to this path")
    parser.add_argument(
        "--describe",
        action="store_true",
        help="print a repository inventory derived from the working copy",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="prompt the developer about report generation (requires a TTY)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print("error: repository root is not a directory: {}".format(root), file=sys.stderr)
        return 2
    if args.interactive and not sys.stdin.isatty():
        print("error: --interactive requires a terminal", file=sys.stderr)
        return 2

    findings = verify(root)
    description = describe_repository(root) if args.describe else None
    if args.format == "json":
        payload: object = [asdict(finding) for finding in findings]
        if description:
            payload = {
                "description": asdict(description),
                "findings": [asdict(finding) for finding in findings],
            }
        print(json.dumps(payload, indent=2))
    else:
        if description:
            print(description_text(description))
            print()
        print(text_report(findings, root))

    report_path = args.report
    if args.interactive:
        selected = _prompt_report_path("self-consistency-report.md")
        report_path = Path(selected) if selected else None
    if report_path:
        if not report_path.is_absolute():
            report_path = root / report_path
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(markdown_report(findings, root), encoding="utf-8")
        print("Markdown report written to {}".format(report_path), file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
