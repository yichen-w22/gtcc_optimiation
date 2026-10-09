"""cooling full system definition."""


SYSTEM_DEFINITIONS = {
    "cooling": {
        "devices": ["cooling_boundary"],
        "work": "cooling.work",
        "heat": "cooling.heat",
        "heat_exergy": "cooling.heat_exergy",
    },
}
