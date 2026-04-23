"""Workflow runner for building and pushing Docker images."""

import csv
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import docker
import requests
from requests.auth import HTTPBasicAuth
from rich import print

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# --- Configuration ---
DOCKERHUB_USERNAME_AL = os.getenv("DOCKERHUB_USERNAME_AL")
DOCKERHUB_API_KEY_AL = os.getenv("DOCKERHUB_API_KEY_AL")
MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")

COMPONENTS_DIR = REPO_ROOT / "Components"
COMPONENTS_JSON = REPO_ROOT / "components.json"
VERSION_MATRIX_CSV = REPO_ROOT / "version_matrix.csv"
GITMODULES_PATH = REPO_ROOT / ".gitmodules"
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY", "")
NO_VERSION_PREFIX = "NO VERSION FOUND"


@dataclass(frozen=True)
class ComponentTarget:
    """Docker build target and source repository metadata."""

    component_name: str
    component_path: Path
    repo_owner: str
    repo_name: str


def run_git_command(args: list[str]) -> str:
    """Run a git command from repository root and return stdout."""
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _parse_utc_timestamp(timestamp: str) -> datetime:
    """Parse UTC timestamps produced by update_version_matrix.py."""
    value = (timestamp or "").strip()
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    if value.endswith("Z"):
        value = f"{value[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def resolve_component_directory(raw_path: str) -> Path | None:
    """Resolve a component path entry to its Docker build directory."""
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate

    if candidate.is_file():
        candidate = candidate.parent

    if not candidate.is_dir():
        return None

    return candidate


def parse_github_url(url: str) -> tuple[str, str] | None:
    """Extract (owner, repo) from common GitHub URL formats."""
    cleaned = url.removesuffix(".git")
    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+)$", cleaned)
    if not match:
        return None
    return match.group("owner"), match.group("repo")


def parse_submodule_mapping() -> dict[str, tuple[str, str]]:
    """Map submodule path -> (owner, repo) from .gitmodules via git config."""
    if not GITMODULES_PATH.is_file():
        print(f"No .gitmodules found at {GITMODULES_PATH}; assuming no submodules")
        return {}

    path_lines = run_git_command(
        ["config", "--file", str(GITMODULES_PATH), "--get-regexp", r"^submodule\..*\.path$"]
    ).splitlines()
    url_lines = run_git_command(
        ["config", "--file", str(GITMODULES_PATH), "--get-regexp", r"^submodule\..*\.url$"]
    ).splitlines()

    path_by_name: dict[str, str] = {}
    for line in path_lines:
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        key, path = parts
        # key format: submodule.<name>.path
        name = key.removeprefix("submodule.").removesuffix(".path")
        if name:
            path_by_name[name] = path.strip()

    url_by_name: dict[str, str] = {}
    for line in url_lines:
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        key, url = parts
        # key format: submodule.<name>.url
        name = key.removeprefix("submodule.").removesuffix(".url")
        if name:
            url_by_name[name] = url.strip()

    mapping: dict[str, tuple[str, str]] = {}
    for name, path in path_by_name.items():
        url = url_by_name.get(name)
        if not url:
            continue
        parsed = parse_github_url(url)
        if parsed:
            mapping[path] = parsed

    print(f"Discovered {len(mapping)} submodule mappings from .gitmodules")

    return mapping


def monorepo_identity() -> tuple[str, str]:
    """Infer monorepo owner/name from GitHub Actions environment."""
    env_owner = os.getenv("MONOREPO_OWNER", "").strip()
    env_repo = os.getenv("MONOREPO_NAME", "").strip()
    if env_owner and env_repo:
        return env_owner, env_repo

    if "/" in GITHUB_REPOSITORY:
        owner, repo = GITHUB_REPOSITORY.split("/", 1)
        if owner and repo:
            return owner, repo
    return "", ""


def discover_component_targets() -> list[ComponentTarget]:
    """Find build targets from Components/ and components.json with repo mapping."""
    print("Discovering component targets...")
    discovered: dict[str, Path] = {}
    submodule_mapping = parse_submodule_mapping()
    monorepo_owner, monorepo_name = monorepo_identity()

    if COMPONENTS_DIR.is_dir():
        for entry in sorted(COMPONENTS_DIR.iterdir()):
            if not entry.is_dir():
                continue
            if (entry / "Dockerfile").is_file():
                discovered[entry.resolve().as_posix()] = entry
    print(f"Found {len(discovered)} Components/* entries with Dockerfile")

    if not COMPONENTS_JSON.is_file():
        raise RuntimeError(f"Required file missing: {COMPONENTS_JSON}")

    components = json.loads(COMPONENTS_JSON.read_text(encoding="utf-8"))
    print(f"Loaded {len(components)} entries from components.json")
    for raw_path in components.values():
        component_dir = resolve_component_directory(str(raw_path))
        if not component_dir:
            continue
        if (component_dir / "Dockerfile").is_file():
            discovered[component_dir.resolve().as_posix()] = component_dir

    targets: list[ComponentTarget] = []
    root = REPO_ROOT
    for key in sorted(discovered.keys()):
        component_path = discovered[key]
        component_name = component_path.name
        repo_owner = monorepo_owner
        repo_name = monorepo_name

        try:
            rel_path = component_path.resolve().relative_to(root).as_posix()
        except ValueError:
            rel_path = component_path.as_posix()

        submodule_repo = submodule_mapping.get(rel_path)
        if submodule_repo:
            repo_owner, repo_name = submodule_repo

        targets.append(
            ComponentTarget(
                component_name=component_name,
                component_path=component_path,
                repo_owner=repo_owner,
                repo_name=repo_name,
            )
        )

    print(f"Resolved {len(targets)} unique component build targets")

    return targets


