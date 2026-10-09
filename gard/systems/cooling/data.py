"""cooling measurements and preprocessing."""
import pandas as pd

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [], columns=["field", "code", "expected_unit", "unit", "scale", "offset"]
).astype({"scale": float, "offset": float})


def read_bindings():
    from gard.data_io import resolve_bindings

    return resolve_bindings(POINT_BINDINGS)


def load_raw_data(directory, start, end):
    from gard.data_io import read_history

    return read_history(directory, start, end, read_bindings())


def prepare_inputs(point_values, raw_pressure_basis=None):
    from gard.data_io import convert_values

    return convert_values(point_values, read_bindings(), raw_pressure_basis)


def load_inputs(directory, start, end, raw_pressure_basis=None):
    """独立加载本系统的半小时历史数据，返回SI字段和输入质量表。"""
    from gard.data_io import summarize_history, attach_quality

    raw = load_raw_data(directory, start, end)
    values, quality = summarize_history(raw, start, end)
    row, inputs = prepare_inputs(values.to_dict(), raw_pressure_basis)
    return (row, attach_quality(inputs, quality))


def prepare_system_inputs(row):
    """Prepare signed boundary quantities for this system (SI units)."""
    inputs = row.copy()
    return inputs
