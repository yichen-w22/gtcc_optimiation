"""heating measurements and preprocessing."""
import pandas as pd
from src.utils.data import resolve_bindings, convert_values, read_history, summarize_history, attach_quality

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [["heat.drain_return.m_dot", "GARD_00NDD80WP011BF01XQ01", "t/h", "t/h", 1 / 3.6, 0.0]],
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


