"""hrsg1_hp active system definition."""

SYSTEM_DEFINITIONS = {
    "hrsg1_hp": {
        "devices": [
            "hp1_pump_split",
            "hp1_pump1",
            "hp1_pump2",
            "hp1_pump_merge",
            "hp1_feed_split",
            "hp1_economizer_group",
            "hp1_drum_evaporator",
            "hp1_superheater_group",
            "hp1_attemperator",
            "hp1_superheater4"
        ],
        "work": "hrsg1_hp.work",
        "heat": "hrsg1_hp.heat",
        "heat_exergy": "hrsg1_hp.heat_exergy"
    }
}
