"""
Tests for the health check endpoint.

Uses Flask's built-in test client — no need to start a real server.
"""

import pytest

from driverguard.app import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_health_returns_200(client):
    """Health endpoint should return HTTP 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_returns_json(client):
    """Health endpoint should return valid JSON."""
    response = client.get("/api/v1/health")
    data = response.get_json()
    assert data is not None


def test_health_has_required_fields(client):
    """Health endpoint JSON should contain all expected fields."""
    response = client.get("/api/v1/health")
    data = response.get_json()

    assert data["status"] == "healthy"
    assert data["service"] == "DriverGuard API"
    assert "version" in data
    assert "timestamp" in data
