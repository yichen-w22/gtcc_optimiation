"""hrsg2_lp full system definition."""


SYSTEM_DEFINITIONS = {
    "hrsg2_lp": {
        "devices": [
            "lp2_heat_recovery_return",
            "lp2_recycle_mix",
            "lp2_economizer",
            "lp2_recycle_split",
            "lp2_pump_split",
            "lp2_pump1",
            "lp2_pump2",
            "lp2_pump_merge",
            "lp2_feedwater_valve",
            "lp2_drum_evaporator",
            "lp2_water_split",
            "lp2_superheater",
            "lp2_main_split"
        ],
        "work": "hrsg2_lp.work",
        "heat": "hrsg2_lp.heat",
        "heat_exergy": "hrsg2_lp.heat_exergy"
    }
}
