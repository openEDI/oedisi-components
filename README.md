# OEDISI-Components

[![Publish on Version Matrix](https://github.com/openEDI/oedisi-components/actions/workflows/publish-on-version-matrix.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/publish-on-version-matrix.yml)


[![Update Components Submodules](https://github.com/openEDI/oedisi-components/actions/workflows/update-components-submodules.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/update-components-submodules.yml)

[![Update Version Matrix](https://github.com/openEDI/oedisi-components/actions/workflows/update-version-matrix.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/update-version-matrix.yml)


[![Lint and Format](https://github.com/openEDI/oedisi-components/actions/workflows/lint-format.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/lint-format.yml)



## Key Workflows

**Repository-wide automation:**
- **[lint-format.yml](.github/workflows/lint-format.yml)** - Code quality enforcement using pre-commit hooks (ruff, trailing whitespace, YAML validation). Runs on every push.
- **[publish-on-version-matrix.yml](.github/workflows/publish-on-version-matrix.yml)** - Builds and publishes Docker images when `version_matrix.csv` changes. Triggered on main branch push or manual workflow dispatch.
- **[update-components-submodules.yml](.github/workflows/update-components-submodules.yml)** - Automatically updates all component submodules under `Components/`. Scheduled weekly (Monday 8 AM UTC) or triggered manually.
- **[update-version-matrix.yml](.github/workflows/update-version-matrix.yml)** - Updates `version_matrix.csv` from working tree and submodule release tags. Creates a pull request with changes. Triggered on release published events or manual workflow dispatch.

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
| [**ORNL-EV-PSO**](https://github.com/openEDI/ornl-ev-pso) | [![Release](https://img.shields.io/github/v/release/openEDI/ornl-ev-pso?sort=semver&display_name=tag)](https://github.com/openEDI/ornl-ev-pso/releases/latest) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-ornl-ev-pso.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-ornl-ev-pso.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-ornl-ev-pso.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-ornl-ev-pso.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-ornl-ev-pso.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-ornl-ev-pso.yml) | liub@ornl.gov |
| [**ORNL-DOPF-PSO**](https://github.com/openEDI/ornl-dopf-pso) | [![Release](https://img.shields.io/github/v/release/openEDI/ornl-dopf-pso?sort=semver&display_name=tag)](https://github.com/openEDI/ornl-dopf-pso/releases/latest) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-ornl-dopf-pso.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-ornl-dopf-pso.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-ornl-dopf-pso.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-ornl-dopf-pso.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-ornl-dopf-pso.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-ornl-dopf-pso.yml) | liub@ornl.gov |
| [**ORNL-DSSE-GNWLS**](https://github.com/openEDI/ornl-dsse-gnwls) | [![Release](https://img.shields.io/github/v/release/openEDI/ornl-dsse-gnwls?sort=semver&display_name=tag)](https://github.com/openEDI/ornl-dsse-gnwls/releases/latest) | [![Unit Tests](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-ornl-dsse-gnwls.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/unit-test-ornl-dsse-gnwls.yml) | [![Verify Components](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-ornl-dsse-gnwls.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-components-ornl-dsse-gnwls.yml) | [![Verify Dockerfiles](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-ornl-dsse-gnwls.yml/badge.svg)](https://github.com/openEDI/oedisi-components/actions/workflows/verify-dockerfiles-ornl-dsse-gnwls.yml) | liub@ornl.gov |


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
- **[ornl-ev-pso](Components/ornl-ev-pso/README.md)** - PSO-based EV charging optimization
- **[ornl-dopf-pso](Components/ornl-dopf-pso/README.md)** - PSO-based distributed optimal power flow
- **[ornl-dsse-gnwls](Components/ornl-dsse-gnwls/README.md)** - Gauss-Newton WLS state estimation

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
   pip install pytest mypy ruff pre-commit
   ```
