"""hrsg2_ip system assembly and composite boundaries."""
import pandas as pd
from src.base.system import SystemBook, ThermodynamicSystem
from .components import build_components


def build_system(row, streams, ports=None):
    s = streams.connect(ports or {})
    components = build_components(row, s, "hrsg2_ip")
    model = SystemBook("hrsg2_ip", row)
    model.add_many(components.components.values())
    ip2_bank = ThermodynamicSystem("ip2_pump_bank", "composite")
    ip2_bank.add_component(model.components["ip2_pump_split"])
    ip2_bank.add_component(model.components["ip2_pump1"])
    ip2_bank.add_component(model.components["ip2_pump2"])
    ip2_bank.add_component(model.components["ip2_pump_merge"])
    model.composites = [ip2_bank.result()]
    return model
