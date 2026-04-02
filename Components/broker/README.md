# OEDISI Broker

Central orchestration service for HELICS co-simulation federates in the OEDISI framework.

## Overview

The broker component provides a FastAPI-based REST API for coordinating HELICS federates in a distributed co-simulation environment. It manages:
- HELICS broker initialization and lifecycle
- Federate registration and coordination
- System-wide wiring diagrams
- Configuration management across federates

## Architecture

The broker serves as the central coordinator in OEDISI co-simulation scenarios:
- **FastAPI Server**: REST API endpoints for federate management
- **HELICS Broker**: Core co-simulation broker functionality
- **Configuration Manager**: Handles system wiring and federate configurations

## Key Features

- ✅ RESTful API for federate orchestration
- ✅ HELICS broker management
- ✅ Health check endpoints
- ✅ Background task execution for federate coordination
- ✅ Multi-federate scenario support

## Dependencies

Core dependencies:
- `helics>=3.4.0` - HELICS co-simulation framework
- `fastapi` - Modern web framework for APIs
- `uvicorn` - ASGI server
- `oedisi~=3.0` - OEDISI framework types
- `pyyaml` - YAML configuration parsing
- `grequests` - Asynchronous HTTP requests
- `python-multipart` - Multipart form data support

See [pyproject.toml](pyproject.toml) for complete dependency list.

## Installation

### From the monorepo root:
```bash
pip install -e Components/broker
```

### As a standalone package:
```bash
cd Components/broker
pip install -e .
```

### With development dependencies:
```bash
pip install -e ".[dev]"
```

## Usage

### Running the Server

```python
# Using the entry point
broker-server

# Or directly with Python
python server.py
```

The server runs on port specified by the `PORT` environment variable (default: 8766).

### API Endpoints

#### Health Check
```bash
GET /
```
Returns hostname and IP information.

#### Configure Federate
```bash
POST /configure
```
Upload and configure federate settings.

#### Run Simulation
```bash
POST /run
```
Start a co-simulation with specified broker configuration.

### Environment Variables

- `PORT`: Port number for the FastAPI server (default: 8766)

## Configuration

The broker accepts `BrokerConfig` for simulation runs, which includes:
- Broker endpoint information
- Federation configuration
- Logging settings

## Testing

Run tests from the component directory:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=broker --cov-report=html
```

The test suite includes:
- Health check endpoint tests
- Configuration endpoint tests
- API validation tests

## Development

### Code Quality

Format code:
```bash
black .
isort .
```

Type checking:
```bash
mypy .
```

Linting:
```bash
flake8 .
```

### File Structure

```
broker/
├── src/
│   └── broker/
│       ├── __init__.py     # Package initialization
│       └── server.py       # Main FastAPI application (279 lines)
## Docker

Build the Docker image:
```bash
docker build -t oedisi-broker .
```

Run the container:
```bash
docker run -p 8766:8766 -e PORT=8766 oedisi-broker
```

## License

BSD 3-Clause License - see [LICENSE.md](../../LICENSE.md) for details.
