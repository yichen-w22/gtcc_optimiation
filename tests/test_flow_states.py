import pandas as pd

from gard.flow_states import pending_states
from gard.plant import build_streams_from_row
from src.working_fluid.steam_water import WaterSteamState


def test_chinese_measurement_columns_build_flat_states():
    row = {
        "低压汽包压力_1": 800_000.0,
        "低压给水流量_1": 10.0,
        "高压省煤器进水压力_1": 10_000_000.0,
        "高压省煤器进水温度_1": 400.0,
        "高压给水流量_1": 5.0,
        "高压主蒸汽压力_1": 9_000_000.0,
        "高压主蒸汽温度_1": 800.0,
        "高压主蒸汽流量_1": 4.0,
        "中压省煤器进水压力_1": 3_000_000.0,
        "中压省煤器进水温度_1": 400.0,
        "中压给水流量_1": 3.0,
        "低压省煤器进水压力_1": 1_000_000.0,
        "低压省煤器进水温度_1": 350.0,
        "低压省煤器进口流量_1": 12.0,
    }
    streams = build_streams_from_row(pd.DataFrame([row]))
    assert type(streams) is dict
    assert len(streams) == 221
    assert all(isinstance(s, WaterSteamState) for s in streams.values())
    assert streams["1号炉低压汽包"].x == 0.0
    assert streams["1号炉低压汽包"].m_dot is None
    assert streams["1号炉低压给水"].m_dot == 10.0
    assert streams["1号炉高压省煤器入口"].m_dot == 5.0
    assert streams["1号炉低压汽包高压给水泵后"].P is None
    assert streams["1号炉高压主蒸汽"].m_dot == 4.0
    assert "2号炉高压主蒸汽" in pending_states(streams)


def test_mass_balance_infers_only_unique_nonnegative_flow():
    row = {
        "hrsg1.hp_pump_in.m_dot": 10.0,
        "hrsg1.hp_pump1_in.m_dot": 4.0,
    }
    streams = build_streams_from_row(pd.DataFrame([row]))
    assert streams["1号炉高压给水泵2入口"].m_dot == 6.0
    assert streams["1号炉高压给水泵1出口"].m_dot == 4.0
    assert streams["1号炉低压汽包高压给水泵后"].m_dot == 10.0
    assert streams["1号炉高压主蒸汽"].m_dot is None


def test_saturated_pt_does_not_invent_steam_quality():
    pressure = 1_000_000.0
    temperature = WaterSteamState.from_Px(pressure, 0.0).T
    row = {
        "hrsg1.hp_main.P": pressure,
        "hrsg1.hp_main.T": temperature,
        "hrsg1.hp_main.m_dot": 2.0,
    }
    streams = build_streams_from_row(pd.DataFrame([row]))
    state = streams["1号炉高压主蒸汽"]
    assert state.h is None
    assert "phase / h / x" in pending_states(streams)[state.name]
