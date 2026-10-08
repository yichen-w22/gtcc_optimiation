"""cooling system assembly and composite boundaries."""
import pandas as pd
from src.base.system import SystemBook, ThermodynamicSystem
from .components import build_components


def build_system(row, streams, ports=None):
    s = streams.connect(ports or {})
    components = build_components(row, s, "cooling")
    model = SystemBook("cooling", row)
    model.add_many(components.components.values())
    model.composites = []
    return model
