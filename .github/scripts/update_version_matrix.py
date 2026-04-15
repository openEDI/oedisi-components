"""Update version_matrix.csv from monorepo working tree and submodule tags."""

from __future__ import annotations

import csv
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import tomllib

COMPONENTS_DIR = Path("Components")
GITMODULES_PATH = Path(".gitmodules")
CSV_PATH = Path("version_matrix.csv")
NO_VERSION_FOUND_IN_WORKING_TREE = "NO VERSION FOUND IN WORKING TREE"
NO_VERSION_FOUND_AT_TAG = "NO VERSION FOUND AT TAG"


@dataclass(frozen=True)
class RepoTarget:
    """Represents one component version source in a GitHub repository."""

    repo_owner: str
    repo_name: str
    component: str
    pyproject_path: str
    is_submodule: bool


def extract_version_from_pyproject(pyproject_text: str) -> str | None:
    """Parse project.version from pyproject.toml text, if available."""
    parsed = tomllib.loads(pyproject_text)
    version = parsed.get("project", {}).get("version")
    if not version:
        return None
    return str(version)


def read_local_pyproject_version(pyproject_path: str) -> str:
    """Read project.version from a local pyproject.toml in the working tree."""
    pyproject_file = Path(pyproject_path)
    if not pyproject_file.exists():
        return NO_VERSION_FOUND_IN_WORKING_TREE

    text = pyproject_file.read_text(encoding="utf-8")
    version = extract_version_from_pyproject(text)
    return version or NO_VERSION_FOUND_IN_WORKING_TREE


def run_git_command(repo_path: Path, args: list[str]) -> str:
    """Run a git command in repo_path and return stdout."""
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def latest_release_tag(repo_path: Path) -> str | None:
    """Return latest local git tag in repo_path, or None when no tags exist."""
    tags_output = run_git_command(repo_path, ["tag", "--sort=-version:refname"])
    tags = [line.strip() for line in tags_output.splitlines() if line.strip()]
    if not tags:
        return None
    return tags[0]


def fetch_local_pyproject_version_at_tag(repo_path: Path, release_tag: str) -> str:
    """Read pyproject.toml at a local git tag and parse project.version."""
    pyproject_text = run_git_command(repo_path, ["show", f"{release_tag}:pyproject.toml"])
    version = extract_version_from_pyproject(pyproject_text)
    return version or NO_VERSION_FOUND_AT_TAG


def parse_submodule_mapping() -> dict[str, tuple[str, str]]:
    """Map submodule directory path -> (owner, repo) from .gitmodules."""
    if not GITMODULES_PATH.exists():
        return {}

    submodule_text = GITMODULES_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\[submodule\s+\"(?P<name>.+?)\"\]\s*" r"path\s*=\s*(?P<path>.+?)\s*" r"url\s*=\s*(?P<url>.+?)\s*(?:\n|$)",
        flags=re.DOTALL,
    )

    mapping: dict[str, tuple[str, str]] = {}
    for match in pattern.finditer(submodule_text):
        path = match.group("path").strip()
        url = match.group("url").strip()
        parsed = parse_github_url(url)
        if parsed:
            mapping[path] = parsed
    return mapping


def parse_github_url(url: str) -> tuple[str, str] | None:
    """Extract (owner, repo) from common GitHub URL formats."""
    cleaned = url.removesuffix(".git")
    https_match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+)$", cleaned)
    if not https_match:
        return None
    return https_match.group("owner"), https_match.group("repo")


def discover_targets(monorepo_owner: str, monorepo_name: str) -> list[RepoTarget]:
    """Discover component pyproject targets from monorepo and submodules."""
    submodule_mapping = parse_submodule_mapping()
    submodule_paths = set(submodule_mapping.keys())

    targets: list[RepoTarget] = []

    for component_dir in sorted(COMPONENTS_DIR.iterdir()):
        if not component_dir.is_dir():
            continue

        rel_component_dir = component_dir.as_posix()
        if rel_component_dir in submodule_paths:
            continue

        pyproject_file = component_dir / "pyproject.toml"
        if pyproject_file.exists():
            targets.append(
                RepoTarget(
                    repo_owner=monorepo_owner,
                    repo_name=monorepo_name,
                    component=component_dir.name,
                    pyproject_path=pyproject_file.as_posix(),
                    is_submodule=False,
                )
            )

    for submodule_path, (owner, repo) in sorted(submodule_mapping.items()):
        component_name = Path(submodule_path).name
        targets.append(
            RepoTarget(
                repo_owner=owner,
                repo_name=repo,
                component=component_name,
                pyproject_path=f"{submodule_path}/pyproject.toml",
                is_submodule=True,
            )
        )

    if not targets:
        raise RuntimeError("No component targets discovered")

    return targets


def read_existing_records() -> dict[tuple[str, str, str, str], dict[str, str]]:
    """Read existing CSV records keyed by repo and release tag."""
    if not CSV_PATH.exists():
        return {}

    with CSV_PATH.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        records: dict[tuple[str, str, str, str], dict[str, str]] = {}
        for row in reader:
            key = (
                row.get("repo_owner", ""),
                row.get("repo_name", ""),
                row.get("release_tag", ""),
                row.get("component", ""),
            )
            if all(key):
                records[key] = row
        return records


def write_records(records: dict[tuple[str, str, str, str], dict[str, str]]) -> None:
    """Write all records to version_matrix.csv with stable ordering."""
    fieldnames = [
        "repo_owner",
        "repo_name",
        "release_tag",
        "component",
        "component_path",
        "version",
        "last_updated_utc",
    ]

    sorted_items = sorted(
        records.items(),
        key=lambda item: (item[0][0], item[0][1], item[0][2], item[0][3]),
    )

    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for _, row in sorted_items:
            writer.writerow(row)


def main() -> None:
    """Update matrix: monorepo from working tree, submodules from latest tags."""
    monorepo_owner = os.environ.get("MONOREPO_OWNER", "").strip()
    monorepo_name = os.environ.get("MONOREPO_NAME", "").strip()
    if not monorepo_owner or not monorepo_name:
        raise RuntimeError("MONOREPO_OWNER and MONOREPO_NAME are required")

    matrix_release_tag = latest_release_tag(Path("."))
    if not matrix_release_tag:
        raise RuntimeError(f"No tags found for {monorepo_owner}/{monorepo_name}")

    targets = discover_targets(monorepo_owner=monorepo_owner, monorepo_name=monorepo_name)

    records = read_existing_records()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    for target in targets:
        if target.is_submodule:
            submodule_path = Path(target.pyproject_path).parent
            submodule_release_tag = latest_release_tag(submodule_path)
            if submodule_release_tag:
                version = submodule_release_tag
            else:
                version = NO_VERSION_FOUND_AT_TAG
        else:
            version = read_local_pyproject_version(target.pyproject_path)

        key = (target.repo_owner, target.repo_name, matrix_release_tag, target.component)
        existing_row = records.get(key)
        if existing_row:
            existing_row["version"] = version
            existing_row["last_updated_utc"] = now
            records[key] = existing_row
        else:
            records[key] = {
                "repo_owner": target.repo_owner,
                "repo_name": target.repo_name,
                "release_tag": matrix_release_tag,
                "component": target.component,
                "component_path": target.pyproject_path,
                "version": version,
                "last_updated_utc": now,
            }

    write_records(records)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        raise SystemExit(f"Error: {error}") from error
