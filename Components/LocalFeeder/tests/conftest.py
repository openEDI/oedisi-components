"""Configure test environment for LocalFeeder tests."""

import os

import pytest

# Change to the LocalFeeder component directory so relative paths in test
# fixtures (e.g., "tests/test_data/master.dss", "gadal_ieee123/...") resolve correctly.
COMPONENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(autouse=True, scope="session")
def change_to_component_dir():
    """Set CWD to LocalFeeder component directory for the test session."""
    original_dir = os.getcwd()
    os.chdir(COMPONENT_DIR)
    yield
    os.chdir(original_dir)
