# OEDISI WLS Federate

Weighted Least Squares (WLS) state estimation for power distribution systems.

## Overview

The WLS federate implements state estimation for power systems using weighted least squares optimization. It estimates the system state (voltage magnitudes and angles) from noisy measurements with known accuracy (weights). This is essential for:
- System observability analysis
- Bad data detection
- Real-time system monitoring
- Control and optimization applications

## Architecture

- **StateEstimatorFederate**: Main federate class (state_estimator_federate.py)
- **WLS Algorithm**: Jacobian-based least squares optimization
- **FastAPI Server**: REST API wrapper (server.py)
- **Test Data**: Multiple test datasets for validation

## Key Features

- ✅ Weighted least squares state estimation
- ✅ Jacobian matrix computation
- ✅ scipy.optimize.least_squares solver
- ✅ Sparse matrix support for efficiency
- ✅ Multiple measurement types (voltage, power, current)
- ✅ Iterative solution with convergence checks
- ✅ HELICS co-simulation integration

## Dependencies

Core dependencies:
- `helics>=3.4.0` - HELICS co-simulation framework
- `scipy` - Scientific computing and optimization
- `numpy` - Numerical operations and linear algebra
- `pydantic` - Configuration validation
- `oedisi~=3.0` - OEDISI framework types
- `fastapi` - REST API framework
- `uvicorn` - ASGI server

See [pyproject.toml](pyproject.toml) for complete dependency list.

## Installation

### From the monorepo root:
```bash
pip install -e Components/wls_federate
```

### As a standalone package:
```bash
cd Components/wls_federate
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
wls-federate-server

# Or directly with Python
python server.py
```

The server runs on port 5683 (configurable via `PORT` environment variable).

### Python API

```python
# Import would be:
# from wls_federate import StateEstimatorFederate

# Create and run state estimator federate
# estimator = StateEstimatorFederate(broker_config)
# estimator.run()
```

### Configuration

The state estimator requires:
- **Network Model**: System topology and parameters
- **Measurements**: Voltage, power, current measurements with weights
- **Initial State**: Starting point for iterative solution
- **Convergence Settings**: Tolerance, max iterations

## Algorithm Details

### Weighted Least Squares Formulation

The WLS state estimation solves:

```
minimize: Σ w_i * (z_i - h_i(x))²
```

Where:
- `z_i` - Measured values
- `h_i(x)` - Measurement functions (nonlinear)
- `w_i` - Measurement weights (inverse of variance)
- `x` - State vector (voltage magnitudes and angles)

### Solution Method

1. **Linearization**: Compute Jacobian matrix H = ∂h/∂x
2. **Normal Equations**: H^T W H Δx = H^T W Δz
3. **Iterative Update**: x_{k+1} = x_k + Δx
4. **Convergence Check**: ||Δx|| < tolerance

### Measurement Types

Supported measurements:
- **Voltage magnitude**: |V_i|
- **Voltage angle**: ∠V_i
- **Real power injection**: P_i
- **Reactive power injection**: Q_i
- **Real power flow**: P_{ij}
- **Reactive power flow**: Q_{ij}

## Testing

Run tests from the component directory:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=wls_federate --cov-report=html
```

The test suite (test_state_estimator.py, 530 lines) includes:
- State estimation algorithm validation
- Multiple test systems (IEEE 123, small SMART-DS variants)
- Convergence tests
- Numerical accuracy checks

Test data directories:
- `tests/ieee123data/`
- `tests/small_smartds_*_v1.0.0/`
- `tests/make_test_data.py` - Test data generation utility

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
wls_federate/
├── __init__.py                # Package initialization
├── state_estimator_federate.py # Main WLS implementation (389 lines)
├── server.py                  # FastAPI REST server
├── component_definition.json
├── pyproject.toml
├── requirements.txt
├── pytest.ini
├── mypy.ini
├── .gitignore
└── tests/
    ├── __init__.py
    ├── test_state_estimator.py (530 lines)
    ├── make_test_data.py
    ├── ieee123data/
    └── small_smartds_*_v1.0.0/
```

## Performance Considerations

### Sparse Matrices

For large power systems, the Jacobian matrix H is sparse:
- Use `scipy.sparse` for efficient storage
- Sparse solvers reduce computational complexity
- Memory usage: O(n) instead of O(n²)

### Convergence

- **Initial Guess**: Flat start (V=1.0∠0°) usually sufficient
- **Iterations**: Typically 3-5 iterations for convergence
- **Bad Data**: Large residuals indicate measurement errors
- **Ill-conditioning**: May occur with poor measurement placement

## Use Cases

1. **State Estimation**: Estimate system state from measurements
2. **Observability Analysis**: Determine if system is observable
3. **Bad Data Detection**: Identify faulty sensors
4. **Sensor Placement**: Optimize sensor locations
5. **Real-time Monitoring**: Track system state during operation

## References

- Classical WLS state estimation for power systems
- Based on Gauss-Newton method
- Standard approach for transmission system state estimation
- Adapted for distribution systems

## Docker

Build the Docker image:
```bash
docker build -t oedisi-wls-federate .
```

Run the container:
```bash
docker run -p 5683:5683 -e PORT=5683 oedisi-wls-federate
```

## License

MIT License - see [LICENSE.md](../../LICENSE.md) for details.
