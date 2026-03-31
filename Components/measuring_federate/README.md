# OEDISI Measuring Federate

Sensor and measurement simulation with configurable noise injection for power system state estimation studies.

## Overview

The measuring federate simulates sensor measurements in power distribution systems by adding realistic noise characteristics to perfect measurements. It provides:
- Additive noise injection (Gaussian)
- Multiplicative noise injection (percentage-based)
- Seeded random number generation for reproducibility
- Configurable noise parameters per measurement

This component is essential for testing state estimation algorithms and understanding the impact of measurement uncertainty on power system analysis.

## Architecture

- **MeasurementRelay**: Main federate class (measuring_federate.py)
- **MeasurementConfig**: Configuration model using Pydantic
- **FastAPI Server**: REST API wrapper (server.py)
- **Test Config Generator**: Utility for creating test configurations (generate_test_config.py)

## Key Features

- ✅ Additive Gaussian noise injection
- ✅ Multiplicative (percentage) noise
- ✅ Configurable noise standard deviations
- ✅ Seeded random generation for reproducibility
- ✅ Per-sensor configuration
- ✅ Real-time measurement relay
- ✅ HELICS co-simulation integration

## Dependencies

Core dependencies:
- `helics>=3.4.0` - HELICS co-simulation framework
- `numpy` - Numerical computing and random generation
- `pandas` - Data handling
- `pyarrow` - Efficient data serialization
- `pydantic` - Configuration validation
- `oedisi~=3.0` - OEDISI framework types
- `fastapi` - REST API framework
- `uvicorn` - ASGI server
- `requests` / `grequests` - HTTP client

See [pyproject.toml](pyproject.toml) for complete dependency list.

## Installation

### From the monorepo root:
```bash
pip install -e Components/measuring_federate
```

### As a standalone package:
```bash
cd Components/measuring_federate
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
measuring-federate-server

# Or directly with Python
python server.py
```

The server runs on port 5684 (configurable via `PORT` environment variable).

### Configuration

The `MeasurementConfig` model accepts:
- `name`: Sensor identifier
- `measurement_file`: Path to the measurement mapping JSON file
- `additive_noise_stddev`: Standard deviation for additive noise
- `multiplicative_noise_stddev`: Standard deviation for multiplicative noise (as fraction)
- `run_freq_time_step`: Frequency of simulation time steps (default: 1.0)

Example configuration:
```python
from measuring_federate import MeasurementConfig

config = MeasurementConfig(
    name="voltage_sensor_1",
    measurement_file="sensors.json",
    additive_noise_stddev=0.01,      # ±0.01 units
    multiplicative_noise_stddev=0.005, # ±0.5%
    run_freq_time_step=1.0
)
```

### Noise Model

For a true measurement value `x`, the noisy measurement `y` is computed as:

```
y = x + ε_additive + x * ε_multiplicative
```

Where:
- `ε_additive ~ N(0, σ_add²)` - Additive Gaussian noise
- `ε_multiplicative ~ N(0, σ_mult²)` - Multiplicative Gaussian noise

### Python API

```python
from measuring_federate import MeasurementRelay, MeasurementConfig

# Create configuration
config = MeasurementConfig(
    name="sensor",
    measurement_file="sensors.json",
    additive_noise_stddev=0.02,
    multiplicative_noise_stddev=0.01
)

# Create and run federate
relay = MeasurementRelay(broker_config)
relay.run()
```

## Testing

Run tests from the component directory:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=measuring_federate --cov-report=html
```

The test suite includes:
- Health check endpoint tests
- Configuration model validation
- Noise reproducibility tests (seeded random generation)

TODO: Add comprehensive tests for:
- Noise injection with various parameters
- Statistical properties of generated noise
- Integration with HELICS subscriptions
- Multiple sensor scenarios

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

### File Structure

```
## Docker

Build the Docker image:
```bash
docker build -t oedisi-measuring-federate .
```

Run the container:
```bash
docker run -p 5684:5684 -e PORT=5684 oedisi-measuring-federate
```

## License

BSD 3-Clause License - see [LICENSE.md](../../LICENSE.md) for details.
