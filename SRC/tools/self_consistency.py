#!/usr/bin/env python3
"""Verify repository documentation and structural consistency.

The checker intentionally uses only Python's standard library so the same command
can run on a developer workstation and in GitHub Actions.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
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
README_FULL_PATH = re.compile(r"^/(?:.*/)?README\.md$")
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
    github_user: str | None
    sync: str
    ahead: int | None
    behind: int | None
    directories: int
    files: int
    directory_paths: tuple[str, ...]
    directory_descriptors: tuple[tuple[str, str], ...]
    file_paths: tuple[str, ...]
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


def _git(root: Path, *args: str) -> str | None:
    """Return stripped Git stdout, or None when Git is unavailable or fails."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(root),
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def _current_branch(root: Path) -> str | None:
    return _git(root, "branch", "--show-current")


def _is_git_root(root: Path) -> bool:
    """Return True only when root is the Git working-copy top level."""
    toplevel = _git(root, "rev-parse", "--show-toplevel")
    if not toplevel:
        return False
    try:
        return Path(toplevel).resolve() == root.resolve()
    except OSError:
        return False


def _parse_github_identity(url: str) -> tuple[str | None, str | None]:
    """Return (GitHub_User, origin-repo) from a supported GitHub origin URL."""
    value = url.strip()
    if value.endswith("/"):
        value = value[:-1]
    if value.endswith(".git"):
        value = value[:-4]
    marker = "github.com"
    lowered = value.lower()
    if marker not in lowered:
        return None, None
    index = lowered.index(marker) + len(marker)
    separator = value[index : index + 1]
    if separator not in {":", "/"}:
        return None, None
    parts = [part for part in value[index + 1 :].split("/") if part]
    if len(parts) < 2:
        return None, None
    return parts[0], parts[1]


def _sync_state(root: Path, branch: str | None) -> tuple[str, int | None, int | None]:
    """Derive local-vs-origin sync without fetching or mutating Git state."""
    if not _is_git_root(root):
        return "no-git", None, None
    if not branch:
        return "detached", None, None
    if _git(root, "remote", "get-url", "origin") is None:
        return "no-origin", None, None
    remote_ref = "refs/remotes/origin/{}".format(branch)
    if _git(root, "rev-parse", "--verify", "--quiet", remote_ref) is None:
        return "remote-branch-absent", None, None
    counts = _git(root, "rev-list", "--left-right", "--count", "HEAD...origin/{}".format(branch))
    if counts is None:
        return "unknown", None, None
    parts = counts.split()
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return "unknown", None, None
    ahead, behind = int(parts[0]), int(parts[1])
    if ahead == 0 and behind == 0:
        status = "synchronized"
    elif behind == 0:
        status = "ahead"
    elif ahead == 0:
        status = "behind"
    else:
        status = "diverged"
    return status, ahead, behind


_SYNC_TEXT = {
    "no-git": "not detected",
    "detached": "detached HEAD",
    "no-origin": "origin missing",
    "remote-branch-absent": "remote branch absent; local only",
    "synchronized": "synchronized",
    "ahead": "ahead",
    "behind": "behind",
    "diverged": "diverged",
    "unknown": "unknown",
}


def _folder_descriptor(directory: Path) -> Path | None:
    candidates = (directory / "README.md", directory / (directory.name + ".md"))
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def _folder_summary(directory: Path) -> str:
    descriptor = _folder_descriptor(directory)
    if descriptor is None:
        return "No summary available."
    text = _read_text(descriptor) or ""
    paragraph: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not paragraph:
            if (
                not stripped
                or stripped.startswith(("#", "```", ">"))
                or README_FULL_PATH.fullmatch(stripped)
            ):
                continue
            paragraph.append(stripped)
        elif not stripped or stripped.startswith(("#", "```")):
            break
        else:
            paragraph.append(stripped)
    return " ".join(paragraph) if paragraph else "No summary available."


