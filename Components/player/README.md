# OEDISI Player

Dataset playback federate for replaying recorded HELICS co-simulation data as typed `MeasurementArray` publications.

## Overview

The Player federate is the reverse of the [Recorder](../recorder/README.md). It reads a pre-recorded dataset from disk and publishes each row as a validated `MeasurementArray` (or subtype) over HELICS at each simulation time step.

Key features:
- Supports Feather and CSV input files (auto-detected by file extension)
- Validates each row against a user-configured `oedisi` data type before publishing
- Supports all `MeasurementArray` subtypes (VoltagesMagnitude, PowersReal, etc.)
- EquipmentNodeArray types (PowersReal, etc.) load `equipment_ids` from a sidecar metadata file
- Stops cleanly when the dataset is exhausted

## Architecture

- **Player**: Main federate class (`play_dataset.py`)
- **FastAPI Server**: REST API wrapper (`server.py`)
- **Input Formats**: Feather (PyArrow) and CSV

### Supported data types

All `MeasurementArray` subtypes from `oedisi.types.data_types`:

- **BusArray**: `VoltagesMagnitude`, `VoltagesAngle`, `VoltagesReal`, `VoltagesImaginary`
- **EquipmentArray**: `CurrentsMagnitude`, `CurrentsAngle`, `CurrentsReal`, `CurrentsImaginary`, `ImpedanceMagnitude`, `ImpedanceAngle`, `ImpedanceReal`, `ImpedanceImaginary`, `SolarIrradiances`, `Temperatures`, `WindSpeeds`, `StatesOfCharge`
- **EquipmentNodeArray**: `PowersMagnitude`, `PowersAngle`, `PowersReal`, `PowersImaginary`
- **Base types**: `MeasurementArray`, `BusArray`, `EquipmentArray`, `EquipmentNodeArray`

### EquipmentNodeArray metadata sidecar

Types that extend `EquipmentNodeArray` (e.g. `PowersReal`) require an `equipment_ids` field not stored in the Feather/CSV dataset. Provide a JSON sidecar file at `{filename}_metadata.json`:

```json
{
    "equipment_ids": ["PVSystem.1", "PVSystem.2", "PVSystem.3"],
    "units": "kW"
}
```

## Time Mapping

The Player uses row-index-based time mapping: row 0 is published at the first HELICS time step, row 1 at the second, etc. When the dataset is exhausted, the federate disconnects cleanly.

## Installation

### From the monorepo root:
```bash
pip install -e Components/player
```

### With development dependencies:
```bash
pip install -e ".[dev]"
```


## Docker

Build the Docker image:
```bash
docker build -t oedisi-player .
```

Run the container:
```bash
docker run -p 5680:5680 -e PORT=5680 -v /data:/data oedisi-player
```

Mount a volume containing your dataset files.
