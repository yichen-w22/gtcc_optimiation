"""hrsg2_hp full system definition."""


SYSTEM_DEFINITIONS = {
    "hrsg2_hp": {
        "devices": ["hp2_pump_split", "hp2_pump1", "hp2_pump2", "hp2_pump_merge", "hp2_feed_split", "hp2_economizer1", "hp2_economizer2", "hp2_economizer3", "hp2_feed_valve", "hp2_drum_evaporator", "hp2_superheater1", "hp2_superheater2", "hp2_attemperator", "hp2_superheater3", "hp2_superheater4", "hp2_main_split", "hp2_bypass_valve", "hp2_bypass_spray"],
        "work": "hrsg2_hp.work",
        "heat": "hrsg2_hp.heat",
        "heat_exergy": "hrsg2_hp.heat_exergy",
    },
}
