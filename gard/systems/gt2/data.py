"""2 号燃机气体输入字段，值由上游预处理为 SI 单位。

温度由排气/锅炉边界的多点测量汇总；未确认的压力基准、流量和成分
保持缺失，不用内部换热器参数代替边界测量。
"""
import pandas as pd


INPUT_UNITS = {
    "gt2.air_in.P": "Pa (absolute)",
    "gt2.air_in.T": "K",
    "gt2.air_in.m_dot": "kg/s",
    "gt2.air_in.composition": "mole fraction / GasComposition",
    "gt2.compressor_out.P": "Pa (absolute)",
    "gt2.compressor_out.T": "K",
    "gt2.compressor_out.m_dot": "kg/s",
    "gt2.fuel.P": "Pa (absolute)",
    "gt2.fuel.T": "K",
    "gt2.fuel.m_dot": "kg/s",
    "gt2.fuel.composition": "mole fraction / GasComposition",
    "gt2.exhaust.P": "Pa (absolute)",
    "gt2.exhaust.T": "K",
    "gt2.exhaust.m_dot": "kg/s",
    "gt2.exhaust.composition": "mole fraction / GasComposition",
    "hrsg2.gas_out.P": "Pa (absolute)",
    "hrsg2.gas_out.T": "K",
    "hrsg2.gas_out.m_dot": "kg/s",
    "gt2.power": "W",
    "gt2.total_pressure_recovery": "dimensionless",
    "gt2.fuel_chemical_exergy": "J/kg",
}


# Raw measurements are not configured yet.
POINT_BINDINGS = pd.DataFrame(
    [], columns=["field", "code", "expected_unit", "unit", "scale", "offset", "pressure_basis"]
).astype({"scale": float, "offset": float})
