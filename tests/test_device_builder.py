from copy import deepcopy
from importlib import import_module

import pytest

from gard.systems.stream_registry import STREAM_DEFINITIONS
from gard.systems.device_registry import DEVICE_DEFINITIONS
from src.base.device_builder import build_device
from src.base.stream import ReferenceEnv
from src.base.stream_builder import build_stream
from src.base.system_builder import build_system
from src.ST_model.mixer import Mixer
from src.GT_model.GT_model import GTModel
from src.GT_model.config import GTModelConfig


SYSTEM_COUNTS = {
    "condenser": 25, "cooling": 1, "heating": 5,
    "hrsg1_hp": 18, "hrsg1_ip": 19, "hrsg1_lp": 17,
    "hrsg2_hp": 18, "hrsg2_ip": 19, "hrsg2_lp": 17,
    "st": 9,
}


@pytest.fixture
def row():
    values = {}
    for definition in STREAM_DEFINITIONS.values():
        for parameter in ("P", "T", "m_dot"):
            source = definition.get(parameter)
            if isinstance(source, str):
                values[source] = {"P": 2e6, "T": 500, "m_dot": 2.0}[parameter]
    for unit in (1, 2):
        for level in ("hp", "ip", "lp"):
            for pump in (1, 2):
                values[f"{level}{unit}_pump{pump}.power"] = 1000.0
    for pump in (1, 2, 3):
        values[f"pre_pump{pump}.power"] = 1000.0
        values[f"cond_pump{pump}.power"] = 1000.0
        values[f"vacuum_pump{pump}.work"] = -1000.0
    values.update({
        "cooling.work": -1000.0, "cooling.heat": -2000.0,
        "cooling.heat_exergy": -100.0,
        "heating_drain.work": -1000.0, "heating_drain.heat": 100.0,
        "heating_drain.heat_exergy": 10.0, "heating.other_heat": 200.0,
        "heating.other_heat_exergy": 20.0, "st.generator_power": 5000.0,
    })
    for unit in (1, 2):
        values.update({
            f"gt{unit}.air_in.composition": {"N2": 0.79, "O2": 0.21},
            f"gt{unit}.fuel.composition": {"CH4": 1.0},
            f"gt{unit}.exhaust.composition": {"N2": 0.75, "O2": 0.10, "CO2": 0.05, "H2O": 0.10},
            f"gt{unit}.power": 30e6,
            f"gt{unit}.total_pressure_recovery": 0.95,
            f"gt{unit}.fuel_chemical_exergy": 55e6,
        })
        for prefix, temperature, pressure, flow in (
            (f"gt{unit}.air_in", 300, 101325, 100),
            (f"gt{unit}.compressor_out", 650, 1.5e6, 100),
            (f"gt{unit}.fuel", 300, 1.6e6, 2),
            (f"gt{unit}.exhaust", 800, 101325, 102),
            (f"hrsg{unit}.gas_out", 400, 101325, 102),
        ):
            values[prefix + ".T"] = temperature
            values[prefix + ".P"] = pressure
            values[prefix + ".m_dot"] = flow
    values.update({
        "condenser.work": -9000.0,
        "heating.work": -1000.0,
        "heating.heat": 300.0,
        "heating.heat_exergy": 30.0,
        "st.work": 5000.0,
    })
    for unit in (1, 2):
        for level in ("hp", "ip", "lp"):
            values[f"hrsg{unit}_{level}.work"] = -2000.0
    return values


def test_only_selected_device_builds_streams_across_directories(row, monkeypatch):
    definitions = {
        "main_merge": {
            "type": "Mixer",
            "inlets": ["1号炉高压蒸汽至汽轮机", "2号炉高压蒸汽至汽轮机"],
            "outlets": ["汽轮机高压缸入口"],
        },
        "unused": {"type": "unsupported"},
    }
    original = deepcopy(definitions)
    row[STREAM_DEFINITIONS["汽轮机高压缸入口"]["m_dot"]] = 4.0
    reference = ReferenceEnv(298.15, 101325)
    built_names = []

    def record_build(name, *args):
        built_names.append(name)
        return build_stream(name, *args)

    monkeypatch.setattr("src.base.device_builder.build_stream", record_build)
    device = build_device("main_merge", definitions, STREAM_DEFINITIONS, row, reference)

    assert isinstance(device, Mixer)
    assert built_names == definitions["main_merge"]["inlets"] + definitions["main_merge"]["outlets"]
    assert device.mass_balance() == 0
    assert device.energy_balance() == pytest.approx(0)
    assert all(stream.ref is reference for stream in device.inlets + device.outlets)
    assert definitions == original


