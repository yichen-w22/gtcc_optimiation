from src.base.device import Device
from src.working_fluid.gas import GasComposition, GasState, calc_fuel_lhv


class Chamber(Device):
    def __init__(
        self, name, inlet_air=None, inlet_fuel=None, outlet_composition=None,
        total_pressure_recovery=None, combustion_efficiency=0.99,
        bleeding=None, fuel_chemical_exergy=None,
    ):
        self.name = name
        self.inlet_air = inlet_air
        self.inlet_fuel = inlet_fuel
        self.outlet_composition = outlet_composition
        self.total_pressure_recovery = total_pressure_recovery
        self.combustion_efficiency = combustion_efficiency
        self.bleeding = bleeding
        self.fuel_chemical_exergy = fuel_chemical_exergy

    @property
    def inlets(self):
        streams = [
            self.inlet_air or GasState(name=f"{self.name}_air"),
            self.inlet_fuel or GasState(name=f"{self.name}_fuel"),
        ]
        if self.bleeding is not None:
            streams.append(self.bleeding)
        return streams

    @property
    def outlets(self):
        return [self.state_3_c]

    @property
    def fuel_lhv(self):
        if self.inlet_fuel is None:
            return None
        try:
            return calc_fuel_lhv(self.inlet_fuel.composition)
        except (ValueError, AttributeError):
            return None

    @property
    def released_heat(self):
        return self.combustion_efficiency * (self.fuel_lhv * getattr(self.inlet_fuel, 'm_dot', None))

    @property
    def energy_source(self):
        # Effective released chemical energy; unreleased fuel energy is excluded.
        return self.released_heat

    @property
    def exergy_source(self):
        # Physical stream exergy alone cannot close a combustion exergy balance.
        return self.fuel_chemical_exergy * getattr(self.inlet_fuel, 'm_dot', None)

    def _outlet_state(self, include_bleed):
        streams = self.inlets if include_bleed else self.inlets[:2]
        m_out = (sum((s.m_dot for s in streams)))
        h_out = (sum([*(s.energy_flow for s in streams), self.released_heat]) / m_out)
        pressure = (getattr(self.inlet_air, 'P', None) * self.total_pressure_recovery)
        return GasState.from_Ph(
            P=pressure,
            h=h_out,
            m_dot=m_out,
            composition=self.outlet_composition,
            name=f"{self.name}_state_3" + ("_c" if include_bleed else ""),
            ref=getattr(self.inlet_air, "ref", None),
        )

    @property
    def state_3(self):
        return self._outlet_state(False)

    @property
    def state_3_c(self):
        return self._outlet_state(True)

    @property
    def pressure_loss(self):
        return getattr(self.inlet_air, 'P', None) - self.state_3.P