def describe_repository(root: Path) -> RepositoryDescription:
    """Derive a compact repository inventory without a maintained static tree."""
    files = list(iter_files(root))
    directories = [
        path
        for path in sorted(root.rglob("*"))
        if path.is_dir() and not _is_ignored(path, root)
    ]
    sections = tuple(
        (path.name + "/", _folder_summary(path))
        for path in sorted(root.iterdir())
        if path.is_dir() and not path.name.startswith(".") and not _is_ignored(path, root)
    )
    git_root = _is_git_root(root)
    branch = _current_branch(root) if git_root else None
    origin_url = _git(root, "remote", "get-url", "origin") if git_root else None
    github_user = _parse_github_identity(origin_url)[0] if origin_url else None
    sync, ahead, behind = _sync_state(root, branch)
    return RepositoryDescription(
        name=root.name,
        branch=branch,
        github_user=github_user,
        sync=sync,
        ahead=ahead,
        behind=behind,
        directories=len(directories),
        files=len(files),
        directory_paths=tuple(
            path.relative_to(root).as_posix() + "/" for path in directories
        ),
        directory_descriptors=tuple(
            (
                path.relative_to(root).as_posix() + "/",
                descriptor.relative_to(root).as_posix(),
            )
            for path in directories
            for descriptor in [_folder_descriptor(path)]
            if descriptor is not None
        ),
        file_paths=tuple(path.relative_to(root).as_posix() for path in files),
        sections=sections,
    )


def description_text(description: RepositoryDescription) -> str:
    sync = _SYNC_TEXT.get(description.sync, description.sync)
    if description.sync == "ahead" and description.ahead is not None:
        sync = "ahead {}".format(description.ahead)
    elif description.sync == "behind" and description.behind is not None:
        sync = "behind {}".format(description.behind)
    elif (
        description.sync == "diverged"
        and description.ahead is not None
        and description.behind is not None
    ):
        sync = "diverged {} ahead, {} behind".format(description.ahead, description.behind)
    lines = [
        "Repository: {}".format(description.name),
        "Branch: {}".format(description.branch or "not detected"),
        "GitHub_User: {}".format(description.github_user or "not detected"),
        "Sync: {}".format(sync),
        "Inventory: {} directories, {} files".format(
            description.directories, description.files
        ),
        "Top-level sections:",
    ]
    lines.extend("- {} {}".format(name, summary) for name, summary in description.sections)
    descriptors = dict(description.directory_descriptors)
    lines.append("Directories:")
    lines.extend(
        "- {} -> {}".format(path, descriptors.get(path, "descriptor not required"))
        for path in description.directory_paths
    )
    lines.append("Files:")
    lines.extend("- {}".format(path) for path in description.file_paths)
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


