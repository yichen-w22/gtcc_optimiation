from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ReferenceEnv:
    T0: float
    P0: float = 101375.0


def create_ref_env(T0, P0=101375.0) -> ReferenceEnv:
    T0 = float(T0)
    P0 = float(P0)
    return ReferenceEnv(T0=T0, P0=P0)


@dataclass
class FlowState:
    name: str = ""
    T: Optional[float] = None
    P: Optional[float] = None
    m_dot: Optional[float] = None
    h: Optional[float] = None
    s: Optional[float] = None
    ref: Optional[ReferenceEnv] = None

    @property
    def energy_flow(self):
        return self.m_dot * self.h

    @property
    def exergy(self):
        return None

    @property
    def exergy_flow(self):
        return self.m_dot * self.exergy
