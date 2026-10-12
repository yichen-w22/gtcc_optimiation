import pandas as pd
import pytest

from src.base import Device, FlowState, Plant, ReferenceEnv, System
from src.GT_model.GT_model import GTModel
from src.ST_model.heat_exchanger import GasWaterHeatExchanger
from src.ST_model.pump import Pump
from src.working_fluid.gas import GasComposition, GasState
from src.working_fluid.steam_water import WaterSteamState, infer_m2_by_enthalpy_balance


def test_heat_exchanger_stored_sides_and_live_totals():
    gas_in = GasState(name="gas_in", m_dot=2, h=100)
    gas_out = GasState(name="gas_out", m_dot=2, h=80)
    water_in = WaterSteamState(name="water_in", m_dot=1, h=10)
    water_out = WaterSteamState(name="water_out", m_dot=1, h=50)
    hx = GasWaterHeatExchanger(
        "hx",
        gas_inlets=[gas_in],
        gas_outlets=[gas_out],
        water_inlets=[water_in],
        water_outlets=[water_out],
    )
    assert hx.mass_in == hx.mass_out == 3
    assert hx.energy_balance() == 0
    assert hx.energy_balance_ratio == 1
    water_in.m_dot = 2
    assert hx.mass_in == 4
    hx.water_inlets.append(WaterSteamState(m_dot=3, h=4))
    assert hx.mass_in == 7
    assert hx.energy_in == 232
    hx.add_gas_inlet(GasState(m_dot=1, h=5))
    assert hx.mass_in == 8
    assert not hx.inlets  # No duplicate storage in the general device list.
    gas_out.h = 100
    assert hx.energy_balance_ratio != 1


def test_pump_and_turbine_use_list_ports():
    from src.ST_model.turbine import Turbine

    ref = ReferenceEnv(298.15, 101325)
    a = WaterSteamState.from_PT(1e6, 350, m_dot=2, ref=ref)
    b = WaterSteamState.from_PT(2e6, 352, m_dot=2, ref=ref)
    pump = Pump("pump", [a], [b])
    assert pump.specific_work == pytest.approx(b.h - a.h)
    assert pump.power_input == pytest.approx(2 * (b.h - a.h))
    assert pump.isentropic_efficiency == pytest.approx((pump.outlet_s.h - a.h) / (b.h - a.h))

    c = WaterSteamState.from_PT(2e6, 700, m_dot=2, ref=ref)
    d = WaterSteamState.from_PT(1e6, 600, m_dot=2, ref=ref)
    turbine = Turbine("turbine", [c], [d])
    assert turbine.power_output == pytest.approx(2 * (c.h - d.h))
    assert turbine.isentropic_efficiency == pytest.approx((c.h - d.h) / (c.h - turbine.outlet_s.h))

def test_control_volume_heat_and_work_and_internal_cancellation():
    inlet = FlowState(name="in", m_dot=1, h=100)
    internal = FlowState(name="internal", m_dot=1, h=90)
    outlet = FlowState(name="out", m_dot=1, h=80)
    first = Device("first", [inlet], [internal])
    second = Device("second", [internal], [outlet])
    assert first.energy_balance() == 10
    system = System("system", [first, second], heat=5, work=25)
    assert system.mass_balance() == 0
    assert system.energy_balance() == 0
    a = System("a", [first], heat=5, work=10)
    b = System("b", [second], work=15)
    plant = Plant("plant", [a, b])
    assert plant.work == 25
    assert plant.heat == 5
    assert plant.energy_balance() == 0
    a.heat = 6
    assert plant.energy_balance() == 1

def test_exergy_work_sign_and_reference_mutation():
    ref = ReferenceEnv(298.15, 101325)
    a = WaterSteamState.from_PT(2e6, 700, m_dot=2, ref=ref)
    b = WaterSteamState.from_PT(1e6, 600, m_dot=2, ref=ref)
    device = Device("t", [a], [b])
    system = System("turbine", [device], work=1000, heat_exergy=200)
    expected = a.exergy_flow - b.exergy_flow - 800
    assert system.exergy_balance() == pytest.approx(expected)
    plant = Plant("plant", [system])
    assert plant.exergy_balance() == pytest.approx(expected)
    assert plant.heat_exergy == 200
    old = a.exergy
    a.ref = ReferenceEnv(310, 101325)
    assert a.exergy != old

def test_heat_exchanger_counts_general_outlet_with_water_side():
    inlet = WaterSteamState(m_dot=3, h=100)
    steam = WaterSteamState(m_dot=2, h=200)
    blowdown = WaterSteamState(m_dot=1, h=120)
    exchanger = GasWaterHeatExchanger("drum", water_inlets=[inlet], water_outlets=[steam])
    exchanger.add_outlet(blowdown)
    assert exchanger.mass_balance() == 0
    assert exchanger.energy_out == 520
    assert exchanger.energy_balance() == -220

