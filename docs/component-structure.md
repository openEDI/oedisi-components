# Component Structure Guide

This document describes the required structure and conventions for building a component (federate) in the OEDISI framework.

---

## Directory Layout

Every component lives under `Components/<component_name>/` or in a seperate repository with the OEDI organisation and follows this structure:

```
<component_name>/
├── component_definition.json       # Interface contract (ports, inputs, outputs)
├── Dockerfile                      # Container image build
├── mypy.ini                        # Type-checking configuration
├── pyproject.toml                  # Package metadata and dependencies
├── pytest.ini                      # Test runner configuration
├── README.md                       # Component documentation
├── src/
│   └── <package_name>/             # Installable Python package (src-layout)
│       ├── __init__.py             # Version and docstring
│       ├── server.py               # FastAPI entry point
│       └── <federate_logic>.py     # HELICS federate simulation logic
└── tests/
    └── test_*.py                   # Unit and integration tests
```

---

## Key Files

### `component_definition.json`

This file declares the federate's I/O contract — what data it consumes and produces.

| Field              | Type            | Description                                                                                     |
| ------------------ | --------------- | ----------------------------------------------------------------------------------------------- |
| `directory`        | `string`        | The component's folder name (e.g. `"wls_federate"`)                                            |
| `execute_function` | `string`        | Legacy CLI command (e.g. `"python state_estimator_federate.py"`)                                |
| `static_inputs`    | `array`         | Configuration parameters set once before simulation (e.g. `name`, `feeder_file`)                |
| `dynamic_inputs`   | `array`         | HELICS subscriptions — data received each timestep, typed with OEDISI data types                |
| `dynamic_outputs`  | `array`         | HELICS publications — data sent each timestep, typed with OEDISI data types                     |

Each entry in `static_inputs`, `dynamic_inputs`, and `dynamic_outputs` has the shape:

```json
{
  "type": "<OedisiDataType>",
  "port_id": "<port_name>",
  "optional": false
}
```

- **`type`** — An OEDISI Pydantic model name from `oedisi.types.data_types` (e.g. `"VoltagesMagnitude"`, `"PowersReal"`, `"Topology"`, `"MeasurementArray"`). Leave empty (`""`) for untyped/config inputs.
- **`port_id`** — A unique identifier for the port within this component.
- **`optional`** — *(dynamic_inputs only)* When `true`, the simulation can proceed even if this input is not wired.

**Example** (`wls_federate`):

```json
{
  "directory": "wls_federate",
  "execute_function": "python state_estimator_federate.py",
  "static_inputs": [],
  "dynamic_inputs": [
    { "type": "VoltagesMagnitude", "port_id": "voltages_magnitude" },
    { "type": "PowersReal", "port_id": "powers_real" },
    { "type": "PowersImaginary", "port_id": "powers_imaginary" },
    { "type": "Topology", "port_id": "topology" }
  ],
  "dynamic_outputs": [
    { "type": "VoltagesMagnitude", "port_id": "voltage_mag" },
    { "type": "VoltagesAngle", "port_id": "voltage_angle" }
  ]
}
```

---

### `pyproject.toml`

Standard `setuptools` src-layout packaging. See the [setuptools quickstart](https://setuptools.pypa.io/en/latest/userguide/quickstart.html) for full reference.

OEDISI-specific conventions:
- Always depend on `helics>=3.4.0`, `fastapi`, `uvicorn`, and `oedisi~=3.0`.
- Expose a console script entry point pointing to `<package>.server:main`.
- Use `[tool.setuptools.packages.find]` with `where = ["src"]` for src-layout discovery.
- Include a `[project.optional-dependencies] dev` group with `pytest`, `mypy`, etc.

---

### `Dockerfile`

All components follow the same container pattern:

```dockerfile
FROM python:3.10.6-slim-bullseye

RUN apt-get update
RUN apt-get install -y git ssh

RUN mkdir <component_dir>
COPY . ./<component_dir>
WORKDIR ./<component_dir>

RUN pip install -e .

EXPOSE <port>/tcp

CMD ["python", "-m", "<package_name>.server"]
```

Each component exposes a unique TCP port for its FastAPI server. Examples:
- Broker: `8766`
- LocalFeeder: `5678`
- wls_federate: `5683`

---

### `src/<package_name>/`

#### `__init__.py`

Contains the package docstring and version:

```python
"""<Component description>."""

__version__ = "0.1.0"
```

#### `server.py` — FastAPI Application

Every component's server exposes three standard REST endpoints:

| Endpoint          | Method | Purpose                                                                                         |
| ----------------- | ------ | ----------------------------------------------------------------------------------------------- |
| `GET /`           | GET    | Health check — returns hostname and IP                                                          |
| `POST /configure` | POST   | Receives a `ComponentStruct`, writes `input_mapping.json` and `static_inputs.json` to disk      |
| `POST /run`       | POST   | Receives a `BrokerConfig`, launches the federate simulation as a background task                 |

**Minimal `server.py` template:**

```python
import socket
import uvicorn
from fastapi import BackgroundTasks, FastAPI
from oedisi.types.common import BrokerConfig, HeathCheck

from <package_name>.<federate_module> import run_simulator

app = FastAPI()


@app.get("/")
async def health_check():
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    return HeathCheck(hostname=hostname, host_ip=host_ip)


@app.post("/configure")
async def configure(component: dict):
    # Write input_mapping.json and static_inputs.json
    ...


@app.post("/run")
async def run(broker_config: BrokerConfig, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_simulator, broker_config)
    return {"status": "running"}


def main():
    uvicorn.run(app, host="0.0.0.0", port=<PORT>)


if __name__ == "__main__":
    main()
```

#### `<federate_logic>.py` — HELICS Federate

Contains a `run_simulator(broker_config)` function that:

1. Reads `static_inputs.json` and `input_mapping.json` from disk
2. Creates a HELICS value federate (`helicsCreateValueFederate`)
3. Registers **subscriptions** for each `dynamic_input` using topics from `input_mapping.json`
4. Registers **publications** for each `dynamic_output`
5. Enters executing mode and runs the time-stepping loop (`helicsFederateRequestTime`)
6. On each timestep: reads subscribed JSON, deserializes into OEDISI Pydantic types, processes data, and publishes results

---

### `tests/`

Tests use `pytest` and commonly include:

- **Unit tests** for core logic (math, data transformation, etc.)
- **API tests** using `fastapi.testclient.TestClient` for REST endpoint validation
- **Test data** in subdirectories or via `conftest.py` fixtures
- OEDISI Pydantic models (`oedisi.types.data_types`) for loading/validating test fixtures


---

## Wiring Components in Scenarios

Scenario files (under `scenarios/`) define how components are instantiated and connected:

```json
{
  "components": [
    {
      "name": "feeder",
      "type": "LocalFeeder",
      "host": "localhost",
      "container_port": 5678,
      "parameters": { ... }
    },
    {
      "name": "state_estimator",
      "type": "StateEstimatorComponent",
      "host": "localhost",
      "container_port": 5683,
      "parameters": {}
    }
  ],
  "links": [
    {
      "source": "feeder",
      "source_port": "voltages_magnitude",
      "target": "state_estimator",
      "target_port": "voltages_magnitude"
    }
  ]
}
```

- **`components[].type`** must match a key in `components.json`.
- **`links[]`** connect a source component's `dynamic_output` port to a target component's `dynamic_input` port.
