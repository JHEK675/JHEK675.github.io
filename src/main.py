"""Main entry point for the application."""

import logging

from fastapi import FastAPI

from src.config import setup_logging, settings
from src.control_panel.api import router as control_panel_router

# Setup logging
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Minecraft Multi-Client Proxy Control Panel",
    description="Manage multiple Minecraft servers through a unified proxy",
    version="0.1.0",
)

# Include routers
app.include_router(control_panel_router, prefix="/api", tags=["control-panel"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event() -> None:
    """Run on application startup."""
    logger.info(
        f"Starting Minecraft Proxy Control Panel in {settings.app_env} mode"
    )
    logger.info(f"API listening on {settings.app_host}:{settings.app_port}")
    logger.info(f"Proxy listening on {settings.proxy_host}:{settings.proxy_port}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Run on application shutdown."""
    logger.info("Shutting down Minecraft Proxy Control Panel")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        log_level=settings.log_level.lower(),
    )
