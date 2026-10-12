from importlib import import_module

import numpy as np
import pandas as pd
import pytest

from gard.data_io import (
    BINDING_COLUMNS, clean_history, convert_values, load_inputs,
    prepare_inputs, read_history, summarize_history, validate_bindings,
)


@pytest.fixture
def bindings():
    return pd.DataFrame([
        ["test.P", "absolute", "MPa", "MPa", 1e6, 0, "absolute"],
        ["test.gauge.P", "gauge", "MPa", "MPa", 1e6, 0, "gauge"],
        ["test.unknown.P", "unknown", "MPa", "MPa", 1e6, 0, "unknown"],
        ["test.T", "temperature", "℃", "℃", 1, 273.15, None],
        ["test.m_dot", "flow", "t/h", "t/h", 1 / 3.6, 0, None],
        ["test.bad.T", "bad_unit", "℃", "%", 1, 273.15, None],
    ], columns=BINDING_COLUMNS)


@pytest.fixture
def window():
    start = pd.Timestamp("2024-06-01T08:00:00+08:00")
    return start, start + pd.Timedelta(minutes=30)


def history(start, end, value=2.0, freq="30s", code="absolute"):
    return pd.DataFrame({
        "time": pd.date_range(start, end, freq=freq, inclusive="left"),
        "code": code, "value": value,
    })


def test_per_point_pressure_and_units_without_quality_or_derived_values(bindings, monkeypatch):
    module = import_module("gard.systems.hrsg1_hp.data")
    monkeypatch.setattr(module, "POINT_BINDINGS", bindings)
    values = {"absolute": 1, "gauge": 1, "unknown": 1, "temperature": 100,
              "flow": 360, "bad_unit": 50, "hp1_pump1.power": 1000}
    row = prepare_inputs("hrsg1_hp", values, atmospheric_pressure=101000)
    assert isinstance(row, dict)
    assert row == {
        "test.P": 1e6, "test.gauge.P": 1101000, "test.unknown.P": None,
        "test.T": 373.15, "test.m_dot": 100, "test.bad.T": None,
    }
    assert convert_values(values, bindings)["test.gauge.P"] is None
    assert values["temperature"] == 100


def test_invalid_values_and_configurations_return_none_or_raise(bindings):
    row = convert_values({"absolute": -1, "temperature": np.inf, "flow": "invalid"}, bindings)
    assert all(value is None for value in row.values())
    with pytest.raises(ValueError, match="atmospheric_pressure"):
        convert_values({}, bindings, atmospheric_pressure=-1)
    bindings.loc[0, "pressure_basis"] = "typo"
    with pytest.raises(ValueError, match="pressure_basis"):
        validate_bindings(bindings)


@pytest.mark.parametrize("system", [
    "gt1", "gt2", "hrsg1_hp", "hrsg1_ip", "hrsg1_lp",
    "hrsg2_hp", "hrsg2_ip", "hrsg2_lp", "st", "condenser", "cooling", "heating",
])
def test_all_systems_have_valid_configuration_and_mpa_is_absolute(system):
    bindings = import_module(f"gard.systems.{system}.data").POINT_BINDINGS
    validate_bindings(bindings)
    assert bindings.loc[bindings.unit.str.lower() == "mpa", "pressure_basis"].eq("absolute").all()


def test_aggregation_uses_duration_instead_of_sample_count(window):
    start, end = window
    # Every minute has 10 s at 10 and 50 s at 20: average is 18 1/3, not 15.
    times = []
    values = []
    for minute in range(30):
        times.extend([start + pd.Timedelta(minutes=minute), start + pd.Timedelta(minutes=minute, seconds=10)])
        values.extend([10, 20])
    raw = pd.DataFrame({"time": times, "code": "absolute", "value": values})
    result = summarize_history(raw, start, end)
    assert result["absolute"] == pytest.approx((10 * 10 + 20 * 50) / 60)


def test_coverage_requires_five_valid_bins_and_does_not_bridge_gaps(window):
    start, end = window
    assert summarize_history(history(start, end), start, end)["absolute"] == 2
    assert summarize_history(history(start, end - pd.Timedelta(minutes=5)), start, end)["absolute"] == 2
    assert summarize_history(history(start, end - pd.Timedelta(minutes=10)), start, end)["absolute"] is None
    assert summarize_history(history(start, end, freq="2min"), start, end)["absolute"] is None
    assert summarize_history(history(start, start + pd.Timedelta(seconds=30)), start, end)["absolute"] is None


def test_invalid_duplicate_records_interrupt_previous_values(window):
    start, end = window
    raw = history(start, end)
    raw.loc[raw.time < start + pd.Timedelta(minutes=10), "value"] = np.nan
    # A later invalid record at the same timestamp must win over the earlier valid one.
    original = history(start, start + pd.Timedelta(minutes=10))
    raw = pd.concat([original, raw], ignore_index=True)
    cleaned = clean_history(raw)
    assert len(cleaned) == 60
    assert pd.isna(cleaned.iloc[0].value)
    assert summarize_history(raw, start, end)["absolute"] is None


def test_parquet_loading_respects_timezones_boundaries_and_missing_files(tmp_path, bindings, window, monkeypatch):
    start, end = window
    raw = history(start - pd.Timedelta(seconds=30), end, value=100, code="temperature")
    raw = pd.concat([raw, pd.DataFrame({"time": [end], "code": ["temperature"], "value": [999]})])
    pd.DataFrame({
        "tbname": raw.code, "ts": raw.time.array.asi8, "col0": raw.value,
    }).to_parquet(tmp_path / "description+temperature.parquet", index=False)
    module = import_module("gard.systems.hrsg1_hp.data")
    monkeypatch.setattr(module, "POINT_BINDINGS", bindings)
    naive = load_inputs("hrsg1_hp", tmp_path, "2024-06-01 08:00:00", "2024-06-01 08:30:00")
    utc = load_inputs("hrsg1_hp", tmp_path, start.tz_convert("UTC"), end.tz_convert("UTC"))
    assert naive == utc
    assert naive["test.T"] == 373.15
    assert naive["test.P"] is None
    assert set(naive) == set(bindings.field)
    with pytest.raises(ValueError, match="30-minute"):
        load_inputs("hrsg1_hp", tmp_path, start, start + pd.Timedelta(minutes=15))


def test_file_matching_is_exact_and_duplicate_matches_raise(tmp_path, bindings, window):
    start, end = window
    raw = pd.DataFrame({"tbname": ["absolute"], "ts": [start.value], "col0": [1.0]})
    raw.to_parquet(tmp_path / "description+absolute_other.parquet", index=False)
    assert read_history(tmp_path, start, end, bindings).empty
    raw.to_parquet(tmp_path / "first+absolute.parquet", index=False)
    raw.to_parquet(tmp_path / "second+absolute.parquet", index=False)
    with pytest.raises(ValueError, match="Multiple Parquet"):
        read_history(tmp_path, start, end, bindings)
