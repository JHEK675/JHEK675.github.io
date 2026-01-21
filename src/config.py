"""Configuration management for the application."""

import logging
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_env: str = "development"
    app_debug: bool = True
    app_port: int = 8000
    app_host: str = "0.0.0.0"

    # Proxy
    proxy_port: int = 25575
    proxy_host: str = "0.0.0.0"
    max_connections: int = 100

    # Minecraft
    minecraft_servers_config: str = "config/servers.json"

    # Logging
    log_level: str = "INFO"

    # RCON
    default_rcon_timeout: int = 10

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


# Global settings instance
settings = get_settings()
