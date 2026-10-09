"""hrsg1_ip full system definition."""


SYSTEM_DEFINITIONS = {
    "hrsg1_ip": {
        "devices": ["ip1_pump_split", "ip1_pump1", "ip1_pump2", "ip1_pump_merge", "ip1_feed_split", "ip1_economizer", "ip1_feed_valve", "ip1_drum_evaporator", "ip1_superheater", "ip1_cold_reheat_bypass_mix", "ip1_fresh_steam_mix", "ip1_reheater1", "ip1_attemperator", "ip1_reheater2", "ip1_reheater3", "ip1_main_split", "ip1_bypass_valve", "ip1_bypass_spray", "ip1_bypass_destination"],
        "work": "hrsg1_ip.work",
        "heat": "hrsg1_ip.heat",
        "heat_exergy": "hrsg1_ip.heat_exergy",
    },
}
