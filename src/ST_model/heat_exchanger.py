from dataclasses import dataclass
from functools import cached_property


from src.base.converter import EnergyConverter

# 在对换热器进行实现的时候，应该将进出接口的首个流股作为气体，其余流股作为水
@dataclass
class GasWaterHeatExchanger(EnergyConverter):

    # energy
    
    @cached_property
    def gas_energy_release(self):
        inlet_energy = self.inlet.energy_flow if self.inlet is not None else None
        outlet_energy = self.outlet.energy_flow if self.outlet is not None else None
        return (inlet_energy - outlet_energy)

    @cached_property
    def water_energy_absorption(self):
        energy_in = sum((stream.energy_flow for stream in self.inlets[1:]))
        energy_out = sum((stream.energy_flow for stream in self.outlets[1:]))
        return (energy_out - energy_in)

    @cached_property
    def energy_loss(self):
        return (self.gas_energy_release - self.water_energy_absorption)

    @cached_property
    def energy_balance_ratio(self):
        return (self.water_energy_absorption / self.gas_energy_release)

    @cached_property
    def energy_effectiveness(self): 
        inlet_energy = self.inlet.energy_flow if self.inlet is not None else None
        return (self.gas_energy_release / inlet_energy)
    
    # exergy

    @cached_property
    def gas_exergy_release(self):
        inlet_exergy = self.inlet.exergy_flow if self.inlet is not None else None
        outlet_exergy = self.outlet.exergy_flow if self.outlet is not None else None
        return (inlet_exergy - outlet_exergy)

    @cached_property
    def water_exergy_absorption(self):
        exergy_in = sum((stream.exergy_flow for stream in self.inlets[1:]))
        exergy_out = sum((stream.exergy_flow for stream in self.outlets[1:]))
        return (exergy_out - exergy_in)

    @cached_property
    def exergy_loss(self):
        return (self.gas_exergy_release - self.water_exergy_absorption)

    @cached_property
    def exergy_balance_ratio(self):
        return (self.water_exergy_absorption / self.gas_exergy_release)

    @cached_property
    def exergy_effectiveness(self): 
        inlet_exergy = self.inlet.exergy_flow if self.inlet is not None else None
        return (self.gas_exergy_release / inlet_exergy)

