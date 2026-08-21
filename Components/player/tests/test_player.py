"""Tests for the Player dataset playback federate."""

import json
import tempfile

import pandas as pd
import pytest
from oedisi.types.common import BrokerConfig
from player.play_dataset import TYPE_MAP, ComponentParameters, Player


@pytest.fixture
def simple_df():
    """A simple MeasurementArray-compatible DataFrame."""
    return pd.DataFrame(
        {
            "bus_1": [1.0, 1.01, 1.02, 1.03, 1.04],
            "bus_2": [0.98, 0.99, 1.0, 1.01, 1.02],
            "bus_3": [0.97, 0.98, 0.99, 1.0, 1.01],
            "time": [
                "2023-01-01 00:00:00",
                "2023-01-01 00:01:00",
                "2023-01-01 00:02:00",
                "2023-01-01 00:03:00",
                "2023-01-01 00:04:00",
            ],
        }
    )


class MocklessPlayer(Player):
    """A version of Player that bypasses HELICS initialization for unit testing."""

    def __init__(self, config: ComponentParameters, broker_config: BrokerConfig):
        """Initialize mockless player for unit tests."""
        if config.data_type not in TYPE_MAP:
            raise ValueError(f"Unknown data_type '{config.data_type}'. Valid types: {sorted(TYPE_MAP.keys())}")
        self.type_class = TYPE_MAP[config.data_type]
        self.dataset = self._load_dataset(config.filename)
        self._dataset_path = config.filename
        self.metadata = self._load_metadata(config.filename)

        if config.start_time_index >= len(self.dataset):
            raise ValueError(
                f"start_time_index {config.start_time_index} is out of range "
                f"for dataset with {len(self.dataset)} row(s)."
            )

        self.dataset = self.dataset.iloc[config.start_time_index : config.start_time_index + config.number_of_timesteps]
        self.t_start = 0
        self.t_steps = len(self.dataset)


class TestPlayerDatasetOperations:
    """Test data loading, starting time, duration, and datatype checking."""

    def test_load_csv_and_feather(self, simple_df):
        """Verify that the player can load CSV and Feather formats correctly."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f_csv:
            simple_df.to_csv(f_csv.name, index=False)
            loaded_csv = Player._load_dataset(f_csv.name)
            assert len(loaded_csv) == 5

        with tempfile.NamedTemporaryFile(suffix=".feather", delete=False) as f_fea:
            simple_df.to_feather(f_fea.name)
            loaded_fea = Player._load_dataset(f_fea.name)
            assert len(loaded_fea) == 5

        with pytest.raises(ValueError, match="Unsupported file format"):
            Player._load_dataset("data.parquet")

    def test_start_time_and_duration(self, simple_df):
        """Verify that the player filters the dataset at correct start index and duration."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            simple_df.to_csv(f.name, index=False)

            # Start index 2, duration (timesteps) 2
            config = ComponentParameters(
                name="test_player",
                filename=f.name,
                data_type="VoltagesMagnitude",
                number_of_timesteps=2,
                start_time_index=2,
            )
            broker_config = BrokerConfig(broker_ip="127.0.0.1")

            player = MocklessPlayer(config, broker_config)

            # Verify filtering: should contain rows at index 2 and 3 of simple_df
            assert len(player.dataset) == 2
            assert player.dataset.iloc[0]["bus_1"] == 1.02
            assert player.dataset.iloc[1]["bus_1"] == 1.03
            assert player.t_steps == 2

            # Start index out of bounds raises ValueError
            invalid_config = ComponentParameters(
                name="test_player",
                filename=f.name,
                data_type="VoltagesMagnitude",
                number_of_timesteps=2,
                start_time_index=10,
            )
            with pytest.raises(ValueError, match="start_time_index 10 is out of range"):
                MocklessPlayer(invalid_config, broker_config)

    def test_datatype_validation(self, simple_df):
        """Verify that the player checks and validates datatype correctly."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            simple_df.to_csv(f.name, index=False)

            # Unknown datatype raises ValueError during initialization
            config_invalid_type = ComponentParameters(
                name="test_player",
                filename=f.name,
                data_type="InvalidDataType",
                number_of_timesteps=2,
                start_time_index=0,
            )
            broker_config = BrokerConfig(broker_ip="127.0.0.1")

            with pytest.raises(ValueError, match="Unknown data_type"):
                MocklessPlayer(config_invalid_type, broker_config)

            # Valid datatype loads correctly
            config_valid = ComponentParameters(
                name="test_player",
                filename=f.name,
                data_type="VoltagesMagnitude",
                number_of_timesteps=2,
                start_time_index=0,
            )
            player = MocklessPlayer(config_valid, broker_config)
            assert player.type_class.__name__ == "VoltagesMagnitude"

    def test_metadata_sidecar_loading(self, tmp_path):
        """Verify that a metadata sidecar JSON is loaded when present."""
        dataset_file = str(tmp_path / "data.csv")
        metadata_file = dataset_file + "_metadata.json"
        metadata = {"equipment_ids": ["A", "B"], "units": "kW"}

        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

        result = Player._load_metadata(dataset_file)
        assert result == metadata

        # Missing sidecar returns empty dict
        assert Player._load_metadata(str(tmp_path / "missing.csv")) == {}
