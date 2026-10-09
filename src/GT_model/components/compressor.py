

from src.base.device import Device
from src.working_fluid.gas import GasState


class Compressor(Device):
    def __init__(
        self, name, inlet_gas=None, outlet_gas=None,
        bleeding_mass_fraction=0.0, bleeding_pressure_fraction=1.0,
        bleeding_energy_fraction=1.0,
    ):
        self.name = name
        self.inlet_gas = inlet_gas
        self.outlet_gas = outlet_gas
        self.bleeding_mass_fraction = bleeding_mass_fraction
        self.bleeding_pressure_fraction = bleeding_pressure_fraction
        self.bleeding_energy_fraction = bleeding_energy_fraction

    @property
    def inlets(self):
        return [self.inlet_gas or GasState(name=f"{self.name}_inlet")]

    @property
    def outlets(self):
        return [self.state_2, self.bleeding]

    @property
    def state_2s(self) -> GasState:
        if self.inlet_gas is None or self.outlet_gas is None:
            return GasState(name=f"{self.name}_state_2s")
        return self.inlet_gas.__class__.from_Ps(
            P=self.outlet_gas.P,
            s=self.inlet_gas.s,
            m_dot=self.outlet_gas.m_dot,
            composition=self.inlet_gas.composition,
            name=f"{self.name}_state_2s",
            ref=self.inlet_gas.ref,
        )

    @property
    def isentropic_efficiency(self) -> float | None:
        return (self.state_2s.h - getattr(self.inlet_gas, 'h', None)) / self.delta_h

    @property
    def exergy_efficiency(self) -> float | None:
        return (getattr(self.outlet_gas, 'exergy', None) - getattr(self.inlet_gas, 'exergy', None)) / self.delta_h

    @property
    def isentropic_loss(self) -> float | None:
        return (getattr(self.outlet_gas, 'h', None) - self.state_2s.h) * getattr(self.outlet_gas, 'm_dot', None)

    @property
    def bleeding(self) -> GasState:
        if self.inlet_gas is None or self.outlet_gas is None:
            return GasState(name=f"{self.name}_bleeding")
        if not 0 <= self.bleeding_mass_fraction <= 1:
            raise ValueError("bleeding_mass_fraction must be between 0 and 1")
        bleeding_mass = (self.inlet_gas.m_dot * self.bleeding_mass_fraction)
        bleeding_pressure = (sum([self.inlet_gas.P, (self.outlet_gas.P - self.inlet_gas.P) * self.bleeding_pressure_fraction]))
        bleeding_energy = (sum([self.inlet_gas.h, self.delta_h * self.bleeding_energy_fraction]))
        return GasState.from_Ph(
            P=bleeding_pressure,
            h=bleeding_energy,
            m_dot=bleeding_mass,
            composition=self.inlet_gas.composition,
            name=f"{self.name}_bleeding",
            ref=self.inlet_gas.ref,
        )

    @property
    def state_2(self) -> GasState:
        if self.inlet_gas is None or self.outlet_gas is None:
            return GasState(name=f"{self.name}_state_2")
        m_dot = (self.inlet_gas.m_dot * (1.0 - self.bleeding_mass_fraction))
        return self.outlet_gas.__class__.from_TP(
            T=self.outlet_gas.T,
            P=self.outlet_gas.P,
            m_dot=m_dot,
            composition=self.outlet_gas.composition,
            name=f"{self.name}_state_2",
            ref=self.outlet_gas.ref,
        )

    @property
    def power(self) -> float | None:
        return self.energy_out - self.energy_in

    @property
    def delta_h(self) -> float | None:
        return getattr(self.outlet_gas, 'h', None) - getattr(self.inlet_gas, 'h', None)
