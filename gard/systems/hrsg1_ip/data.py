"""hrsg1_ip measurement configuration."""
import pandas as pd

UNIT_OVERRIDES = {
    "hrsg1.ip_pump2.current": {
        "code": "GARD_11LAB82QM003BC01XQ01", "original_unit": "%", "effective_unit": "A",
        "authority": "用户于2026-10-13明确要求中压电流按A解释",
    },
    "hrsg1.hot_reheat.T": {
        "code": "GARD_11LBB01WP001BT13XQ01", "original_unit": "%", "effective_unit": "℃",
        "authority": "用户于2026-10-13明确要求当前热再热温度选择值按摄氏度解释；导入转K",
    },
}

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [
        ["hrsg1.lp_drum_pressure", "GARD_11HBK11CM001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.ip_pump1.current", "GARD_11LAB81QM003BC01XQ01", "A", "A", 1.0, 0.0, None],
        ["hrsg1.ip_pump2.current", "GARD_11LAB82QM003BC01XQ01", "A", "A", 1.0, 0.0, None],
        ["hrsg1.ip_pump1_out.P", "GARD_11LAB81WP011BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.ip_pump2_out.P", "GARD_11LAB82WP012BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.ip_feed.P", "GARD_11HAC02WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.ip_feed.T", "GARD_11HAC02WP001BT01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.ip_feed.m_dot", "GARD_11HAC02WP001BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg1.ip_to_drum.T", "GARD_11LAF80WP002BT01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.ip_drum_pressure", "GARD_11HBK02CM001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.ip_fresh.P", "GARD_11HAH80WP011BP02XQ01", "Mpa", "Mpa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.ip_fresh.T", "GARD_11HAH80WP011BT02XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.ip_fresh.m_dot", "GARD_11HAH80WP011BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg1.reheat_mixed.P", "GARD_11LBC80WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.reheat_mixed.T", "GARD_11LBC80WP001BT01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.rh_spray.m_dot", "GARD_11LAF80WP001BF02XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg1.rh_before_spray.T", "GARD_11HAJ80WP001BT01XQ01", "℃", "℃", 1.0, 273.15, None],
        ["hrsg1.rh_after_spray.T", "GARD_11HAJ80WP011BT07XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.hot_reheat.P", "GARD_11LBB01WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.hot_reheat.T", "GARD_11LBB01WP001BT13XQ01", "℃", "℃", 1.0, 273.15, None],
        ["hrsg1.hot_reheat.m_dot", "GARD_11LBB01WP001BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg1.cold_reheat.P", "GARD_11LBC10WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.cold_reheat.T", "GARD_11LBC10WP001BT02XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.rh_to_st.P", "GARD_11LBB10WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.rh_to_st.T", "GARD_11LBB10WP001BT05XQ01", "℃", "\u2103", 1.0, 273.15, None],
    ],
    columns=["field", "code", "expected_unit", "unit", "scale", "offset", "pressure_basis"],
).astype({"scale": float, "offset": float})
