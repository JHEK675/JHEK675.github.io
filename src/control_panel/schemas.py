"""Pydantic schemas for request/response validation."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ServerStatus(str, Enum):
    """Server status enum."""

    ONLINE = "online"
    OFFLINE = "offline"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"


class ServerConfig(BaseModel):
    """Minecraft server configuration."""

    name: str = Field(..., description="Server name")
    host: str = Field(..., description="Server hostname/IP")
    port: int = Field(25575, description="RCON port")
    password: str = Field(..., description="RCON password")
    description: Optional[str] = Field(None, description="Server description")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "name": "Main Server",
                "host": "mc.example.com",
                "port": 25575,
                "password": "secret",
                "description": "Production server",
            }
        }


class ServerInfo(BaseModel):
    """Server information response."""

    name: str
    host: str
    port: int
    status: ServerStatus
    players_online: int = 0
    max_players: int = 20
    description: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
