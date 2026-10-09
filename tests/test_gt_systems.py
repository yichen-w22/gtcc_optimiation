from importlib import import_module

import pytest

from src.base.stream import ReferenceEnv
from src.GT_model.GT_model import GTModel
from src.GT_model.config import GTModelConfig
from src.working_fluid.gas import GasComposition, GasState
from src.base.stream_builder import build_streams


@pytest.mark.parametrize("unit", [1, 2])
def test_gt_defines_required_gases_and_shared_hrsg_inlet(unit):
    module = import_module(f"gard.systems.gt{unit}")
    names = [
        f"{unit}号燃机进气", f"{unit}号燃机压气机出口", f"{unit}号燃机燃料",
        f"{unit}号燃机排气", f"{unit}号余热锅炉出口烟气",
    ]
    fractions = {"N2": 0.75, "O2": 0.10, "CO2": 0.05, "H2O": 0.10}
    row = {
        f"gt{unit}.air_in.composition": {"N2": 0.79, "O2": 0.21},
        f"gt{unit}.fuel.composition": {"CH4": 1.0},
        f"gt{unit}.exhaust.composition": fractions,
        f"gt{unit}.total_pressure_recovery": 0.95,
    }
    for prefix, temperature, pressure, flow in (
        (f"gt{unit}.air_in", 300, 101325, 100),
        (f"gt{unit}.compressor_out", 650, 1.5e6, 100),
        (f"gt{unit}.fuel", 300, 1.6e6, 2),
        (f"gt{unit}.exhaust", 800, 101325, 102),
        (f"hrsg{unit}.gas_out", 400, 101325, 102),
    ):
        row[prefix + ".P"] = pressure
        row[prefix + ".T"] = temperature
        row[prefix + ".m_dot"] = flow
    reference = ReferenceEnv(T0=298.15, P0=101325)

    streams = build_streams(names, module.STREAM_DEFINITIONS, row, reference)

    assert list(module.STREAM_DEFINITIONS) == names
    assert all(isinstance(stream, GasState) for stream in streams.values())
    assert [stream.T for stream in streams.values()] == [300, 650, 300, 800, 400]
    assert all(stream.h is not None for stream in streams.values())
    assert streams[names[0]].composition == streams[names[1]].composition
    assert streams[names[2]].composition.CH4 == 1.0
    assert streams[names[3]].composition == streams[names[4]].composition
    hrsg_inlet = streams[module.HRSG_INLET_STREAM_NAME]
    model = module.build_system(row, streams, config=GTModelConfig(compressor_bleeding_mass_fraction=0))
    assert model.state_1 is streams[names[0]]
    assert model.compressor_outlet is streams[names[1]]
    assert model.fuel is streams[names[2]]
    assert model.state_4 is hrsg_inlet
    assert hrsg_inlet.energy_flow > streams[names[4]].energy_flow
    assert f"{unit}号余热锅炉进口烟气" not in module.STREAM_DEFINITIONS
    assert not any(code.startswith(f"hrsg{unit}.gas_in.") for code in module.INPUT_UNITS)
    assert model.mass_balance() == pytest.approx(0.0)
    assert model.net_power is not None


@pytest.mark.parametrize("unit", [1, 2])
def test_gt_reuses_external_fuel_and_air_inputs(unit):
    module = import_module(f"gard.systems.gt{unit}")
    air = GasComposition(N2=0.79, O2=0.21)
    reference = ReferenceEnv(T0=298.15, P0=101325)
    row = {
        f"gt{unit}.exhaust.P": 101325,
        f"gt{unit}.exhaust.T": 800,
        f"gt{unit}.exhaust.m_dot": 102.0,
        f"gt{unit}.exhaust.composition": {"N2": 0.75, "O2": 0.10, "CO2": 0.05, "H2O": 0.10},
        f"gt{unit}.power": 30e6,
        f"gt{unit}.total_pressure_recovery": 0.95,
    }
    streams = build_streams([f"{unit}号燃机排气"], module.STREAM_DEFINITIONS, row, reference)
    ports = {
        f"{unit}号燃机进气": GasState.from_TP(T=300, P=101325, m_dot=100, composition=air, ref=reference, name=f"{unit}号燃机进气"),
        f"{unit}号燃机压气机出口": GasState.from_TP(T=650, P=1.5e6, m_dot=100, composition=air, ref=reference, name=f"{unit}号燃机压气机出口"),
        f"{unit}号燃机燃料": GasState.from_TP(T=300, P=1.6e6, m_dot=2, composition=GasComposition(CH4=1), ref=reference, name=f"{unit}号燃机燃料"),
    }

    model = module.build_system(row, streams, ports, config=GTModelConfig(compressor_bleeding_mass_fraction=0))

    assert isinstance(model, GTModel)
    assert model.name == f"gt{unit}"
    assert model.state_4 is streams[f"{unit}号燃机排气"]
    assert model.state_1 is ports[f"{unit}号燃机进气"]
    assert model.actual_power == 30e6
    assert model.mass_balance() == pytest.approx(0.0)
    assert model.net_power is not None
    assert len(streams) == 1


@pytest.mark.parametrize("unit", [1, 2])
def test_missing_gt_measurements_do_not_create_internal_hrsg_gas(unit):
    module = import_module(f"gard.systems.gt{unit}")
    streams = build_streams(list(module.STREAM_DEFINITIONS), module.STREAM_DEFINITIONS, {}, None)

    model = module.build_system({}, streams)

    assert model.state_1 is streams[f"{unit}号燃机进气"]
    assert model.state_1.h is None
    assert all(stream.h is None for stream in streams.values())
