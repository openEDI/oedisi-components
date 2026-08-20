"""Regression tests for the narrowly scoped EV load command path."""

import importlib
from types import SimpleNamespace

import pytest
from localfeeder.FeederSimulator import FeederSimulator, OpenDSSState
from oedisi.types.data_types import Command

feeder_module = importlib.import_module("localfeeder.FeederSimulator")


class FakeDSS:
    """Small OpenDSS surface used by the EV command tests."""

    def __init__(self):
        """Create deterministic fake OpenDSS interfaces and call records."""
        self.commands = []
        self.active_elements = []
        self.selected_loads = []
        self.Loads = SimpleNamespace(
            Name=self._select_load,
            kV=lambda: 2.4,
            Vminpu=lambda: 0.9,
            IsDelta=lambda: False,
        )
        self.Circuit = SimpleNamespace(SetActiveElement=self.active_elements.append)
        self.CktElement = SimpleNamespace(
            BusNames=lambda: ["48.1"],
            NumPhases=lambda: 1,
            AllPropertyNames=lambda: ["kW", "kvar"],
            Name=lambda: "Load.base_load",
        )
        self.Text = SimpleNamespace(Command=self.commands.append)

    def _select_load(self, name):
        self.selected_loads.append(name)


def make_sim(load_bus_map=None):
    """Create an initialized simulator shell without loading a feeder."""
    sim = FeederSimulator.__new__(FeederSimulator)
    sim._state = OpenDSSState.SNAPSHOT_RUN
    if load_bus_map is not None:
        sim._load_bus_map = load_bus_map
    return sim


def test_ev_command_creates_separate_load_and_reuses_it(monkeypatch):
    """EV commands create one shapeless load and reuse it for later updates."""
    fake_dss = FakeDSS()
    monkeypatch.setattr(feeder_module, "dss", fake_dss)
    sim = make_sim({"48.1": "base_load", "48": "base_load"})

    sim.change_obj([Command(obj_name="EVLoad.48.1", obj_property="kW", val="22")])
    sim.change_obj([Command(obj_name="EVLoad.48.1", obj_property="kvar", val="3")])

    assert fake_dss.selected_loads == ["base_load"]
    assert fake_dss.commands == [
        "New Load.evinj_48_1 bus1=48.1 phases=1 conn=wye "
        "kV=2.4 kW=0 kvar=0 model=1 Vminpu=0.9 Vmaxpu=1.2",
        "Load.evinj_48_1.kW=22",
        "Load.evinj_48_1.kvar=3",
    ]


def test_unknown_ev_bus_fails_instead_of_fuzzy_matching(monkeypatch):
    """A partial bus name fails rather than selecting a fuzzy match."""
    fake_dss = FakeDSS()
    monkeypatch.setattr(feeder_module, "dss", fake_dss)
    sim = make_sim({"p1ulv4108.1": "smartds_load", "p1ulv4108": "smartds_load"})

    with pytest.raises(ValueError, match="No OpenDSS load found"):
        sim.change_obj([Command(obj_name="EVLoad.p1ulv410", obj_property="kW", val="22")])

    assert fake_dss.commands == []


def test_ev_command_rejects_non_power_property(monkeypatch):
    """The EV-only path accepts real and reactive power properties only."""
    fake_dss = FakeDSS()
    monkeypatch.setattr(feeder_module, "dss", fake_dss)
    sim = make_sim({"48.1": "base_load"})

    with pytest.raises(ValueError, match="Unsupported EV load property"):
        sim.change_obj([Command(obj_name="EVLoad.48.1", obj_property="daily", val="shape")])

    assert fake_dss.commands == []


def test_non_ev_command_uses_existing_command_path(monkeypatch):
    """Ordinary OpenDSS commands remain on the original command path."""
    fake_dss = FakeDSS()
    monkeypatch.setattr(feeder_module, "dss", fake_dss)
    sim = make_sim()

    sim.change_obj([Command(obj_name="Load.base_load", obj_property="kW", val="10")])

    assert fake_dss.active_elements == ["Load.base_load"]
    assert fake_dss.selected_loads == []
    assert fake_dss.commands == ["Load.base_load.kW=10"]
