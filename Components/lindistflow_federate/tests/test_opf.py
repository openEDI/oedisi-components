"""Tests for LinDistFlow optimal power flow federate."""

import json
from pathlib import Path

from lindistflow_federate import ComponentParameters


class TestLinDistFlowOptimization:
    """Test optimal power flow algorithms."""

    def test_generate_schema(self) -> None:
        """Generate schema.json from ComponentParameters model."""
        schema_path = Path(__file__).parent.parent / "schema.json"
        schema_dict = ComponentParameters.model_json_schema()

        # Verify fields are mapped correctly
        assert "name" in schema_dict["properties"]
        assert "deltat" in schema_dict["properties"]
        assert "control_type" in schema_dict["properties"]
        assert "pf_flag" in schema_dict["properties"]

        # Write schema to file
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema_dict, f, indent=2)
            f.write("\n")

    def test_component_definition_matches_federate(self) -> None:
        """Test that component_definition.json is accurate with the component and schema."""
        # Load component_definition.json
        comp_def_path = Path(__file__).parent.parent / "component_definition.json"
        with open(comp_def_path, encoding="utf-8") as f:
            comp_def = json.load(f)

        # Load schema.json
        schema_path = Path(__file__).parent.parent / "schema.json"
        with open(schema_path, encoding="utf-8") as f:
            schema = json.load(f)

        # 1. Verify static inputs match schema.json properties
        static_inputs = {item["port_id"] for item in comp_def.get("static_inputs", [])}
        expected_static = set(schema.get("properties", {}).keys())
        assert static_inputs == expected_static, f"Static inputs mismatch: {static_inputs} vs {expected_static}"

        # 2. Verify dynamic inputs (subscriptions)
        dynamic_inputs = {item["port_id"]: item["type"] for item in comp_def.get("dynamic_inputs", [])}
        expected_inputs = {
            "topology": "Topology",
            "voltages_magnitude": "VoltagesMagnitude",
            "injections": "Injection",
        }
        assert dynamic_inputs == expected_inputs, f"Dynamic inputs mismatch: {dynamic_inputs} vs {expected_inputs}"

        # 3. Verify dynamic outputs (publications)
        dynamic_outputs = {item["port_id"]: item["type"] for item in comp_def.get("dynamic_outputs", [])}
        expected_outputs = {
            "change_commands": "CommandList",
            "opf_voltages_magnitude": "VoltagesMagnitude",
            "opf_voltages_angle": "VoltagesAngle",
            "opf_power_magnitude": "PowersMagnitude",
            "opf_power_angle": "PowersAngle",
            "opf_control_power_real": "PowersReal",
            "opf_control_power_imaginary": "PowersImaginary",
        }
        assert dynamic_outputs == expected_outputs, f"Dynamic outputs mismatch: {dynamic_outputs} vs {expected_outputs}"
