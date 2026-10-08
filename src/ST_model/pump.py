from dataclasses import dataclass
from functools import cached_property

from src.working_fluid.steam_water import WaterSteamState

from src.base.converter import EnergyConverter


@dataclass
class Pump(EnergyConverter):
    @cached_property
    def outlet_s(self) -> WaterSteamState:
        inlet = self.inlet
        outlet = self.outlet
        return WaterSteamState.from_Ps(
            P=outlet.P if outlet is not None else None,
            s=inlet.s if inlet is not None else None,
            m_dot=outlet.m_dot if outlet is not None else None,
            name=f"{self.name}_outlet_s",
            ref=inlet.ref if inlet is not None else None,
        )

    @cached_property
    def specific_work(self) -> float | None:
        inlet_h = self.inlet.h if self.inlet is not None else None
        outlet_h = self.outlet.h if self.outlet is not None else None
        return (outlet_h - inlet_h)

    @cached_property
    def power_input(self) -> float | None:
        mass_flow = self.outlet.m_dot if self.outlet is not None else None
        return (mass_flow * self.specific_work)

    @cached_property
    def isentropic_efficiency(self) -> float | None:
        inlet_h = self.inlet.h if self.inlet is not None else None
        numerator = (self.outlet_s.h - inlet_h)
        denominator = self.specific_work
        return (numerator / denominator)


from src.base.converter import AccountingConverter
import pandas as pd

class AccountingPump(AccountingConverter, Pump):

    def __init__(self, name, inlet, outlet, system, power=None):
        super().__init__(
            name,
            "pump",
            system,
            work=None if power is None else -power,
            note="绝热泵及驱动整体；power 为独立输入功率 W，缺失不以电流替代",
        )
        self.add_inlet(inlet)
        self.add_outlet(outlet)
        self.inlet = inlet
        self.outlet = outlet

    def result(self):
        result = super().result()
        result["fluid_energy_rise"] = None
        result["fluid_exergy_rise"] = None
        result["isentropic_efficiency"] = None
        if self.outlet.energy_flow is not None and self.inlet.energy_flow is not None:
            result["fluid_energy_rise"] = (
                self.outlet.energy_flow - self.inlet.energy_flow
            )
        if self.outlet.exergy_flow is not None and self.inlet.exergy_flow is not None:
            result["fluid_exergy_rise"] = (
                self.outlet.exergy_flow - self.inlet.exergy_flow
            )
        if (
            self.outlet.P is not None
            and self.inlet.s is not None
            and (self.outlet.h is not None)
        ):
            ideal = WaterSteamState.from_Ps(self.outlet.P, self.inlet.s)
            result["isentropic_efficiency"] = (float(ideal.h) - self.inlet.h) / (
                self.outlet.h - self.inlet.h
            )
        return result


