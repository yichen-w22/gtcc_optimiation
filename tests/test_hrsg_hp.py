"""Behavioral coverage of the confirmed HP circuits; independent of plant registries."""
from copy import deepcopy
from importlib import import_module

import pandas as pd
import pytest

from gard.config import reference_environment
from gard.data_io import load_inputs, prepare_inputs, summarize_history
from gard.systems import build_system
from gard.systems.hrsg_hp import HPPreparationConfig, prepare_hp_inputs, qualify_current_history
from src.ST_model.pump import Pump
from src.working_fluid.steam_water import WaterSteamState


def inputs(unit, currents=(30, 0)):
    p = f"hrsg{unit}"
    return {f"{p}.{key}": value for key, value in {
        "lp_drum_pressure": 0.5e6, "hp_pump1.current": currents[0], "hp_pump2.current": currents[1],
        "hp_pump1_out.P": 12e6, "hp_pump2_out.P": 12.5e6,
        "hp_feed.P": 11.5e6, "hp_feed.T": 430, "hp_feed.m_dot": 95,
        "hp_to_drum.T": 560, "hp_drum_pressure": 11e6,
        "hp_before_spray.T": 790, "hp_after_spray.T": 760,
        "hp_main.P": 10e6, "hp_main.T": 810, "hp_main.m_dot": 100,
        "hp_to_st.P": 9.8e6, "hp_to_st.T": 805,
    }.items()}


@pytest.mark.parametrize("unit", [1, 2])
@pytest.mark.parametrize("active", [1, 2])
def test_exclusive_pump_thermodynamics_and_topology(unit, active):
    row = inputs(unit, (30, -0.5) if active == 1 else (0.5, 40))
    original = deepcopy(row)
    system = build_system(f"hrsg{unit}_hp", row)
    p = system.preparation
    prefix = f"hrsg{unit}"
    assert row == original and p.active_pump == active
    assert len(system.devices) == 10
    assert not any("filter" in d.name or "bypass" in d.name for d in system.devices)
    inlet = p.states[f"{unit}号炉高压给水泵{active}入口"]
    outlet = p.states[f"{unit}号炉高压给水泵{active}出口"]
    assert inlet.P == 0.5e6 and inlet.x == 0 and inlet.m_dot == 100
    assert outlet.P == row[f"{prefix}.hp_pump{active}_out.P"]
    assert outlet.s == pytest.approx(inlet.s, abs=1e-5)
    assert outlet.T > inlet.T and outlet.h > inlet.h
    assert p.row[f"{prefix}.hp_pump{3-active}_out.m_dot"] == 0
    assert p.row[f"{prefix}.hp_spray.m_dot"] == 5
    assert p.row[f"{prefix}.hp_spray.h"] == pytest.approx(outlet.h)
    assert p.row[f"{prefix}.hp_spray.P"] == outlet.P
    assert p.row[f"{prefix}.hp_to_drum.P"] == row[f"{prefix}.hp_drum_pressure"]
    assert p.row[f"{prefix}.hp_before_spray.P"] == row[f"{prefix}.hp_main.P"]
    assert system.mass_balance() == pytest.approx(0)
    assert system.energy_balance() == pytest.approx(0, abs=1e-6)
    assert system.exergy_balance() is None and system.electrical_power_input is None
    pump = system.device[f"hp{unit}_pump{active}"]
    assert pump.power_input == pytest.approx(p.modeled_pump_power)
    assert pump.isentropic_efficiency == pytest.approx(1)
    assert system.device[f"hp{unit}_pump{3-active}"].isentropic_efficiency is None


