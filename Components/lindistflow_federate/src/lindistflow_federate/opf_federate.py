"""HELICS federate for LinDistFlow-based optimal power flow."""

import json
import logging
from datetime import datetime

import helics as h
from oedisi.types.common import BrokerConfig
from oedisi.types.data_types import (
    Command,
    CommandList,
    Injection,
    Topology,
    VoltagesMagnitude,
)
from pydantic import BaseModel, Field

from . import adapter, lindistflow
from .area import area_info

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class ComponentParameters(BaseModel):
    """Static configuration parameters defining schema."""

    name: str
    deltat: float = Field(default=0.1, ge=0.0, title="Time Step (s)")
    control_type: lindistflow.ControlType = Field(
        default=lindistflow.ControlType.WATT, title="Control Type (Watt or VAR)"
    )
    pf_flag: bool = Field(default=True, title="Run Relaxed Power Flow")

    model_config = {"title": "LinDistFlowConfig", "description": "Configuration for the LinDistFlow OPF federate."}


class Subscriptions:
    """Container for HELICS subscriptions."""

    voltages_mag: VoltagesMagnitude
    injections: Injection
    topology: Topology


class Federate:
    """Federate for executing optimal power flow based on system state."""

    def __init__(self, broker_config: BrokerConfig | None = None) -> None:
        """Initialize the OPF federate, loading configurations and registering with HELICS."""
        self.sub = Subscriptions()
        self.pv_capacities: dict[str, float] = {}
        self.load_static_inputs()
        self.load_input_mapping()
        self.initialize(broker_config)
        self.load_component_definition()
        self.register_subscription()
        self.register_publication()

    def load_component_definition(self) -> None:
        """Load component definition from JSON file."""
        path = "component_definition.json"
        with open(path, encoding="UTF-8") as file:
            self.component_config = json.load(file)

    def load_input_mapping(self):
        """Load input mapping for subscriptions from JSON file."""
        path = "input_mapping.json"
        with open(path, encoding="UTF-8") as file:
            self.inputs = json.load(file)

    def load_static_inputs(self):
        """Load static configuration inputs from JSON file."""
        path = "static_inputs.json"
        with open(path, encoding="UTF-8") as file:
            config = json.load(file)

        self.static = ComponentParameters(**config)

    def initialize(self, broker_config: BrokerConfig | None) -> None:
        """Initialize HELICS federate and configure broker connection."""
        self.info = h.helicsCreateFederateInfo()

        if broker_config is not None:
            h.helicsFederateInfoSetBroker(self.info, broker_config.broker_ip)
            h.helicsFederateInfoSetBrokerPort(self.info, broker_config.broker_port)

        self.info.core_name = self.static.name
        self.info.core_type = h.HELICS_CORE_TYPE_ZMQ
        self.info.core_init = "--federates=1"

        h.helicsFederateInfoSetTimeProperty(self.info, h.helics_property_time_delta, self.static.deltat)

        self.fed = h.helicsCreateValueFederate(self.static.name, self.info)

    def register_subscription(self) -> None:
        """Register HELICS subscriptions for topology, voltages, and injections."""
        self.sub.topology = self.fed.register_subscription(self.inputs["topology"], "")
        self.sub.voltages_mag = self.fed.register_subscription(self.inputs["voltages_magnitude"], "")
        self.sub.injections = self.fed.register_subscription(self.inputs["injections"], "")

    def register_publication(self) -> None:
        """Register HELICS publications for commands and voltages."""
        self.pub_commands = self.fed.register_publication("change_commands", h.HELICS_DATA_TYPE_STRING, "")
        self.pub_voltages = self.fed.register_publication("opf_voltages_magnitude", h.HELICS_DATA_TYPE_STRING, "")
        self.pub_voltages_angle = self.fed.register_publication("opf_voltages_angle", h.HELICS_DATA_TYPE_STRING, "")
        self.pub_power_magnitude = self.fed.register_publication("opf_power_magnitude", h.HELICS_DATA_TYPE_STRING, "")
        self.pub_power_angle = self.fed.register_publication("opf_power_angle", h.HELICS_DATA_TYPE_STRING, "")
        self.pub_control_power_real = self.fed.register_publication(
            "opf_control_power_real", h.HELICS_DATA_TYPE_STRING, ""
        )
        self.pub_control_power_imaginary = self.fed.register_publication(
            "opf_control_power_imaginary", h.HELICS_DATA_TYPE_STRING, ""
        )

    def run(self) -> None:
        """Run the main execution loop for data exchange and OPF calculation."""
        logger.info(f"Federate connected: {datetime.now()}")
        self.fed.enter_executing_mode()
        granted_time = h.helicsFederateRequestTime(self.fed, h.HELICS_TIME_MAXTIME)

        while granted_time < h.HELICS_TIME_MAXTIME:
            if not self.sub.voltages_mag.is_updated():
                granted_time = h.helicsFederateRequestTime(self.fed, h.HELICS_TIME_MAXTIME)
                continue

            topology = Topology.model_validate(self.sub.topology.json)
            if not self.pv_capacities:
                for val, eq_id in zip(
                    topology.injections.power_real.values,
                    topology.injections.power_real.equipment_ids,
                    strict=True,
                ):
                    if eq_id.lower().startswith("pvsystem."):
                        self.pv_capacities[eq_id.lower()] = self.pv_capacities.get(eq_id.lower(), 0.0) + float(val)

            [branch_info, bus_info] = adapter.extract_info(topology)

            slack = topology.slack_bus[0]
            [slack_bus, phase] = slack.split(".")

            area_branch, area_bus = area_info(branch_info, bus_info, slack_bus)

            voltages_mag = VoltagesMagnitude.model_validate(self.sub.voltages_mag.json)

            area_bus = adapter.extract_voltages(area_bus, voltages_mag)

            time = voltages_mag.time
            logger.info(time)

            injection = Injection.model_validate(self.sub.injections.json)
            area_bus = adapter.extract_injection(area_bus, injection)

            voltages, power_flow, control, conversion = lindistflow.optimal_power_flow(
                area_branch,
                area_bus,
                slack_bus,
                lindistflow.ControlType(self.static.control_type),
                self.static.pf_flag,
            )

            commands = []
            for key, val in control.items():
                if key in area_bus:
                    bus = area_bus[key]
                    if "eqid" in bus:
                        eqid = bus["eqid"]
                        [type, _] = eqid.split(".")
                        if type == "PVSystem":
                            setpoint = lindistflow.ignore_phase(val) * conversion
                            if setpoint < 0.1:
                                continue

                            if self.static.control_type == lindistflow.ControlType.WATT:
                                max_pv = self.pv_capacities.get(eqid.lower(), 50.0)
                                if max_pv <= 0:
                                    obj_val = 100.0
                                elif setpoint == 0:
                                    obj_val = 0.0
                                elif setpoint < max_pv:
                                    obj_val = setpoint / float(max_pv) * 100.0
                                else:
                                    obj_val = 100.0

                                logger.debug(f"{eqid}, {setpoint} kW -> {obj_val} %Pmpp")
                                commands.append(
                                    Command(
                                        obj_name=eqid,
                                        obj_property="%Pmpp",
                                        val=str(obj_val),
                                    )
                                )
                            elif self.static.control_type == lindistflow.ControlType.VAR:
                                commands.append(Command(obj_name=eqid, obj_property="kvar", val=str(setpoint)))

            logger.info(commands)
            if commands:
                self.pub_commands.publish(CommandList(root=commands).model_dump_json())

            pub_mags = adapter.pack_voltages(voltages, time)
            self.pub_voltages.publish(pub_mags.model_dump_json())

            pub_angles = adapter.pack_voltages_angle(voltages, time)
            self.pub_voltages_angle.publish(pub_angles.model_dump_json())

            pub_pow_mag, pub_pow_ang = adapter.pack_power_flow(power_flow, time)
            self.pub_power_magnitude.publish(pub_pow_mag.model_dump_json())
            self.pub_power_angle.publish(pub_pow_ang.model_dump_json())

            pub_ctrl_real, pub_ctrl_imag = adapter.pack_control_powers(
                control, area_bus, self.static.control_type, conversion, time
            )
            self.pub_control_power_real.publish(pub_ctrl_real.model_dump_json())
            self.pub_control_power_imaginary.publish(pub_ctrl_imag.model_dump_json())

        self.stop()

    def stop(self) -> None:
        """Finalize and disconnect the federate from HELICS."""
        h.helicsFederateDisconnect(self.fed)
        h.helicsFederateFree(self.fed)
        h.helicsCloseLibrary()
        logger.info(f"Federate disconnected: {datetime.now()}")


if __name__ == "__main__":
    fed = Federate()
    fed.run()
