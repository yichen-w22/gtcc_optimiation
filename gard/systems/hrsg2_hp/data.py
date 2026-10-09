"""hrsg2_hp measurements and preprocessing."""
import pandas as pd

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [
        ["hrsg2.hp_pump1_out.P", "GARD_12LAB71WP011BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg2.hp_pump2_out.P", "GARD_12LAB72WP012BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg2.hp_feed.P", "GARD_12LAB75WP004BP02XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg2.hp_feed.T", "GARD_12LAB75WP021BP03XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg2.hp_feed.m_dot", "GARD_12LAB75WP021BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0],
        ["hrsg2.hp_to_drum.T", "GARD_12HAG01WP001BT01XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg2.hp_drum_pressure", "GARD_12HAG01CM001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg2.hp_before_spray.T", "GARD_12HBK11WP021BT02XQ01", "℃", "%", 1.0, 273.15],
        ["hrsg2.hp_after_spray.T", "GARD_12HBK11WP021BT03XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg2.hp_main.P", "GARD_12LBA21WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg2.hp_main.T", "GARD_12LBA21WP001BT13XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg2.hp_main.m_dot", "GARD_12LBA21WP001BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0],
        ["hrsg2.hp_to_st.P", "GARD_12LBA10WP001BF03XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg2.hp_to_st.T", "GARD_12LBA10WP001BT03XQ01", "℃", "\u2103", 1.0, 273.15],
    ],
    columns=["field", "code", "expected_unit", "unit", "scale", "offset"],
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
    inputs["hrsg2_hp.work"] = -row["hp2_pump1.power"] - row["hp2_pump2.power"]
    return inputs
