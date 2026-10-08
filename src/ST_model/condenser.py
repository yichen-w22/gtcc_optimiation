from dataclasses import dataclass
from functools import cached_property


from src.base.converter import EnergyConverter

@dataclass
class Condenser(EnergyConverter):
    @cached_property
    def heat_rejection(self):
        inlet_energy = self.inlet.energy_flow 
        outlet_energy = self.outlet.energy_flow 
        return (inlet_energy - outlet_energy)
