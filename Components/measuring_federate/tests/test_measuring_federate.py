"""Tests for measuring federate sensor/measurement simulation."""

import numpy as np
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the measuring federate FastAPI app."""
    from measuring_federate.server import app

    return TestClient(app)


class TestMeasuringFederateHealthCheck:
    """Test measuring federate health check endpoint."""

    def test_root_endpoint_returns_health_info(self, client):
        """Test that the root endpoint returns hostname and IP information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "hostname" in data
        assert "host_ip" in data


class TestMeasurementConfiguration:
    """Test measurement configuration."""

    def test_measurement_config_creation(self):
        """Test MeasurementConfig model can be created."""
        from measuring_federate import MeasurementConfig

        # Test basic configuration
        config = MeasurementConfig(
            name="test_sensor",
            measurement_file="sensors.json",
            additive_noise_stddev=0.01,
            multiplicative_noise_stddev=0.005,
        )

        assert config.name == "test_sensor"
        assert config.measurement_file == "sensors.json"
        assert config.additive_noise_stddev == 0.01
        assert config.multiplicative_noise_stddev == 0.005


class TestNoiseInjection:
    """Test noise injection functionality."""

    def test_measurement_relay_initialization(self):
        """Test MeasurementRelay can be imported and has expected structure."""
        from measuring_federate import MeasurementRelay

        assert MeasurementRelay is not None
        assert hasattr(MeasurementRelay, "__init__")

    @pytest.mark.parametrize("seed", [42, 123, 999])
    def test_seeded_noise_reproducibility(self, seed):
        """Test that noise generation is reproducible with same seed."""
        np.random.seed(seed)
        noise1 = np.random.normal(0, 0.01, 100)

        np.random.seed(seed)
        noise2 = np.random.normal(0, 0.01, 100)

        np.testing.assert_array_equal(noise1, noise2)


# TODO: Add comprehensive tests for:
# - Additive noise injection with various parameters
# - Multiplicative noise injection
# - Noise injection with various parameters
# - Statistical properties of generated noise
# - Integration with HELICS subscriptions
# - Measurement types
