"""Simple project scaffolding helper.

This script prompts for a project name (unless provided as an argument) and
creates a starter folder structure for the new project.  The default structure
is intentionally generic so it works for a variety of projects, and it can be
customised by pointing to a JSON file that lists folder names.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable, List

DEFAULT_FOLDERS: List[str] = [
    "docs",
    "config",
    "scripts",
    "ci",
    "public",
    "public/images",
    "public/fonts",
    "src",
    "src/components",
    "src/hooks",
    "src/utils",
    "src/styles",
    "src/assets",
    "tests",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a folder structure for a new project."
    )
    parser.add_argument(
        "project_name",
        nargs="?",
        help="Name of the project. When omitted, you will be prompted for it.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=".",
        help="Directory where the project will be created. Defaults to the current directory.",
    )
    parser.add_argument(
        "-s",
        "--structure-file",
        type=Path,
        help=(
            "Optional path to a JSON file containing a list of folder names or a "
            'dictionary with a top-level "folders" list.'
        ),
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help=(
            "Allow using an existing project directory (contents will be preserved). "
            "Without this flag the script will abort if the directory is not empty."
        ),
    )
    return parser.parse_args()


def sanitize_project_name(raw_name: str) -> str:
    """Convert the provided name into a filesystem-friendly slug."""
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", raw_name.strip())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    if not cleaned:
        raise ValueError("Project name cannot be empty after sanitization.")
    return cleaned


def load_structure(structure_file: Path | None) -> List[str]:
    if structure_file is None:
        return DEFAULT_FOLDERS

    if not structure_file.exists():
        raise FileNotFoundError(f"Cannot read structure file: {structure_file}")

    parsed = json.loads(structure_file.read_text())
    folder_list = parsed.get("folders") if isinstance(parsed, dict) else parsed

    if not isinstance(folder_list, list) or not all(
        isinstance(item, str) for item in folder_list
    ):
        raise ValueError("Structure file must contain a list of folder names.")

    return folder_list


def create_folders(project_root: Path, folders: Iterable[str]) -> list[Path]:
    created_paths: list[Path] = []
    for folder in folders:
        folder_path = project_root / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        created_paths.append(folder_path)
    return created_paths


def ensure_target_directory(target: Path, force: bool) -> None:
    target.mkdir(parents=True, exist_ok=True)

    if force:
        return

    if any(target.iterdir()):
        raise FileExistsError(
            f"{target} already exists and is not empty. Re-run with --force to reuse it."
        )


def main() -> None:
    args = parse_args()

    project_name = args.project_name or input("Enter project name: ").strip()
    try:
        sanitized_name = sanitize_project_name(project_name)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir).expanduser().resolve()
    project_root = output_dir / sanitized_name

    try:
        ensure_target_directory(project_root, args.force)
    except FileExistsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        folders = load_structure(args.structure_file)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error reading structure: {exc}", file=sys.stderr)
        sys.exit(1)

    created = create_folders(project_root, folders)

    print(f"Project '{sanitized_name}' created at: {project_root}")
    if args.structure_file:
        print(f"Structure loaded from: {args.structure_file}")

    print("Folders created:")
    for path in created:
        print(f" - {path.relative_to(project_root)}")


if __name__ == "__main__":
    main()
