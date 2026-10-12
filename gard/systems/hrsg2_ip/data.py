"""hrsg2_ip measurement configuration."""
import pandas as pd

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [
        ["hrsg2.ip_pump1_out.P", "GARD_12LAB81WP011BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.ip_pump2_out.P", "GARD_12LAB82WP012BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.ip_feed.P", "GARD_12HAC02WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.ip_feed.T", "GARD_12HAC02WP001BT01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg2.ip_feed.m_dot", "GARD_12HAC02WP001BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg2.ip_to_drum.T", "GARD_12LAF80WP002BT01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg2.ip_drum_pressure", "GARD_12HAG02CM001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.ip_fresh.P", "GARD_12HAH80WP011BP02XQ01", "Mpa", "Mpa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.ip_fresh.T", "GARD_12HAH80WP011BT02XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg2.ip_fresh.m_dot", "GARD_12HAH80WP011BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg2.reheat_mixed.P", "GARD_12LBC80WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.reheat_mixed.T", "GARD_12LBC80WP001BT01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg2.rh_spray.m_dot", "GARD_12LAF80WP001BF02XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg2.rh_after_spray.T", "GARD_12HAJ80WP011BT07XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg2.hot_reheat.P", "GARD_12LBB01WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.hot_reheat.m_dot", "GARD_12LBB01WP001BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg2.cold_reheat.P", "GARD_12LBC10WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.cold_reheat.T", "GARD_12LBC10WP001BT02XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg2.rh_to_st.P", "GARD_12LBB10WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.rh_to_st.T", "GARD_12LBB10WP001BT05XQ01", "℃", "\u2103", 1.0, 273.15, None],
    ],
    columns=["field", "code", "expected_unit", "unit", "scale", "offset", "pressure_basis"],
).astype({"scale": float, "offset": float})
