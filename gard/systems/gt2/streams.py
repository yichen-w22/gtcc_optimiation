"""2 号燃机气体流股及余热锅炉出口烟气，输入使用 SI 单位。"""

HRSG_INLET_STREAM_NAME = "2号燃机排气"

STREAM_DEFINITIONS = {
    "2号燃机进气": {
        "type": "GasState",
        "method": "from_TP",
        "P": "gt2.air_in.P",
        "T": "gt2.air_in.T",
        "m_dot": "gt2.air_in.m_dot",
        "composition": "gt2.air_in.composition",
    },
    "2号燃机压气机出口": {
        "type": "GasState",
        "method": "from_TP",
        "P": "gt2.compressor_out.P",
        "T": "gt2.compressor_out.T",
        "m_dot": "gt2.compressor_out.m_dot",
        "composition": "gt2.air_in.composition",
    },
    "2号燃机燃料": {
        "type": "GasState",
        "method": "from_TP",
        "P": "gt2.fuel.P",
        "T": "gt2.fuel.T",
        "m_dot": "gt2.fuel.m_dot",
        "composition": "gt2.fuel.composition",
    },
    "2号燃机排气": {
        "type": "GasState",
        "method": "from_TP",
        "P": "gt2.exhaust.P",
        "T": "gt2.exhaust.T",
        "m_dot": "gt2.exhaust.m_dot",
        "composition": "gt2.exhaust.composition",
        "note": "燃机出口与余热锅炉进口共用此流股",
    },
    "2号余热锅炉出口烟气": {
        "type": "GasState",
        "method": "from_TP",
        "P": "hrsg2.gas_out.P",
        "T": "hrsg2.gas_out.T",
        "m_dot": "hrsg2.gas_out.m_dot",
        "composition": "gt2.exhaust.composition",
    },
}
