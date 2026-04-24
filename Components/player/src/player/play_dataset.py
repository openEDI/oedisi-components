"""Player federate for replaying recorded datasets as HELICS publications."""

import json
import logging
import os
from pathlib import Path
from typing import Any

import helics as h
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


class ComponentParameters(BaseModel):
    """Configuration for the Player federate."""

    name: str
    filename: str
    data_type: str
    number_of_timesteps: int
    start_time_index: int


class Player:
    """HELICS player federate — publishes a recorded dataset as a MeasurementArray stream."""

    def __init__(
        self,
        config: ComponentParameters,
        broker_config: BrokerConfig,
    ):
        """Initialize the player federate."""
        if config.data_type not in TYPE_MAP:
            raise ValueError(
                f"Unknown data_type '{config.data_type}'. "
                f"Valid types: {sorted(TYPE_MAP.keys())}"
            )
        self.type_class = TYPE_MAP[config.data_type]
        self.dataset = self._load_dataset(config.filename)
        self._metadata_path = config.filename
        self.metadata = self._load_metadata(config.filename)
        self.t_steps = config.number_of_timesteps
        self.t_start = config.start_time_index

        fedinfo = h.helicsCreateFederateInfo()
        h.helicsFederateInfoSetBroker(fedinfo, broker_config.broker_ip)
        h.helicsFederateInfoSetBrokerPort(fedinfo, broker_config.broker_port)

        fedinfo.core_name = config.name
        fedinfo.core_type = h.HELICS_CORE_TYPE_ZMQ
        fedinfo.core_init = "--federates=1"
        logger.debug(config.name)

        h.helicsFederateInfoSetTimeProperty(
            fedinfo, h.helics_property_time_delta, config.run_freq_time_step
        )

        self.vfed = h.helicsCreateValueFederate(config.name, fedinfo)
        logger.info("Value federate created")

        self.pub = self.vfed.register_publication(
            "publication", h.HELICS_DATA_TYPE_STRING, ""
        )

    def _load_dataset(self, filename: str) -> pd.DataFrame:
        """Load dataset from a Feather or CSV file (detected by extension)."""
        ext = Path(filename).suffix.lower()
        if ext == ".feather":
            return pd.read_feather(filename)
        elif ext == ".csv":
            return pd.read_csv(filename)
        else:
            raise ValueError(
                f"Unsupported file format '{ext}'. Expected .feather or .csv"
            )

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
        """Run the player execution loop, publishing one row per granted time step."""
        self.vfed.enter_initializing_mode()
        self.vfed.enter_executing_mode()
        logger.info("Entering execution mode")

        num_rows = len(self.dataset)
        row_index = 0

        granted_time = h.helicsFederateRequestTime(self.vfed, h.HELICS_TIME_MAXTIME)

        while granted_time < h.HELICS_TIME_MAXTIME:
            if row_index >= num_rows:
                logger.info(f"Dataset exhausted after {num_rows} rows. Finalizing.")
                break

            row = self.dataset.iloc[self.t_start : self.t_start + self.t_steps]
            measurement = self._build_measurement(row, row_index)
            self.pub.publish(measurement.model_dump_json())
            logger.info(f"Published row {row_index} at HELICS time {granted_time}")
            row_index += 1

            granted_time = h.helicsFederateRequestTime(self.vfed, h.HELICS_TIME_MAXTIME)

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