@pytest.mark.parametrize("system_name, count", SYSTEM_COUNTS.items())
def test_systems_build_all_declared_ports_from_registry(system_name, count, row):
    module = import_module(f"gard.systems.{system_name}")
    definitions = module.DEVICE_DEFINITIONS
    reference = ReferenceEnv(298.15, 101325)

    inputs = row.copy()
    model = build_system(
        system_name, module.SYSTEM_DEFINITIONS, DEVICE_DEFINITIONS,
        STREAM_DEFINITIONS, inputs, reference,
    )

    assert len(model.devices) == count
    assert [device.name for device in model.devices] == list(definitions)
    for device in model.devices:
        for port, names in definitions[device.name].items():
            if port == "type":
                continue
            streams = getattr(device, port)
            assert [stream.name for stream in streams] == names
            assert all(stream.ref is reference for stream in streams)
        assert device.energy_in >= 0
        assert device.exergy_in >= 0
    assert model.mass_balance() == sum(device.mass_balance() for device in model.devices)
    expected_work = {
        "condenser": -9000, "cooling": -1000, "heating": -1000,
        "hrsg1_hp": -2000, "hrsg1_ip": -2000, "hrsg1_lp": -2000,
        "hrsg2_hp": -2000, "hrsg2_ip": -2000, "hrsg2_lp": -2000,
        "st": 5000,
    }
    assert model.work == expected_work[system_name]
    assert inputs is not row
    assert row["hrsg1_hp.work"] == -2000.0


@pytest.mark.parametrize("unit", [1, 2])
@pytest.mark.parametrize("level", ["hp", "ip", "lp"])
def test_drum_water_side_includes_blowdown(unit, level, row):
    module = import_module(f"gard.systems.hrsg{unit}_{level}")
    device = build_device(
        f"{level}{unit}_drum_evaporator", module.DEVICE_DEFINITIONS,
        STREAM_DEFINITIONS, row, ReferenceEnv(298.15, 101325),
    )

    assert f"{unit}号炉{'高' if level == 'hp' else '中' if level == 'ip' else '低'}压汽包排污" in [
        stream.name for stream in device.water_outlets
    ]
    assert not device.outlets
    assert device.water_energy_absorption == pytest.approx(device.energy_out - device.energy_in)


def test_system_builder_only_builds_selected_system_and_resolves_sources(row, monkeypatch):
    definitions = {
        "selected": {
            "devices": ["hp1_pump1", "hp2_pump1"],
            "work": "boundary.work",
            "heat": 100.0,
            "heat_exergy": 10.0,
        },
        "unused": {"devices": ["unsupported"]},
    }
    original = deepcopy(definitions)
    row["boundary.work"] = -2000.0
    reference = ReferenceEnv(298.15, 101325)
    built_names = []

    def record_build(name, *args):
        built_names.append(name)
        return build_device(name, *args)

    monkeypatch.setattr("src.base.system_builder.build_device", record_build)
    model = build_system(
        "selected", definitions, DEVICE_DEFINITIONS,
        STREAM_DEFINITIONS, row, reference,
    )

    assert built_names == ["hp1_pump1", "hp2_pump1"]
    assert model.name == "selected"
    assert model.work == -2000
    assert model.heat == 100
    assert model.heat_exergy == 10
    assert model.energy_balance() == pytest.approx(
        sum(device.energy_balance() for device in model.devices) + 2100
    )
    assert model.exergy_balance() == pytest.approx(
        sum(device.exergy_balance() for device in model.devices) + 2010
    )
    assert definitions == original


def test_hp_definition_builds_complete_high_pressure_system(row):
    from gard.systems.hrsg1_hp import SYSTEM_DEFINITIONS

    inputs = row.copy()
    model = build_system(
        "hrsg1_hp", SYSTEM_DEFINITIONS, DEVICE_DEFINITIONS,
        STREAM_DEFINITIONS, inputs, ReferenceEnv(298.15, 101325),
    )

    assert list(SYSTEM_DEFINITIONS) == ["hrsg1_hp"]
    assert model.name == "hrsg1_hp"
    assert len(model.devices) == 18
    assert {"hp1_economizer1", "hp1_drum_evaporator", "hp1_superheater4", "hp1_bypass_spray"} <= {
        device.name for device in model.devices
    }
    assert model.work == -2000
    assert model.heat is None
    assert model.heat_exergy is None


@pytest.mark.parametrize("name, count", {**SYSTEM_COUNTS, "gt1": 3, "gt2": 3}.items())
def test_all_twelve_systems_use_common_entry(name, count, row):
    import math
    from gard.systems import build_system as build_by_name
    from gard.systems.system_registry import SYSTEM_DEFINITIONS

    inputs = row.copy()
    inputs.setdefault(f"{name}.heat", 1000.0)
    inputs.setdefault(f"{name}.heat_exergy", 100.0)
    original = deepcopy(inputs)
    reference = ReferenceEnv(298.15, 101325)

    model = build_by_name(name, inputs, reference)

    assert set(SYSTEM_DEFINITIONS) == set(SYSTEM_COUNTS) | {"gt1", "gt2"}
    assert model.name == name
    assert len(model.devices) == count
    assert math.isfinite(model.mass_balance())
    assert math.isfinite(model.energy_balance())
    assert math.isfinite(model.exergy_balance())
    assert inputs == original
    if name in ("gt1", "gt2"):
        assert isinstance(model, GTModel)
        assert model.mass_balance() == pytest.approx(0)
        assert model.hrsg_inlet is model.state_4
        assert model.hrsg_outlet.T == 400
        assert model.hrsg_outlet.ref is reference


