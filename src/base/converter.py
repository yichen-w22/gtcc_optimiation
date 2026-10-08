from dataclasses import dataclass, field
from functools import cached_property
from typing import List

from src.working_fluid.fluid import FlowState

@dataclass
class EnergyConverter:
    name: str
    inlets: List[FlowState] = field(default_factory=list)
    outlets: List[FlowState] = field(default_factory=list)

    def add_inlet(self, stream: FlowState):
        self.inlets.append(stream)

    def add_outlet(self, stream: FlowState):
        self.outlets.append(stream)

    @cached_property
    def mass_in(self):
        return sum((s.m_dot for s in self.inlets))

    @cached_property
    def mass_out(self):
        return sum((s.m_dot for s in self.outlets))

    @cached_property
    def energy_in(self):
        return sum((s.energy_flow for s in self.inlets))

    @cached_property
    def energy_out(self):
        return sum((s.energy_flow for s in self.outlets))

    @cached_property
    def exergy_in(self):
        return sum((s.exergy_flow for s in self.inlets))

    @cached_property
    def exergy_out(self):
        return sum((s.exergy_flow for s in self.outlets))

    @cached_property
    def mass_balance(self):
        return (self.mass_in - self.mass_out)

    @cached_property
    def energy_balance(self):
        return (self.energy_in - self.energy_out)

    @cached_property
    def exergy_balance(self):
        return (self.exergy_in - self.exergy_out)

    @cached_property
    def inlet(self):
        return self.inlets[0] if self.inlets else None

    @cached_property
    def outlet(self):
        return self.outlets[0] if self.outlets else None

