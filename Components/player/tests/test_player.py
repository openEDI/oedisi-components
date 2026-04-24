"""Tests for the Player dataset playback federate."""

import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the player FastAPI app."""
    from player.server import app

    return TestClient(app)


@pytest.fixture
def simple_df():
    """A simple MeasurementArray-compatible DataFrame (no equipment_ids)."""
    return pd.DataFrame(
        {
            "bus_1": [1.0, 1.01, 1.02],
            "bus_2": [0.98, 0.99, 1.0],
            "bus_3": [0.97, 0.98, 0.99],
            "time": [
                "2023-01-01 00:00:00",
                "2023-01-01 00:01:00",
                "2023-01-01 00:02:00",
            ],
        }
    )


@pytest.fixture
def equipment_node_df():
    """A DataFrame compatible with EquipmentNodeArray types (e.g. PowersReal)."""
    return pd.DataFrame(
        {
            "node_1": [10.0, 10.5],
            "node_2": [20.0, 20.5],
            "time": ["2023-01-01 00:00:00", "2023-01-01 00:01:00"],
        }
    )


class TestPlayerHealthCheck:
    """Test player health check endpoint."""

    def test_root_endpoint_returns_health_info(self, client):
        """Test that the root endpoint returns hostname and IP information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "hostname" in data
        assert "host_ip" in data


class TestPlayerImport:
    """Test player module imports."""

    def test_player_can_be_imported(self):
        """Test that Player class can be imported."""
        from player import Player

        assert Player is not None
        assert hasattr(Player, "__init__")
        assert hasattr(Player, "run")

    def test_player_config_can_be_imported(self):
        """Test that ComponentParameters can be imported."""
        from player import ComponentParameters

        assert ComponentParameters is not None

    def test_type_map_can_be_imported(self):
        """Test that TYPE_MAP is accessible and populated."""
        from player import TYPE_MAP

        assert "MeasurementArray" in TYPE_MAP
        assert "VoltagesMagnitude" in TYPE_MAP
        assert "PowersReal" in TYPE_MAP
        assert len(TYPE_MAP) > 10


class TestPlayerLoadDataset:
    """Test dataset loading from different file formats."""

    def test_load_csv(self, simple_df):
        """Test that a CSV file is loaded correctly."""
        from player.play_dataset import Player

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            simple_df.to_csv(f.name, index=False)
            result = Player._load_dataset(None, f.name)

        assert list(result.columns) == list(simple_df.columns)
        assert len(result) == len(simple_df)

    def test_load_feather(self, simple_df):
        """Test that a Feather file is loaded correctly."""
        from player.play_dataset import Player

        with tempfile.NamedTemporaryFile(suffix=".feather", delete=False) as f:
            simple_df.to_feather(f.name)
            result = Player._load_dataset(None, f.name)

        assert list(result.columns) == list(simple_df.columns)
        assert len(result) == len(simple_df)

    def test_unsupported_format_raises(self):
        """Test that an unsupported file extension raises ValueError."""
        from player.play_dataset import Player

        with pytest.raises(ValueError, match="Unsupported file format"):
            Player._load_dataset(None, "data.parquet")


