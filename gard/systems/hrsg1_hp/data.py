"""hrsg1_hp measurement configuration."""
import pandas as pd

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [
        ["hrsg1.lp_drum_pressure", "GARD_11HBK11CM001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.hp_pump1.current", "GARD_11LAC71GP001BC01XQ01", "A", "A", 1.0, 0.0, None],
        ["hrsg1.hp_pump2.current", "GARD_11LAC72GP001BC01XQ01", "A", "A", 1.0, 0.0, None],
        ["hrsg1.hp_pump1_out.P", "GARD_11LAB71WP011BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.hp_pump2_out.P", "GARD_11LAB72WP012BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.hp_feed.P", "GARD_11LAB75WP004BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.hp_feed.T", "GARD_11LAB75WP021BP03XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.hp_feed.m_dot", "GARD_11LAB75WP021BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg1.hp_to_drum.T", "GARD_11HAG01WP001BT01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.hp_drum_pressure", "GARD_11HAG01CM001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.hp_before_spray.T", "GARD_11HBK11WP021BT02XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.hp_after_spray.T", "GARD_11HBK11WP021BT03XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.hp_main.P", "GARD_11LBA21WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.hp_main.T", "GARD_11LBA21WP001BT13XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.hp_main.m_dot", "GARD_11LBA21WP001BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg1.hp_to_st.P", "GARD_11LBA10WP001BF03XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.hp_to_st.T", "GARD_11LBA10WP001BT03XQ01", "℃", "\u2103", 1.0, 273.15, None],
    ],
    columns=["field", "code", "expected_unit", "unit", "scale", "offset", "pressure_basis"],
).astype({"scale": float, "offset": float})
