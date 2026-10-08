"""hrsg1_hp system assembly and composite boundaries."""
import pandas as pd
from src.base.system import SystemBook, ThermodynamicSystem
from .components import build_components


def build_system(row, streams, ports=None):
    s = streams.connect(ports or {})
    components = build_components(row, s, "hrsg1_hp")
    model = SystemBook("hrsg1_hp", row)
    model.add_many(components.components.values())
    hp1_bank = ThermodynamicSystem("hp1_pump_bank", "composite")
    hp1_bank.add_component(model.components["hp1_pump_split"])
    hp1_bank.add_component(model.components["hp1_pump1"])
    hp1_bank.add_component(model.components["hp1_pump2"])
    hp1_bank.add_component(model.components["hp1_pump_merge"])
    model.composites = [hp1_bank.result()]
    return model
