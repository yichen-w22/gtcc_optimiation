"""heating full system definition."""


SYSTEM_DEFINITIONS = {
    "heating": {
        "devices": ["heating_steam_merge", "heating_exchangers_boundary", "heating_drain_return_boundary", "heat_recovery1", "heat_recovery2"],
        "work": "heating.work",
        "heat": "heating.heat",
        "heat_exergy": "heating.heat_exergy",
    },
}
