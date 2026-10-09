from src.base.system import System
from src.GT_model.components.chamber import Chamber
from src.GT_model.components.compressor import Compressor
from src.GT_model.components.turbine import Turbine
from src.GT_model.config import GTModelConfig


class GTModel(System):
    """Gas-turbine system with a fresh connected device graph per evaluation."""

    def __init__(
        self,
        state_1=None,
        compressor_outlet=None,
        fuel=None,
        state_4=None,
        config=None,
        actual_power=None,
        *,
        total_pressure_recovery: float | None = None,
        name="GT",
        fuel_chemical_exergy=None,
        hrsg_outlet=None,
    ):
        self.name = name
        self.state_1 = state_1
        self.compressor_outlet = compressor_outlet
        self.fuel = fuel
        self.state_4 = state_4
        self.config = config if config is not None else GTModelConfig()
        self.actual_power = actual_power
        self.total_pressure_recovery = total_pressure_recovery
        self.fuel_chemical_exergy = fuel_chemical_exergy
        self.hrsg_outlet = hrsg_outlet

    @property
    def hrsg_inlet(self):
        return self.state_4

    @property
    def work(self):
        return self.actual_power if self.actual_power is not None else self.net_power

    def energy_balance(self):
        # 流股焓只包含显热，燃料有效化学释热单独计入。
        return super().energy_balance() + self.chamber.energy_source

    def exergy_balance(self):
        # 流股只计算物理火用，燃料化学火用单独计入。
        return super().exergy_balance() + self.chamber.exergy_source

    @property
    def devices(self):
        compressor = Compressor(
            name=f"{self.name}_compressor",
            inlet_gas=self.state_1,
            outlet_gas=self.compressor_outlet,
            bleeding_mass_fraction=self.config.compressor_bleeding_mass_fraction,
            bleeding_pressure_fraction=self.config.compressor_bleeding_pressure_fraction,
            bleeding_energy_fraction=self.config.compressor_bleeding_energy_fraction,
        )
        chamber = Chamber(
            name=f"{self.name}_chamber",
            inlet_air=compressor.state_2,
            inlet_fuel=self.fuel,
            outlet_composition=getattr(self.state_4, "composition", None),
            total_pressure_recovery=self.total_pressure_recovery,
            combustion_efficiency=self.config.combustion_efficiency,
            bleeding=compressor.bleeding,
            fuel_chemical_exergy=self.fuel_chemical_exergy,
        )
        turbine = Turbine(
            name=f"{self.name}_turbine",
            state_3_c=chamber.state_3_c,
            state_4=self.state_4,
        )
        return [compressor, chamber, turbine]

    @property
    def compressor(self):
        return self.devices[0]

    @property
    def chamber(self):
        return self.devices[1]

    @property
    def turbine(self):
        return self.devices[2]

    @property
    def state_2(self):
        return self.compressor.state_2

    @property
    def state_3(self):
        return self.chamber.state_3

    @property
    def state_3_c(self):
        return self.chamber.state_3_c

    @property
    def flue_gas_flow(self):
        return getattr(self.state_4, "m_dot", None)

    @property
    def net_power(self):
        compressor, _, turbine = self.devices
        return turbine.power - compressor.power

    @property
    def fuel_energy(self):
        return self.chamber.fuel_lhv * getattr(self.fuel, 'm_dot', None)

    @property
    def thermal_efficiency(self):
        return self.actual_power / self.fuel_energy

    @property
    def generation_power_share(self):
        return self.thermal_efficiency

    @property
    def compressor_power_share(self):
        return self.compressor.power / self.fuel_energy

    @property
    def exhaust_loss_share(self):
        # Remaining fuel input also contains other losses; retained for compatibility.
        return 1.0 - self.generation_power_share
