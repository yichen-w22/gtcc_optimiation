"""heating component topology."""
from src.base.system import ComponentBook
from src.ST_model.accounting import EnergyConverter, Pump, Turbine, Mixer, Splitter, ThrottleValve, HeatExchanger


def build_components(row, streams, system_name):
    s = streams
    model = ComponentBook(system_name, row)
    heating_header = Mixer(
        "heating_steam_merge",
        s["st.heat_extraction"],
        s["hrsg1.lp_to_heat"],
        s["heat.steam_header"],
        system_name,
    )
    heating_header.add_inlet(s["hrsg2.lp_to_heat"])
    heating_header.add_inlet(s["hrsg1.ip_bypass_to_heat"])
    heating_header.add_inlet(s["hrsg2.ip_bypass_to_heat"])
    model.add(heating_header)
    heating_hx = HeatExchanger(
        "heating_exchangers_boundary",
        s["heat.return_water"],
        s["heat.supply_water"],
        system_name,
        s["heat.steam_header"],
        s["heat.drain_before_pump"],
    )
    heating_hx.note += "；供热站组合边界，内部台数/烟气余热输入尚待核对"
    heating_hx.transfers.loc[heating_hx.name, ["heat", "heat_exergy"]] = [
        row.get("heating.other_heat"),
        row.get("heating.other_heat_exergy"),
    ]
    model.add(heating_hx)
    drain = EnergyConverter(
        "heating_drain_return_boundary",
        "unresolved_group",
        system_name,
        work=row.get("heating_drain.work"),
        heat=row.get("heating_drain.heat"),
        heat_exergy=row.get("heating_drain.heat_exergy"),
        note="疏水冷却/泵送总边界，内部设备数量与接法待核对",
    )
    drain.add_inlet(s["heat.drain_before_pump"])
    drain.add_outlet(s["heat.drain_return"])
    model.add(drain)
    model.add(
        HeatExchanger(
            "heat_recovery1",
            s["heat.recovery1_water_in"],
            s["heat.recovery1_water_out"],
            system_name,
            s["hrsg1.lp_to_heat_recovery"],
            s["hrsg1.lp_from_heat_recovery"],
        )
    )
    model.add(
        HeatExchanger(
            "heat_recovery2",
            s["heat.recovery2_water_in"],
            s["heat.recovery2_water_out"],
            system_name,
            s["hrsg2.lp_to_heat_recovery"],
            s["hrsg2.lp_from_heat_recovery"],
        )
    )
    return model