@pytest.mark.parametrize("unit", [1, 2])
@pytest.mark.parametrize("currents,status,active", [
    ((40, None), "pump1_assumed_standby", 1), ((None, 40), "pump2_assumed_standby", 2),
    ((0.5, None), "pump2_assumed_running", 2), ((None, -0.5), "pump1_assumed_running", 1),
    ((40, 40), "both_running", None), ((0.5, -0.5), "stopped", None),
    ((None, None), "unknown", None),
])
def test_operation_inference_and_refusal(unit, currents, status, active):
    p = prepare_hp_inputs(unit, inputs(unit, currents))
    assert (p.operation_status, p.active_pump) == (status, active)
    for j in (1, 2):
        assert p.row[f"hrsg{unit}.hp_pump{j}_in.m_dot"] == (None if active is None else 100 if j == active else 0)
    if "assumed" in status:
        assert "pump_selection_uses_exclusive_duty_assumption" in p.issues
    if active is None:
        assert p.modeled_pump_power is None
        assert build_system(f"hrsg{unit}_hp", inputs(unit, currents)).mass_balance() is None


@pytest.mark.parametrize("unit", [1, 2])
@pytest.mark.parametrize("missing", ["lp_drum_pressure", "hp_pump1_out.P", "hp_main.m_dot", "hp_feed.T", "hp_main.T"])
def test_missing_measurements_do_not_crash_or_invent_complete_balances(unit, missing):
    row = inputs(unit)
    del row[f"hrsg{unit}.{missing}"]
    system = build_system(f"hrsg{unit}_hp", row)
    assert system.preparation.issues
    assert system.energy_balance() is None
    assert system.exergy_balance() is None


@pytest.mark.parametrize("unit", [1, 2])
@pytest.mark.parametrize("currents", [(0, 0), (40, 0), (0, 40)])
def test_zero_flow(unit, currents):
    row = inputs(unit, currents)
    row.update({f"hrsg{unit}.hp_main.m_dot": 0, f"hrsg{unit}.hp_feed.m_dot": 0})
    system = build_system(f"hrsg{unit}_hp", row)
    assert system.preparation.modeled_pump_power == 0
    assert system.mass_balance() == 0 and system.energy_balance() == 0
    for j in (1, 2):
        pump = system.device[f"hp{unit}_pump{j}"]
        assert pump.power_input == 0 and pump.isentropic_efficiency is None


@pytest.mark.parametrize("unit", [1, 2])
def test_negative_spray_and_stale_derived_fields(unit):
    prefix = f"hrsg{unit}"
    row = inputs(unit)
    row.update({f"{prefix}.hp_feed.m_dot": 110, f"{prefix}.hp_spray.m_dot": 123,
                f"{prefix}.hp_pump1_in.m_dot": 44, f"{prefix}.hp_spray.T": 999,
                f"{prefix}.hp_before_spray.P": 2e6, f"{prefix}.hp_operation_status": "pump2"})
    system = build_system(f"{prefix}_hp", row)
    assert system.preparation.active_pump == 1
    assert system.preparation.row[f"{prefix}.hp_spray.m_dot"] is None
    assert system.preparation.row[f"{prefix}.hp_pump1_in.m_dot"] == 100
    assert system.preparation.row[f"{prefix}.hp_spray.T"] != 999
    assert system.mass_balance() is None and system.energy_balance() is None
    assert system.heat is None


@pytest.mark.parametrize("unit", [1, 2])
@pytest.mark.parametrize("active", [1, 2])
def test_efficiency_current_independence_and_repreparation(unit, active):
    row = inputs(unit, (30,0) if active == 1 else (0,30))
    ideal = prepare_hp_inputs(unit, row)
    config = HPPreparationConfig(pump_efficiencies=(0.8, 0.75), attemperator_pressure_drop=20000)
    system = build_system(f"hrsg{unit}_hp", row, config=config)
    p = system.preparation
    eta = config.pump_efficiencies[active-1]
    assert p.modeled_pump_power == pytest.approx(ideal.ideal_pump_power / eta)
    assert system.device[f"hp{unit}_pump{active}"].isentropic_efficiency == pytest.approx(eta, rel=1e-5)
    assert p.row[f"hrsg{unit}.hp_before_spray.P"] == 10e6 + 20000
    row[f"hrsg{unit}.hp_pump{active}.current"] = 70
    assert prepare_hp_inputs(unit, row, config=config).modeled_pump_power == p.modeled_pump_power
    rebuilt = prepare_hp_inputs(unit, ideal.row, config=config)
    assert rebuilt.modeled_pump_power == p.modeled_pump_power
    assert rebuilt.row[f"hrsg{unit}_hp.work"] == -p.modeled_pump_power
    assert rebuilt.work_basis == "declared_pump_model"
    assert ideal.raw_inputs == inputs(unit, (30,0) if active == 1 else (0,30))


