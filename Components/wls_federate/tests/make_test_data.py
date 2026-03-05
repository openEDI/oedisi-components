import os
from pathlib import Path

import pandas as pd
from oedisi.types.data_types import (
    PowersImaginary,
    PowersReal,
    Topology,
    VoltagesImaginary,
    VoltagesMagnitude,
    VoltagesReal,
)


def load_timestep(filename, timestep):
    df = pd.read_feather(filename).drop("time", axis=1)
    return {"ids": list(df.columns), "values": list(df.iloc[timestep, :])}


def write_test_data(outputsdir, targetdir, timestep):
    topology = Topology.model_validate_json((outputsdir / "topology.json").read_text())
    power_real = load_timestep(outputsdir / "measured_power_real.feather", timestep)
    power_imag = load_timestep(outputsdir / "measured_power_imag.feather", timestep)
    voltage_mag = load_timestep(outputsdir / "measured_voltage_magnitude.feather", timestep)
    voltage_real = load_timestep(outputsdir / "voltage_real.feather", timestep)
    voltage_imag = load_timestep(outputsdir / "voltage_imag.feather", timestep)

    with open(targetdir / "topology.json", "w") as f:
        f.write(topology.model_dump_json())
    with open(targetdir / "power_real.json", "w") as f:
        f.write(PowersReal(**power_real, equipment_ids=[]).model_dump_json())
    with open(targetdir / "power_imag.json", "w") as f:
        f.write(PowersImaginary(**power_imag, equipment_ids=[]).model_dump_json())
    with open(targetdir / "voltage_magnitude.json", "w") as f:
        f.write(VoltagesMagnitude(**voltage_mag).model_dump_json())
    with open(targetdir / "voltage_real.json", "w") as f:
        f.write(VoltagesReal(**voltage_real).model_dump_json())
    with open(targetdir / "voltage_imaginary.json", "w") as f:
        f.write(VoltagesImaginary(**voltage_imag).model_dump_json())


test_data_dir = "wls_federate/tests/small_smartds_tap_time_3"
if not os.path.exists(test_data_dir):
    os.makedirs(test_data_dir)
write_test_data(Path("outputs"), Path(test_data_dir), 3)

test_data_dir = "wls_federate/tests/small_smartds_tap_time_40"
if not os.path.exists(test_data_dir):
    os.makedirs(test_data_dir)
write_test_data(Path("outputs"), Path(test_data_dir), 40)
