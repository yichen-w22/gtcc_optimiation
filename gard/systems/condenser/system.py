"""condenser full system definition."""


SYSTEM_DEFINITIONS = {
    "condenser": {
        "devices": ["condenser", "vacuum_pump1", "vacuum_pump2", "vacuum_pump3", "hotwell_outlet_pipe", "pre_pump_split", "pre_pump1", "pre_pump2", "pre_pump3", "pre_pump_merge", "pre_recycle_split", "cond_control_split", "cond_control", "cond_control_bypass", "cond_control_merge", "heating_drain_mix", "gland_heater", "cond_pump_split", "cond_pump1", "cond_pump2", "cond_pump3", "cond_pump_merge", "cond_users_split", "iron_filter", "boiler_feed_split"],
        "work": "condenser.work",
        "heat": "condenser.heat",
        "heat_exergy": "condenser.heat_exergy",
    },
}
