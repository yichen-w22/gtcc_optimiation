"""auxiliary component topology."""
from src.base.system import ComponentBook
from src.ST_model.accounting import EnergyConverter, Pump, Turbine, Mixer, Splitter, ThrottleValve, HeatExchanger


def build_components(row, streams, system_name):
    s = streams
    model = ComponentBook(system_name, row)
    auxiliary = EnergyConverter(
        "auxiliary_boundary",
        "unresolved_group",
        system_name,
        work=row.get("aux.work"),
        heat=row.get("aux.heat"),
        heat_exergy=row.get("aux.heat_exergy"),
        note="轴封、疏水及辅助蒸汽组合边界；内部连接待核对",
    )
    auxiliary.add_inlet(s["st.gland_leakage"])
    auxiliary.add_inlet(s["st.ip_leakage"])
    auxiliary.add_inlet(s["aux.external_steam"])
    auxiliary.add_inlet(s["aux.gland_drain"])
    auxiliary.add_inlet(s["hrsg1.hp_drum_drain"])
    auxiliary.add_inlet(s["hrsg2.hp_drum_drain"])
    auxiliary.add_inlet(s["hrsg1.ip_drum_drain"])
    auxiliary.add_inlet(s["hrsg2.ip_drum_drain"])
    auxiliary.add_inlet(s["hrsg1.lp_drum_drain"])
    auxiliary.add_inlet(s["hrsg2.lp_drum_drain"])
    auxiliary.add_outlet(s["aux.gland_exhaust"])
    auxiliary.add_outlet(s["aux.external_drain"])
    auxiliary.add_outlet(s["cond.drains"])
    model.add(auxiliary)
    return model
