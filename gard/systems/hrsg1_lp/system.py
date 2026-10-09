"""hrsg1_lp full system definition."""


SYSTEM_DEFINITIONS = {
    "hrsg1_lp": {
        "devices": ["lp1_heat_recovery_return", "lp1_feed_split", "lp1_recycle_mix", "lp1_economizer", "lp1_recycle_split", "lp1_pump_split", "lp1_pump1", "lp1_pump2", "lp1_pump_merge", "lp1_bypass_mix", "lp1_drum_feed_valve", "lp1_drum_evaporator", "lp1_water_split", "lp1_superheater", "lp1_main_split", "lp1_bypass_valve", "lp1_bypass_spray"],
        "work": "hrsg1_lp.work",
        "heat": "hrsg1_lp.heat",
        "heat_exergy": "hrsg1_lp.heat_exergy",
    },
}
