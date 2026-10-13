from dataclasses import dataclass
import math

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
        inlet_h = getattr(self.inlets[0], 'h', None)
        outlet_h = getattr(self.outlets[0], 'h', None)
        if inlet_h is None or outlet_h is None:
            return None
        return outlet_h - inlet_h

    @property
    def power_input(self) -> float:
        """Fluid enthalpy-rise power (W), not measured electrical input."""
        if any(s.m_dot is None or (s.m_dot != 0 and s.h is None) for s in self.inlets + self.outlets):
            return None
        if all(s.m_dot == 0 for s in self.inlets + self.outlets):
            return 0.0
        return self.energy_out - self.energy_in

    @property
    def isentropic_efficiency(self) -> float:
        if any(s.m_dot is None or s.m_dot <= 0 for s in self.inlets + self.outlets):
            return None
        inlet_h = getattr(self.inlets[0], "h", None)
        outlet_h = getattr(self.outlets[0], "h", None)
        ideal_h = self.outlet_s.h
        if any(v is None or not math.isfinite(v) for v in (inlet_h, outlet_h, ideal_h)):
            return None
        numerator = ideal_h - inlet_h
        denominator = outlet_h - inlet_h
        if abs(denominator) < 1e-9:
            return None
        return numerator / denominator


