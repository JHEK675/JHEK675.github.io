"""Minecraft protocol integration using RCON."""

import asyncio
import logging
from typing import Optional

from mcrcon import MCRcon

logger = logging.getLogger(__name__)


class MinecraftError(Exception):
    """Base exception for Minecraft-related errors."""

    pass


class MinecraftClient:
    """Client for interacting with Minecraft servers via RCON."""

    def __init__(
        self, host: str, port: int = 25575, password: str = "", timeout: int = 10
    ) -> None:
        """Initialize Minecraft client.

        Args:
            host: Server hostname/IP
            port: RCON port (default: 25575)
            password: RCON password
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.rcon: Optional[MCRcon] = None

    async def connect(self) -> None:
        """Connect to Minecraft server via RCON."""
        try:
            loop = asyncio.get_event_loop()
            self.rcon = await loop.run_in_executor(
                None, MCRcon, self.host, self.port, self.password, self.timeout
            )
            logger.info(f"Connected to Minecraft server at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Minecraft server: {e}")
            raise MinecraftError(f"Connection failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Minecraft server."""
        if self.rcon:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.rcon.close)
                logger.info(f"Disconnected from Minecraft server at {self.host}")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")

    async def send_command(self, command: str) -> str:
        """Send a command to the Minecraft server.

        Args:
            command: The command to send

        Returns:
            Server response

        Raises:
            MinecraftError: If not connected or command fails
        """
        if not self.rcon:
            raise MinecraftError("Not connected to server")

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.rcon.command, command)
            logger.debug(f"Command executed: {command}")
            return response
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise MinecraftError(f"Command failed: {e}")

    async def get_players(self) -> list[str]:
        """Get list of online players.

        Returns:
            List of player names
        """
        try:
            response = await self.send_command("list")
            # Parse player list from response
            # Format: "There are X of max Y players online: player1, player2, ..."
            if "players online:" in response:
                players_part = response.split("players online:")[-1].strip()
                return [p.strip() for p in players_part.split(",") if p.strip()]
            return []
        except MinecraftError as e:
            logger.warning(f"Failed to get player list: {e}")
            return []

    async def say(self, message: str) -> str:
        """Broadcast a message to all players.

        Args:
            message: Message to broadcast

        Returns:
            Server response
        """
        return await self.send_command(f"say {message}")
