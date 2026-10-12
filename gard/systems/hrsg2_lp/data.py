"""hrsg2_lp measurement configuration."""
import pandas as pd

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [
        ["hrsg2.lp_feed.P", "GARD_12HAA70WP021BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.lp_feed.T", "GARD_12HAA70WP021BT01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg2.lp_feed.m_dot", "GARD_12HAA70WP021BF02XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg2.lp_economizer_out.T", "GARD_12HAA80QN102BT01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg2.lp_drum_valve_in.P", "GARD_12HAA80QN102BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.lp_to_drum.T", "GARD_12HAA80QN102BT02XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg2.lp_recirc_pump1_out.P", "GARD_12HAA85WP011BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.lp_recirc_pump2_out.P", "GARD_12HAA85WP012BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.lp_main.P", "GARD_12LBA01WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.lp_main.m_dot", "GARD_12LBA01WP001BF04XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg2.lp_to_st.P", "GARD_12LBA20WP011BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg2.lp_to_st.T", "GARD_12LBA20WP011BP04XQ01", "℃", "\u2103", 1.0, 273.15, None],
    ],
    columns=["field", "code", "expected_unit", "unit", "scale", "offset", "pressure_basis"],
).astype({"scale": float, "offset": float})
