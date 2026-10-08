"""全场：创建系统流股、显式连接、组装并汇总。"""

from src.working_fluid.fluid import ReferenceEnv
from src.working_fluid.stream import StreamBook
from src.base.system import PlantBook
from gard.systems import (
    hrsg1_hp,
    hrsg1_ip,
    hrsg1_lp,
    hrsg2_hp,
    hrsg2_ip,
    hrsg2_lp,
    st,
    condenser,
    heating,
    cooling,
    auxiliary,
)


def build_ref_env_from_row(df, idx=0):
    row = df.iloc[idx]
    return ReferenceEnv(float(row.get("T0", 298.15)), float(row.get("P0", 101325.0)))


def build_stream_book_from_row(df, idx=0, ref_env=None):
    ref = ref_env or build_ref_env_from_row(df, idx)
    streams = StreamBook(df.iloc[idx], ref)
    streams.add_system("hrsg1_hp", hrsg1_hp.build_streams(df.iloc[idx], ref))
    streams.add_system("hrsg1_ip", hrsg1_ip.build_streams(df.iloc[idx], ref))
    streams.add_system("hrsg1_lp", hrsg1_lp.build_streams(df.iloc[idx], ref))
    streams.add_system("hrsg2_hp", hrsg2_hp.build_streams(df.iloc[idx], ref))
    streams.add_system("hrsg2_ip", hrsg2_ip.build_streams(df.iloc[idx], ref))
    streams.add_system("hrsg2_lp", hrsg2_lp.build_streams(df.iloc[idx], ref))
    streams.add_system("st", st.build_streams(df.iloc[idx], ref))
    streams.add_system("condenser", condenser.build_streams(df.iloc[idx], ref))
    streams.add_system("heating", heating.build_streams(df.iloc[idx], ref))
    streams.add_system("cooling", cooling.build_streams(df.iloc[idx], ref))
    streams.add_system("auxiliary", auxiliary.build_streams(df.iloc[idx], ref))
    return streams


def build_streams_from_row(df, idx=0, ref_env=None):
    """返回中文名称到 WaterSteamState 的扁平字典。

    未知的测点保留为 None；仅对明确的设备质量守恒关系反推唯一未知流量。
    现有核算所需的系统分组由 build_stream_book_from_row 保留。
    """
    import pandas as pd
    from gard.flow_states import build_named_states, normalize_chinese_columns

    row = normalize_chinese_columns(df.iloc[idx])
    book = build_stream_book_from_row(pd.DataFrame([row]), 0, ref_env)
    return build_named_states(book, row)


