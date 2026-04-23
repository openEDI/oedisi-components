# oedisi-example

[![Main - Integration Tests](https://github.com/openEDI/oedisi-example/actions/workflows/test-api.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/test-api.yml)
[![Main - Docker Build Test](https://github.com/openEDI/oedisi-example/actions/workflows/docker-test.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/docker-test.yml)
[![Main - Unit Tests](https://github.com/openEDI/oedisi-example/actions/workflows/unit-test-federates.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/unit-test-federates.yml)

This example shows how to use the GADAL api to manage simulations. We also
use it as a testing ground for the testing the combination of feeders,
state estimation, and distributed OPF.

## Component Status

| Component | Version | Tests | Config files | Docker | Maintainer |
|-----------|---------|-------|--------------|--------|------------|
| **Broker** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-components/main/Components/broker/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-broker.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-broker.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-broker.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-broker.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-broker.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-broker.yml) | Joseph.McKinsey@nlr.gov |
| **LinDistFlow** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-components/main/Components/lindistflow_federate/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-lindistflow_federate.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-lindistflow_federate.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-lindistflow_federate.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-lindistflow_federate.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-lindistflow_federate.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-lindistflow_federate.yml) | Joseph.McKinsey@nlr.gov |
| **LocalFeeder** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-components/main/Components/LocalFeeder/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-localfeeder.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-localfeeder.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-localfeeder.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-localfeeder.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-localfeeder.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-localfeeder.yml) | Joseph.McKinsey@nlr.gov |
| **Measuring** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-components/main/Components/measuring_federate/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-measuring_federate.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-measuring_federate.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-measuring_federate.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-measuring_federate.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-measuring_federate.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-measuring_federate.yml) | Joseph.McKinsey@nlr.gov |
| **OMOO** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-components/main/Components/omoo_federate/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-omoo_federate.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-omoo_federate.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-omoo_federate.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-omoo_federate.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-omoo_federate.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-omoo_federate.yml) | Joseph.McKinsey@nlr.gov |
| **Recorder** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-components/main/Components/recorder/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-recorder.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-recorder.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-recorder.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-recorder.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-recorder.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-recorder.yml) | Joseph.McKinsey@nlr.gov |
| **WLS** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-components/main/Components/wls_federate/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-wls_federate.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-wls_federate.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-wls_federate.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-wls_federate.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-wls_federate.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-wls_federate.yml) | Joseph.McKinsey@nlr.gov |
| [**PNNL-DOPF-ADMM**](https://github.com/openEDI/pnnl-dopf-admm) | [![Release](https://img.shields.io/github/v/release/openEDI/pnnl-dopf-admm?sort=semver&display_name=tag)](https://github.com/openEDI/pnnl-dopf-admm/releases/latest) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-pnnl-dopf-admm.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-pnnl-dopf-admm.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-pnnl-dopf-admm.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-pnnl-dopf-admm.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-pnnl-dopf-admm.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-pnnl-dopf-admm.yml) | tylor.slay@pnnl.gov |
| [**PNNL-Hub-Voltage**](https://github.com/openEDI/pnnl-hub-voltage) | [![Release](https://img.shields.io/github/v/release/openEDI/pnnl-hub-voltage?sort=semver&display_name=tag)](https://github.com/openEDI/pnnl-hub-voltage/releases/latest) | - | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-pnnl-hub-voltage.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-pnnl-hub-voltage.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-pnnl-hub-voltage.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-pnnl-hub-voltage.yml) | tylor.slay@pnnl.gov |
| [**PNNL-Hub-Control**](https://github.com/openEDI/pnnl-hub-control) | [![Release](https://img.shields.io/github/v/release/openEDI/pnnl-hub-control?sort=semver&display_name=tag)](https://github.com/openEDI/pnnl-hub-control/releases/latest) | - | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-pnnl-hub-control.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-pnnl-hub-control.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-pnnl-hub-control.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-pnnl-hub-control.yml) | tylor.slay@pnnl.gov |
| [**PNNL-Hub-Power**](https://github.com/openEDI/pnnl-hub-power) | [![Release](https://img.shields.io/github/v/release/openEDI/pnnl-hub-power?sort=semver&display_name=tag)](https://github.com/openEDI/pnnl-hub-power/releases/latest) | - | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-pnnl-hub-power.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-pnnl-hub-power.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-pnnl-hub-power.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-pnnl-hub-power.yml) | tylor.slay@pnnl.gov |
| [**PNNL-DSSE-EKF**](https://github.com/openEDI/pnnl-dsse-ekf) | [![Release](https://img.shields.io/github/v/release/openEDI/pnnl-dsse-ekf?sort=semver&display_name=tag)](https://github.com/openEDI/pnnl-dsse-ekf/releases/latest) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-pnnl-dsse-ekf.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-pnnl-dsse-ekf.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-pnnl-dsse-ekf.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-pnnl-dsse-ekf.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-pnnl-dsse-ekf.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-pnnl-dsse-ekf.yml) | tylor.slay@pnnl.gov |
| [**PNNL-Imputation-FFNN**](https://github.com/openEDI/pnnl-imputation-ffnn) | [![Release](https://img.shields.io/github/v/release/openEDI/pnnl-imputation-ffnn?sort=semver&display_name=tag)](https://github.com/openEDI/pnnl-imputation-ffnn/releases/latest) | - | - | - | tylor.slay@pnnl.gov |
| [**PNNL-Profiler-SDV**](https://github.com/openEDI/pnnl-profiler-sdv) | [![Release](https://img.shields.io/github/v/release/openEDI/pnnl-profiler-sdv?sort=semver&display_name=tag)](https://github.com/openEDI/pnnl-profiler-sdv/releases/latest) | - | - | - | tylor.slay@pnnl.gov |
| [**NLP-DOPF**](https://github.com/openEDI/nlpdopf) | [![Release](https://img.shields.io/github/v/release/openEDI/nlpdopf?sort=semver&display_name=tag)](https://github.com/openEDI/nlpdopf/releases/latest) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-nlpdopf.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-nlpdopf.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-nlpdopf.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-nlpdopf.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-nlpdopf.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-nlpdopf.yml) | - |
| [**NLP-DSSE**](https://github.com/openEDI/nlpdsse) | [![Release](https://img.shields.io/github/v/release/openEDI/nlpdsse?sort=semver&display_name=tag)](https://github.com/openEDI/nlpdsse/releases/latest) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-nlpdsse.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-nlpdsse.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-nlpdsse.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-nlpdsse.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-nlpdsse.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-nlpdsse.yml) | - |


## Repository Structure

This repository is organized as a Python repository containing  components for power system co-simulation. See the **Component Status** table above for test and Docker build status for each component.

**Components:**
- **[broker](Components/broker/README.md)** - Central orchestration service for HELICS federates
- **[lindistflow_federate](Components/lindistflow_federate/README.md)** - Optimal power flow using linear distflow
- **[localfeeder](Components/LocalFeeder/README.md)** - OpenDSS-based distribution feeder simulator
- **[measuring_federate](Components/measuring_federate/README.md)** - Sensor simulation with noise injection
- **[omoo_federate](Components/omoo_federate/README.md)** - Online model-based optimal operation
- **[recorder](Components/recorder/README.md)** - Data recording for co-simulation outputs
- **[wls_federate](Components/wls_federate/README.md)** - Weighted least squares state estimation
- **[pnnl-dopf-admm](Components/pnnl-dopf-admm/README.md)** - Distributed OPF using ADMM
- **[pnnl-hub-voltage](Components/pnnl-hub-voltage/README.md)** - Voltage aggregation and distribution hub
- **[pnnl-hub-control](Components/pnnl-hub-control/README.md)** - Control aggregation and distribution hub
- **[pnnl-hub-power](Components/pnnl-hub-power/README.md)** - Power aggregation and distribution hub
- **[pnnl-dsse-ekf](Components/pnnl-dsse-ekf/README.md)** - Extended Kalman Filter state estimation
- **[pnnl-imputation-ffnn](Components/pnnl-imputation-ffnn/README.md)** - Feed-forward neural network for data imputation
- **[pnnl-profiler-sdv](Components/pnnl-profiler-sdv/README.md)** - Synthetic data generation via profiling
- **[nlpdopf](Components/nlpdopf/README.md)** - NLP-based distributed optimal power flow
- **[nlpdsse](Components/nlpdsse/README.md)** - NLP-based distribution system state estimation

**Each component includes:**
- `pyproject.toml` for modern Python packaging (PEP 621)
- Comprehensive test suite with pytest
- Individual README documentation
- Standardized code quality tools (mypy, pytest, black, isort)
- Dockerfile for containerization
- GitHub Actions workflow for automated testing

### Continuous Integration

Each component has its own GitHub Actions workflow that:
- Runs tests on Python 3.10 and 3.11
- Performs type checking with mypy
- Generates code coverage reports
- Triggers on changes to component code

Additionally:
- **Dockerfile Verification**: Ensures all components have valid Dockerfiles
- **Integration Tests**: End-to-end system testing
- **Docker Build Tests**: Validates container builds

### Quick Start - Development Installation

Install all components in editable mode from the repository root:

```bash
# Install all components for development
pip install -e Components/broker -e Components/lindistflow_federate -e Components/LocalFeeder \
            -e Components/measuring_federate -e Components/omoo_federate \
            -e Components/recorder -e Components/wls_federate

# Or install with dev dependencies
pip install -e "Components/broker[dev]" -e "Components/lindistflow_federate[dev]" \
            -e "Components/LocalFeeder[dev]" -e "Components/measuring_federate[dev]" \
            -e "Components/omoo_federate[dev]" -e "Components/recorder[dev]" \
            -e "Components/wls_federate[dev]"
```

### Running Tests

Run all tests from the repository root:
```bash
pytest Components/
```

Run tests for a specific component:
```bash
pytest Components/broker/tests/
pytest Components/wls_federate/tests/
```

Run with coverage:
```bash
pytest --cov=Components --cov-report=html Components/
```

### Code Quality

The repository enforces code quality standards through automated linting and formatting via GitHub Actions and pre-commit hooks.

**GitHub Actions Lint Workflow** (`.github/workflows/lint-format.yml`):
- Runs on every push and can be triggered manually
- Uses Python 3.13 to ensure compatibility with latest standards
- Executes all pre-commit hooks to validate code quality

**Pre-commit Hooks** (`.pre-commit-config.yaml`):
- **Standard hooks**: Trailing whitespace removal, EOF fixing, YAML validation, large file detection
- **Ruff**: Modern Python linter and formatter (replaces flake8, black, isort)
  - `ruff check --fix`: Automatic fixing of linting issues
  - `ruff format`: Code formatting for consistency

To set up pre-commit hooks locally:
```bash
pip install pre-commit
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

# Install and Running Locally

## Installation

1. Install component dependencies. You can either:

   **Option A: Install all components in editable mode** (recommended for developers)
   ```bash
   pip install -e Components/broker \
               -e Components/LocalFeeder \
               -e Components/measuring_federate \
               -e Components/recorder \
               -e Components/wls_federate
   ```

3. **Verify Installation**
 development tools (optional):
   ```bash
   pip install pytest mypy black isort flake8 pydocstyle pre-commit
   ```

## Troubleshooting

If the simulation fails, you may **need** to kill the `helics_broker` manually before you can start a new simulation.

When debugging, you should check the `.log` files for errors. Error code `-9` usually occurs
when it is killed by the broker as opposed to failing directly.

You can use the `oedisi` CLI tools to help debug specific components or timing.

- `oedisi run-with-pause`
- `oedisi debug-component --foreground feeder`

# Components

All the required components are defined in folders within this repo. Each component
pulls types from `oedisi.types.data_types`.

![Block diagram of simulation](sgidal-example.png)

## Component Overview

Each component is a standalone Python package with its own documentation. Click the component name for detailed information:

### **[Broker](Components/broker/README.md)**
Central orchestration service for HELICS federates. Provides REST API endpoints for federate coordination and HELICS broker management.

### **[LinDistFlow Federate](Components/lindistflow_federate/README.md)**
Optimal power flow using linear distflow formulation. Implements convex optimization (cvxpy) for three-phase distribution system control.

### **[LocalFeeder](Components/LocalFeeder/README.md)** (AWSFeeder)
OpenDSS-based distribution feeder simulator. Loads SMART-DS feeders and outputs:
- Topology: Y-matrix, slack bus, initial phases
- Powers and voltages for all nodes
- Real-time power flow simulation

### **[Measuring Federate](Components/measuring_federate/README.md)**
Sensor simulation with noise injection. Takes MeasurementArray inputs and outputs subsets at specified nodes with:
- Additive Gaussian noise
- Multiplicative (percentage) noise
- Configurable per-sensor parameters

This federate is instantiated as multiple sensors for each type of measurement.

### **[OMOO Federate](Components/omoo_federate/README.md)**
Online Model-based Optimal Operation for distribution systems with high PV penetration. Uses primal-dual optimization with linearized power flow sensitivity matrices for:
- Voltage regulation via PV curtailment and reactive power control
- Real-time optimal setpoint computation
- Constraint enforcement (voltage limits)

### **[WLS Federate](Components/wls_federate/README.md)**
Weighted Least Squares state estimation. Reads topology from the feeder simulation and measurements from the measuring federates, then outputs estimated voltages and power with angles.

### **[Recorder](Components/recorder/README.md)**
Data recording federate. Connects to HELICS subscriptions and saves data to:
- `.feather` files (PyArrow columnar format - efficient)
- `.csv` files (human-readable format)

This component is instantiated multiple times in the simulation for every subscription of interest.
This is similar to the HELICS observer functionality, but with more specific data types.

## Component Package Structure

Each component follows a standardized src-layout structure:
```
Components/{component}/
├── src/
│   └── {package_name}/
│       ├── __init__.py          # Package initialization with version
│       ├── server.py            # FastAPI REST server with main() entry point
│       └── {main_module}.py     # Core federate implementation
├── tests/                       # Test suite (outside src for isolation)
│   ├── __init__.py
│   └── test_*.py
├── pyproject.toml               # Modern Python packaging (PEP 621)
├── README.md                    # Comprehensive component documentation
├── pytest.ini                   # Test configuration
├── mypy.ini                     # Type checking configuration
├── .gitignore                   # Python gitignore patterns
├── Dockerfile                   # Container image definition
└── component_definition.json    # OEDISI component spec (inputs/outputs)
```

**Benefits of src-layout:**
- Clear separation between source code and tests
- Prevents accidental imports from development directory
- Ensures tests run against installed package
- Standard practice for modern Python packages

## Component Definitions

Components use `component_definition.json` files in each directory to define their dynamic inputs and outputs. This allows the OEDISI framework to:
- Configure connections between federates
- Validate wiring diagrams
- Generate appropriate subscriptions/publications
- Build simulation systems declaratively
