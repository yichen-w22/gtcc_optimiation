"""统一入口：原始输入/历史窗口 → 全场计算 → 输出；文件入口也在这里。"""

import argparse
import json
from pathlib import Path
import pandas as pd
from src.utils.data import (
    resolve_bindings,
    convert_values,
    read_history,
    summarize_history,
    attach_quality,
)
from gard.plant import (
    build_ref_env_from_row,
    build_stream_book_from_row,
    build_plant_from_streams,
)
from gard.hrsg_gas_data import POINT_BINDINGS as HRSG_GAS_POINT_BINDINGS
from gard.systems import (
    hrsg1_hp,
    hrsg1_ip,
    hrsg1_lp,
    hrsg2_hp,
    hrsg2_ip,
    hrsg2_lp,
    st,
    condenser,
    heating,
    cooling,
    auxiliary,
)

POINT_BINDINGS = pd.concat(
    [
        hrsg1_hp.POINT_BINDINGS,
        hrsg1_ip.POINT_BINDINGS,
        hrsg1_lp.POINT_BINDINGS,
        hrsg2_hp.POINT_BINDINGS,
        hrsg2_ip.POINT_BINDINGS,
        hrsg2_lp.POINT_BINDINGS,
        st.POINT_BINDINGS,
        condenser.POINT_BINDINGS,
        heating.POINT_BINDINGS,
        cooling.POINT_BINDINGS,
        auxiliary.POINT_BINDINGS,
        HRSG_GAS_POINT_BINDINGS,
    ],
    ignore_index=True,
)


def read_bindings():
    return resolve_bindings(POINT_BINDINGS)


def apply_unit_conversions(point_values, raw_pressure_basis=None):
    row, inputs = convert_values(point_values, read_bindings(), raw_pressure_basis)
    return row, inputs


def read_window(directory, start, end):
    data = read_history(directory, start, end, read_bindings())
    if data.empty:
        raise FileNotFoundError("没有与测点绑定相符的 Parquet 数据")
    return data.drop_duplicates(["time", "code", "value"])


def prepare_window(data, start, end, raw_pressure_basis=None):
    """1 秒时间网格近似时间加权；最多保持 60 秒，不外推长缺口。"""
    means, quality = summarize_history(data, start, end)
    row, inputs = apply_unit_conversions(means.to_dict(), raw_pressure_basis)
    inputs = attach_quality(inputs, quality)
    required = inputs.field.isin(
        [
            "st.generator_power",
            "hrsg1.hp_main.m_dot",
            "hrsg2.hp_main.m_dot",
            "hrsg1.hp_main.P",
            "hrsg2.hp_main.P",
            "hrsg1.hp_main.T",
            "hrsg2.hp_main.T",
        ]
    )
    screening = inputs.loc[required].copy()
    screening["limit"] = 0.02
    screening.loc[screening.field.str.endswith(".P"), "limit"] = 0.01
    screening["stable"] = screening.relative_range <= screening.limit
    temperature = screening.field.str.endswith(".T")
    screening.loc[temperature, "stable"] = (
        screening.loc[temperature, "temperature_range_K"] <= 2.0
    )
    screening["stable"] &= (screening.valid_bins >= 5) & (
        screening.binding_status == "ready"
    )
    power = row.get("st.generator_power")
    steady = bool(
        screening.stable.all()
        and len(screening) == 7
        and (power is not None)
        and (power > 10000000.0)
    )
    return row, inputs, screening, steady


def evaluate_window(directory, start, end, raw_pressure_basis=None):
    data = read_window(directory, start, end)
    row, inputs, screening, steady = prepare_window(
        data, start, end, raw_pressure_basis
    )
    tables = cal_property(pd.DataFrame([row]))
    tables["inputs"] = inputs
    tables["screening"] = screening
    tables["plant"]["steady_window"] = steady
    tables["plant"]["mode_confirmed"] = False
    return tables


def build_online_dataframe(payload, frame_index=0, raw_pressure_basis=None):
    if isinstance(payload, (str, Path)):
        payload = json.loads(Path(payload).read_text(encoding="utf-8-sig"))
    frame = payload["frames"][frame_index].copy()
    timestamp = frame.pop("timestamp", None)
    row, inputs = apply_unit_conversions(frame, raw_pressure_basis)
    return (pd.DataFrame([row]), timestamp, inputs)


