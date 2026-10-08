from dataclasses import dataclass
from functools import cached_property
from typing import Optional


@dataclass(frozen=True)
class ReferenceEnv:
    T0: float
    P0: float


def create_ref_env(T0, P0) -> ReferenceEnv:
    T0 = float(T0)
    P0 = float(P0)
    return ReferenceEnv(T0=T0, P0=P0)


@dataclass
class FlowState:
    T: Optional[float] = None
    P: Optional[float] = None
    m_dot: Optional[float] = None
    h: Optional[float] = None
    s: Optional[float] = None
    ref: Optional[object] = None

    @cached_property
    def energy_flow(self):
        if self.m_dot == 0:
            return 0.0
        if self.m_dot is None or self.h is None:
            return None
        return self.m_dot * self.h

    @cached_property
    def exergy(self):
        raise NotImplementedError

    @cached_property
    def exergy_flow(self):
        if self.m_dot == 0:
            return 0.0
        if self.m_dot is None or self.exergy is None:
            return None
        return self.m_dot * self.exergy




