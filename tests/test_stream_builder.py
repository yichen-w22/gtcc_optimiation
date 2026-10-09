from copy import deepcopy

import pytest

from gard.systems.hrsg1_hp.streams import STREAM_DEFINITIONS
from src.base.stream import ReferenceEnv
from src.working_fluid.steam_water import WaterSteamState
from src.base.stream_builder import build_stream


@pytest.mark.parametrize("method, parameter", [
    ("from_PT", "T"),
    ("from_Px", "x"),
    ("from_Ph", "h"),
    ("from_Ps", "s"),
])
def test_build_single_stream_with_each_state_pair(method, parameter):
    reference = ReferenceEnv(T0=298.15, P0=101325)
    expected = WaterSteamState.from_Px(P=2e6, x=0.5)
    if method != "from_Px":
        expected = WaterSteamState.from_PT(P=2e6, T=500)
    definitions = {
        "selected": {
            "method": method,
            "P": "selected.P",
            parameter: "selected.state",
            "m_dot": 2.0,
        },
        "unused": {"method": "unsupported"},
    }
    row = {"selected.P": expected.P, "selected.state": getattr(expected, parameter)}
    original_definitions = deepcopy(definitions)
    original_row = row.copy()

    stream = build_stream("selected", definitions, row, reference)

    assert stream.name == "selected"
    assert stream.ref is reference
    assert stream.P == pytest.approx(expected.P)
    assert stream.h == pytest.approx(expected.h, rel=1e-5)
    assert stream.s == pytest.approx(expected.s, rel=1e-5)
    assert stream.m_dot == 2.0
    assert definitions == original_definitions
    assert row == original_row


def test_hp_pump_return_missing_measurements_and_zero_flow():
    stream = build_stream(
        "1号炉高压给水泵回流",
        STREAM_DEFINITIONS,
        {"hrsg1.hp_pump_return.m_dot": 0.0},
        None,
    )

    assert stream.P is None
    assert stream.T is None
    assert stream.h is None
    assert stream.m_dot == 0.0


def test_hp_drum_steam_uses_drum_pressure_and_saturated_vapor():
    stream = build_stream(
        "1号炉高压汽包饱和蒸汽",
        STREAM_DEFINITIONS,
        {"hrsg1.hp_drum_pressure": 10e6},
        None,
    )
    expected = WaterSteamState.from_Px(P=10e6, x=1.0)

    assert stream.x == 1.0
    assert stream.T == pytest.approx(expected.T)
    assert stream.h == pytest.approx(expected.h)
