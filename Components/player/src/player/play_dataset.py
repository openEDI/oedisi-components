"""Player federate for replaying recorded datasets as HELICS publications."""

import json
import logging
import os
from pathlib import Path
from typing import Any

import helics as h
import numpy as np
import pandas as pd
from oedisi.types.common import BrokerConfig
from oedisi.types.data_types import (
    BusArray,
    CurrentsAngle,
    CurrentsImaginary,
    CurrentsMagnitude,
    CurrentsReal,
    EquipmentArray,
    EquipmentNodeArray,
    ImpedanceAngle,
    ImpedanceImaginary,
    ImpedanceMagnitude,
    ImpedanceReal,
    MeasurementArray,
    PowersAngle,
    PowersImaginary,
    PowersMagnitude,
    PowersReal,
    SolarIrradiances,
    StatesOfCharge,
    Temperatures,
    VoltagesAngle,
    VoltagesImaginary,
    VoltagesMagnitude,
    VoltagesReal,
    WindSpeeds,
)
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

TYPE_MAP: dict[str, type[MeasurementArray]] = {
    "MeasurementArray": MeasurementArray,
    "BusArray": BusArray,
    "EquipmentArray": EquipmentArray,
    "EquipmentNodeArray": EquipmentNodeArray,
    "VoltagesMagnitude": VoltagesMagnitude,
    "VoltagesAngle": VoltagesAngle,
    "VoltagesReal": VoltagesReal,
    "VoltagesImaginary": VoltagesImaginary,
    "CurrentsMagnitude": CurrentsMagnitude,
    "CurrentsAngle": CurrentsAngle,
    "CurrentsReal": CurrentsReal,
    "CurrentsImaginary": CurrentsImaginary,
    "ImpedanceMagnitude": ImpedanceMagnitude,
    "ImpedanceAngle": ImpedanceAngle,
    "ImpedanceReal": ImpedanceReal,
    "ImpedanceImaginary": ImpedanceImaginary,
    "PowersMagnitude": PowersMagnitude,
    "PowersAngle": PowersAngle,
    "PowersReal": PowersReal,
    "PowersImaginary": PowersImaginary,
    "SolarIrradiances": SolarIrradiances,
    "Temperatures": Temperatures,
    "WindSpeeds": WindSpeeds,
    "StatesOfCharge": StatesOfCharge,
}


def resample_dataset(
    df: pd.DataFrame,
    run_freq_time_step: float,
    t_start: int,
    t_steps: int,
) -> pd.DataFrame:
    """Resample a dataset to evenly-spaced time steps via linear interpolation.

    The target time grid begins at the timestamp of the source row at *t_start*
    and produces exactly *t_steps* entries spaced *run_freq_time_step* seconds
    apart.  Values are linearly interpolated from the source data; target
    points outside the source time range are clamped to the nearest boundary
    value (with a warning).

    If the dataset has no ``time`` column the original DataFrame is returned
    unchanged (with a warning).

    Parameters
    ----------
    df:
        Source dataset. Must contain numeric data columns and, optionally, a
        ``time`` column parseable by ``pd.to_datetime``.
    run_freq_time_step:
        Desired output interval in seconds.
    t_start:
        Row index in the **source** dataset from which the output time grid
        should start.
    t_steps:
        Number of output rows to produce.

    Returns:
    -------
    pd.DataFrame
        Resampled DataFrame with the same column order as the source.
        If no ``time`` column is present the original DataFrame is returned.
    """
    if "time" not in df.columns:
        logger.warning("Dataset has no 'time' column; skipping interpolation resampling.")
        return df

    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    if df["time"].duplicated().any():
        n_dups = df["time"].duplicated().sum()
        logger.warning(f"Found {n_dups} duplicate timestamp(s); keeping last occurrence per timestamp.")
        df = df.drop_duplicates(subset="time", keep="last").reset_index(drop=True)

    if t_start >= len(df):
        raise ValueError(f"start_time_index {t_start} is out of range for dataset with {len(df)} row(s).")

    data_cols = [c for c in df.columns if c != "time"]
    t0 = df["time"].iloc[0]
    x_data = (df["time"] - t0).dt.total_seconds().to_numpy()

    x_start = x_data[t_start]
    x_target = x_start + np.arange(t_steps) * run_freq_time_step

    if x_target[-1] > x_data[-1]:
        logger.warning(
            f"Requested end time {t0 + pd.to_timedelta(x_target[-1], unit='s')} "
            f"exceeds source data end {df['time'].iloc[-1]}. "
            "Out-of-range values will be clamped to the last source value."
        )

    result: dict[str, Any] = {}
    for col in data_cols:
        result[col] = np.interp(x_target, x_data, df[col].to_numpy(dtype=float))
    result["time"] = [t0 + pd.to_timedelta(s, unit="s") for s in x_target]

    return pd.DataFrame(result, columns=data_cols + ["time"])


class ComponentParameters(BaseModel):
    """Configuration for the Player federate."""

    name: str
    filename: str
    data_type: str
    number_of_timesteps: int
    start_time_index: int
    run_freq_time_step: float = 900.0


