"""Test fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient

from syntaxis.service.app import app


@pytest.fixture
def client():
    """Create a TestClient for integration tests."""
    return TestClient(app)
