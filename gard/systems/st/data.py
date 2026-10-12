"""st measurement configuration."""
import pandas as pd

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [
        ["st.hp_in.P", "GARD_13MST0100000BT03XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["st.hp_in.T", "GARD_13LBA1000000BP01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["st.hp_out.P", "GARD_13LBC1000000BL01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["st.hp_out.T", "GARD_13MAA5000000BT05XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["st.ip_in.P", "GARD_13LBB1000000BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["st.ip_in.T", "GARD_13LBB1000000BT01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["st.ip_out.T", "GARD_13LBD4400000BT03XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["st.generator_power", "GARD_13MKA01CE001BJ01XQ01", "MW", "MW", 1000000.0, 0.0, None],
        ["st.lp_out.P", "GARD_13MAG1000000BP03XQ01", "kPa.a", "kPa.a", 1000.0, 0.0, "absolute"],
    ],
    columns=["field", "code", "expected_unit", "unit", "scale", "offset", "pressure_basis"],
).astype({"scale": float, "offset": float})