def cal_property(df, idx=0):
    ref = build_ref_env_from_row(df, idx)
    streams = build_stream_book_from_row(df, idx, ref)
    model = build_plant_from_streams(streams, df.iloc[idx])
    model.plant.transfers = model.plant.transfers.drop(
        index=["hp_turbine", "ip_turbine", "lp_turbine"]
    )
    model.plant.transfers.loc["st_generator"] = [
        df.iloc[idx].get("st.generator_power"),
        0.0,
        0.0,
    ]
    plant_result = model.plant.result()
    components = pd.DataFrame(model.component_results)
    systems = pd.DataFrame(model.system_results)
    composite = pd.DataFrame(model.composites)
    plant_result["generator_power"] = df.iloc[idx].get("st.generator_power")
    plant_result["net_power"] = plant_result["work_output"]
    plant_result["exergy_efficiency"] = None
    plant_result["note"] += "；净功和效率需完整泵功、烟气及外部热量边界"
    return {
        "streams": streams.table(),
        "components": components,
        "systems": systems,
        "plant": pd.DataFrame([plant_result]),
        "composites": composite,
        "connections": model.plant.ports.copy(),
        "external_boundaries": model.plant.boundary(),
    }


def build_output_json(tables, timestamp=None):
    return {
        "timestamp": timestamp,
        "boundary": "GARD steam-water cycle",
        "units": {"P": "Pa absolute", "T": "K", "m_dot": "kg/s", "power": "W"},
        "streams": json.loads(tables["streams"].to_json(orient="records")),
        "components": json.loads(tables["components"].to_json(orient="records")),
        "systems": json.loads(tables["systems"].to_json(orient="records")),
        "plant": json.loads(tables["plant"].to_json(orient="records"))[0],
        "composites": json.loads(tables["composites"].to_json(orient="records")),
        "connections": json.loads(tables["connections"].to_json(orient="records")),
        "external_boundaries": json.loads(
            tables["external_boundaries"].to_json(orient="records")
        ),
    }


def write_tables(tables, output_directory):
    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    tables["streams"].to_csv(
        directory / "streams.csv", index=False, encoding="utf-8-sig"
    )
    tables["components"].to_csv(
        directory / "components.csv", index=False, encoding="utf-8-sig"
    )
    tables["systems"].to_csv(
        directory / "systems.csv", index=False, encoding="utf-8-sig"
    )
    tables["plant"].to_csv(directory / "plant.csv", index=False, encoding="utf-8-sig")
    tables["composites"].to_csv(
        directory / "composites.csv", index=False, encoding="utf-8-sig"
    )
    tables["connections"].to_csv(
        directory / "connections.csv", index=False, encoding="utf-8-sig"
    )
    tables["external_boundaries"].to_csv(
        directory / "external_boundaries.csv", index=False, encoding="utf-8-sig"
    )


def compute(payload, frame_index=0, raw_pressure_basis=None):
    df, timestamp, inputs = build_online_dataframe(
        payload, frame_index, raw_pressure_basis
    )
    result = build_output_json(cal_property(df), timestamp)
    result["inputs"] = json.loads(inputs.to_json(orient="records"))
    return result


def compute_si(row, timestamp=None):
    """P=绝压 Pa，T=K，m_dot=kg/s，h=J/kg，power=W。"""
    row = dict(row)
    return build_output_json(cal_property(pd.DataFrame([row])), timestamp)


def main():
    parser = argparse.ArgumentParser(description="GARD 汽水循环㶲分析")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="frames 原始测点 JSON；--si 时为 SI 字段 JSON")
    source.add_argument("--history", help="原始 Parquet 目录")
    parser.add_argument("--si", action="store_true")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--pressure-basis", choices=["absolute", "gauge"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    timestamp = None
    if args.history:
        tables = evaluate_window(
            args.history, args.start, args.end, args.pressure_basis
        )
        timestamp = args.start
    elif args.si:
        row = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
        tables = cal_property(pd.DataFrame([row]))
    else:
        df, timestamp, inputs = build_online_dataframe(
            args.input, raw_pressure_basis=args.pressure_basis
        )
        tables = cal_property(df)
        tables["inputs"] = inputs
    write_tables(tables, args.output)
    output = Path(args.output)
    if "inputs" in tables:
        tables["inputs"].to_csv(
            output / "inputs.csv", index=False, encoding="utf-8-sig"
        )
    if "screening" in tables:
        tables["screening"].to_csv(
            output / "screening.csv", index=False, encoding="utf-8-sig"
        )
    (output / "result.json").write_text(
        json.dumps(
            build_output_json(tables, timestamp),
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        ),
        encoding="utf-8",
    )
    print(
        f"streams={len(tables['streams'])}, components={len(tables['components'])}, systems={len(tables['systems'])}"
    )
    print(f"output={output.resolve()}")
