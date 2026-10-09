from copy import deepcopy
from importlib import import_module

import pytest

from src.base.stream import ReferenceEnv
from src.ST_model.heat_exchanger import GasWaterHeatExchanger
from src.working_fluid.gas import GasComposition, GasState
from src.working_fluid.steam_water import WaterSteamState
from src.base.stream_builder import build_stream, build_streams
from src.base.system_builder import build_system
from gard.systems.device_registry import DEVICE_DEFINITIONS
from gard.systems.stream_registry import STREAM_DEFINITIONS


@pytest.mark.parametrize("method, parameter", [
    ("from_TP", "T"),
    ("from_Ph", "h"),
    ("from_Ps", "s"),
])
@pytest.mark.parametrize("composition_source", ["inline", "row_dict", "row_object"])
def test_gas_methods_and_composition_sources(method, parameter, composition_source):
    fractions = {"N2": 0.75, "O2": 0.10, "CO2": 0.05, "H2O": 0.10}
    composition = GasComposition.from_dict(fractions)
    reference = ReferenceEnv(T0=298.15, P0=101325)
    expected = GasState.from_TP(T=700, P=101325, composition=composition, ref=reference)
    definition = {
        "type": "GasState",
        "method": method,
        "P": "gas.P",
        parameter: "gas.state",
        "m_dot": 2.0,
        "composition": "gas.composition",
        "note": "measured flue gas",
    }
    row = {"gas.P": expected.P, "gas.state": getattr(expected, parameter)}
    if composition_source == "inline":
        definition["composition"] = fractions
    elif composition_source == "row_dict":
        row["gas.composition"] = fractions
    else:
        row["gas.composition"] = composition
    definitions = {"gas": definition, "unused": {"method": "unsupported"}}
    original_definition = deepcopy(definition)
    original_row = row.copy()

    streams = build_streams(["gas"], definitions, row, reference)
    stream = streams["gas"]

    assert list(streams) == ["gas"]
    assert isinstance(stream, GasState)
    assert stream.ref is reference
    assert stream.T == pytest.approx(expected.T, rel=1e-5)
    assert stream.h == pytest.approx(expected.h, rel=1e-5)
    assert stream.s == pytest.approx(expected.s, rel=1e-5)
    assert stream.exergy == pytest.approx(expected.exergy, rel=1e-5)
    assert stream.composition.H2O == pytest.approx(0.10)
    assert stream.m_dot == 2.0
    assert definition == original_definition
    assert row == original_row


@pytest.mark.parametrize("method, parameter", [
    ("from_TP", "T"),
    ("from_Ph", "h"),
    ("from_Ps", "s"),
])
def test_missing_composition_keeps_gas_incomplete(method, parameter):
    definitions = {
        "gas": {
            "type": "GasState",
            "method": method,
            "P": 101325,
            parameter: 700,
            "m_dot": 0.0,
            "composition": "missing.composition",
        },
    }

    stream = build_stream("gas", definitions, {}, None)

    assert isinstance(stream, GasState)
    assert stream.P == 101325
    assert stream.h is None or stream.s is None
    assert sum(stream.composition.as_dict().values()) == 0.0
    assert stream.m_dot == 0.0


def test_gas_and_water_with_same_method_select_different_state_classes():
    definitions = {
        "gas": {
            "type": "GasState", "method": "from_Ph", "P": 101325, "h": None,
        },
        "water": {"method": "from_Ph", "P": 101325, "h": None},
    }

    streams = build_streams(["gas", "water"], definitions, {}, None)

    assert isinstance(streams["gas"], GasState)
    assert isinstance(streams["water"], WaterSteamState)


@pytest.mark.parametrize("unit", [1, 2])
@pytest.mark.parametrize("level", ["hp", "ip", "lp"])
def test_hrsg_assembles_without_unmeasured_internal_gas(unit, level):
    definitions = {}
    for system in ("condenser", "cooling", "heating", "st"):
        definitions.update(import_module(f"gard.systems.{system}").STREAM_DEFINITIONS)
    for boiler in (1, 2):
        for section in ("hp", "ip", "lp"):
            definitions.update(import_module(f"gard.systems.hrsg{boiler}_{section}").STREAM_DEFINITIONS)
    assert all(definition.get("type") != "GasState" for definition in definitions.values())
    row = {}
    for definition in definitions.values():
        for parameter in ("P", "T", "m_dot"):
            source = definition.get(parameter)
            if isinstance(source, str):
                row[source] = {"P": 101325, "T": 500, "m_dot": 2.0}[parameter]
    module = import_module(f"gard.systems.hrsg{unit}_{level}")
    row[f"{level}{unit}_pump1.power"] = 1000.0
    row[f"{level}{unit}_pump2.power"] = 2000.0
    reference = ReferenceEnv(298.15, 101325)
    inputs = module.prepare_system_inputs(row)
    model = build_system(
        f"hrsg{unit}_{level}", module.SYSTEM_DEFINITIONS, DEVICE_DEFINITIONS,
        STREAM_DEFINITIONS, inputs, reference,
    )
    exchangers = [device for device in model.devices if isinstance(device, GasWaterHeatExchanger)]

    assert exchangers
    for exchanger in exchangers:
        assert exchanger.gas_inlets == []
        assert exchanger.gas_outlets == []
        assert exchanger.water_inlets
        assert exchanger.water_outlets
        assert exchanger.water_inlets[0].ref is reference

    assert model.work == -3000.0
    assert model.name == f"hrsg{unit}_{level}"
    for exchanger in exchangers:
        assert exchanger.energy_balance() == pytest.approx(
            exchanger.energy_in - exchanger.energy_out
        )
