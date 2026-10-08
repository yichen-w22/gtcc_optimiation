from dataclasses import dataclass

from src.base.converter import EnergyConverter


@dataclass
class Mixer(EnergyConverter):
    pass


from src.base.converter import AccountingConverter

class AccountingMixer(AccountingConverter, Mixer):

    def __init__(self, name, inlet1, inlet2, outlet, system):
        super().__init__(name, "mixer", system, note="稳态、绝热、无轴功混合")
        self.add_inlet(inlet1)
        self.add_inlet(inlet2)
        self.add_outlet(outlet)