def latest_repo_tag(repo_owner: str, repo_name: str) -> str | None:
    """Return latest repository tag using git CLI against GitHub remote."""
    if not repo_owner or not repo_name:
        return None

    remote = f"https://github.com/{repo_owner}/{repo_name}.git"
    print(f"Fetching latest tag from {remote}")
    output = run_git_command(
        [
            "ls-remote",
            "--refs",
            "--tags",
            "--sort=-version:refname",
            remote,
        ]
    )
    if not output:
        return None

    first_line = output.splitlines()[0].strip()
    if not first_line:
        return None

    # Format: <sha>\trefs/tags/<tag>
    parts = first_line.split("\t", 1)
    if len(parts) != 2:
        return None
    ref = parts[1]
    prefix = "refs/tags/"
    if not ref.startswith(prefix):
        return None

    tag_name = ref[len(prefix) :].strip()
    if tag_name:
        print(f"Latest tag for {repo_owner}/{repo_name}: {tag_name}")
    return tag_name or None


def resolve_component_tag(
    target: ComponentTarget,
    matrix_rows: list[dict[str, str]],
    tag_cache: dict[tuple[str, str], str | None],
) -> str:
    """Resolve Docker tag from version_matrix.csv for the repository's latest tag."""
    repo_key = (target.repo_owner, target.repo_name)
    latest_tag = tag_cache.get(repo_key)

    if repo_key not in tag_cache:
        try:
            latest_tag = latest_repo_tag(target.repo_owner, target.repo_name)
        except subprocess.CalledProcessError as error:
            print(f"Failed to read latest tag for {target.repo_owner}/{target.repo_name}: {error}")
            latest_tag = None
        tag_cache[repo_key] = latest_tag

    if not latest_tag:
        raise RuntimeError(
            f"No repository tag found for {target.repo_owner}/{target.repo_name}; "
            f"cannot resolve CSV version for {target.component_name}"
        )

    csv_version = version_from_matrix(target, latest_tag, matrix_rows)

    if not csv_version:
        raise RuntimeError(
            f"No CSV version found for component={target.component_name}, "
            f"repo={target.repo_owner}/{target.repo_name}, release_tag={latest_tag}"
        )

    print(f"Tag decision for {target.component_name}: " f"repo_tag={latest_tag}, selected_csv_version={csv_version}")
    return csv_version


def load_matrix_rows() -> list[dict[str, str]]:
    """Read all records from version_matrix.csv."""
    if not VERSION_MATRIX_CSV.is_file():
        return []

    with VERSION_MATRIX_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def version_from_matrix(target: ComponentTarget, release_tag: str | None, rows: list[dict[str, str]]) -> str | None:
    """Return component version for a specific repo + release tag selection."""
    if not rows:
        return None

    candidates: list[tuple[datetime, str]] = []

    for row in rows:
        repo_owner = (row.get("repo_owner") or "").strip()
        repo_name = (row.get("repo_name") or "").strip()
        if repo_owner != target.repo_owner or repo_name != target.repo_name:
            continue

        row_tag = (row.get("release_tag") or "").strip()
        if release_tag and row_tag != release_tag:
            continue

        component = (row.get("component") or "").strip()
        path_name = Path(row.get("component_path") or "").parent.name.strip()
        if target.component_name not in {component, path_name}:
            continue

        version = (row.get("version") or "").strip()
        if not version or version.upper().startswith(NO_VERSION_PREFIX):
            continue

        updated = _parse_utc_timestamp(row.get("last_updated_utc") or "")
        candidates.append((updated, version))

    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def collect_components():
    """Collect components and build/push Docker images."""
    print("Collecting components...")
    targets = discover_component_targets()
    if not targets:
        raise RuntimeError("No component directories with Dockerfile were discovered")

    matrix_rows = load_matrix_rows()
    print(f"Loaded {len(matrix_rows)} rows from version_matrix.csv")
    tag_cache: dict[tuple[str, str], str | None] = {}

    for target in targets:
        tag = resolve_component_tag(target, matrix_rows, tag_cache)
        print(
            "Building image for component "
            f"{target.component_name} from {target.repo_owner}/{target.repo_name} "
            f"with tag {tag}..."
        )
        build_and_push_docker_image(
            target.component_name,
            target.component_path,
            tag,
        )
        print(f"Finished component {target.component_name}")


