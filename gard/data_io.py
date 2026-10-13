"""共用测点数据准备；仅返回 SI 数值，不计算派生量或生成质量表。

原始 Parquet 使用 tbname / ts / col0，ts 是 Unix 纳秒时间戳。
无时区的输入时间按 Asia/Shanghai 解释；有时区的时间保留其含义。
每次加载一个半小时窗口：先算五分钟时间加权均值，再汇总合格窗口。
测量值最多保持 60 秒，不跨长缺口补齐；五分钟覆盖至少 80%，
半小时至少包含五个合格窗口。缺失或无法转换的字段返回 None。
"""

from importlib import import_module
from pathlib import Path
import math

import numpy as np
import pandas as pd
from gard.config import DEFAULT_ENVIRONMENT_PRESSURE


MAX_HOLD = pd.Timedelta(seconds=60)
BIN_SIZE = pd.Timedelta(minutes=5)
WINDOW_SIZE = pd.Timedelta(minutes=30)
MIN_BIN_COVERAGE = 0.8
MIN_VALID_BINS = 5
BINDING_COLUMNS = (
    "field", "code", "expected_unit", "unit", "scale", "offset", "pressure_basis",
)
PRESSURE_UNITS = {"pa", "kpa", "mpa", "pa.a", "kpa.a", "mpa.a", "pa.g", "kpa.g", "mpa.g"}


def _unit(value):
    return str(value).strip().lower().replace("°c", "℃")


def _finite(value):
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return result if math.isfinite(result) else None


def _window(start, end, timezone):
    def timestamp(value):
        result = pd.Timestamp(value)
        if pd.isna(result):
            raise ValueError("start/end must be valid timestamps")
        if result.tzinfo is None:
            result = result.tz_localize(timezone)
        return result.tz_convert("UTC")

    start, end = timestamp(start), timestamp(end)
    if end - start != WINDOW_SIZE:
        raise ValueError("load_inputs requires a 30-minute window")
    return start, end


def _bindings(system_name):
    if not isinstance(system_name, str) or not system_name.isidentifier():
        raise ValueError("system_name must be a system directory name")
    bindings = import_module(f"gard.systems.{system_name}.data").POINT_BINDINGS
    validate_bindings(bindings)
    return bindings


def validate_bindings(bindings):
    """检查配置结构；单位不匹配的测点在转换时保留为空。"""
    if not set(BINDING_COLUMNS).issubset(bindings.columns):
        raise ValueError(f"POINT_BINDINGS requires columns: {BINDING_COLUMNS}")
    if bindings["field"].duplicated().any():
        raise ValueError("POINT_BINDINGS contains duplicate model fields")
    for binding in bindings.itertuples(index=False):
        if not all(isinstance(value, str) and value.strip() for value in (binding.field, binding.code)):
            raise ValueError("field and code must be nonempty strings")
        if _finite(binding.scale) is None or _finite(binding.offset) is None:
            raise ValueError(f"Invalid conversion coefficients: {binding.field}")
        if _unit(binding.expected_unit) in PRESSURE_UNITS:
            if binding.pressure_basis not in ("gauge", "absolute", "unknown"):
                raise ValueError(f"Invalid pressure_basis: {binding.field}")
        elif not pd.isna(binding.pressure_basis):
            raise ValueError(f"Non-pressure field requires pressure_basis=None: {binding.field}")


def read_history(directory, start, end, bindings, *, timezone="Asia/Shanghai"):
    """按编码读取窗口记录及最多 60 秒的窗口前记录，不加载全量历史。"""
    start, end = _window(start, end, timezone)
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"Raw data directory not found: {directory}")
    files = {}
    for path in directory.glob("*.parquet"):
        code = path.stem.rsplit("+", 1)[-1]
        files.setdefault(code, []).append(path)

    frames = []
    for code in bindings["code"].unique():
        matches = files.get(code, [])
        if len(matches) > 1:
            raise ValueError(f"Multiple Parquet files match point code: {code}")
        if not matches:
            continue
        frame = pd.read_parquet(
            matches[0], engine="pyarrow", columns=["tbname", "ts", "col0"],
            filters=[
                ("tbname", "==", code),
                ("ts", ">=", (start - MAX_HOLD).value),
                ("ts", "<", end.value),
            ],
        )
        if not frame.empty:
            frames.append(pd.DataFrame({
                "time": pd.to_datetime(frame["ts"], unit="ns", utc=True, errors="coerce"),
                "code": frame["tbname"],
                "value": frame["col0"],
            }))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["time", "code", "value"])


def clean_history(raw):
    """同一编码同一时间保留最后一条；无效值保留为缺失以中断前值保持。"""
    raw = raw[["time", "code", "value"]].copy()
    raw["time"] = pd.to_datetime(raw["time"], utc=True, errors="coerce").astype("datetime64[ns, UTC]")
    raw["value"] = pd.to_numeric(raw["value"], errors="coerce")
    raw.loc[~np.isfinite(raw["value"]), "value"] = np.nan
    return (
        raw.dropna(subset=["time", "code"])
        .drop_duplicates(["code", "time"], keep="last")
        .sort_values(["code", "time"], kind="stable")
        .reset_index(drop=True)
    )


