"""Tests for OMOO federate."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the OMOO FastAPI app."""
    from omoo_federate.server import app

    return TestClient(app)


class TestOMOOHealthCheck:
    """Test OMOO federate health check endpoint."""

    def test_root_endpoint_returns_health_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "hostname" in data
        assert "host_ip" in data


class TestOMOOConfiguration:
    """Test OMOO configuration endpoint."""

    def test_configure_endpoint_exists(self, client):
        response = client.post("/configure", json={})
        assert response.status_code in [200, 422]


class TestOMOOImports:
    """Test that OMOO classes can be imported."""

    def test_omoo_class_importable(self):
        from omoo_federate import OMOO, OMOOFederate, OMOOParameters

        assert OMOO is not None
        assert OMOOFederate is not None
        assert OMOOParameters is not None

    def test_default_parameters(self):
        from omoo_federate import OMOOParameters

        params = OMOOParameters()
        assert params.Vmax == 1.05
        assert params.Vmin == 0.95
        assert params.alpha == 0.5
