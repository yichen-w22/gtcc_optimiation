"""本系统流股定义；按需构建，输入使用 SI 单位。"""

STREAM_DEFINITIONS = {
    "热网低压补汽母管": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "heat.lp_steam_header.P",
        "T": "heat.lp_steam_header.T",
        "m_dot": "heat.lp_steam_header.m_dot",
    },
    "供热系统疏水返回": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "heat.drain_return.P",
        "T": "heat.drain_return.T",
        "m_dot": "heat.drain_return.m_dot",
    },
    "供热系统回水": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "heat.return_water.P",
        "T": "heat.return_water.T",
        "m_dot": "heat.return_water.m_dot",
    },
    "供热系统供水": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "heat.supply_water.P",
        "T": "heat.supply_water.T",
        "m_dot": "heat.supply_water.m_dot",
    },
    "供热系统蒸汽母管": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "heat.steam_header.P",
        "T": "heat.steam_header.T",
        "m_dot": "heat.steam_header.m_dot",
    },
    "供热系统疏水泵前": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "heat.drain_before_pump.P",
        "T": "heat.drain_before_pump.T",
        "m_dot": "heat.drain_before_pump.m_dot",
    },
    "供热系统余热回收1水入口": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "heat.recovery1_water_in.P",
        "T": "heat.recovery1_water_in.T",
        "m_dot": "heat.recovery1_water_in.m_dot",
    },
    "供热系统余热回收1水出口": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "heat.recovery1_water_out.P",
        "T": "heat.recovery1_water_out.T",
        "m_dot": "heat.recovery1_water_out.m_dot",
    },
    "供热系统余热回收2水入口": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "heat.recovery2_water_in.P",
        "T": "heat.recovery2_water_in.T",
        "m_dot": "heat.recovery2_water_in.m_dot",
    },
    "供热系统余热回收2水出口": {
        "type": "WaterSteamState",
        "method": "from_PT",
        "P": "heat.recovery2_water_out.P",
        "T": "heat.recovery2_water_out.T",
        "m_dot": "heat.recovery2_water_out.m_dot",
    },
}
