"""st system assembly and composite boundaries."""
import pandas as pd
from src.base.system import SystemBook, ThermodynamicSystem
from .components import build_components


def build_system(row, streams, ports=None):
    s = streams.connect(ports or {})
    components = build_components(row, s, "st")
    model = SystemBook("st", row)
    model.add_many(components.components.values())
    st_generator = ThermodynamicSystem("st_generator", "composite")
    st_generator.add_component(model.system)
    st_generator.transfers = pd.DataFrame(
        [
            {
                "component": "st_generator",
                "work": row.get("st.generator_power"),
                "heat": 0.0,
                "heat_exergy": 0.0,
            }
        ]
    ).set_index("component")
    st_generator.note = "汽轮机加发电机绝热组合边界；不把实测电功分摊到各缸"
    model.composites = [st_generator.result()]
    return model
