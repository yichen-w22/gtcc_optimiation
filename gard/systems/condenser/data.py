"""condenser measurements and preprocessing."""
import pandas as pd

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [
        ["cond.pre_header_in.P", "GARD_13LCA10WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.pre_header_in.T", "GARD_13LCA10GP001BT10XQ01", "℃", "\u2103", 1.0, 273.15],
        ["cond.pre_pump1_out.P", "GARD_13LCA11GP101BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.pre_pump2_out.P", "GARD_13LCA1200000BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.pre_pump3_out.P", "GARD_13LCA13WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.pre_header_out.P", "GARD_13PGB20WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.pre_header_out.T", "GARD_13PGB20WP001BT10XQ01", "℃", "\u2103", 1.0, 273.15],
        ["cond.gland_heater_in.P", "GARD_13PGB20WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.gland_heater_in.m_dot", "GARD_13LCR20CAL01BF01XQ01", "t/h", "t/h", 1 / 3.6, 0.0],
        ["cond.gland_heater_out.P", "GARD_13LBC1000000BP04XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.gland_heater_out.T", "GARD_13LCB4000000BP01XQ01", "℃", "\u2103", 1.0, 273.15],
        ["cond.pump1_out.P", "GARD_13LCB4000000BT01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.pump2_out.P", "GARD_13LCB4100000BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.pump3_out.P", "GARD_13PGB60WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.pump_header_out.P", "GARD_13LCB5000000BF01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.filter_in.P", "GARD_13LDB1000000BF01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.filter_in.T", "GARD_13LDB1000000BP01XQ01", "℃", "\u2103", 1.0, 273.15],
        ["cond.to_boilers.P", "GARD_13LCB5000000BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.to_boilers.T", "GARD_13LCB5000000BP02XQ01", "℃", "\u2103", 1.0, 273.15],
        ["cond.to_boilers.m_dot", "GARD_13LCR50CAL01BF01XQ01", "t/h", "t/h", 1 / 3.6, 0.0],
        ["cond.main_recycle.m_dot", "GARD_13LCE64CF101BF01XQ01", "t/h", "t/h", 1 / 3.6, 0.0],
        ["cond.makeup.P", "GARD_00LCR10CP001BP01XG01", "MPa", "MPa", 1000000.0, 0.0],
        ["cond.makeup.m_dot", "GARD_00LCR10CAL01BF01XQ01", "t/h", "t/h", 1 / 3.6, 0.0],
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
    pre_pump_work = -sum(row[f"pre_pump{i}.power"] for i in (1, 2, 3))
    cond_pump_work = -sum(row[f"cond_pump{i}.power"] for i in (1, 2, 3))
    vacuum_pump_work = sum(row[f"vacuum_pump{i}.work"] for i in (1, 2, 3))
    inputs["condenser.work"] = pre_pump_work + cond_pump_work + vacuum_pump_work
    return inputs
