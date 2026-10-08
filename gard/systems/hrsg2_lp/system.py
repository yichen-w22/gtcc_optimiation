"""hrsg2_lp system assembly and composite boundaries."""
import pandas as pd
from src.base.system import SystemBook, ThermodynamicSystem
from .components import build_components


def build_system(row, streams, ports=None):
    s = streams.connect(ports or {})
    components = build_components(row, s, "hrsg2_lp")
    model = SystemBook("hrsg2_lp", row)
    model.add_many(components.components.values())
    lp2_bank = ThermodynamicSystem("lp2_pump_bank", "composite")
    lp2_bank.add_component(model.components["lp2_pump_split"])
    lp2_bank.add_component(model.components["lp2_pump1"])
    lp2_bank.add_component(model.components["lp2_pump2"])
    lp2_bank.add_component(model.components["lp2_pump_merge"])
    model.composites = [lp2_bank.result()]
    return model
