from dataclasses import dataclass, field

from src.base.device import Device
from src.working_fluid.gas import GasState
from src.working_fluid.steam_water import WaterSteamState

@dataclass
class HeatExchanger(Device):
    """???????????????? inlets/outlets ??"""


@dataclass
class GasWaterHeatExchanger(Device):
    gas_inlets: list[GasState] = field(default_factory=list)
    gas_outlets: list[GasState] = field(default_factory=list)
    water_inlets: list[WaterSteamState] = field(default_factory=list)
    water_outlets: list[WaterSteamState] = field(default_factory=list)

    def add_gas_inlet(self, stream: GasState):
        self.gas_inlets.append(stream)

    def add_gas_outlet(self, stream: GasState):
        self.gas_outlets.append(stream)

    def add_water_inlet(self, stream: WaterSteamState):
        self.water_inlets.append(stream)

    def add_water_outlet(self, stream: WaterSteamState):
        self.water_outlets.append(stream)

    @property
    def mass_in(self):
        return sum(
            stream.m_dot
            for stream in self.inlets + self.gas_inlets + self.water_inlets
        )

    @property
    def mass_out(self):
        return sum(
            stream.m_dot
            for stream in self.outlets + self.gas_outlets + self.water_outlets
        )

    @property
    def energy_in(self):
        return sum(
            stream.energy_flow
            for stream in self.inlets + self.gas_inlets + self.water_inlets
        )

    @property
    def energy_out(self):
        return sum(
            stream.energy_flow
            for stream in self.outlets + self.gas_outlets + self.water_outlets
        )

    @property
    def exergy_in(self):
        return sum(
            stream.exergy_flow
            for stream in self.inlets + self.gas_inlets + self.water_inlets
        )

    @property
    def exergy_out(self):
        return sum(
            stream.exergy_flow
            for stream in self.outlets + self.gas_outlets + self.water_outlets
        )

    # energy

    @property
    def gas_energy_release(self):
        inlet_energy = (sum((stream.energy_flow for stream in self.gas_inlets)))
        outlet_energy = (sum((stream.energy_flow for stream in self.gas_outlets)))
        return inlet_energy - outlet_energy

    @property
    def water_energy_absorption(self):
        energy_in = (sum((stream.energy_flow for stream in self.water_inlets)))
        energy_out = (sum((stream.energy_flow for stream in self.water_outlets)))
        return energy_out - energy_in

    @property
    def energy_loss(self):
        return self.gas_energy_release - self.water_energy_absorption

    @property
    def energy_balance_ratio(self):
        return self.water_energy_absorption / self.gas_energy_release

    @property
    def energy_effectiveness(self):
        inlet_energy = (sum((stream.energy_flow for stream in self.gas_inlets)))
        return self.gas_energy_release / inlet_energy

    # exergy

    @property
    def gas_exergy_release(self):
        inlet_exergy = (sum((stream.exergy_flow for stream in self.gas_inlets)))
        outlet_exergy = (sum((stream.exergy_flow for stream in self.gas_outlets)))
        return inlet_exergy - outlet_exergy

    @property
    def water_exergy_absorption(self):
        exergy_in = (sum((stream.exergy_flow for stream in self.water_inlets)))
        exergy_out = (sum((stream.exergy_flow for stream in self.water_outlets)))
        return exergy_out - exergy_in

    @property
    def exergy_loss(self):
        return self.gas_exergy_release - self.water_exergy_absorption

    @property
    def exergy_balance_ratio(self):
        return self.water_exergy_absorption / self.gas_exergy_release

    @property
    def exergy_effectiveness(self):
        inlet_exergy = (sum((stream.exergy_flow for stream in self.gas_inlets)))
        return self.gas_exergy_release / inlet_exergy