def connect_systems(streams):
    return {
        "hrsg1_hp": {},
        "hrsg1_ip": {
            "hrsg1.hp_bypass_out": streams.systems["hrsg1_hp"]["hrsg1.hp_bypass_out"]
        },
        "hrsg1_lp": {
            "hrsg1.hp_pump_return": streams.systems["hrsg1_hp"]["hrsg1.hp_pump_return"],
            "hrsg1.hp_pump_in": streams.systems["hrsg1_hp"]["hrsg1.hp_pump_in"],
            "hrsg1.ip_pump_in": streams.systems["hrsg1_ip"]["hrsg1.ip_pump_in"],
        },
        "hrsg2_hp": {},
        "hrsg2_ip": {
            "hrsg2.hp_bypass_out": streams.systems["hrsg2_hp"]["hrsg2.hp_bypass_out"]
        },
        "hrsg2_lp": {
            "hrsg2.hp_pump_return": streams.systems["hrsg2_hp"]["hrsg2.hp_pump_return"],
            "hrsg2.hp_pump_in": streams.systems["hrsg2_hp"]["hrsg2.hp_pump_in"],
            "hrsg2.ip_pump_in": streams.systems["hrsg2_ip"]["hrsg2.ip_pump_in"],
        },
        "st": {
            "hrsg1.hp_to_st": streams.systems["hrsg1_hp"]["hrsg1.hp_to_st"],
            "hrsg2.hp_to_st": streams.systems["hrsg2_hp"]["hrsg2.hp_to_st"],
            "hrsg1.cold_reheat": streams.systems["hrsg1_ip"]["hrsg1.cold_reheat"],
            "hrsg2.cold_reheat": streams.systems["hrsg2_ip"]["hrsg2.cold_reheat"],
            "hrsg1.rh_to_st": streams.systems["hrsg1_ip"]["hrsg1.rh_to_st"],
            "hrsg2.rh_to_st": streams.systems["hrsg2_ip"]["hrsg2.rh_to_st"],
            "hrsg1.lp_to_st": streams.systems["hrsg1_lp"]["hrsg1.lp_to_st"],
            "hrsg2.lp_to_st": streams.systems["hrsg2_lp"]["hrsg2.lp_to_st"],
        },
        "condenser": {
            "cooling.supply": streams.systems["cooling"]["cooling.supply"],
            "cooling.return": streams.systems["cooling"]["cooling.return"],
            "st.lp_out": streams.systems["st"]["st.lp_out"],
            "hrsg1.ip_bypass_to_condenser": streams.systems["hrsg1_ip"][
                "hrsg1.ip_bypass_to_condenser"
            ],
            "hrsg2.ip_bypass_to_condenser": streams.systems["hrsg2_ip"][
                "hrsg2.ip_bypass_to_condenser"
            ],
            "hrsg1.lp_bypass_out": streams.systems["hrsg1_lp"]["hrsg1.lp_bypass_out"],
            "hrsg2.lp_bypass_out": streams.systems["hrsg2_lp"]["hrsg2.lp_bypass_out"],
            "hrsg1.ip_bypass_spray": streams.systems["hrsg1_ip"][
                "hrsg1.ip_bypass_spray"
            ],
            "hrsg2.ip_bypass_spray": streams.systems["hrsg2_ip"][
                "hrsg2.ip_bypass_spray"
            ],
            "hrsg1.lp_bypass_spray": streams.systems["hrsg1_lp"][
                "hrsg1.lp_bypass_spray"
            ],
            "hrsg2.lp_bypass_spray": streams.systems["hrsg2_lp"][
                "hrsg2.lp_bypass_spray"
            ],
            "heat.drain_return": streams.systems["heating"]["heat.drain_return"],
            "aux.gland_exhaust": streams.systems["auxiliary"]["aux.gland_exhaust"],
            "aux.gland_drain": streams.systems["auxiliary"]["aux.gland_drain"],
            "hrsg1.lp_feed": streams.systems["hrsg1_lp"]["hrsg1.lp_feed"],
            "hrsg2.lp_feed": streams.systems["hrsg2_lp"]["hrsg2.lp_feed"],
        },
        "heating": {
            "st.heat_extraction": streams.systems["st"]["st.heat_extraction"],
            "hrsg1.lp_to_heat": streams.systems["hrsg1_lp"]["hrsg1.lp_to_heat"],
            "hrsg2.lp_to_heat": streams.systems["hrsg2_lp"]["hrsg2.lp_to_heat"],
            "hrsg1.ip_bypass_to_heat": streams.systems["hrsg1_ip"][
                "hrsg1.ip_bypass_to_heat"
            ],
            "hrsg2.ip_bypass_to_heat": streams.systems["hrsg2_ip"][
                "hrsg2.ip_bypass_to_heat"
            ],
            "hrsg1.lp_to_heat_recovery": streams.systems["hrsg1_lp"][
                "hrsg1.lp_to_heat_recovery"
            ],
            "hrsg1.lp_from_heat_recovery": streams.systems["hrsg1_lp"][
                "hrsg1.lp_from_heat_recovery"
            ],
            "hrsg2.lp_to_heat_recovery": streams.systems["hrsg2_lp"][
                "hrsg2.lp_to_heat_recovery"
            ],
            "hrsg2.lp_from_heat_recovery": streams.systems["hrsg2_lp"][
                "hrsg2.lp_from_heat_recovery"
            ],
        },
        "cooling": {},
        "auxiliary": {
            "st.gland_leakage": streams.systems["st"]["st.gland_leakage"],
            "st.ip_leakage": streams.systems["st"]["st.ip_leakage"],
            "hrsg1.hp_drum_drain": streams.systems["hrsg1_hp"]["hrsg1.hp_drum_drain"],
            "hrsg2.hp_drum_drain": streams.systems["hrsg2_hp"]["hrsg2.hp_drum_drain"],
            "hrsg1.ip_drum_drain": streams.systems["hrsg1_ip"]["hrsg1.ip_drum_drain"],
            "hrsg2.ip_drum_drain": streams.systems["hrsg2_ip"]["hrsg2.ip_drum_drain"],
            "hrsg1.lp_drum_drain": streams.systems["hrsg1_lp"]["hrsg1.lp_drum_drain"],
            "hrsg2.lp_drum_drain": streams.systems["hrsg2_lp"]["hrsg2.lp_drum_drain"],
            "cond.drains": streams.systems["condenser"]["cond.drains"],
        },
    }


def build_plant_from_streams(s, row):
    ports = connect_systems(s)
    model = PlantBook(row)
    model.add_system(
        hrsg1_hp.build_system(row, s.systems["hrsg1_hp"], ports["hrsg1_hp"])
    )
    model.add_system(
        hrsg1_ip.build_system(row, s.systems["hrsg1_ip"], ports["hrsg1_ip"])
    )
    model.add_system(
        hrsg1_lp.build_system(row, s.systems["hrsg1_lp"], ports["hrsg1_lp"])
    )
    model.add_system(
        hrsg2_hp.build_system(row, s.systems["hrsg2_hp"], ports["hrsg2_hp"])
    )
    model.add_system(
        hrsg2_ip.build_system(row, s.systems["hrsg2_ip"], ports["hrsg2_ip"])
    )
    model.add_system(
        hrsg2_lp.build_system(row, s.systems["hrsg2_lp"], ports["hrsg2_lp"])
    )
    model.add_system(st.build_system(row, s.systems["st"], ports["st"]))
    model.add_system(
        condenser.build_system(row, s.systems["condenser"], ports["condenser"])
    )
    model.add_system(heating.build_system(row, s.systems["heating"], ports["heating"]))
    model.add_system(cooling.build_system(row, s.systems["cooling"], ports["cooling"]))
    model.add_system(
        auxiliary.build_system(row, s.systems["auxiliary"], ports["auxiliary"])
    )
    return model
