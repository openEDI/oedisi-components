"""Tests for recorder data logging functionality."""

import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the recorder FastAPI app."""
    from recorder.server import app
    return TestClient(app)


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestRecorderHealthCheck:
    """Test recorder health check endpoint."""

    def test_root_endpoint_returns_health_info(self, client):
        """Test that the root endpoint returns hostname and IP information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "hostname" in data
        assert "host_ip" in data


class TestRecorderInitialization:
    """Test recorder initialization."""

    def test_recorder_can_be_imported(self):
        """Test that Recorder class can be imported."""
        from recorder import Recorder
        
        assert Recorder is not None
        assert hasattr(Recorder, '__init__')


class TestRecorderDataOutput:
    """Test recorder data output functionality."""

    def test_feather_format_support(self):
        """Test that PyArrow is available for feather format."""
        import pyarrow
        import pyarrow.feather
        
        # Basic test that pyarrow is importable
        assert pyarrow is not None
        assert pyarrow.feather is not None

    def test_csv_format_support(self):
        """Test that pandas CSV writing is available."""
        import pandas as pd
        
        # Create a simple test dataframe
        df = pd.DataFrame({'time': [0.0, 1.0, 2.0], 'value': [1.0, 2.0, 3.0]})
        assert df is not None
        
    def test_output_directory_creation(self, temp_output_dir):
        """Test that output directories can be created."""
        test_dir = temp_output_dir / "test_output"
        test_dir.mkdir(exist_ok=True)
        
        assert test_dir.exists()
        assert test_dir.is_dir()


# TODO: Add comprehensive tests for:
# - Recording subscription data from HELICS
# - Writing data to feather format
# - Writing data to CSV format
# - Time-series data aggregation
# - Handling multiple subscriptions
# - Performance with large datasets
# - File naming and organization
