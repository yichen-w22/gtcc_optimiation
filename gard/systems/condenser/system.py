"""condenser system assembly and composite boundaries."""
import pandas as pd
from src.base.system import SystemBook, ThermodynamicSystem
from .components import build_components


def build_system(row, streams, ports=None):
    s = streams.connect(ports or {})
    components = build_components(row, s, "condenser")
    model = SystemBook("condenser", row)
    model.add_many(components.components.values())
    pre_bank = ThermodynamicSystem("pre_pump_bank", "composite")
    pre_bank.add_component(model.components["pre_pump_split"])
    pre_bank.add_component(model.components["pre_pump1"])
    pre_bank.add_component(model.components["pre_pump2"])
    pre_bank.add_component(model.components["pre_pump3"])
    pre_bank.add_component(model.components["pre_pump_merge"])
    cond_bank = ThermodynamicSystem("cond_pump_bank", "composite")
    cond_bank.add_component(model.components["cond_pump_split"])
    cond_bank.add_component(model.components["cond_pump1"])
    cond_bank.add_component(model.components["cond_pump2"])
    cond_bank.add_component(model.components["cond_pump3"])
    cond_bank.add_component(model.components["cond_pump_merge"])
    model.composites = [pre_bank.result(), cond_bank.result()]
    return model