def test_boundary_work_heat_and_heat_exergy_are_independent():
    row = inputs(1)
    row.update({"hrsg1_hp.work": -2e6, "hrsg1_hp.heat": 2.5e8})
    system = build_system("hrsg1_hp", row)
    p = system.preparation
    assert p.work_basis == "explicit_boundary_work"
    assert system.work == -2e6 and system.heat == 2.5e8
    assert system.energy_balance() != 0 and system.exergy_balance() is None
    row["hrsg1_hp.heat_exergy"] = 1.5e8
    system = build_system("hrsg1_hp", row)
    inlet = system.preparation.states["1号炉高压给水泵入口母管"]
    outlet = system.preparation.states["1号炉高压主蒸汽"]
    expected = 100*(inlet.exergy-outlet.exergy) + 1.5e8 + 2e6
    assert system.exergy_balance() == pytest.approx(expected)


def current_history(values1, values2=None):
    start = pd.Timestamp("2026-10-01 08:00:00", tz="Asia/Shanghai")
    end = start + pd.Timedelta(minutes=30)
    times = pd.date_range(start, end, freq="30s", inclusive="left")
    frames = [pd.DataFrame({"time": times, "code": "c1", "value": values1})]
    if values2 is not None:
        frames.append(pd.DataFrame({"time": times, "code": "c2", "value": values2}))
    return pd.concat(frames), start, end


@pytest.mark.parametrize("values1,values2,expected", [
    ([40]*30+[0]*30, [0]*30+[40]*30, "unstable"),
    ([40]*30+[0]*30, None, "unstable"),
    (40, 0, "pump1"), (0, 40, "pump2"),
    (40, None, "pump1_assumed_standby"), (-0.5, None, "pump2_assumed_running"),
    (40, 40, "both_running"), (float("nan"), None, "unknown"),
    ([40]*10+[float("nan")]*50, 0, "unknown"),
])
def test_raw_current_history_rejects_switching_gaps_and_missing(values1, values2, expected):
    raw, start, end = current_history(values1, values2)
    assert qualify_current_history(raw, start, end, ("c1", "c2"), 100) == expected
    if expected == "unstable":
        assert summarize_history(raw, start, end)["c1"] == 20  # Average hides a switch.


@pytest.mark.parametrize("unit", [1, 2])
def test_load_inputs_uses_raw_history_not_average_and_preserves_missing_pump2(tmp_path, unit):
    bindings = import_module(f"gard.systems.hrsg{unit}_hp.data").POINT_BINDINGS
    c1 = bindings.set_index("field").loc[f"hrsg{unit}.hp_pump1.current", "code"]
    raw, start, end = current_history([40]*30+[0]*30)
    pd.DataFrame({"tbname": c1, "ts": raw.time.array.asi8, "col0": raw.value}).to_parquet(tmp_path/f"pump+{c1}.parquet")
    row = load_inputs(f"hrsg{unit}_hp", tmp_path, start, end)
    assert row[f"hrsg{unit}.hp_pump1.current"] == 20
    assert row[f"hrsg{unit}.hp_pump2.current"] is None
    assert row[f"hrsg{unit}.hp_operation_status"] == "unstable"
    assert prepare_hp_inputs(unit, row).active_pump is None


