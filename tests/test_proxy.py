"""Tests for the proxy module."""

import pytest

from src.proxy.minecraft import MinecraftClient, MinecraftError


@pytest.mark.unit
class TestMinecraftClient:
    """Tests for MinecraftClient."""

    @pytest.fixture
    def client(self) -> MinecraftClient:
        """Create a test Minecraft client."""
        return MinecraftClient(
            host="localhost", port=25575, password="test", timeout=5
        )

    def test_client_initialization(self, client: MinecraftClient) -> None:
        """Test client initialization."""
        assert client.host == "localhost"
        assert client.port == 25575
        assert client.password == "test"
        assert client.timeout == 5

    @pytest.mark.asyncio
    async def test_client_not_connected(self, client: MinecraftClient) -> None:
        """Test that send_command raises error when not connected."""
        with pytest.raises(MinecraftError, match="Not connected"):
            await client.send_command("list")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_connect_to_server(self, client: MinecraftClient) -> None:
        """Test connecting to a real Minecraft server.

        Note: This test requires a running Minecraft server on localhost:25575
        """
        try:
            await client.connect()
            # Connection successful
            await client.disconnect()
        except MinecraftError:
            # Server not available, skip
            pytest.skip("Minecraft server not available")


@pytest.mark.unit
class TestProxyErrors:
    """Tests for proxy error handling."""

    def test_minecraft_error_message(self) -> None:
        """Test MinecraftError exception."""
        error = MinecraftError("Connection failed")
        assert str(error) == "Connection failed"
