"""本系统流股定义；按需构建，输入使用 SI 单位。

给水泵入口直接采用对应低压汽包的饱和液水状态。
"""

STREAM_DEFINITIONS = {
    "1号炉中压给水泵入口母管": {
        "type": "WaterSteamState",
        "method": "from_Px",
        "P": "hrsg1.lp_drum_pressure",
        "x": 0.0,
        "m_dot": "hrsg1.ip_pump_in.m_dot"
    },
    "1号炉中压给水泵1入口": {
        "type": "WaterSteamState",
        "method": "from_Px",
        "P": "hrsg1.lp_drum_pressure",
        "x": 0.0,
        "m_dot": "hrsg1.ip_pump1_in.m_dot"
    },
    "1号炉中压给水泵2入口": {
        "type": "WaterSteamState",
        "method": "from_Px",
        "P": "hrsg1.lp_drum_pressure",
        "x": 0.0,
        "m_dot": "hrsg1.ip_pump2_in.m_dot"
    },
    "1号炉中压给水泵1出口": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.ip_pump1_out.P",
        "T": "hrsg1.ip_pump1_out.T",
        "m_dot": "hrsg1.ip_pump1_out.m_dot"
    },
    "1号炉中压给水泵2出口": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.ip_pump2_out.P",
        "T": "hrsg1.ip_pump2_out.T",
        "m_dot": "hrsg1.ip_pump2_out.m_dot"
    },
    "1号炉中压给水泵出口母管": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.ip_pump_out.P",
        "T": "hrsg1.ip_pump_out.T",
        "m_dot": "hrsg1.ip_pump_out.m_dot"
    },
    "1号炉中压给水": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.ip_feed.P",
        "T": "hrsg1.ip_feed.T",
        "m_dot": "hrsg1.ip_feed.m_dot"
    },
    "1号炉中压汽包入口": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.ip_drum_pressure",
        "T": "hrsg1.ip_to_drum.T",
        "m_dot": "hrsg1.ip_to_drum.m_dot"
    },
    "1号炉中压汽包饱和蒸汽": {
        "type": "WaterSteamState",
        "method": "from_Px",
        "P": "hrsg1.ip_drum_pressure",
        "x": 1.0,
        "m_dot": "hrsg1.ip_fresh.m_dot"
    },
    "1号炉中压新蒸汽": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.ip_fresh.P",
        "T": "hrsg1.ip_fresh.T",
        "m_dot": "hrsg1.ip_fresh.m_dot"
    },
    "1号炉冷再热蒸汽": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.cold_reheat.P",
        "T": "hrsg1.cold_reheat.T",
        "m_dot": "hrsg1.cold_reheat.m_dot"
    },
    "1号炉再热器入口混合蒸汽": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.reheat_mixed.P",
        "T": "hrsg1.reheat_mixed.T",
        "m_dot": "hrsg1.reheat_mixed.m_dot"
    },
    "1号炉再热减温水": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.rh_spray.P",
        "T": "hrsg1.rh_spray.T",
        "m_dot": "hrsg1.rh_spray.m_dot"
    },
    "1号炉再热减温后蒸汽": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.rh_after_spray.P",
        "T": "hrsg1.rh_after_spray.T",
        "m_dot": "hrsg1.rh_after_spray.m_dot"
    },
    "1号炉热再热蒸汽": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.hot_reheat.P",
        "T": "hrsg1.hot_reheat.T",
        "m_dot": "hrsg1.hot_reheat.m_dot"
    },
    "1号炉再热蒸汽至汽轮机": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.rh_to_st.P",
        "T": "hrsg1.rh_to_st.T",
        "m_dot": "hrsg1.hot_reheat.m_dot"
    },
    "1号炉再热减温前蒸汽": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "hrsg1.hot_reheat.P",
        "T": "hrsg1.rh_before_spray.T",
        "m_dot": "hrsg1.rh_before_spray.m_dot"
    }
}
