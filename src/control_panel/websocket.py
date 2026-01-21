"""WebSocket handlers for real-time updates."""

import asyncio
import logging
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self) -> None:
        """Initialize connection manager."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection.

        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Disconnect a WebSocket.

        Args:
            websocket: WebSocket connection
        """
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, message: dict) -> None:
        """Broadcast a message to all connected clients.

        Args:
            message: Message to broadcast
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def send_personal(self, websocket: WebSocket, message: dict) -> None:
        """Send a message to a specific client.

        Args:
            websocket: Target WebSocket connection
            message: Message to send
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")


# Global connection manager
manager = ConnectionManager()


async def handle_server_status_updates(
    websocket: WebSocket, server_name: str, client
) -> None:
    """Handle real-time server status updates.

    Args:
        websocket: WebSocket connection
        server_name: Server to monitor
        client: Minecraft client instance
    """
    try:
        while True:
            try:
                players = await client.get_players()
                await manager.send_personal(
                    websocket,
                    {
                        "type": "server_status",
                        "server": server_name,
                        "players_online": len(players),
                        "status": "online",
                    },
                )
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.warning(f"Error getting server status: {e}")
                await manager.send_personal(
                    websocket,
                    {"type": "server_status", "server": server_name, "status": "error"},
                )
                await asyncio.sleep(10)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for server {server_name}")
