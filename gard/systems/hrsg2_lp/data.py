"""hrsg2_lp measurements and preprocessing."""
import pandas as pd
from src.utils.data import resolve_bindings, convert_values, read_history, summarize_history, attach_quality

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [
        ["hrsg2.lp_feed.P", "GARD_12HAA70WP021BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg2.lp_feed.T", "GARD_12HAA70WP021BT01XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg2.lp_feed.m_dot", "GARD_12HAA70WP021BF02XQ01", "t/h", "t/h", 1 / 3.6, 0.0],
        ["hrsg2.lp_economizer_out.T", "GARD_12HAA80QN102BT01XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg2.lp_drum_valve_in.P", "GARD_12HAA80QN102BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg2.lp_to_drum.T", "GARD_12HAA80QN102BT02XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg2.lp_recirc_pump1_out.P", "GARD_12HAA85WP011BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg2.lp_recirc_pump2_out.P", "GARD_12HAA85WP012BP02XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg2.lp_main.P", "GARD_12LBA01WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg2.lp_main.m_dot", "GARD_12LBA01WP001BF04XQ01", "t/h", "t/h", 1 / 3.6, 0.0],
        ["hrsg2.lp_to_st.P", "GARD_12LBA20WP011BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg2.lp_to_st.T", "GARD_12LBA20WP011BP04XQ01", "℃", "\u2103", 1.0, 273.15],
    ],
    columns=["field", "code", "expected_unit", "unit", "scale", "offset"],
).astype({"scale": float, "offset": float})


def read_bindings():
    return resolve_bindings(POINT_BINDINGS)


def load_raw_data(directory, start, end):
    return read_history(directory, start, end, read_bindings())


def prepare_inputs(point_values, raw_pressure_basis=None):
    return convert_values(point_values, read_bindings(), raw_pressure_basis)


def load_inputs(directory, start, end, raw_pressure_basis=None):
    """独立加载本系统的半小时历史数据，返回SI字段和输入质量表。"""
    raw = load_raw_data(directory, start, end)
    values, quality = summarize_history(raw, start, end)
    row, inputs = prepare_inputs(values.to_dict(), raw_pressure_basis)
    return (row, attach_quality(inputs, quality))


