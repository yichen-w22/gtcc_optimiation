

from src.base.device import Device
from src.working_fluid.gas import GasState


class Turbine(Device):
    def __init__(self, name, state_3_c=None, state_4=None):
        self.name = name
        self.state_3_c = state_3_c
        self.state_4 = state_4

    @property
    def inlets(self):
        return [self.state_3_c or GasState(name=f"{self.name}_inlet")]

    @property
    def outlets(self):
        return [self.state_4 or GasState(name=f"{self.name}_outlet")]

    @property
    def state_4s(self) -> GasState:
        if self.state_3_c is None or self.state_4 is None:
            return GasState(name=f"{self.name}_state_4s")
        return self.state_3_c.__class__.from_Ps(
            P=self.state_4.P,
            s=self.state_3_c.s,
            m_dot=self.state_4.m_dot,
            composition=self.state_3_c.composition,
            name=f"{self.name}_state_4s",
            ref=self.state_3_c.ref,
        )

    @property
    def isentropic_efficiency(self) -> float | None:
        inlet_h = getattr(self.state_3_c, "h", None)
        return (inlet_h - getattr(self.state_4, 'h', None)) / (inlet_h - self.state_4s.h)

    @property
    def exergy_efficiency(self) -> float | None:
        return self.power / (self.exergy_in - self.exergy_out)

    @property
    def isentropic_loss(self) -> float | None:
        return (getattr(self.state_4, 'h', None) - self.state_4s.h) * getattr(self.state_4, 'm_dot', None)

    @property
    def power(self) -> float | None:
        return self.energy_in - self.energy_out