def test_gt_connected_graph_and_formulas_follow_updated_inputs():
    ref = ReferenceEnv(298.15, 101325)
    air = GasComposition(N2=0.79, O2=0.21)
    flue = GasComposition(N2=0.75, O2=0.1, CO2=0.05, H2O=0.1)
    inlet = GasState.from_TP(
        300, 101325, m_dot=100, composition=air, ref=ref, name="air"
    )
    compressed = GasState.from_TP(650, 1.5e6, m_dot=100, composition=air, ref=ref)
    fuel = GasState.from_TP(
        300, 1.6e6, m_dot=2, composition=GasComposition(CH4=1), ref=ref, name="fuel"
    )
    exhaust = GasState.from_TP(
        800, 101325, m_dot=102, composition=flue, ref=ref, name="exhaust"
    )
    gt = GTModel(inlet, compressed, fuel, exhaust, total_pressure_recovery=0.95)
    assert gt.state_3.P == pytest.approx(0.95 * compressed.P)
    gt.total_pressure_recovery = 0.9
    assert gt.state_3.P == pytest.approx(0.9 * compressed.P)
    gt.total_pressure_recovery = 0.95
    assert isinstance(gt, System)
    assert all(isinstance(d, Device) for d in gt.devices)
    compressor = gt.compressor
    assert compressor.state_2.m_dot == 85
    assert compressor.bleeding.m_dot == 15
    assert compressor.bleeding.P == pytest.approx(101325 + 0.9 * (1.5e6 - 101325))
    assert compressor.isentropic_efficiency == pytest.approx(
        (compressor.state_2s.h - inlet.h) / (compressed.h - inlet.h)
    )
    assert gt.mass_balance() == pytest.approx(0)
    # GasState.from_Ph 的焓反求采用 1e-6 相对精度。
    assert gt.energy_balance() == pytest.approx(0, abs=1e-6 * gt.chamber.released_heat)
    gt.fuel_chemical_exergy = 55e6
    assert gt.exergy_balance() == pytest.approx(
        inlet.exergy_flow + fuel.exergy_flow + 55e6 * fuel.m_dot
        - exhaust.exergy_flow - gt.work
    )
    gt.actual_power = 30e6
    assert gt.energy_balance() == pytest.approx(
        inlet.energy_flow + fuel.energy_flow + gt.chamber.released_heat
        - exhaust.energy_flow - 30e6
    )
    power = gt.net_power
    inlet.m_dot = 120
    exhaust.m_dot = 122
    assert gt.state_2.m_dot == 102
    assert gt.mass_balance() == pytest.approx(0)
    assert gt.net_power != power
    gt.config.compressor_bleeding_mass_fraction = 0
    assert gt.mass_balance() == pytest.approx(0)
    assert gt.chamber.state_3_c.m_dot == 122


def test_mixing_flow_closes_independent_energy_balance():
    P, T1, T2, T3 = 1e6, 400, 300, 350
    m2, m3 = infer_m2_by_enthalpy_balance(2, T1, P, T2, P, T3, P, q_dot=1000)
    h1, h2, h3 = [WaterSteamState.from_PT(P, T).h for T in (T1, T2, T3)]
    assert m3 == pytest.approx(2 + m2)
    assert 2 * h1 + m2 * h2 + 1000 == pytest.approx(m3 * h3)


def test_gard_partial_input_and_hrsg_device_sides():
    gard = pytest.importorskip("gard")
    if not hasattr(gard, "compute_si"):
        pytest.skip("Legacy gard.compute_si API has been removed")
    from gard import compute_si
    from gard.plant import build_stream_groups_from_row, build_plant_from_streams

    result = compute_si({})
    assert len(result["systems"]) == 10
    assert len(result["components"]) == 148
    assert result["plant"]["status"] == "partial"
    assert result["plant"]["net_power"] is None
    assert len({s["name"] for s in result["streams"]}) == len(result["streams"])
    assert all("?" not in s["name"] for s in result["streams"])
    boundaries = {s["name"]: s["direction"] for s in result["external_boundaries"]}
    assert boundaries["汽轮机轴封漏汽"] == "out"
    assert boundaries["汽轮机中压缸漏汽"] == "out"
    assert boundaries["1号炉高压汽包排污"] == "out"
    assert boundaries["凝结水系统疏水汇集"] == "in"
    assert boundaries["凝结水系统轴封加热器汽侧入口"] == "in"
    assert boundaries["凝结水系统轴封加热器疏水出口"] == "out"
    groups = build_stream_groups_from_row(pd.DataFrame([{}]))
    plant = build_plant_from_streams(groups, {})
    exchanger = next(
        d for d in plant.systems[0].devices if isinstance(d, GasWaterHeatExchanger)
    )
    assert isinstance(exchanger.gas_inlets[0], GasState)
    assert isinstance(exchanger.water_inlets[0], WaterSteamState)
    assert exchanger.gas_energy_release is None
