"""hrsg1_hp full system definition."""


SYSTEM_DEFINITIONS = {
    "hrsg1_hp": {
        "devices": ["hp1_pump_split", "hp1_pump1", "hp1_pump2", "hp1_pump_merge", "hp1_feed_split", "hp1_economizer1", "hp1_economizer2", "hp1_economizer3", "hp1_feed_valve", "hp1_drum_evaporator", "hp1_superheater1", "hp1_superheater2", "hp1_attemperator", "hp1_superheater3", "hp1_superheater4", "hp1_main_split", "hp1_bypass_valve", "hp1_bypass_spray"],
        "work": "hrsg1_hp.work",
        "heat": "hrsg1_hp.heat",
        "heat_exergy": "hrsg1_hp.heat_exergy",
    },
}
