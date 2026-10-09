"""A plant contains systems and aggregates their external boundaries."""

from dataclasses import dataclass, field

from .system import System


@dataclass
class Plant:
    name: str
    systems: list[System] = field(default_factory=list)

    @property
    def system(self):
        """按名称索引整厂系统。"""
        return {system.name: system for system in self.systems}

    @property
    def work(self):
        return sum(system.work for system in self.systems)

    @property
    def heat(self):
        return sum(system.heat for system in self.systems)

    @property
    def heat_exergy(self):
        return sum(system.heat_exergy for system in self.systems)

    def add_system(self, system):
        self.systems.append(system)

    def mass_balance(self):
        return sum(system.mass_balance() for system in self.systems)

    def energy_balance(self):
        return sum(system.energy_balance() for system in self.systems)

    def exergy_balance(self):
        return sum(system.exergy_balance() for system in self.systems)
