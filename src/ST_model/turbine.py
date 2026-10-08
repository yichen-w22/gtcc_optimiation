from dataclasses import dataclass
from functools import cached_property

from src.working_fluid.steam_water import WaterSteamState

from src.base.converter import EnergyConverter

@dataclass
class Turbine(EnergyConverter):
    @cached_property
    def outlet_s(self) -> WaterSteamState:
        inlet = self.inlet
        outlet = self.outlet
        return WaterSteamState.from_Ps(
            P=outlet.P, 
            s=inlet.s,
            m_dot=outlet.m_dot,
            name=f"{self.name}_outlet_s",
            ref=inlet.ref 
        )

    @cached_property
    def specific_work(self) -> float:
        inlet_h = self.inlet.h 
        outlet_h = self.outlet.h 
        return (inlet_h - outlet_h)

    @cached_property
    def power_output(self) -> float:
        mass_flow = self.outlet.m_dot 
        return (mass_flow * self.specific_work)

    @cached_property
    def isentropic_efficiency(self) -> float:
        inlet_h = self.inlet.h 
        denominator = (inlet_h - self.outlet_s.h)
        return (self.specific_work / denominator)

    @cached_property
    def exergy_efficiency(self) -> float:
        inlet_exergy = self.inlet.exergy 
        outlet_exergy = self.outlet.exergy 
        exergy_drop = (inlet_exergy - outlet_exergy)
        return (self.specific_work / exergy_drop)