@pytest.mark.parametrize("unit", [1, 2])
def test_gt_dictionary_builds_only_boundary_gases_and_preserves_config(unit, row, monkeypatch):
    from gard.systems import build_system as build_by_name

    built_names = []
    config = GTModelConfig(compressor_bleeding_mass_fraction=0)
    row[f"gt{unit}.config"] = config

    def record_stream(name, *args):
        built_names.append(name)
        return build_stream(name, *args)

    monkeypatch.setattr("src.base.system_builder.build_stream", record_stream)
    model = build_by_name(f"gt{unit}", row, ReferenceEnv(298.15, 101325))

    assert built_names == [f"{unit}号燃机进气", f"{unit}号燃机压气机出口", f"{unit}号燃机燃料", f"{unit}号燃机排气", f"{unit}号余热锅炉出口烟气"]
    assert model.config is config
    assert model.compressor.state_2.m_dot == 100
    assert model.hrsg_inlet is model.state_4
    assert model.hrsg_inlet.energy_flow > model.hrsg_outlet.energy_flow


def test_common_entry_does_not_derive_boundary_work(row):
    from gard.systems import build_system as build_by_name

    row.pop("hrsg1_hp.work")
    original = deepcopy(row)
    model = build_by_name("hrsg1_hp", row, ReferenceEnv(298.15, 101325))

    assert model.work is None
    assert model.name == "hrsg1_hp"
    assert len(model.devices) == 18
    assert row == original


@pytest.fixture
def plant_row(row):
    inputs = row.copy()
    inputs.update({
        "hrsg1.heat": -1000.0, "hrsg1.heat_exergy": -100.0,
        "hrsg2.heat": -1000.0, "hrsg2.heat_exergy": -100.0,
        "condenser.heat": -3000.0, "condenser.heat_exergy": -300.0,
    })
    for name, temperature in (
        ("1号炉高压省煤器入口", 400), ("1号炉高压省煤器1出口", 430),
        ("1号炉高压省煤器2出口", 450), ("1号炉高压汽包入口", 470),
    ):
        inputs[STREAM_DEFINITIONS[name]["T"]] = temperature
    return inputs


def test_plant_name_lookup_keeps_subsystems_and_shared_devices(plant_row):
    from gard.plant import build_plant

    original = deepcopy(plant_row)
    reference = ReferenceEnv(298.15, 101325)
    plant = build_plant(plant_row, reference)

    assert list(plant.system) == ["gt1", "gt2", "hrsg1", "hrsg2", "st", "condenser", "cooling", "heating"]
    assert len(plant.systems) == 8
    assert sum(len(system.devices) for system in plant.systems) == 156
    hp1 = plant.system["hrsg1"].subsystems["hrsg1_hp"]
    economizer = hp1.device["hp1_economizer1"]
    assert len(hp1.devices) == 18
    assert economizer is plant.system["hrsg1"].device["hp1_economizer1"]
    assert economizer.water_energy_absorption > 0
    assert economizer.water_inlets[0].ref is reference
    assert economizer.water_outlets[0].ref is reference
    assert plant_row == original


@pytest.mark.parametrize("unit", [1, 2])
def test_whole_boiler_reuses_gas_boundary_and_excludes_internal_heat(unit, plant_row):
    from gard.plant import build_plant

    plant = build_plant(plant_row, ReferenceEnv(298.15, 101325))
    gt = plant.system[f"gt{unit}"]
    boiler = plant.system[f"hrsg{unit}"]
    gas_boundary = boiler.device[f"hrsg{unit}_gas_boundary"]

    assert len(boiler.devices) == 55
    assert list(boiler.subsystems) == [f"hrsg{unit}_hp", f"hrsg{unit}_ip", f"hrsg{unit}_lp"]
    assert gas_boundary.inlets[0] is gt.state_4
    assert gas_boundary.inlets[0] is gt.hrsg_inlet
    assert gas_boundary.outlets[0] is gt.hrsg_outlet
    assert boiler.work == -6000
    energy_balance = plant.energy_balance()
    exergy_balance = plant.exergy_balance()
    for subsystem in boiler.subsystems.values():
        subsystem.heat = 123456789.0
        subsystem.heat_exergy = 987654321.0
    assert plant.energy_balance() == pytest.approx(energy_balance)
    assert plant.exergy_balance() == pytest.approx(exergy_balance)
    assert plant.work == 59_982_000
    assert plant.heat == -6700
    assert plant.heat_exergy == -570


def test_plant_system_lookup_tracks_add_system():
    from src.base.plant import Plant
    from src.base.system import System

    plant = Plant("test")
    boiler = System("hrsg1")
    plant.add_system(boiler)
    assert plant.system["hrsg1"] is boiler
