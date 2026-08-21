"""Tests to verify the JSON schema matches the ComponentParameters definition."""

import json
import sys
from pathlib import Path

# Insert package source directory to python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from player.play_dataset import ComponentParameters  # noqa: E402


def test_component_parameters_schema() -> None:
    """Generate and verify that schema.json matches ComponentParameters."""
    schema = ComponentParameters.model_json_schema()
    schema_path = Path(__file__).resolve().parents[1] / "schema.json"

    # If schema.json doesn't exist, write it
    if not schema_path.exists():
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)
            f.write("\n")

    with open(schema_path, encoding="utf-8") as f:
        existing_schema = json.load(f)

    assert existing_schema == schema
