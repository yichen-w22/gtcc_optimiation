from dataclasses import dataclass
from functools import cached_property


from src.base.converter import EnergyConverter

@dataclass
class ThrottleValve(EnergyConverter):
    @cached_property
    def pressure_drop(self) -> float | None:
        inlet_pressure = self.inlet.P if self.inlet is not None else None
        outlet_pressure = self.outlet.P if self.outlet is not None else None
        return (inlet_pressure - outlet_pressure)



from src.base.converter import AccountingConverter

class AccountingThrottleValve(AccountingConverter, ThrottleValve):

    def __init__(self, name, inlet, outlet, system):
        super().__init__(name, "valve", system, note="绝热、无轴功；保留压降和能量残差")
        self.add_inlet(inlet)
        self.add_outlet(outlet)