def test_confirmed_point_sources_override_and_reference_pressure():
    code = "GARD_12HBK11WP021BT02XQ01"
    row = prepare_inputs("hrsg2_hp", {code: 500, "GARD_12HAG11CM001BP02XQ01": 0.5})
    assert row["hrsg2.hp_before_spray.T"] == 773.15
    assert row["hrsg2.lp_drum_pressure"] == 0.5e6
    assert reference_environment().P0 == 101375
    assert reference_environment(P0=100000).P0 == 100000
    b = import_module("gard.systems.hrsg1_hp.data").POINT_BINDINGS
    assert b.set_index("field").loc["hrsg1.lp_drum_pressure", "code"] == "GARD_11HBK11CM001BP02XQ01"


def test_disabled_inference_and_config_validation():
    config = HPPreparationConfig(allow_single_current_inference=False)
    assert prepare_hp_inputs(1, inputs(1, (40, None)), config=config).active_pump is None
    for kwargs in ({"pump_efficiencies": (0, 1)}, {"current_threshold_A": -1}, {"attemperator_pressure_drop": -1}):
        with pytest.raises(ValueError):
            HPPreparationConfig(**kwargs)
    inlet = WaterSteamState(m_dot=None)
    outlet = WaterSteamState(m_dot=None)
    pump = Pump("missing", inlets=[inlet], outlets=[outlet])
    assert pump.specific_work is None and pump.power_input is None and pump.isentropic_efficiency is None


def test_current_threshold_is_configurable_and_stop_noise_is_not_running():
    row = inputs(1, (1, -0.5))
    assert prepare_hp_inputs(1, row).operation_status == 'stopped'
    assert prepare_hp_inputs(1, row, config=HPPreparationConfig(current_threshold_A=0.9)).active_pump == 1


@pytest.mark.parametrize('unit', [1, 2])
def test_active_graph_ports_match_authoritative_topology(unit):
    import re
    from pathlib import Path
    path = Path(__file__).resolve().parents[1]/f'gard/systems/hrsg{unit}_hp/topology.md'
    edges = re.findall(r'^\s+(\w+) -->\|([^|]+)\| (\w+)$', path.read_text(encoding='utf-8'), re.M)
    definitions = import_module(f'gard.systems.hrsg{unit}_hp.devices').DEVICE_DEFINITIONS
    for source, stream, target in edges:
        if source in definitions:
            d = definitions[source]
            assert stream in d.get('outlets', []) + d.get('water_outlets', [])
        if target in definitions:
            d = definitions[target]
            assert stream in d.get('inlets', []) + d.get('water_inlets', [])
    graph_streams = {e[1] for e in edges}
    device_streams = {s for d in definitions.values() for key, values in d.items() if key != 'type' for s in values}
    assert device_streams == graph_streams


def test_history_operation_config_is_carried_and_cannot_be_silently_reinterpreted(tmp_path):
    bindings = import_module('gard.systems.hrsg1_hp.data').POINT_BINDINGS
    codes = bindings.set_index('field').code
    raw, start, end = current_history(0.8, 0)
    for field, channel in [('hrsg1.hp_pump1.current','c1'), ('hrsg1.hp_pump2.current','c2')]:
        frame = raw[raw.code == channel]
        pd.DataFrame({'tbname':codes[field], 'ts':frame.time.array.asi8, 'col0':frame.value}).to_parquet(tmp_path/f'current+{codes[field]}.parquet')
    config = HPPreparationConfig(current_threshold_A=0.7)
    loaded = load_inputs('hrsg1_hp', tmp_path, start, end, hp_config=config)
    row = {**inputs(1), **loaded}
    assert build_system('hrsg1_hp', row).preparation.active_pump == 1
    p = build_system('hrsg1_hp', row, config=HPPreparationConfig()).preparation
    assert p.active_pump is None
    assert 'operation_config_changed_reload_raw_history' in p.issues
