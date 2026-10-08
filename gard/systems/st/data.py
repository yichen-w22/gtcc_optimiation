"""st measurements and preprocessing."""
import pandas as pd
from src.utils.data import resolve_bindings, convert_values, read_history, summarize_history, attach_quality

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [
        ["st.hp_in.P", "GARD_13MST0100000BT03XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["st.hp_in.T", "GARD_13LBA1000000BP01XQ01", "℃", "\u2103", 1.0, 273.15],
        ["st.hp_out.P", "GARD_13LBC1000000BL01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["st.hp_out.T", "GARD_13MAA5000000BT05XQ01", "℃", "\u2103", 1.0, 273.15],
        ["st.ip_in.P", "GARD_13LBB1000000BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["st.ip_in.T", "GARD_13LBB1000000BT01XQ01", "℃", "\u2103", 1.0, 273.15],
        ["st.ip_out.T", "GARD_13LBD4400000BT03XQ01", "℃", "\u2103", 1.0, 273.15],
        ["st.generator_power", "GARD_13MKA01CE001BJ01XQ01", "MW", "MW", 1000000.0, 0.0],
        ["st.lp_out.P", "GARD_13MAG1000000BP03XQ01", "kPa.a", "kPa.a", 1000.0, 0.0],
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


