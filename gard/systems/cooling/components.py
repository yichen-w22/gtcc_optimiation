"""cooling component topology."""
from src.base.system import ComponentBook
from src.ST_model.accounting import EnergyConverter, Pump, Turbine, Mixer, Splitter, ThrottleValve, HeatExchanger


def build_components(row, streams, system_name):
    s = streams
    model = ComponentBook(system_name, row)
    cooling_group = EnergyConverter(
        "cooling_boundary",
        "unresolved_group",
        system_name,
        work=row.get("cooling.work"),
        heat=row.get("cooling.heat"),
        heat_exergy=row.get("cooling.heat_exergy"),
        note="循环冷却水内部泵/换热设备待补图核对",
    )
    cooling_group.add_inlet(s["cooling.return"])
    cooling_group.add_inlet(s["cooling.external_in"])
    cooling_group.add_outlet(s["cooling.supply"])
    cooling_group.add_outlet(s["cooling.external_out"])
    model.add(cooling_group)
    return model
