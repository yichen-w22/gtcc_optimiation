"""cooling device definitions."""


DEVICE_DEFINITIONS = {
    "cooling_boundary": {
        "type": "Device",
        "inlets": ["冷却水回水", "冷却水外部入口"],
        "outlets": ["冷却水供水", "冷却水外部出口"],
    },
}
