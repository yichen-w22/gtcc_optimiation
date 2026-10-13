"""hrsg2_hp active system definition."""

SYSTEM_DEFINITIONS = {
    "hrsg2_hp": {
        "devices": [
            "hp2_pump_split",
            "hp2_pump1",
            "hp2_pump2",
            "hp2_pump_merge",
            "hp2_feed_split",
            "hp2_economizer_group",
            "hp2_drum_evaporator",
            "hp2_superheater_group",
            "hp2_attemperator",
            "hp2_superheater4"
        ],
        "work": "hrsg2_hp.work",
        "heat": "hrsg2_hp.heat",
        "heat_exergy": "hrsg2_hp.heat_exergy"
    }
}
