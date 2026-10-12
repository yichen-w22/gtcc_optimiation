"""condenser measurement configuration."""
import pandas as pd

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [
        ["cond.pre_header_in.P", "GARD_13LCA10WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.pre_header_in.T", "GARD_13LCA10GP001BT10XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["cond.pre_pump1_out.P", "GARD_13LCA11GP101BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.pre_pump2_out.P", "GARD_13LCA1200000BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.pre_pump3_out.P", "GARD_13LCA13WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.pre_header_out.P", "GARD_13PGB20WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.pre_header_out.T", "GARD_13PGB20WP001BT10XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["cond.gland_heater_in.P", "GARD_13PGB20WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.gland_heater_in.m_dot", "GARD_13LCR20CAL01BF01XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["cond.gland_heater_out.P", "GARD_13LBC1000000BP04XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.gland_heater_out.T", "GARD_13LCB4000000BP01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["cond.pump1_out.P", "GARD_13LCB4000000BT01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.pump2_out.P", "GARD_13LCB4100000BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.pump3_out.P", "GARD_13PGB60WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.pump_header_out.P", "GARD_13LCB5000000BF01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.filter_in.P", "GARD_13LDB1000000BF01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.filter_in.T", "GARD_13LDB1000000BP01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["cond.to_boilers.P", "GARD_13LCB5000000BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.to_boilers.T", "GARD_13LCB5000000BP02XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["cond.to_boilers.m_dot", "GARD_13LCR50CAL01BF01XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["cond.main_recycle.m_dot", "GARD_13LCE64CF101BF01XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["cond.makeup.P", "GARD_00LCR10CP001BP01XG01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["cond.makeup.m_dot", "GARD_00LCR10CAL01BF01XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
    ],
    columns=["field", "code", "expected_unit", "unit", "scale", "offset", "pressure_basis"],
).astype({"scale": float, "offset": float})
