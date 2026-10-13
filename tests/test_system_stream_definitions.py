from importlib import import_module

import pytest

from src.base.stream import ReferenceEnv
from src.working_fluid.steam_water import WaterSteamState
from src.base.stream_builder import build_stream, build_streams


SYSTEMS = [
    "gt1",
    "gt2",
    "condenser",
    "cooling",
    "heating",
    "hrsg1_hp",
    "hrsg1_ip",
    "hrsg1_lp",
    "hrsg2_hp",
    "hrsg2_ip",
    "hrsg2_lp",
    "st",
]


@pytest.mark.parametrize("system_name", SYSTEMS)
def test_each_system_supports_selected_streams_by_name(system_name):
    module = import_module(f"gard.systems.{system_name}.streams")
    definitions = module.STREAM_DEFINITIONS.copy()
    names = list(definitions)
    selected = [names[-1], names[0]]
    row = {}
    for definition in definitions.values():
        for parameter in ("P", "T", "m_dot"):
            source = definition.get(parameter)
            if isinstance(source, str):
                row[source] = {"P": 2e6, "T": 500, "m_dot": 2.0}[parameter]
        if definition.get("type") == "GasState":
            row[definition["composition"]] = {
                "N2": 0.75, "O2": 0.10, "CO2": 0.05, "H2O": 0.10,
            }
    definitions["unused"] = {"method": "unsupported"}
    reference = ReferenceEnv(T0=298.15, P0=101325)

    streams = build_streams(selected, definitions, row, reference)

    assert list(streams) == selected
    for name in selected:
        assert streams[name].name == name
        assert streams[name].ref is reference
        assert streams[name].h is not None
        assert streams[name].m_dot == 2.0
    assert build_streams([], definitions, row, reference) == {}


@pytest.mark.parametrize("unit", [1, 2])
@pytest.mark.parametrize("level, label, quality", [
    ("hp", "高压汽包饱和蒸汽", 1.0),
    ("ip", "中压汽包饱和蒸汽", 1.0),
    ("lp", "低压汽包饱和蒸汽", 1.0),
    ("lp", "低压汽包水", 0.0),
])
def test_drum_steam_and_water_use_correct_saturated_phase(unit, level, label, quality):
    module = import_module(f"gard.systems.hrsg{unit}_{level}.streams")
    name = f"{unit}号炉{label}"
    row = {f"hrsg{unit}.{level}_drum_pressure": 2e6}

    stream = build_stream(name, module.STREAM_DEFINITIONS, row, None)
    expected = WaterSteamState.from_Px(P=2e6, x=quality)

    assert stream.P == 2e6
    assert stream.x == quality
    assert stream.T == pytest.approx(expected.T)
    assert stream.h == pytest.approx(expected.h)
    assert stream.s == pytest.approx(expected.s)
