"""FastAPI routes for control panel."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from src import __version__
from src.control_panel.schemas import (
    ErrorResponse,
    HealthResponse,
    ServerConfig,
    ServerInfo,
    ServerStatus,
)
from src.proxy.minecraft import MinecraftClient, MinecraftError

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for servers (replace with database in production)
servers: dict[str, ServerConfig] = {}
minecraft_clients: dict[str, MinecraftClient] = {}


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version=__version__)


@router.post("/servers", response_model=ServerInfo, status_code=status.HTTP_201_CREATED)
async def create_server(config: ServerConfig) -> ServerInfo:
    """Create a new server configuration.

    Args:
        config: Server configuration

    Returns:
        Server info

    Raises:
        HTTPException: If server already exists or connection fails
    """
    if config.name in servers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Server '{config.name}' already exists",
        )

    try:
        # Create Minecraft client
        client = MinecraftClient(
            host=config.host, port=config.port, password=config.password
        )
        await client.connect()

        # Store configuration and client
        servers[config.name] = config
        minecraft_clients[config.name] = client

        logger.info(f"Server '{config.name}' created and connected")

        return ServerInfo(
            name=config.name,
            host=config.host,
            port=config.port,
            status=ServerStatus.ONLINE,
            description=config.description,
        )
    except MinecraftError as e:
        logger.error(f"Failed to connect to server: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to Minecraft server: {e}",
        )


@router.get("/servers", response_model=list[ServerInfo])
async def list_servers() -> list[ServerInfo]:
    """List all configured servers.

    Returns:
        List of server info
    """
    result = []
    for name, config in servers.items():
        status = ServerStatus.ONLINE
        players = 0

        try:
            client = minecraft_clients.get(name)
            if client:
                players_list = await client.get_players()
                players = len(players_list)
        except Exception:
            status = ServerStatus.ERROR

        result.append(
            ServerInfo(
                name=config.name,
                host=config.host,
                port=config.port,
                status=status,
                players_online=players,
                description=config.description,
            )
        )

    return result


@router.get("/servers/{server_name}", response_model=ServerInfo)
async def get_server(server_name: str) -> ServerInfo:
    """Get server information.

    Args:
        server_name: Server name

    Returns:
        Server info

    Raises:
        HTTPException: If server not found
    """
    if server_name not in servers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Server not found"
        )

    config = servers[server_name]
    status = ServerStatus.ONLINE
    players = 0

    try:
        client = minecraft_clients.get(server_name)
        if client:
            players_list = await client.get_players()
            players = len(players_list)
    except Exception:
        status = ServerStatus.ERROR

    return ServerInfo(
        name=config.name,
        host=config.host,
        port=config.port,
        status=status,
        players_online=players,
        description=config.description,
    )


@router.delete("/servers/{server_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(server_name: str) -> None:
    """Delete a server configuration.

    Args:
        server_name: Server name

    Raises:
        HTTPException: If server not found
    """
    if server_name not in servers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Server not found"
        )

    # Disconnect client
    client = minecraft_clients.get(server_name)
    if client:
        await client.disconnect()
        del minecraft_clients[server_name]

    del servers[server_name]
    logger.info(f"Server '{server_name}' deleted")


@router.post("/servers/{server_name}/command")
async def send_command(server_name: str, command: str) -> dict[str, str]:
    """Send a command to a Minecraft server.

    Args:
        server_name: Server name
        command: Command to send

    Returns:
        Command response

    Raises:
        HTTPException: If server not found or command fails
    """
    if server_name not in servers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Server not found"
        )

    try:
        client = minecraft_clients[server_name]
        response = await client.send_command(command)
        return {"response": response}
    except MinecraftError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Command failed: {e}",
        )
