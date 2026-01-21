# Copilot Instructions for JHEK675.github.io

## Project Overview
**Multi-Client Proxy / Minecraft Control Panel** for managing server configurations and workflows. This project coordinates multiple client connections to Minecraft servers through a centralized proxy and control interface, enabling server administrators to manage deployments, configurations, and operations from a single point.

## Recommended Tech Stack
- **Framework**: FastAPI (async/await for real-time proxy connections, WebSocket support for control panel)
- **Minecraft Integration**: `mcstatus` (server pinging), `mcrcon` (remote console via RCON protocol)
- **Async**: `asyncio` with `aiofiles` for file operations
- **Real-time Communication**: WebSockets for control panel live updates
- **Testing**: pytest with `pytest-asyncio` for async tests
- **Type Checking**: mypy with `--strict` mode
- **Code Quality**: Ruff (linting and formatting)
- **Config Management**: `python-dotenv` for `.env` files
- **Data Serialization**: Pydantic for request/response validation

**Why this stack**: FastAPI is ideal for a proxy application needing async concurrency. Pydantic enforces data safety. mcstatus/mcrcon are battle-tested Minecraft libraries. This combination is beginner-friendly but production-ready.

## Recommended Project Structure
```
src/
├── proxy/
│   ├── __init__.py
│   ├── server.py          # Main proxy server logic
│   ├── connection.py      # Client connection handling
│   └── minecraft.py       # Minecraft protocol interaction
├── control_panel/
│   ├── __init__.py
│   ├── api.py             # FastAPI routes
│   ├── websocket.py       # WebSocket handlers
│   └── schemas.py         # Pydantic models
├── config.py              # Configuration and env parsing
└── main.py                # Entry point
tests/
├── __init__.py
├── test_proxy.py
└── test_control_panel.py
requirements.txt
.env.example
Makefile
docker-compose.yml
```

## Key Conventions & Patterns
- **Async-First**: All I/O operations (network, file, Minecraft RCON) use async functions
- **Error Handling**: Use custom exception classes (`ProxyError`, `MinecraftError`, `ConfigError`) for clear error propagation
- **Pydantic Models**: Define all API request/response schemas in `schemas.py`; reuse for validation
- **RCON Communication**: Wrap mcstatus/mcrcon in proxy layer to abstract Minecraft protocol details from control panel
- **Environment Variables**: Load via `.env` file; document all required vars in `.env.example`

## Development Workflows

### Initial Setup
```bash
# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy example config
cp .env.example .env
```

### Running Locally
```bash
# Development server with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# With Docker (testing against real Minecraft servers)
docker-compose up
```

### Testing & Code Quality
```bash
# Run all tests with coverage
pytest --cov=src/ tests/

# Type checking
mypy src/

# Format and lint
ruff check --fix src/
ruff format src/

# Pre-commit hook (runs all above before commits)
pre-commit install
```

### Makefile Targets (Recommended)
Create a `Makefile` with:
- `make dev` - Run local development server
- `make test` - Run tests and type checks
- `make lint` - Format and lint code
- `make docker-up` - Start with Docker Compose
- `make docker-test` - Run tests in Docker

## Critical Patterns

### Proxy Connection Pattern
```python
# src/proxy/connection.py - Handle each client connection
async def handle_client(reader, writer):
    try:
        # Read client request
        request = await reader.read(1024)
        # Forward to Minecraft server via RCON
        response = await minecraft.send_command(request)
        # Write response back to client
        writer.write(response)
    except MinecraftError as e:
        logger.error(f"Minecraft error: {e}")
        # Send error response to client
```

### Control Panel API Pattern
```python
# src/control_panel/api.py - FastAPI routes
from fastapi import FastAPI, WebSocket
from .schemas import ServerConfig

app = FastAPI()

@app.post("/servers")
async def create_server(config: ServerConfig):
    # Validate via Pydantic, forward to proxy
    return await proxy.add_server(config)

@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    # Real-time server status updates
    await websocket.accept()
    while True:
        status = await proxy.get_status()
        await websocket.send_json(status)
```

## Integration Points
- **Proxy ↔ Minecraft**: RCON protocol (port 25575 default) for server commands
- **Control Panel ↔ Proxy**: In-process or socket communication (recommend in-process for v1)
- **Client ↔ Control Panel**: REST API + WebSockets for real-time updates
- **Configuration**: Stored as JSON files in `config/` directory, loaded on startup

## Next Steps
1. Initialize `src/`, `tests/`, create `requirements.txt` with base dependencies
2. Implement `proxy/server.py` with connection listener and RCON wrapper
3. Build `control_panel/api.py` with FastAPI app and basic endpoints
4. Add pytest tests for both proxy and API layers
5. Set up pre-commit hooks and CI/CD (GitHub Actions)