def summarize_history(raw, start, end, *, timezone="Asia/Shanghai"):
    """返回按测点编码索引的时间加权统计值，不输出质量表。"""
    start, end = _window(start, end, timezone)
    raw = clean_history(raw)
    raw = raw[(raw["time"] >= start - MAX_HOLD) & (raw["time"] < end)]
    result = {}
    edges = pd.date_range(start, end, freq=BIN_SIZE).as_unit("ns").asi8
    for code, frame in raw.groupby("code", sort=False):
        times = frame["time"].array.asi8
        values = frame["value"].to_numpy(dtype=float)
        # 前值最多保持 MAX_HOLD，下一条无效记录同样中断保持。
        stops = np.minimum(np.r_[times[1:], end.value], times + MAX_HOLD.value)
        weighted_sum, coverage, valid_bins = 0.0, 0, 0
        finite = np.isfinite(values)
        for left, right in zip(edges[:-1], edges[1:]):
            durations = np.maximum(0, np.minimum(stops, right) - np.maximum(times, left))
            durations = durations[finite]
            covered = int(durations.sum())
            if covered >= MIN_BIN_COVERAGE * BIN_SIZE.value:
                weighted_sum += float(np.dot(values[finite], durations))
                coverage += covered
                valid_bins += 1
        result[code] = weighted_sum / coverage if valid_bins >= MIN_VALID_BINS else None
    return result


def convert_values(point_values, bindings, *, atmospheric_pressure=None):
    """按测点配置生成 SI 字典；大气压力单位为 Pa，仅用于表压转换。"""
    validate_bindings(bindings)
    atmosphere = _finite(atmospheric_pressure)
    if atmospheric_pressure is not None and (atmosphere is None or atmosphere <= 0):
        raise ValueError("atmospheric_pressure must be a positive finite value in Pa")
    row = {}
    for binding in bindings.itertuples(index=False):
        value = _finite(point_values.get(binding.code))
        if value is None or _unit(binding.unit) != _unit(binding.expected_unit):
            row[binding.field] = None
            continue
        value = value * binding.scale + binding.offset
        if _unit(binding.expected_unit) in PRESSURE_UNITS:
            if binding.pressure_basis == "unknown":
                value = None
            elif binding.pressure_basis == "gauge":
                value = value + atmosphere if atmosphere is not None else None
            if value is not None and value <= 0:
                value = None
        row[binding.field] = _finite(value)
    return row


def prepare_inputs(system_name, point_values, *, atmospheric_pressure=DEFAULT_ENVIRONMENT_PRESSURE):
    """将已有原始测点数值转换为 SI 字典，不生成派生字段。"""
    return convert_values(point_values, _bindings(system_name), atmospheric_pressure=atmospheric_pressure)


def load_inputs(system_name, directory, start, end, *, atmospheric_pressure=DEFAULT_ENVIRONMENT_PRESSURE, timezone="Asia/Shanghai", hp_config=None, ip_config=None, lp_config=None):
    """加载一个半小时工况，仅返回 row；压力基准由系统 data.py 决定。"""
    bindings = _bindings(system_name)
    raw = read_history(directory, start, end, bindings, timezone=timezone)
    values = summarize_history(raw, start, end, timezone=timezone)
    row = convert_values(values, bindings, atmospheric_pressure=atmospheric_pressure)
    if system_name in {"hrsg1_hp", "hrsg2_hp", "hrsg1_ip", "hrsg2_ip", "hrsg1_lp", "hrsg2_lp"}:
        from gard.systems.hrsg_hp import HPPreparationConfig, qualify_current_history
        level=system_name.split('_')[1]
        if level=='hp':
            operation_config=hp_config or HPPreparationConfig()
        elif level=='ip':
            from gard.systems.hrsg_ip import IPPreparationConfig
            operation_config=ip_config or IPPreparationConfig()
        else:
            from gard.systems.hrsg_lp import LPPreparationConfig
            operation_config=lp_config or LPPreparationConfig()
        prefix = system_name.split("_")[0]
        pump_stem = 'lp_recirc_pump' if level=='lp' else f'{level}_pump'
        codes = tuple(bindings.loc[bindings.field == f"{prefix}.{pump_stem}{j}.current", "code"].iloc[0]
                      if (bindings.field == f"{prefix}.{pump_stem}{j}.current").any() else "" for j in (1, 2))
        # Custom bindings used by callers may omit the operation channels.
        if any(codes):
            operation_flow=row.get(f"{prefix}.hp_main.m_dot")
            if level=='ip':
                feed=_finite(row.get(f'{prefix}.ip_feed.m_dot'))
                spray=_finite(row.get(f'{prefix}.rh_spray.m_dot'))
                operation_flow=feed+spray if feed is not None and feed>=0 and spray is not None and spray>=0 else None
            elif level=='lp':
                operation_flow=_finite(row.get(f'{prefix}.lp_recirc_in.m_dot'))
            row[f"{prefix}.{level}_operation_status"] = qualify_current_history(
                raw, start, end, codes, operation_flow, operation_config, timezone)
            row[f"{prefix}.{level}_operation_source"] = "raw_history"
            row[f"{prefix}.{level}_operation_parameters"] = {
                "current_threshold_A": operation_config.current_threshold_A,
                "allow_single_current_inference": operation_config.allow_single_current_inference,
            }
    return row
