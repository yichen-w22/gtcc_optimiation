"""st full system definition."""


SYSTEM_DEFINITIONS = {
    "st": {
        "devices": ["hp_main_merge", "hp_turbine", "cold_reheat_split", "hot_reheat_merge", "ip_turbine", "ip_exhaust_split", "lp_admission_merge", "lp_inlet_mix", "lp_turbine"],
        "work": "st.work",
        "heat": 0.0,
        "heat_exergy": 0.0,
    },
}
