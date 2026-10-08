"""auxiliary system assembly and composite boundaries."""
import pandas as pd
from src.base.system import SystemBook, ThermodynamicSystem
from .components import build_components


def build_system(row, streams, ports=None):
    s = streams.connect(ports or {})
    components = build_components(row, s, "auxiliary")
    model = SystemBook("auxiliary", row)
    model.add_many(components.components.values())
    model.composites = []
    return model