class Player:
    """HELICS player federate — publishes a recorded dataset as a MeasurementArray stream."""

    def __init__(
        self,
        config: ComponentParameters,
        broker_config: BrokerConfig,
    ):
        """Initialize the player federate."""
        if config.data_type not in TYPE_MAP:
            raise ValueError(f"Unknown data_type '{config.data_type}'. Valid types: {sorted(TYPE_MAP.keys())}")
        self.type_class = TYPE_MAP[config.data_type]
        self.dataset = self._load_dataset(config.filename)
        self._metadata_path = config.filename
        self.metadata = self._load_metadata(config.filename)
        self.t_steps = config.number_of_timesteps

        if "time" in self.dataset.columns:
            self.dataset = resample_dataset(
                self.dataset,
                config.run_freq_time_step,
                config.start_time_index,
                config.number_of_timesteps,
            )
            self.t_start = 0
        else:
            self.t_start = config.start_time_index

        fedinfo = h.helicsCreateFederateInfo()
        h.helicsFederateInfoSetBroker(fedinfo, broker_config.broker_ip)
        h.helicsFederateInfoSetBrokerPort(fedinfo, broker_config.broker_port)

        fedinfo.core_name = config.name
        fedinfo.core_type = h.HELICS_CORE_TYPE_ZMQ
        fedinfo.core_init = "--federates=1"
        logger.debug(config.name)

        # Use a small delta_t (like the feeder) so HELICS doesn't skip the
        # federate to MAXTIME in one step.  run_freq_time_step is the physical
        # publish interval recorded in the data; it is NOT the HELICS time unit.
        h.helicsFederateInfoSetTimeProperty(fedinfo, h.helics_property_time_delta, 0.01)

        self.vfed = h.helicsCreateValueFederate(config.name, fedinfo)
        logger.info("Value federate created")

        self.pub = self.vfed.register_publication("publication", h.HELICS_DATA_TYPE_STRING, "")

    def _load_dataset(self, filename: str) -> pd.DataFrame:
        """Load dataset from a Feather or CSV file (detected by extension)."""
        ext = Path(filename).suffix.lower()
        if ext == ".feather":
            return pd.read_feather(filename)
        elif ext == ".csv":
            return pd.read_csv(filename)
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Expected .feather or .csv")

    def _load_metadata(self, filename: str) -> dict[str, Any]:
        """Load optional sidecar metadata JSON for EquipmentNodeArray types."""
        metadata_path = filename + "_metadata.json"
        if os.path.exists(metadata_path):
            with open(metadata_path) as f:
                return json.load(f)
        return {}

    def _build_measurement(self, row: pd.Series, row_index: int) -> MeasurementArray:
        """Construct and validate a typed measurement object from a DataFrame row.

        Raises ValueError if required metadata is missing, or pydantic ValidationError
        if the row data does not match the configured type.
        """
        ids = [col for col in row.index if col != "time"]
        values = [float(row[col]) for col in ids]
        time = row.get("time", None)

        data: dict[str, Any] = {
            "ids": ids,
            "values": values,
            "time": time,
        }

        # Only set units if metadata explicitly provides it; otherwise let type defaults apply.
        # For the base MeasurementArray type (no default units), metadata must supply it.
        units = self.metadata.get("units")
        if units is not None:
            data["units"] = units

        if issubclass(self.type_class, EquipmentNodeArray):
            equipment_ids = self.metadata.get("equipment_ids")
            if equipment_ids is None:
                raise ValueError(
                    f"data_type '{self.type_class.__name__}' requires 'equipment_ids' "
                    f"but no metadata sidecar was found. "
                    f"Create a '{self._metadata_path}_metadata.json' file with 'equipment_ids'."
                )
            data["equipment_ids"] = equipment_ids

        return self.type_class.model_validate(data)

    def run(self):
        """Run the player execution loop, publishing one row per granted time step.

        Follows the feeder pattern: request sequential integer timesteps (1, 2,
        3, …) instead of HELICS_TIME_MAXTIME.  In HELICS 3.6+, source-only
        federates that request MAXTIME are granted MAXTIME immediately, so we
        must request bounded times to keep the co-simulation properly stepped.
        Time starts at 1 (not 0) because subscriber federates with time_delta
        >= 1.0 cannot be granted time 0 after enter_executing_mode() — their
        first valid grant is current_time + delta >= 1.0.
        """
        self.vfed.enter_initializing_mode()
        self.vfed.enter_executing_mode()
        logger.info("Entering execution mode")

        num_rows = len(self.dataset)
        # Start at t=1 so that subscriber federates whose time_delta >= 1.0
        # (e.g. the measuring federate) can be granted time 1 as their first
        # step.  After enter_executing_mode() a federate is at time 0, so its
        # minimum next grant is 0 + delta.  If the player published row 0 at
        # t=0 the subscriber's first grant (t=1) would see row 1 as the most
        # recent value (<=1), silently dropping row 0.
        request_time = 1

        for row_index in range(self.t_steps):
            dataset_index = self.t_start + row_index
            if dataset_index >= num_rows:
                logger.info(f"Dataset exhausted after {row_index} rows. Finalizing.")
                break

            granted_time = h.helicsFederateRequestTime(self.vfed, request_time)

            row = self.dataset.iloc[dataset_index]
            measurement = self._build_measurement(row, row_index)
            self.pub.publish(measurement.model_dump_json())
            logger.info(f"Published row {row_index} at HELICS time {granted_time}")

            request_time += 1

        self.destroy()

    def destroy(self):
        """Clean up and disconnect the federate."""
        h.helicsFederateDisconnect(self.vfed)
        logger.info("Federate disconnected")
        h.helicsFederateFree(self.vfed)
        h.helicsCloseLibrary()


def run_simulator(broker_config: BrokerConfig):
    """Entry point for running the player simulator."""
    with open("static_inputs.json") as f:
        config = ComponentParameters(**json.load(f))

    sfed = Player(config, broker_config)
    sfed.run()


if __name__ == "__main__":
    schema = ComponentParameters.schema_json(indent=2)
    with open("schema.json", "w") as f:
        f.write(schema)
    run_simulator(BrokerConfig(broker_ip="127.0.0.1"))
