"""Tests for LinDistFlow optimal power flow federate."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the lindistflow FastAPI app."""
    from lindistflow_federate.server import app

    return TestClient(app)


class TestLinDistFlowHealthCheck:
    """Test lindistflow federate health check endpoint."""

    def test_root_endpoint_returns_health_info(self, client):
        """Test that the root endpoint returns hostname and IP information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "hostname" in data
        assert "host_ip" in data


class TestLinDistFlowConfiguration:
    """Test lindistflow configuration."""

    def test_configure_endpoint_exists(self, client):
        """Test that the configure endpoint exists."""
        response = client.post("/configure", json={})
        assert response.status_code in [200, 422]


class TestLinDistFlowOptimization:
    """Test optimal power flow algorithms."""

    def test_echo_federate_initialization(self):
        """Test EchoFederate can be imported and basic structure exists."""
        from lindistflow_federate import EchoFederate

        # Basic import test
        assert EchoFederate is not None
        assert hasattr(EchoFederate, "__init__")
