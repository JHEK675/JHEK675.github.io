"""Proxy server implementation."""

import asyncio
import logging
from typing import Callable, Optional

from src.config import settings

logger = logging.getLogger(__name__)


class ProxyServer:
    """TCP proxy server for Minecraft connections."""

    def __init__(
        self,
        host: str = settings.proxy_host,
        port: int = settings.proxy_port,
        max_connections: int = settings.max_connections,
    ) -> None:
        """Initialize proxy server.

        Args:
            host: Host to bind to
            port: Port to bind to
            max_connections: Maximum concurrent connections
        """
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.server: Optional[asyncio.Server] = None
        self.active_connections = 0
        self.client_handler: Optional[Callable] = None

    def set_client_handler(self, handler: Callable) -> None:
        """Set the handler for client connections.

        Args:
            handler: Async function to handle client connections
        """
        self.client_handler = handler

    async def start(self) -> None:
        """Start the proxy server."""
        try:
            self.server = await asyncio.start_server(
                self._handle_connection, self.host, self.port
            )
            async with self.server:
                logger.info(f"Proxy server started on {self.host}:{self.port}")
                await self.server.serve_forever()
        except Exception as e:
            logger.error(f"Failed to start proxy server: {e}")
            raise

    async def _handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle individual client connections.

        Args:
            reader: Stream reader for client
            writer: Stream writer for client
        """
        if self.active_connections >= self.max_connections:
            logger.warning("Max connections reached, rejecting new connection")
            writer.close()
            await writer.wait_closed()
            return

        self.active_connections += 1
        peer_name = writer.get_extra_info("peername")
        logger.info(f"Client connected: {peer_name}")

        try:
            if self.client_handler:
                await self.client_handler(reader, writer)
        except Exception as e:
            logger.error(f"Error handling client {peer_name}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            self.active_connections -= 1
            logger.info(f"Client disconnected: {peer_name}")

    async def stop(self) -> None:
        """Stop the proxy server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Proxy server stopped")
