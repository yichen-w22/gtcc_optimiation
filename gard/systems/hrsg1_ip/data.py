"""hrsg1_ip measurements and preprocessing."""
import pandas as pd

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [
        ["hrsg1.ip_pump1_out.P", "GARD_11LAB81WP011BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg1.ip_pump2_out.P", "GARD_11LAB82WP012BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg1.ip_feed.P", "GARD_11HAC02WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg1.ip_feed.T", "GARD_11HAC02WP001BT01XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg1.ip_feed.m_dot", "GARD_11HAC02WP001BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0],
        ["hrsg1.ip_to_drum.T", "GARD_11LAF80WP002BT01XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg1.ip_drum_pressure", "GARD_11HBK02CM001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg1.ip_fresh.P", "GARD_11HAH80WP011BP02XQ01", "Mpa", "Mpa", 1000000.0, 0.0],
        ["hrsg1.ip_fresh.T", "GARD_11HAH80WP011BT02XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg1.ip_fresh.m_dot", "GARD_11HAH80WP011BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0],
        ["hrsg1.reheat_mixed.P", "GARD_11LBC80WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg1.reheat_mixed.T", "GARD_11LBC80WP001BT01XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg1.rh_spray.m_dot", "GARD_11LAF80WP001BF02XQ01", "t/h", "t/h", 1 / 3.6, 0.0],
        ["hrsg1.rh_after_spray.T", "GARD_11HAJ80WP011BT07XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg1.hot_reheat.P", "GARD_11LBB01WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg1.hot_reheat.m_dot", "GARD_11LBB01WP001BF03XQ01", "t/h", "t/h", 1 / 3.6, 0.0],
        ["hrsg1.cold_reheat.P", "GARD_11LBC10WP001BP01XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg1.cold_reheat.T", "GARD_11LBC10WP001BT02XQ01", "℃", "\u2103", 1.0, 273.15],
        ["hrsg1.rh_to_st.P", "GARD_11LBB10WP001BP02XQ01", "MPa", "MPa", 1000000.0, 0.0],
        ["hrsg1.rh_to_st.T", "GARD_11LBB10WP001BT05XQ01", "℃", "\u2103", 1.0, 273.15],
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
    inputs["hrsg1_ip.work"] = -row["ip1_pump1.power"] - row["ip1_pump2.power"]
    return inputs
