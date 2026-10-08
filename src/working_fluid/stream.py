"""公共流股、部件和边界账本；系统拓扑在 systems 中显式定义。"""

from dataclasses import asdict, dataclass

import pandas as pd

from src.working_fluid.fluid import ReferenceEnv
from src.working_fluid.steam_water import WaterSteamState


@dataclass(frozen=True)
class Stream:
    name: str
    P: float | None
    T: float | None
    m_dot: float | None
    h: float | None
    s: float | None
    e: float | None
    T0: float
    P0: float
    source: str = ""
    note: str = ""

    @property
    def energy_flow(self):
        if self.m_dot == 0:
            return 0.0
        if self.m_dot is None or self.h is None:
            return None
        return self.m_dot * self.h

    @property
    def exergy_flow(self):
        if self.m_dot == 0:
            return 0.0
        if self.m_dot is None or self.e is None:
            return None
        return self.m_dot * self.e

    def record(self):
        result = asdict(self)
        result["energy_flow"] = self.energy_flow
        result["exergy_flow"] = self.exergy_flow
        result["status"] = "complete"
        if self.m_dot is None or self.energy_flow is None or self.exergy_flow is None:
            result["status"] = "partial"
        if self.P is None and self.T is None and self.h is None and self.m_dot is None:
            result["status"] = "unavailable"
        if self.m_dot is not None and self.m_dot < 0:
            result["status"] = "invalid"
        result["missing_fields"] = []
        if self.m_dot is None:
            result["missing_fields"].append("m_dot")
        if self.h is None or self.s is None:
            result["missing_fields"].append("state: P+T / P+h / P+x")
        return result


def water(
    name, *, P=None, T=None, m_dot=None, h=None, x=None, ref=None, source="", note=""
):
    ref = ref or ReferenceEnv(298.15, 101325.0)
    P = None if pd.isna(P) else float(P)
    T = None if pd.isna(T) else float(T)
    m_dot = None if pd.isna(m_dot) else float(m_dot)
    h = None if pd.isna(h) else float(h)
    x = None if pd.isna(x) else float(x)
    if P is not None and P <= 0:
        raise ValueError(f"{name}: 必须使用正的绝对压力 Pa")
    if x is not None and not 0 <= x <= 1:
        raise ValueError(f"{name}: 干度必须在 0 到 1 之间")
    if h is not None:
        state = WaterSteamState.from_Ph(P, h)
    elif x is not None:
        state = WaterSteamState.from_Px(P, x)
    elif T is not None and T >= 273.15:
        state = WaterSteamState.from_PT(P, T)
    else:
        state = WaterSteamState(P=P, T=T)
    reference = WaterSteamState.from_PT(ref.P0, ref.T0)
    e = None
    if state.h is not None and state.s is not None:
        e = state.h - reference.h - ref.T0 * (state.s - reference.s)
    return Stream(
        name,
        P,
        state.T,
        m_dot,
        None if state.h is None else float(state.h),
        None if state.s is None else float(state.s),
        e,
        ref.T0,
        ref.P0,
        source,
        note,
    )


class StreamBook(dict):
    def __init__(self, row, ref):
        super().__init__()
        self.row = row
        self.ref = ref
        self.records = []
        self.systems = {}

    def add(self, name, note=""):
        if name in self:
            raise ValueError("流股重复定义: " + name)
        row = self.row
        stream = water(
            name,
            P=row.get(name + ".P"),
            T=row.get(name + ".T"),
            m_dot=row.get(name + ".m_dot"),
            h=row.get(name + ".h"),
            x=row.get(name + ".x"),
            ref=self.ref,
            source=row.get(name + ".source", "输入字段见同名 P/T/m_dot/h/x"),
            note=note,
        )
        self[name] = stream
        self.records.append(stream.record())

    def add_system(self, name, streams):
        if name in self.systems or self.keys() & streams.keys():
            raise ValueError("系统或流股重复定义: " + name)
        self.systems[name] = streams
        self.update(streams)
        self.records.extend(streams.records)

    def connect(self, ports):
        if self.keys() & ports.keys():
            raise ValueError("对外连接不能覆盖本系统流股")
        return dict(self) | ports

    def table(self):
        return pd.DataFrame(self.records)
