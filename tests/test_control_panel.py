"""Tests for the control panel API."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


@pytest.mark.unit
class TestControlPanelAPI:
    """Tests for control panel API."""

    def test_health_check(self) -> None:
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_list_servers_empty(self) -> None:
        """Test listing servers when none exist."""
        response = client.get("/api/servers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_nonexistent_server(self) -> None:
        """Test getting a server that doesn't exist."""
        response = client.get("/api/servers/nonexistent")
        assert response.status_code == 404

    def test_delete_nonexistent_server(self) -> None:
        """Test deleting a server that doesn't exist."""
        response = client.delete("/api/servers/nonexistent")
        assert response.status_code == 404

    @pytest.mark.integration
    def test_create_server(self) -> None:
        """Test creating a server configuration.

        Note: This test requires a running Minecraft server
        """
        server_config = {
            "name": "TestServer",
            "host": "localhost",
            "port": 25575,
            "password": "test",
            "description": "Test server",
        }

        response = client.post("/api/servers", json=server_config)

        # Expect either 201 (success) or 503 (server unavailable)
        assert response.status_code in [201, 503]

        if response.status_code == 201:
            data = response.json()
            assert data["name"] == "TestServer"
            assert data["host"] == "localhost"

    def test_send_command_nonexistent_server(self) -> None:
        """Test sending command to nonexistent server."""
        response = client.post("/api/servers/nonexistent/command", params={"command": "list"})
        assert response.status_code == 404
