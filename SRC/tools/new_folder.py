#!/usr/bin/env python3
"""Create a named folder and its canonical README descriptor.

Implements the portable growth step:

    mkDirNameOfFolder
    nameOfFolder.new(nameOfFolder.Readme)

The script creates the directory, writes a README that satisfies repository
descriptor contracts, and lists the new child in the parent descriptor.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import self_consistency as verifier

FOLDER_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


class GrowthError(ValueError):
    """A rejected folder-growth request."""


@dataclass(frozen=True)
class GrowthResult:
    """Paths written or updated by one growth operation."""

    directory: Path
    readme: Path
    parent_descriptor: Path | None
    parent_updated: bool


def _relative(path: Path, root: Path) -> Path:
    try:
        return path.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise GrowthError("path escapes the repository root: {}".format(path)) from error


def _validate_parts(parts: Sequence[str]) -> None:
    if not parts:
        raise GrowthError("folder name is empty")
    for part in parts:
        if part in verifier.IGNORED_DIRECTORIES or part.startswith("."):
            raise GrowthError("folder name is reserved or hidden: {}".format(part))
        if not FOLDER_NAME.fullmatch(part):
            raise GrowthError(
                "folder name must be letters, digits, '_' or '-': {}".format(part)
            )


def _default_summary(name: str) -> str:
    return "{} folder.".format(name)


def _readme_text(directory: Path, root: Path, summary: str) -> str:
    relative = _relative(directory, root).as_posix()
    return "/{}/README.md\n\n# {}\n\n{}\n".format(relative, directory.name, summary)


def _descriptor(directory: Path) -> Path | None:
    if directory.name == "":
        candidates = (directory / "README.md",)
    else:
        candidates = (directory / "README.md", directory / (directory.name + ".md"))
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def _bullet(child_readme: Path, descriptor: Path, root: Path, summary: str) -> str:
    label = child_readme.relative_to(root).as_posix()
    href = Path(os.path.relpath(child_readme, descriptor.parent)).as_posix()
    return "- [`{}`]({}) — {}".format(label, href, summary)


def _insert_subfolder_bullet(text: str, bullet: str) -> str:
    lines = text.splitlines()
    insert_at: int | None = None
    last_bullet: int | None = None
    in_subfolders = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped in {"Subfolders:", "## Subfolders"}:
            in_subfolders = True
            insert_at = index + 1
            last_bullet = None
            continue
        if in_subfolders:
            if stripped.startswith("- "):
                last_bullet = index
            elif stripped.startswith("#"):
                break
            elif stripped == "" and last_bullet is not None:
                break
    if last_bullet is not None:
        lines.insert(last_bullet + 1, bullet)
    elif insert_at is not None:
        while insert_at < len(lines) and lines[insert_at].strip() == "":
            insert_at += 1
        lines.insert(insert_at, bullet)
    else:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append("Subfolders:")
        lines.append(bullet)
    return "\n".join(lines) + "\n"


def _update_parent_index(
    directory: Path, root: Path, summary: str
) -> tuple[Path | None, bool]:
    parent = directory.parent
    descriptor = _descriptor(parent)
    if descriptor is None:
        return None, False
    text = descriptor.read_text(encoding="utf-8")
    if directory.name + "/" in text:
        return descriptor, False
    updated = _insert_subfolder_bullet(
        text, _bullet(directory / "README.md", descriptor, root, summary)
    )
    descriptor.write_text(updated, encoding="utf-8")
    return descriptor, True


def new_folder(
    root: Path,
    name: str,
    summary: str | None = None,
    approve_structure: bool = False,
) -> GrowthResult:
    """Create ``name`` under ``root`` and write its canonical README."""
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise GrowthError("repository root is not a directory: {}".format(root))

    requested = Path(name)
    if requested.is_absolute():
        relative = _relative(requested, root)
    else:
        if ".." in requested.parts:
            raise GrowthError("folder name must not contain '..'")
        relative = Path(*requested.parts)

    parts = relative.parts
    _validate_parts(parts)
    if len(parts) == 1 and not approve_structure:
        raise GrowthError(
            "creating a top-level folder is a structural change; "
            "pass --approve-structure after developer approval"
        )

    target = (root / relative).resolve()
    _relative(target, root)
    parent = target.parent
    if not parent.is_dir():
        raise GrowthError("parent directory does not exist: {}".format(
            parent.relative_to(root).as_posix()
        ))
    if target.exists():
        raise GrowthError("folder already exists: {}".format(relative.as_posix()))

    cleaned_summary = (summary or _default_summary(target.name)).strip()
    if not cleaned_summary or "\n" in cleaned_summary:
        raise GrowthError("summary must be a single non-empty line")

    target.mkdir()
    readme = target / "README.md"
    readme.write_text(_readme_text(target, root, cleaned_summary), encoding="utf-8")
    parent_descriptor, parent_updated = _update_parent_index(
        target, root, cleaned_summary
    )
    return GrowthResult(
        directory=target,
        readme=readme,
        parent_descriptor=parent_descriptor,
        parent_updated=parent_updated,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "name",
        help="folder path relative to the repository root, or an absolute path under it",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root (default: cwd)",
    )
    parser.add_argument(
        "--summary",
        help="single-line README purpose (default: '<name> folder.')",
    )
    parser.add_argument(
        "--approve-structure",
        action="store_true",
        help="allow a new top-level folder after developer approval",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.expanduser().resolve()
    try:
        result = new_folder(
            root,
            args.name,
            summary=args.summary,
            approve_structure=args.approve_structure,
        )
    except GrowthError as error:
        print("error: {}".format(error), file=sys.stderr)
        return 2

    print("Created {}".format(result.directory.relative_to(root).as_posix() + "/"))
    print("Wrote {}".format(result.readme.relative_to(root).as_posix()))
    if result.parent_descriptor is not None:
        parent_display = result.parent_descriptor.relative_to(root).as_posix()
        if result.parent_updated:
            print("Updated {}".format(parent_display))
        else:
            print("Parent already lists the folder: {}".format(parent_display))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