def validate_required_env() -> None:
    """Validate required environment variables for local and CI execution."""
    missing = []
    if not DOCKERHUB_USERNAME_AL:
        missing.append("DOCKERHUB_USERNAME_AL")
    if not DOCKERHUB_API_KEY_AL:
        missing.append("DOCKERHUB_API_KEY_AL")

    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing required environment variables: {joined}. Set them in .env.")


def docker_login() -> None:
    """Login to Docker Hub without exposing secrets in a shell command."""
    print("Connecting to Docker daemon...")
    client = docker.from_env()
    print("Docker daemon reachable. Logging in to Docker Hub...")
    client.login(username=DOCKERHUB_USERNAME_AL, password=DOCKERHUB_API_KEY_AL)
    print("Docker login successful")


def build_and_push_docker_image(image_name, docker_file_path, tag):
    """Build and push a Docker image to Docker Hub."""
    client = docker.from_env()
    REPOSITORY_NAME = f"{DOCKERHUB_USERNAME_AL}/{image_name}:{tag}".lower()
    email_msg = f"Building Docker image: {REPOSITORY_NAME} from directory {docker_file_path}"

    try:
        # Build the image
        image, _ = client.images.build(
            path=str(docker_file_path),
            tag=REPOSITORY_NAME,
            rm=True,  # Remove intermediate containers after a successful build
            nocache=False,  # Do not use cache when building the image
        )

        email_msg += f"\nSuccessfully built image: {REPOSITORY_NAME}"

        labels = image.attrs["Config"].get("Labels") or {}
        author_names = []
        author_emails = []
        authors_label = labels.get("org.opencontainers.image.authors")
        if authors_label:
            for author in authors_label.split(","):
                author = author.strip()
                if "<" in author and ">" in author:
                    name, email = author.split("<", 1)
                    author_names.append(name.strip())
                    author_emails.append(email.strip("> ").strip())
                else:
                    author_names.append(author)
                    author_emails.append(None)

            print(f"Image authors: {{'names': {author_names}, 'emails': {author_emails}}}")

    except docker.errors.BuildError as e:
        email_msg += f"\nError building image: {e}"
        print(f"Error building image: {e}")
        return

    print(f"2. Logging in to Docker Hub as {DOCKERHUB_USERNAME_AL}")
    email_msg += f"\nLogging in to Docker Hub as {DOCKERHUB_USERNAME_AL}"

    email_msg += f"\nPushing image to Docker Hub: {REPOSITORY_NAME}"
    print(f"3. Pushing image to Docker Hub: {REPOSITORY_NAME}")
    try:
        # Push the image to Docker Hub
        # The push operation returns an iterator of events
        push_logs = client.images.push(
            repository=f"{DOCKERHUB_USERNAME_AL}/{image_name}".lower(),
            tag=tag,
            stream=True,
            decode=True,
        )
        for line in push_logs:
            if "status" in line:
                print(line["status"])
            elif "error" in line:
                print(f"Error during push: {line['error']}")
                email_msg += f"\nError during push: {line['error']}"

        print("Image pushed successfully to Docker Hub.")
        email_msg += "\nImage pushed successfully to Docker Hub."

    except docker.errors.APIError as e:
        print(f"Docker API Error during push: {e}")
        email_msg += f"Docker API Error during push: {e}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        email_msg += f"An unexpected error occurred: {e}"

    if not MAILJET_API_KEY or not MAILJET_API_SECRET:
        print("MAILJET_API_KEY/MAILJET_API_SECRET not configured; skipping email notifications")
        return

    for name, email in zip(author_names, author_emails, strict=False):
        if not email:
            print(f"Skipping author '{name}' - no email available")
            continue

        payload = {
            "Messages": [
                {
                    "From": {"Email": "aadil.latif@gmail.com", "Name": "Aadil Latif"},
                    "To": [{"Email": email, "Name": name}],
                    "Subject": "OEDISI GitHub Workflow Notification",
                    "TextPart": email_msg,
                }
            ]
        }

        try:
            response = requests.post(
                "https://api.mailjet.com/v3.1/send",
                json=payload,
                auth=HTTPBasicAuth(MAILJET_API_KEY, MAILJET_API_SECRET),
                timeout=30,
            )
            response.raise_for_status()
            print(f"Mail sent to {email}: {response.status_code}")
        except requests.exceptions.HTTPError as http_err:
            # Surface the server response body to help debugging 400 errors
            try:
                err_text = response.text
            except Exception:
                err_text = str(http_err)
            print(f"Mailjet HTTP error for {email}: {response.status_code} - {err_text}")
        except Exception as e:
            print(f"Failed to send mail to {email}: {e}")


if __name__ == "__main__":
    print("Validating required environment variables...")
    validate_required_env()
    print("Environment variables validated")
    docker_login()
    print("Starting component collection and build workflow...")
    collect_components()
