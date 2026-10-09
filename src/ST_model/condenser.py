from dataclasses import dataclass


from src.base.device import Device

@dataclass
class Condenser(Device):
    @property
    def heat_rejection(self):
        return self.energy_in - self.energy_out
