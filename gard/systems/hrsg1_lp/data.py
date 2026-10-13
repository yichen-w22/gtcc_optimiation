"""hrsg1_lp measurement configuration."""
import pandas as pd

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [
        ["hrsg1.lp_feed_after_recovery.P", "GARD_11HAA70WP021BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.lp_feed_after_recovery.T", "GARD_11HAA70WP021BT01XQ01", "℃", "℃", 1.0, 273.15, None],
        ["hrsg1.lp_from_heat_recovery.P", "GARD_11HAA13QN101BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.lp_from_heat_recovery.T", "GARD_11HAA11WP011BT02XQ01", "℃", "℃", 1.0, 273.15, None],
        ["hrsg1.lp_feed.m_dot", "GARD_11HAA70WP021BF02XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg1.lp_economizer_out.T", "GARD_11HAA80QN102BT01XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.lp_drum_valve_in.P", "GARD_11HAA80QN102BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.lp_to_drum.T", "GARD_11HAA80QN102BT02XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.lp_recirc_pump1_out.P", "GARD_11HAA85WP011BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.lp_recirc_pump2_out.P", "GARD_11HAA85WP012BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.lp_main.P", "GARD_11LBA01WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.lp_main.m_dot", "GARD_11LBA01WP001BF04XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg1.lp_to_st.P", "GARD_11LBA20WP011BP01XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.lp_to_st.T", "GARD_11LBA20WP011BP04XQ01", "℃", "\u2103", 1.0, 273.15, None],
        ["hrsg1.lp_drum_pressure", "GARD_11HBK11CM001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0, "absolute"],
        ["hrsg1.lp_economizer_in.T", "GARD_11HAA70WP021BT02XQ01", "℃", "℃", 1.0, 273.15, None],
        ["hrsg1.lp_recirc_in.m_dot", "GARD_11HAA85WP001BF01XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg1.lp_main.T", "GARD_11LBA01WP001BT03XQ01", "℃", "℃", 1.0, 273.15, None],
        ["hrsg1.lp_recirc_pump1.current", "GARD_11HAA85GP001BC01XQ01", "A", "A", 1.0, 0.0, None],
        ["hrsg1.lp_recirc_pump2.current", "GARD_11HAA85GP002BC02XQ01", "A", "A", 1.0, 0.0, None],
        ["hrsg1.hp_main.m_dot", "GARD_11LBA21WP001BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg1.ip_feed.m_dot", "GARD_11HAC02WP001BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
        ["hrsg1.rh_spray.m_dot", "GARD_11LAF80WP001BF02XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None],
    ],
    columns=["field", "code", "expected_unit", "unit", "scale", "offset", "pressure_basis"],
).astype({"scale": float, "offset": float})

# Original point-table labels remain evidence. The user directs this LP review
# to use engineering units and not treat unit-label differences as open issues.
UNIT_OVERRIDES = {
    "hrsg1.lp_from_heat_recovery.T": {"code": "GARD_11HAA11WP011BT02XQ01", "original_unit": "%", "effective_unit": "℃", "authority": "用户指定热网返回水温度测点；按已确认工程温度单位导入，原标注保留"},
    "hrsg1.lp_main.T": {"code": "GARD_11LBA01WP001BT03XQ01", "original_unit": "%", "effective_unit": "℃", "authority": "用户：默认单位正确，本轮不考虑单位问题；按温度工程单位导入"},
    "hrsg1.lp_recirc_pump1.current": {"code": "GARD_11HAA85GP001BC01XQ01", "original_unit": "%", "effective_unit": "A", "authority": "用户：默认单位正确，本轮不考虑单位问题；按电流工程单位导入"},
    "hrsg1.lp_recirc_pump2.current": {"code": "GARD_11HAA85GP002BC02XQ01", "original_unit": "%", "effective_unit": "A", "authority": "用户：默认单位正确，本轮不考虑单位问题；按电流工程单位导入"},
}
