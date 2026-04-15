"""Update version_matrix.csv using latest GitHub release tags per repository."""

from __future__ import annotations

import csv
import json
import os
import re
import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


COMPONENTS_DIR = Path("Components")
GITMODULES_PATH = Path(".gitmodules")
CSV_PATH = Path("version_matrix.csv")


@dataclass(frozen=True)
class RepoTarget:
    """Represents one component version source in a GitHub repository."""

    repo_owner: str
    repo_name: str
    component: str
    pyproject_path: str


def github_api_json(path: str, token: str) -> object:
    """Call GitHub API and parse JSON payload."""
    request = Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(request) as response:  # nosec B310 - trusted GitHub API URL
        return json.loads(response.read().decode("utf-8"))


def github_api_raw(path: str, token: str) -> str:
    """Call GitHub API and return raw text payload."""
    request = Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github.raw",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(request) as response:  # nosec B310 - trusted GitHub API URL
        return response.read().decode("utf-8")


def latest_release_tag(owner: str, repo: str, token: str) -> str:
    """Get latest published release tag, or fallback to most recent tag."""
    release_path = f"/repos/{owner}/{repo}/releases/latest"
    try:
        response = github_api_json(release_path, token)
    except HTTPError as error:
        if error.code != 404:
            raise
    else:
        if isinstance(response, dict) and response.get("tag_name"):
            return str(response["tag_name"])

    tags_path = f"/repos/{owner}/{repo}/tags?per_page=1"
    tags = github_api_json(tags_path, token)
    if isinstance(tags, list) and tags:
        first = tags[0]
        if isinstance(first, dict) and first.get("name"):
            return str(first["name"])

    raise RuntimeError(f"No tags found for {owner}/{repo}")


def extract_version_from_pyproject(pyproject_text: str) -> str:
    """Parse project.version from pyproject.toml text."""
    parsed = tomllib.loads(pyproject_text)
    version = parsed.get("project", {}).get("version")
    if not version:
        raise ValueError("project.version not found in pyproject.toml")
    return str(version)


def fetch_pyproject_version(
    owner: str,
    repo: str,
    pyproject_path: str,
    release_tag: str,
    token: str,
) -> str:
    """Fetch pyproject.toml at a release tag and return package version."""
    encoded_path = quote(pyproject_path)
    encoded_tag = quote(release_tag)
    api_path = f"/repos/{owner}/{repo}/contents/{encoded_path}?ref={encoded_tag}"
    text = github_api_raw(api_path, token)
    return extract_version_from_pyproject(text)


def parse_submodule_mapping() -> dict[str, tuple[str, str]]:
    """Map submodule directory path -> (owner, repo) from .gitmodules."""
    if not GITMODULES_PATH.exists():
        return {}

    submodule_text = GITMODULES_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\[submodule\s+\"(?P<name>.+?)\"\]\s*"
        r"path\s*=\s*(?P<path>.+?)\s*"
        r"url\s*=\s*(?P<url>.+?)\s*(?:\n|$)",
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
                )
            )

    for submodule_path, (owner, repo) in sorted(submodule_mapping.items()):
        component_name = Path(submodule_path).name
        targets.append(
            RepoTarget(
                repo_owner=owner,
                repo_name=repo,
                component=component_name,
                pyproject_path="pyproject.toml",
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
    """Discover releases/versions and upsert version_matrix.csv rows."""
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required")

    monorepo_owner = os.environ.get("MONOREPO_OWNER", "").strip()
    monorepo_name = os.environ.get("MONOREPO_NAME", "").strip()
    if not monorepo_owner or not monorepo_name:
        raise RuntimeError("MONOREPO_OWNER and MONOREPO_NAME are required")

    targets = discover_targets(monorepo_owner=monorepo_owner, monorepo_name=monorepo_name)
    unique_repos = sorted({(target.repo_owner, target.repo_name) for target in targets})

    release_tags: dict[tuple[str, str], str] = {}
    for owner, repo in unique_repos:
        release_tags[(owner, repo)] = latest_release_tag(owner=owner, repo=repo, token=token)

    records = read_existing_records()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    for target in targets:
        release_tag = release_tags[(target.repo_owner, target.repo_name)]
        version = fetch_pyproject_version(
            owner=target.repo_owner,
            repo=target.repo_name,
            pyproject_path=target.pyproject_path,
            release_tag=release_tag,
            token=token,
        )

        key = (target.repo_owner, target.repo_name, release_tag, target.component)
        records[key] = {
            "repo_owner": target.repo_owner,
            "repo_name": target.repo_name,
            "release_tag": release_tag,
            "component": target.component,
            "component_path": target.pyproject_path,
            "version": version,
            "last_updated_utc": now,
        }

    write_records(records)


if __name__ == "__main__":
    try:
        main()
    except (HTTPError, URLError, ValueError, RuntimeError) as error:
        raise SystemExit(f"Error: {error}") from error