class TestPlayerBuildMeasurement:
    """Test _build_measurement constructs typed measurement objects correctly."""

    def _make_player_stub(self, data_type: str, metadata: dict | None = None):
        """Create a minimal Player-like stub without HELICS."""
        from player.play_dataset import TYPE_MAP, Player

        _metadata = metadata if metadata is not None else {}

        class Stub:
            type_class = TYPE_MAP[data_type]
            _metadata_path = "data.csv"

            @property
            def metadata(self):
                return _metadata

        stub = Stub()
        stub._build_measurement = Player._build_measurement.__get__(stub)
        return stub

    def test_build_voltages_magnitude(self, simple_df):
        """Test building a VoltagesMagnitude measurement from a DataFrame row."""
        stub = self._make_player_stub("VoltagesMagnitude")
        row = simple_df.iloc[0]
        measurement = stub._build_measurement(row, 0)

        from oedisi.types.data_types import VoltagesMagnitude

        assert isinstance(measurement, VoltagesMagnitude)
        assert measurement.ids == ["bus_1", "bus_2", "bus_3"]
        assert measurement.values == [1.0, 0.98, 0.97]
        assert measurement.units == "V"  # oedisi 3.x default for VoltagesMagnitude

    def test_build_measurement_array_base_type(self, simple_df):
        """Test building a base MeasurementArray type (requires units in metadata)."""
        stub = self._make_player_stub("MeasurementArray", metadata={"units": "pu"})
        row = simple_df.iloc[0]
        measurement = stub._build_measurement(row, 0)

        from oedisi.types.data_types import MeasurementArray

        assert isinstance(measurement, MeasurementArray)
        assert measurement.ids == ["bus_1", "bus_2", "bus_3"]
        assert measurement.units == "pu"

    def test_build_equipment_node_array_with_metadata(self, equipment_node_df):
        """Test building a PowersReal measurement with equipment_ids from metadata."""
        metadata = {"equipment_ids": ["PVSystem.1", "PVSystem.2"], "units": "kW"}
        stub = self._make_player_stub("PowersReal", metadata=metadata)
        row = equipment_node_df.iloc[0]
        measurement = stub._build_measurement(row, 0)

        from oedisi.types.data_types import PowersReal

        assert isinstance(measurement, PowersReal)
        assert measurement.equipment_ids == ["PVSystem.1", "PVSystem.2"]
        assert measurement.ids == ["node_1", "node_2"]
        assert measurement.values == [10.0, 20.0]

    def test_build_equipment_node_array_missing_metadata_raises(
        self, equipment_node_df
    ):
        """Test that missing equipment_ids metadata raises ValueError."""
        stub = self._make_player_stub("PowersReal", metadata={})
        row = equipment_node_df.iloc[0]

        with pytest.raises(ValueError, match="equipment_ids"):
            stub._build_measurement(row, 0)

    def test_build_measurement_preserves_time(self, simple_df):
        """Test that the time column is passed through to the measurement."""
        stub = self._make_player_stub("VoltagesMagnitude")
        row = simple_df.iloc[0]
        measurement = stub._build_measurement(row, 0)

        assert measurement.time is not None


class TestPlayerTypeMap:
    """Test the TYPE_MAP covers all expected types."""

    def test_all_bus_array_subtypes_present(self):
        from player import TYPE_MAP

        for name in [
            "VoltagesMagnitude",
            "VoltagesAngle",
            "VoltagesReal",
            "VoltagesImaginary",
        ]:
            assert name in TYPE_MAP, f"{name} missing from TYPE_MAP"

    def test_all_equipment_array_subtypes_present(self):
        from player import TYPE_MAP

        for name in [
            "CurrentsMagnitude",
            "CurrentsAngle",
            "CurrentsReal",
            "CurrentsImaginary",
            "SolarIrradiances",
            "Temperatures",
            "WindSpeeds",
            "StatesOfCharge",
            "ImpedanceMagnitude",
            "ImpedanceAngle",
            "ImpedanceReal",
            "ImpedanceImaginary",
        ]:
            assert name in TYPE_MAP, f"{name} missing from TYPE_MAP"

    def test_all_equipment_node_array_subtypes_present(self):
        from player import TYPE_MAP

        for name in ["PowersMagnitude", "PowersAngle", "PowersReal", "PowersImaginary"]:
            assert name in TYPE_MAP, f"{name} missing from TYPE_MAP"


class TestComponentParameters:
    """Test ComponentParameters validation."""

    def test_unknown_data_type_raises_on_player_init(self):
        """Test that an unknown data_type raises ValueError during Player instantiation.

        The data_type check happens before file loading, so no actual file is needed.
        """
        from player.play_dataset import Player, ComponentParameters
        from oedisi.types.common import BrokerConfig

        config = ComponentParameters(
            name="test",
            filename="nonexistent.csv",
            data_type="NotARealType",
            number_of_timesteps=1,
            start_time_index=0,
        )
        with pytest.raises(ValueError, match="Unknown data_type"):
            Player(config, BrokerConfig(broker_ip="127.0.0.1"))

    def test_valid_config_accepted(self):
        """Test that a valid ComponentParameters is accepted."""
        from player.play_dataset import ComponentParameters

        config = ComponentParameters(
            name="test_player",
            filename="data.feather",
            data_type="VoltagesMagnitude",
            number_of_timesteps=1,
            start_time_index=0,
        )
        assert config.data_type == "VoltagesMagnitude"
        assert config.number_of_timesteps == 1
        assert config.start_time_index == 0

    def test_metadata_sidecar_loaded(self, tmp_path):
        """Test that a metadata sidecar JSON is loaded when present."""
        from player.play_dataset import Player

        dataset_file = str(tmp_path / "data.csv")
        metadata_file = dataset_file + "_metadata.json"
        metadata = {"equipment_ids": ["A", "B"], "units": "kW"}

        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

        result = Player._load_metadata(None, dataset_file)
        assert result == metadata

    def test_missing_metadata_sidecar_returns_empty_dict(self, tmp_path):
        """Test that missing metadata sidecar returns an empty dict."""
        from player.play_dataset import Player

        result = Player._load_metadata(None, str(tmp_path / "data.csv"))
        assert result == {}
