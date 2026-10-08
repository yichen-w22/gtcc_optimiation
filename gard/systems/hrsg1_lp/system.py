"""hrsg1_lp system assembly and composite boundaries."""
import pandas as pd
from src.base.system import SystemBook, ThermodynamicSystem
from .components import build_components


def build_system(row, streams, ports=None):
    s = streams.connect(ports or {})
    components = build_components(row, s, "hrsg1_lp")
    model = SystemBook("hrsg1_lp", row)
    model.add_many(components.components.values())
    lp1_bank = ThermodynamicSystem("lp1_pump_bank", "composite")
    lp1_bank.add_component(model.components["lp1_pump_split"])
    lp1_bank.add_component(model.components["lp1_pump1"])
    lp1_bank.add_component(model.components["lp1_pump2"])
    lp1_bank.add_component(model.components["lp1_pump_merge"])
    model.composites = [lp1_bank.result()]
    return model
