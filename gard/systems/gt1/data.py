"""1 号燃机气体输入字段，值由上游预处理为 SI 单位。

温度由排气/锅炉边界的多点测量汇总；未确认的压力基准、流量和成分
保持缺失，不用内部换热器参数代替边界测量。
"""

INPUT_UNITS = {
    "gt1.air_in.P": "Pa (absolute)",
    "gt1.air_in.T": "K",
    "gt1.air_in.m_dot": "kg/s",
    "gt1.air_in.composition": "mole fraction / GasComposition",
    "gt1.compressor_out.P": "Pa (absolute)",
    "gt1.compressor_out.T": "K",
    "gt1.compressor_out.m_dot": "kg/s",
    "gt1.fuel.P": "Pa (absolute)",
    "gt1.fuel.T": "K",
    "gt1.fuel.m_dot": "kg/s",
    "gt1.fuel.composition": "mole fraction / GasComposition",
    "gt1.exhaust.P": "Pa (absolute)",
    "gt1.exhaust.T": "K",
    "gt1.exhaust.m_dot": "kg/s",
    "gt1.exhaust.composition": "mole fraction / GasComposition",
    "hrsg1.gas_out.P": "Pa (absolute)",
    "hrsg1.gas_out.T": "K",
    "hrsg1.gas_out.m_dot": "kg/s",
    "gt1.power": "W",
    "gt1.total_pressure_recovery": "dimensionless",
    "gt1.fuel_chemical_exergy": "J/kg",
}


def prepare_system_inputs(row):
    """燃机输入已使用 SI 单位，直接复制供系统构建使用。"""
    return row.copy()
