"""hrsg1_ip system assembly and composite boundaries."""
import pandas as pd
from src.base.system import SystemBook, ThermodynamicSystem
from .components import build_components


def build_system(row, streams, ports=None):
    s = streams.connect(ports or {})
    components = build_components(row, s, "hrsg1_ip")
    model = SystemBook("hrsg1_ip", row)
    model.add_many(components.components.values())
    ip1_bank = ThermodynamicSystem("ip1_pump_bank", "composite")
    ip1_bank.add_component(model.components["ip1_pump_split"])
    ip1_bank.add_component(model.components["ip1_pump1"])
    ip1_bank.add_component(model.components["ip1_pump2"])
    ip1_bank.add_component(model.components["ip1_pump_merge"])
    model.composites = [ip1_bank.result()]
    return model