def check_readme_full_paths(root: Path) -> list[Finding]:
    """Require every README to declare its repository-absolute path first."""
    findings: list[Finding] = []
    for path in iter_files(root):
        if path.name != "README.md":
            continue
        text = _read_text(path) or ""
        lines = text.splitlines()
        first_line = lines[0] if lines else ""
        expected = "/" + path.relative_to(root).as_posix()
        if first_line != expected:
            findings.append(
                Finding(
                    "missing-readme-full-path",
                    path.relative_to(root).as_posix(),
                    1,
                    "start the file with {!r}".format(expected),
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


def _section(text: str, heading: str) -> str:
    """Return a level-two Markdown section body, or an empty string."""
    match = re.search(
        r"^## {}\s*$\n(.*?)(?=^## |\Z)".format(re.escape(heading)),
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def _metadata(text: str, key: str) -> str | None:
    match = re.search(
        r"^- \*\*{}:\*\*\s*(.+?)\s*$".format(re.escape(key)),
        text,
        flags=re.MULTILINE,
    )
    return match.group(1) if match else None


def check_plan_registries(root: Path) -> list[Finding]:
    """Validate linked plan status against a portable Markdown registry."""
    findings: list[Finding] = []
    row_pattern = re.compile(
        r"^\|\s*\[[^\]]+\]\(([^)]+)\)\s*\|\s*([^|]+?)\s*\|",
        flags=re.MULTILINE,
    )
    status_pattern = re.compile(r"^\|\s*([^|]+?)\s*\|", flags=re.MULTILINE)
    for path in iter_files(root):
        if path.name != "README.md":
            continue
        text = _read_text(path) or ""
        status_model = _section(text, "Status model")
        registry = _section(text, "Registry")
        if not status_model or not registry:
            continue
        allowed = {
            match.group(1).strip()
            for match in status_pattern.finditer(status_model)
            if match.group(1).strip() not in {"Status", "---"}
        }
        registered: set[Path] = set()
        for match in row_pattern.finditer(registry):
            target = _link_target(match.group(1))
            registry_status = match.group(2).strip()
            if not target or target.startswith(("#", "/", "mailto:")) or "://" in target:
                continue
            destination = (path.parent / target).resolve()
            if destination.is_dir():
                destination = destination / "README.md"
            if not destination.is_file():
                continue  # Broken-link verification reports this first.
            try:
                relative = destination.relative_to(root).as_posix()
            except ValueError:
                continue
            registered.add(destination)
            detail = _read_text(destination) or ""
            detail_status = _metadata(detail, "Status")
            detail_date = _document_date(_metadata(detail, "Updated"))
            if detail_date is None:
                findings.append(
                    Finding(
                        "invalid-plan-date",
                        relative,
                        0,
                        "add valid ISO date metadata '- **Updated:** YYYY-MM-DD'",
                    )
                )
            if registry_status not in allowed:
                findings.append(
                    Finding(
                        "invalid-plan-status",
                        path.relative_to(root).as_posix(),
                        0,
                        "registry status {!r} is absent from the status model".format(
                            registry_status
                        ),
                    )
                )
            if detail_status is None:
                findings.append(
                    Finding(
                        "missing-plan-status",
                        relative,
                        0,
                        "add '- **Status:** <status>' metadata",
                    )
                )
            elif detail_status != registry_status:
                findings.append(
                    Finding(
                        "plan-status-mismatch",
                        relative,
                        0,
                        "detail status {!r} differs from registry status {!r}".format(
                            detail_status, registry_status
                        ),
                    )
                )
        for child in sorted(path.parent.iterdir()):
            detail = child / "README.md"
            if (
                child.is_dir()
                and not child.name.startswith(".")
                and not _is_ignored(child, root)
                and detail.is_file()
                and detail.resolve() not in registered
            ):
                findings.append(
                    Finding(
                        "unregistered-plan",
                        detail.relative_to(root).as_posix(),
                        0,
                        "add this plan to the parent registry",
                    )
                )
    return findings


def _document_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _positive_integer(value: str | None) -> int | None:
    if value is None or not value.isdigit() or int(value) < 1:
        return None
    return int(value)


def check_session_tracking(root: Path) -> list[Finding]:
    """Validate rolling-context and compact-log schemas by their headings."""
    findings: list[Finding] = []
    rolling: list[tuple[Path, date | None, int | None]] = []
    logs: list[tuple[Path, list[date], list[int]]] = []
    required_context_sections = (
        "Latest outcome",
        "Current state",
        "Validation baseline",
        "Next agent",
    )
    for path in iter_files(root):
        if path.suffix.lower() != ".md":
            continue
        text = _read_text(path) or ""
        if re.search(r"^# Rolling session context\s*$", text, re.MULTILINE):
            updated = _document_date(_metadata(text, "Updated"))
            revision = _positive_integer(_metadata(text, "Log revision"))
            rolling.append((path, updated, revision))
            if updated is None:
                findings.append(
                    Finding(
                        "invalid-context-date",
                        path.relative_to(root).as_posix(),
                        0,
                        "add valid ISO date metadata '- **Updated:** YYYY-MM-DD'",
                    )
                )
            if revision is None:
                findings.append(
                    Finding(
                        "invalid-context-revision",
                        path.relative_to(root).as_posix(),
                        0,
                        "add positive integer metadata '- **Log revision:** N'",
                    )
                )
            for heading in required_context_sections:
                if not _section(text, heading).strip():
                    findings.append(
                        Finding(
                            "missing-context-section",
                            path.relative_to(root).as_posix(),
                            0,
                            "add non-empty '## {}' section".format(heading),
                        )
                    )
        if re.search(r"^# Compact session log\s*$", text, re.MULTILINE):
            entry_dates: list[date] = []
            revisions: list[int] = []
            entries = list(
                re.finditer(
                    r"^## (\d{4}-\d{2}-\d{2})\s+—[^\n]+$", text, re.MULTILINE
                )
            )
            if not entries:
                findings.append(
                    Finding(
                        "missing-log-entry",
                        path.relative_to(root).as_posix(),
                        0,
                        "add at least one '## YYYY-MM-DD — title' entry",
                    )
                )
            for index, entry in enumerate(entries):
                parsed = _document_date(entry.group(1))
                if parsed:
                    entry_dates.append(parsed)
                end = entries[index + 1].start() if index + 1 < len(entries) else len(text)
                body = text[entry.end() : end]
                for field in ("Revision", "Outcome", "Decisions", "Validation"):
                    if not re.search(
                        r"^- \*\*{}:\*\*\s+.+".format(field), body, re.MULTILINE
                    ):
                        findings.append(
                            Finding(
                                "missing-log-field",
                                path.relative_to(root).as_posix(),
                                0,
                                "entry {!r} needs **{}:**".format(
                                    entry.group(0)[3:], field
                                ),
                            )
                        )
                entry_revision = _positive_integer(_metadata(body, "Revision"))
                if entry_revision is not None:
                    revisions.append(entry_revision)
            if len(revisions) == len(entries) and any(
                current <= previous
                for previous, current in zip(revisions, revisions[1:])
            ):
                findings.append(
                    Finding(
                        "nonmonotonic-log-revision",
                        path.relative_to(root).as_posix(),
                        0,
                        "log revisions must be unique and strictly increasing",
                    )
                )
            logs.append((path, entry_dates, revisions))
    for context_path, updated, revision in rolling:
        sibling_logs = [
            (dates, revisions)
            for log_path, dates, revisions in logs
            if log_path.parent == context_path.parent
        ]
        sibling_dates = [
            entry_date for dates, _ in sibling_logs for entry_date in dates
        ]
        sibling_revisions = [
            entry_revision
            for _, revisions in sibling_logs
            for entry_revision in revisions
        ]
        if not sibling_logs:
            findings.append(
                Finding(
                    "missing-session-log",
                    context_path.relative_to(root).as_posix(),
                    0,
                    "add a sibling compact session log",
                )
            )
        if updated and sibling_dates and max(sibling_dates) > updated:
            findings.append(
                Finding(
                    "stale-session-context",
                    context_path.relative_to(root).as_posix(),
                    0,
                    "context date predates the newest compact-log entry",
                )
            )
        if revision and sibling_revisions and revision != max(sibling_revisions):
            findings.append(
                Finding(
                    "context-log-revision-mismatch",
                    context_path.relative_to(root).as_posix(),
                    0,
                    "context Log revision must equal the newest log Revision",
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
        check_readme_full_paths,
        check_readme_link_names,
        check_folder_descriptions,
        check_folder_indexes,
        check_stale_placeholders,
        check_canonical_names,
        check_plan_registries,
        check_session_tracking,
        check_branch_references,
        check_formatting,
    )
    findings: list[Finding] = []
    for check in checks:
        findings.extend(check(root))
    return sorted(set(findings), key=lambda finding: (finding.path, finding.line, finding.code))


def fix_readme_full_paths(root: Path) -> int:
    """Insert or correct README path declarations; return changed file count."""
    changed = 0
    for path in iter_files(root):
        if path.name != "README.md":
            continue
        text = _read_text(path) or ""
        lines = text.splitlines()
        expected = "/" + path.relative_to(root).as_posix()
        if lines and lines[0] == expected:
            continue
        had_final_newline = text.endswith("\n")
        if lines and README_FULL_PATH.fullmatch(lines[0]):
            lines[0] = expected
        else:
            lines = [expected, ""] + lines
        updated = "\n".join(lines)
        if had_final_newline and not updated.endswith("\n"):
            updated += "\n"
        path.write_text(updated, encoding="utf-8")
        changed += 1
    return changed


def _canonical_readme_link(match: re.Match[str], path: Path, root: Path) -> str:
    raw_target = match.group(2).strip()
    target = _link_target(raw_target)
    if not target or target.startswith(("#", "/", "mailto:")) or "://" in target:
        return match.group(0)
    target_path = target.split("#", 1)[0].split("?", 1)[0]
    clean_target = unquote(target_path)
    destination = (path.parent / clean_target).resolve()
    try:
        destination.relative_to(root)
    except ValueError:
        return match.group(0)
    if destination.is_dir() and (destination / "README.md").is_file():
        destination = destination / "README.md"
    if not destination.is_file():
        return match.group(0)
    label = destination.relative_to(root).as_posix()
    href = Path(os.path.relpath(destination, path.parent)).as_posix()
    suffix = target[len(target_path) :]
    return "[`{}`]({}{})".format(label, href, suffix)


def fix_readme_links(root: Path) -> int:
    """Canonicalize internal README links; return changed file count."""
    changed = 0
    for path in iter_files(root):
        if path.name != "README.md":
            continue
        text = _read_text(path) or ""
        updated = README_LINK.sub(
            lambda match: _canonical_readme_link(match, path, root), text
        )
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def fix_text_formatting(root: Path) -> int:
    """Remove trailing whitespace and add final newlines to text files."""
    changed = 0
    for path in iter_files(root):
        text = _read_text(path)
        if text is None:
            continue
        updated = "\n".join(line.rstrip(" \t") for line in text.splitlines())
        if text or updated:
            updated += "\n"
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def _confirm(prompt: str) -> bool:
    return input(prompt + " [y/N] ").strip().lower() in {"y", "yes"}


def interactive_safe_fixes(root: Path, findings: Sequence[Finding]) -> list[Finding]:
    """Preview and apply developer-approved groups of deterministic safe fixes."""
    groups = (
        (
            "README full paths",
            {"missing-readme-full-path"},
            fix_readme_full_paths,
        ),
        (
            "README internal links",
            {"implicit-readme-link", "noncanonical-link-name"},
            fix_readme_links,
        ),
        (
            "text formatting",
            {"trailing-whitespace", "missing-final-newline"},
            fix_text_formatting,
        ),
    )
    print("\nGrouped safe-fix preview")
    applied = False
    for name, codes, fixer in groups:
        count = sum(finding.code in codes for finding in findings)
        if not count:
            continue
        print("- {}: {} finding(s)".format(name, count))
        if _confirm("Apply {} fixes?".format(name)):
            changed = fixer(root)
            print("  changed {} file(s)".format(changed))
            applied = True
        else:
            print("  skipped")
    if not applied:
        print("No safe fixes applied.")
        return list(findings)
    updated_findings = verify(root)
    print("\nAfter approved fixes:")
    print(text_report(updated_findings, root))
    return updated_findings


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
        help="prompt for grouped safe fixes and report generation (requires a TTY)",
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
    if args.interactive and args.format == "json":
        print("error: --interactive cannot be combined with --format json", file=sys.stderr)
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

    if args.interactive:
        findings = interactive_safe_fixes(root, findings)

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
