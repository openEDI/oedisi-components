import json
import os
from pathlib import Path

import docker
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from rich import print

load_dotenv()

# --- Configuration ---
DOCKERHUB_USERNAME_AL = os.getenv("DOCKERHUB_USERNAME_AL")
DOCKERHUB_API_KEY_AL = os.getenv("DOCKERHUB_API_KEY_AL")
MAILJET_API_KEY = os.environ["MAILJET_API_KEY"]
MAILJET_API_SECRET = os.environ["MAILJET_API_SECRET"]
TAG = os.environ["RELEASE_TAG"]


def collect_components():
    # Simulate collecting components
    print("Collecting components...")
    components = json.load(open("components.json"))  # Load components from a JSON file
    for component_name, component_path in components.items():
        try:
            print(f"Building image for component {component_name}...")
            component_path = Path(component_path).parent
            if not component_path.is_dir():
                raise ValueError(f"Component path {component_path} is not a directory")
            if not (component_path / "Dockerfile").is_file():
                raise ValueError(f"No Dockerfile found in {component_path}")
            build_and_push_docker_image(
                component_name,
                component_path,
            )
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def build_and_push_docker_image(image_name, docker_file_path, tag="v0.0.1"):
    client = docker.from_env()
    REPOSITORY_NAME = f"{DOCKERHUB_USERNAME_AL}/{image_name}:{tag}".lower()
    email_msg = f"Building Docker image: {REPOSITORY_NAME} from directory {docker_file_path}"

    try:
        # Build the image
        image, build_logs = client.images.build(
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
            tag=TAG,
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
    os.system(f"docker login -u {DOCKERHUB_USERNAME_AL} -p {DOCKERHUB_API_KEY_AL}")
    collect_components()
