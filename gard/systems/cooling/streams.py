"""本系统流股定义；按需构建，输入使用 SI 单位。"""

STREAM_DEFINITIONS = {
    "冷却水供水": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "cooling.supply.P",
        "T": "cooling.supply.T",
        "m_dot": "cooling.supply.m_dot",
    },
    "冷却水回水": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "cooling.return.P",
        "T": "cooling.return.T",
        "m_dot": "cooling.return.m_dot",
    },
    "冷却水外部入口": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "cooling.external_in.P",
        "T": "cooling.external_in.T",
        "m_dot": "cooling.external_in.m_dot",
    },
    "冷却水外部出口": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "cooling.external_out.P",
        "T": "cooling.external_out.T",
        "m_dot": "cooling.external_out.m_dot",
    },
}
