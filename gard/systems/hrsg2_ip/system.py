"""hrsg2_ip full system definition."""


SYSTEM_DEFINITIONS = {
    "hrsg2_ip": {
        "devices": ["ip2_pump_split", "ip2_pump1", "ip2_pump2", "ip2_pump_merge", "ip2_feed_split", "ip2_economizer", "ip2_feed_valve", "ip2_drum_evaporator", "ip2_superheater", "ip2_cold_reheat_bypass_mix", "ip2_fresh_steam_mix", "ip2_reheater1", "ip2_attemperator", "ip2_reheater2", "ip2_reheater3", "ip2_main_split", "ip2_bypass_valve", "ip2_bypass_spray", "ip2_bypass_destination"],
        "work": "hrsg2_ip.work",
        "heat": "hrsg2_ip.heat",
        "heat_exergy": "hrsg2_ip.heat_exergy",
    },
}
