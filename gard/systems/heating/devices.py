"""heating device definitions."""


DEVICE_DEFINITIONS = {
    "heating_steam_merge": {
        "type": "Mixer",
        "inlets": ["汽轮机供热抽汽", "1号炉低压蒸汽至供热", "2号炉低压蒸汽至供热", "1号炉中压旁路至供热", "2号炉中压旁路至供热"],
        "outlets": ["供热系统蒸汽母管"],
    },
    "heating_exchangers_boundary": {
        "type": "HeatExchanger",
        "inlets": ["供热系统回水", "供热系统蒸汽母管"],
        "outlets": ["供热系统供水", "供热系统疏水泵前"],
    },
    "heating_drain_return_boundary": {
        "type": "Device",
        "inlets": ["供热系统疏水泵前"],
        "outlets": ["供热系统疏水返回"],
    },
    "heat_recovery1": {
        "type": "HeatExchanger",
        "inlets": ["供热系统余热回收1水入口", "1号炉低压水至余热回收"],
        "outlets": ["供热系统余热回收1水出口", "1号炉余热回收返回低压水"],
    },
    "heat_recovery2": {
        "type": "HeatExchanger",
        "inlets": ["供热系统余热回收2水入口", "2号炉低压水至余热回收"],
        "outlets": ["供热系统余热回收2水出口", "2号炉余热回收返回低压水"],
    },
}
