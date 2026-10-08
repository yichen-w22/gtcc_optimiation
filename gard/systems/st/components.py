"""st component topology."""
from src.base.system import ComponentBook
from src.ST_model.accounting import EnergyConverter, Pump, Turbine, Mixer, Splitter, ThrottleValve, HeatExchanger


def build_components(row, streams, system_name):
    s = streams
    model = ComponentBook(system_name, row)
    model.add(
        Mixer(
            "hp_main_merge",
            s["hrsg1.hp_to_st"],
            s["hrsg2.hp_to_st"],
            s["st.hp_in"],
            system_name,
        )
    )
    hp = Turbine(
        "hp_turbine",
        s["st.hp_in"],
        s["st.hp_out"],
        system_name,
        row.get("hp_turbine.power"),
    )
    hp.add_outlet(s["st.gland_leakage"])
    model.add(hp)
    model.add(
        Splitter(
            "cold_reheat_split",
            s["st.hp_out"],
            s["hrsg1.cold_reheat"],
            s["hrsg2.cold_reheat"],
            system_name,
        )
    )
    model.add(
        Mixer(
            "hot_reheat_merge",
            s["hrsg1.rh_to_st"],
            s["hrsg2.rh_to_st"],
            s["st.ip_in"],
            system_name,
        )
    )
    ip = Turbine(
        "ip_turbine",
        s["st.ip_in"],
        s["st.ip_out"],
        system_name,
        row.get("ip_turbine.power"),
    )
    ip.add_outlet(s["st.ip_leakage"])
    model.add(ip)
    model.add(
        Splitter(
            "ip_exhaust_split",
            s["st.ip_out"],
            s["st.ip_to_lp"],
            s["st.heat_extraction"],
            system_name,
        )
    )
    model.add(
        Mixer(
            "lp_admission_merge",
            s["hrsg1.lp_to_st"],
            s["hrsg2.lp_to_st"],
            s["st.lp_admission"],
            system_name,
        )
    )
    model.add(
        Mixer(
            "lp_inlet_mix",
            s["st.ip_to_lp"],
            s["st.lp_admission"],
            s["st.lp_in"],
            system_name,
        )
    )
    model.add(
        Turbine(
            "lp_turbine",
            s["st.lp_in"],
            s["st.lp_out"],
            system_name,
            row.get("lp_turbine.power"),
        )
    )
    return model
