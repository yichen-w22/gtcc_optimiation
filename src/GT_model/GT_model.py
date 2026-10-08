from functools import cached_property

from dataclasses import dataclass, field
from typing import Optional

from src.GT_model.components.chamber import Chamber
from src.GT_model.components.compressor import Compressor
from src.GT_model.components.turbine import Turbine
from src.GT_model.config import GTModelConfig
from src.working_fluid.gas import GasState


@dataclass
class GTModel:
    state_1: GasState | None = None
    compressor_outlet: GasState | None = None
    fuel: GasState | None = None
    state_4: GasState | None = None
    config: GTModelConfig = field(default_factory=GTModelConfig)
    actual_power: Optional[float] = None

    # ── 组件 ──

    @cached_property
    def compressor(self) -> Compressor:
        return Compressor(
            name="compressor",
            inlet_gas=self.state_1,
            outlet_gas=self.compressor_outlet,
            bleeding_mass_fraction=self.config.compressor_bleeding_mass_fraction,
            bleeding_pressure_fraction=self.config.compressor_bleeding_pressure_fraction,
            bleeding_energy_fraction=self.config.compressor_bleeding_energy_fraction,
        )

    @cached_property
    def chamber(self) -> Chamber:
        return Chamber(
            name="chamber",
            inlet_air=self.compressor.state_2,
            inlet_fuel=self.fuel,
            outlet_composition=self.state_4.composition,
            total_pressure_recovery=self.config.total_pressure_recovery,
            combustion_efficiency=self.config.combustion_efficiency,
            bleeding=self.compressor.bleeding,
        )

    @cached_property
    def turbine(self) -> Turbine:
        return Turbine(
            name="turbine",
            state_3_c=self.chamber.state_3_c,
            state_4=self.state_4,
        )

    # ── 状态点（state_1, state_4 为构造参数） ──

    @cached_property
    def state_2(self) -> GasState:
        return self.compressor.state_2

    @cached_property
    def state_3(self) -> GasState:
        return self.chamber.state_3

    @cached_property
    def state_3_c(self) -> GasState:
        return self.chamber.state_3_c

    # ── 性能指标 ──

    @cached_property
    def flue_gas_flow(self) -> Optional[float]:
        return self.state_4.m_dot

    @cached_property
    def net_power(self) -> Optional[float]:
        return (self.turbine.power - self.compressor.power)

    @cached_property
    def fuel_energy(self) -> Optional[float]:
        if self.fuel is None:
            return None
        return (self.chamber.fuel_lhv * self.fuel.m_dot)

    @cached_property
    def thermal_efficiency(self) -> Optional[float]:
        return (self.actual_power / self.fuel_energy)

    @cached_property
    def generation_power_share(self) -> Optional[float]:
        return (self.actual_power / self.fuel_energy)

    @cached_property
    def compressor_power_share(self) -> Optional[float]:
        return (self.compressor.power / self.fuel_energy)

    @cached_property
    def exhaust_loss_share(self) -> Optional[float]:
        return (1 - self.generation_power_share)
