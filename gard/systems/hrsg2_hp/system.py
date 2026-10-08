"""hrsg2_hp system assembly and composite boundaries."""
import pandas as pd
from src.base.system import SystemBook, ThermodynamicSystem
from .components import build_components


def build_system(row, streams, ports=None):
    s = streams.connect(ports or {})
    components = build_components(row, s, "hrsg2_hp")
    model = SystemBook("hrsg2_hp", row)
    model.add_many(components.components.values())
    hp2_bank = ThermodynamicSystem("hp2_pump_bank", "composite")
    hp2_bank.add_component(model.components["hp2_pump_split"])
    hp2_bank.add_component(model.components["hp2_pump1"])
    hp2_bank.add_component(model.components["hp2_pump2"])
    hp2_bank.add_component(model.components["hp2_pump_merge"])
    model.composites = [hp2_bank.result()]
    return model
