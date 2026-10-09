from dataclasses import dataclass

from src.working_fluid.steam_water import WaterSteamState

from src.base.device import Device


@dataclass
class Pump(Device):

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
        return getattr(self.outlets[0], 'h', None) - getattr(self.inlets[0], 'h', None)

    @property
    def power_input(self) -> float:
        return self.energy_out - self.energy_in

    @property
    def isentropic_efficiency(self) -> float:
        inlet_h = getattr(self.inlets[0], "h", None)
        numerator = (self.outlet_s.h - inlet_h)
        denominator = self.specific_work
        return numerator / denominator


