"""hrsg1_lp device definitions."""


DEVICE_DEFINITIONS = {
    "lp1_heat_recovery_return": {
        "type": "Mixer",
        "inlets": [
            "1号炉低压给水",
            "1号炉热网水水换热器回水"
        ],
        "outlets": [
            "1号炉低压给水余热回收后"
        ]
    },
    "lp1_recycle_mix": {
        "type": "Mixer",
        "inlets": [
            "1号炉低压给水余热回收后",
            "1号炉低压再循环泵出口母管"
        ],
        "outlets": [
            "1号炉低压省煤器入口"
        ]
    },
    "lp1_economizer": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "1号炉低压省煤器入口"
        ],
        "water_outlets": [
            "1号炉低压省煤器出口"
        ]
    },
    "lp1_recycle_split": {
        "type": "Splitter",
        "inlets": [
            "1号炉低压省煤器出口"
        ],
        "outlets": [
            "1号炉低压汽包给水调节阀入口",
            "1号炉低压再循环泵入口母管",
            "1号炉低压水至余热回收"
        ]
    },
    "lp1_pump_split": {
        "type": "Splitter",
        "inlets": [
            "1号炉低压再循环泵入口母管"
        ],
        "outlets": [
            "1号炉低压再循环泵1入口",
            "1号炉低压再循环泵2入口"
        ]
    },
    "lp1_pump1": {
        "type": "Pump",
        "inlets": [
            "1号炉低压再循环泵1入口"
        ],
        "outlets": [
            "1号炉低压再循环泵1出口"
        ]
    },
    "lp1_pump2": {
        "type": "Pump",
        "inlets": [
            "1号炉低压再循环泵2入口"
        ],
        "outlets": [
            "1号炉低压再循环泵2出口"
        ]
    },
    "lp1_pump_merge": {
        "type": "Mixer",
        "inlets": [
            "1号炉低压再循环泵1出口",
            "1号炉低压再循环泵2出口"
        ],
        "outlets": [
            "1号炉低压再循环泵出口母管"
        ]
    },
    "lp1_feedwater_valve": {
        "type": "ThrottleValve",
        "inlets": [
            "1号炉低压汽包给水调节阀入口"
        ],
        "outlets": [
            "1号炉低压汽包入口"
        ]
    },
    "lp1_drum_evaporator": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "1号炉低压汽包入口"
        ],
        "water_outlets": [
            "1号炉低压汽包饱和蒸汽",
            "1号炉低压汽包水"
        ]
    },
    "lp1_water_split": {
        "type": "Splitter",
        "inlets": [
            "1号炉低压汽包水"
        ],
        "outlets": [
            "1号炉高压给水泵入口母管",
            "1号炉中压给水泵入口母管"
        ]
    },
    "lp1_superheater": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "1号炉低压汽包饱和蒸汽"
        ],
        "water_outlets": [
            "1号炉低压主蒸汽"
        ]
    },
    "lp1_main_split": {
        "type": "Splitter",
        "inlets": [
            "1号炉低压主蒸汽"
        ],
        "outlets": [
            "1号炉低压蒸汽至汽轮机",
            "1号炉低压蒸汽至供热"
        ]
    }
}
