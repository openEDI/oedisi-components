# oedisi-components
[![Main - Integration Tests](https://github.com/openEDI/oedisi-example/actions/workflows/test-api.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/test-api.yml)
[![Main - Unit Tests](https://github.com/openEDI/oedisi-example/actions/workflows/unit-test-components.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/unit-test-components.yml)
[![Main - Verify Components](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml)
[![Main - Verify Dockerfiles](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml)

This repository is an OEDISI co-simulation example composed of multiple
federated components (feeder simulation, state estimation, OPF, recorder,
and broker orchestration). It is also used as a CI-tested integration target
for component compatibility.

## Component Status

| Component | Version | Tests | Config files | Docker | Maintainer |
|-----------|---------|-------|--------------|--------|------------|
| **Broker** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-example/main/Components/broker/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Test - Broker](https://github.com/openEDI/oedisi-example/actions/workflows/test-broker.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/test-broker.yml) | [![Verify Components](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml) | Joseph.McKinsey@nlr.gov |
| **LinDistFlow** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-example/main/Components/lindistflow_federate/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Test - LinDistFlow](https://github.com/openEDI/oedisi-example/actions/workflows/test-lindistflow.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/test-lindistflow.yml) | [![Verify Components](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml) | Joseph.McKinsey@nlr.gov |
| **LocalFeeder** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-example/main/Components/LocalFeeder/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Test - LocalFeeder](https://github.com/openEDI/oedisi-example/actions/workflows/test-localfeeder.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/test-localfeeder.yml) | [![Verify Components](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml) | Joseph.McKinsey@nlr.gov |
| **Measuring** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-example/main/Components/measuring_federate/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Test - Measuring Federate](https://github.com/openEDI/oedisi-example/actions/workflows/test-measuring.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/test-measuring.yml) | [![Verify Components](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml) | Joseph.McKinsey@nlr.gov |
| **OMOO** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-example/main/Components/omoo_federate/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Test - OMOO Federate](https://github.com/openEDI/oedisi-example/actions/workflows/test-omoo.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/test-omoo.yml) | [![Verify Components](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml) | Joseph.McKinsey@nlr.gov |
| **Recorder** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-example/main/Components/recorder/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Test - Recorder](https://github.com/openEDI/oedisi-example/actions/workflows/test-recorder.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/test-recorder.yml) | [![Verify Components](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml) | Joseph.McKinsey@nlr.gov |
| **WLS** | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/oedisi-example/main/Components/wls_federate/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Test - WLS Federate](https://github.com/openEDI/oedisi-example/actions/workflows/test-wls.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/test-wls.yml) | [![Verify Components](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-components.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml/badge.svg)](https://github.com/openEDI/oedisi-example/actions/workflows/verify-dockerfiles.yml) | Joseph.McKinsey@nlr.gov |
| [**PNNL-DOPF-ADMM**](https://github.com/openEDI/pnnl-dopf-admm) | ![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/openEDI/pnnl-dopf-admm/main/pyproject.toml&query=$.project.version&label=version&color=blue) | [![Unit Tests](https://github.com/openEDI/pnnl-dopf-admm/actions/workflows/tests.yml/badge.svg)](https://github.com/openEDI/pnnl-dopf-admm/actions/workflows/tests.yml) | [![Verify Components](https://github.com/openEDI/pnnl-dopf-admm/actions/workflows/verify-components.yml/badge.svg)](https://github.com/openEDI/pnnl-dopf-admm/actions/workflows/verify-components.yml) | [![Verify Dockerfiles](https://github.com/openEDI/pnnl-dopf-admm/actions/workflows/verify-dockerfiles.yml/badge.svg)](https://github.com/openEDI/pnnl-dopf-admm/actions/workflows/verify-dockerfiles.yml) | tylor.slay@pnnl.gov |


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
- **[pnnl-dopf-admm](Components/pnnl-dopf-admm/README.md)** - Distributed OPF component (git submodule)

**Each component includes:**
- `pyproject.toml` for modern Python packaging (PEP 621)
- Comprehensive test suite with pytest
- Individual README documentation
- Standardized code quality tools (mypy, pytest, black, isort)
- Dockerfile for containerization
- GitHub Actions workflow for automated testing

### Continuous Integration

Current CI coverage includes:
- Component unit tests on Python 3.11 and 3.13
- Integration/API and DOPF workflows using current supported environments
- Lint and formatting checks via pre-commit
- Component metadata and Dockerfile verification workflows

Additionally:
- **Dockerfile Verification**: Ensures all components have valid Dockerfiles
- **Integration Tests**: End-to-end system testing

## Adding A Submodule Under Components

Some components can be managed in separate repositories and included here as
git submodules under `Components/`.

### Add The Submodule

```bash
git submodule add https://github.com/<org>/<repo> Components/<component-name>
git submodule update --init --recursive
git add .gitmodules Components/<component-name>
git commit -m "Add <component-name> as submodule"
```

Notes:
- Commit both `.gitmodules` and the gitlink entry at `Components/<component-name>`.
- The submodule should include its own `README.md` and `Dockerfile`.
- Include `component_definition.json`.

### Workflows Applied To Submodules

Submodules under `Components/` are validated by the same repository workflows
as in-repo components:

- `verify-components.yml` (via `reusable_verify_components.yml`)
   - Checks `README.md` for all `Components/*` directories.
   - Checks `component_definition.json` for all `Components/*` directories except `broker`.
- `verify-dockerfiles.yml` (via `reusable_verify_dockerfiles.yml`)
   - Checks `Dockerfile` for all `Components/*` directories.

These reusable workflows use `actions/checkout` with `submodules: recursive`,
so submodule contents are available during file existence checks.

### Workflow Scope Clarification

- Verification workflows in this repository validate submodule metadata files
   and Dockerfile presence.
- Unit or integration tests for submodule code are not automatically run here
   unless explicitly added to this repository's test workflows.
- If the submodule has its own CI (recommended), link its badges in the
   Component Status table.

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

The repository uses standardized code quality tools configured in [pyproject.toml](pyproject.toml):

```bash
# Format code
black Components/
isort Components/

# Type checking
mypy Components/

# Linting
flake8 Components/

# Check docstrings
pydocstyle Components/
```

Install pre-commit hooks:
```bash
pre-commit install
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

## Running Simulations

1. Build the simulation system:
```bash
oedisi build --system scenarios/docker_system.json
```

This initializes the system defined in `scenarios/test_system.json` in a `build` directory.

You can specify your own directory with `--build-dir` and your own system json
with `--system`.

2. Run `oedisi run`

3. Analyze the results using `python post_analysis.py`

This computes some percentage relative errors in magnitude (MAPE) and angle (MAE),
as well as plots in `errors.png`, `voltage_magnitudes_0.png`, `voltage_angles_0.png`, etc.

If you put your outputs in a separate directory, you can run `python post_analysis.py [output_directory]`.

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
