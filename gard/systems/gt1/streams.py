"""1 号燃机气体流股及余热锅炉出口烟气，输入使用 SI 单位。"""

HRSG_INLET_STREAM_NAME = "1号燃机排气"

STREAM_DEFINITIONS = {
    "1号燃机进气": {
        "type": "GasState",
        "method": "from_TP",
        "P": "gt1.air_in.P",
        "T": "gt1.air_in.T",
        "m_dot": "gt1.air_in.m_dot",
        "composition": "gt1.air_in.composition",
    },
    "1号燃机压气机出口": {
        "type": "GasState",
        "method": "from_TP",
        "P": "gt1.compressor_out.P",
        "T": "gt1.compressor_out.T",
        "m_dot": "gt1.compressor_out.m_dot",
        "composition": "gt1.air_in.composition",
    },
    "1号燃机燃料": {
        "type": "GasState",
        "method": "from_TP",
        "P": "gt1.fuel.P",
        "T": "gt1.fuel.T",
        "m_dot": "gt1.fuel.m_dot",
        "composition": "gt1.fuel.composition",
    },
    "1号燃机排气": {
        "type": "GasState",
        "method": "from_TP",
        "P": "gt1.exhaust.P",
        "T": "gt1.exhaust.T",
        "m_dot": "gt1.exhaust.m_dot",
        "composition": "gt1.exhaust.composition",
        "note": "燃机出口与余热锅炉进口共用此流股",
    },
    "1号余热锅炉出口烟气": {
        "type": "GasState",
        "method": "from_TP",
        "P": "hrsg1.gas_out.P",
        "T": "hrsg1.gas_out.T",
        "m_dot": "hrsg1.gas_out.m_dot",
        "composition": "gt1.exhaust.composition",
    },
}
