from dataclasses import dataclass

from src.working_fluid.steam_water import WaterSteamState

from src.base.device import Device

@dataclass
class Turbine(Device):

    @property
    def outlet_s(self) -> WaterSteamState:
        inlet = self.inlets[0]
        outlet = self.outlets[0]
        if inlet is None or outlet is None:
            return WaterSteamState(name=f"{self.name}_outlet_s")
        return WaterSteamState.from_Ps(
            P=outlet.P,
            s=inlet.s,
            m_dot=outlet.m_dot,
            name=f"{self.name}_outlet_s",
            ref=inlet.ref
        )

    @property
    def specific_work(self) -> float:
        return getattr(self.inlets[0], 'h', None) - getattr(self.outlets[0], 'h', None)

    @property
    def power_output(self) -> float:
        return self.energy_in - self.energy_out

    @property
    def isentropic_efficiency(self) -> float:
        inlet_h = getattr(self.inlets[0], "h", None)
        denominator = (inlet_h - self.outlet_s.h)
        return self.specific_work / denominator

    @property
    def exergy_efficiency(self) -> float:
        exergy_drop = (getattr(self.inlets[0], 'exergy', None) - getattr(self.outlets[0], 'exergy', None))
        return self.specific_work / exergy_drop


