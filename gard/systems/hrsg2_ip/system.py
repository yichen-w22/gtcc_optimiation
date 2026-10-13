"""hrsg2_ip full system definition."""


SYSTEM_DEFINITIONS = {
    "hrsg2_ip": {
        "devices": [
            "ip2_pump_split",
            "ip2_pump1",
            "ip2_pump2",
            "ip2_pump_merge",
            "ip2_feed_split",
            "ip2_economizer",
            "ip2_drum_evaporator",
            "ip2_superheater",
            "ip2_fresh_steam_mix",
            "ip2_reheater_group",
            "ip2_attemperator",
            "ip2_reheater3"
        ],
        "work": "hrsg2_ip.work",
        "heat": "hrsg2_ip.heat",
        "heat_exergy": "hrsg2_ip.heat_exergy"
    }
}
