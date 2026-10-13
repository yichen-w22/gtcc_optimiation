"""hrsg1_lp full system definition."""


SYSTEM_DEFINITIONS = {
    "hrsg1_lp": {
        "devices": [
            "lp1_heat_recovery_return",
            "lp1_recycle_mix",
            "lp1_economizer",
            "lp1_recycle_split",
            "lp1_pump_split",
            "lp1_pump1",
            "lp1_pump2",
            "lp1_pump_merge",
            "lp1_feedwater_valve",
            "lp1_drum_evaporator",
            "lp1_water_split",
            "lp1_superheater",
            "lp1_main_split"
        ],
        "work": "hrsg1_lp.work",
        "heat": "hrsg1_lp.heat",
        "heat_exergy": "hrsg1_lp.heat_exergy"
    }
}
