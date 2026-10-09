"""设备只统计进出口流股；对外热量和功在 System 中记录。"""

from dataclasses import dataclass, field

from .stream import FlowState


@dataclass
class Device:
    name: str
    inlets: list[FlowState] = field(default_factory=list)
    outlets: list[FlowState] = field(default_factory=list)

    def add_inlet(self, stream):
        self.inlets.append(stream)

    def add_outlet(self, stream):
        self.outlets.append(stream)

    @property
    def mass_in(self):
        return sum(s.m_dot for s in self.inlets)

    @property
    def mass_out(self):
        return sum(s.m_dot for s in self.outlets)

    @property
    def energy_in(self):
        return sum(s.energy_flow for s in self.inlets)

    @property
    def energy_out(self):
        return sum(s.energy_flow for s in self.outlets)

    @property
    def exergy_in(self):
        return sum(s.exergy_flow for s in self.inlets)

    @property
    def exergy_out(self):
        return sum(s.exergy_flow for s in self.outlets)

    def mass_balance(self):
        return self.mass_in - self.mass_out

    def energy_balance(self):
        """流股能量净流入，不包含系统对外热量和功。"""
        return self.energy_in - self.energy_out

    def exergy_balance(self):
        """流股火用净流入，不等同于设备火用损失。"""
        return self.exergy_in - self.exergy_out
