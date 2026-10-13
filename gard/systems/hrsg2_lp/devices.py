"""hrsg2_lp device definitions."""


DEVICE_DEFINITIONS = {
    "lp2_heat_recovery_return": {
        "type": "Mixer",
        "inlets": [
            "2号炉低压给水",
            "2号炉热网水水换热器回水"
        ],
        "outlets": [
            "2号炉低压给水余热回收后"
        ]
    },
    "lp2_recycle_mix": {
        "type": "Mixer",
        "inlets": [
            "2号炉低压给水余热回收后",
            "2号炉低压再循环泵出口母管"
        ],
        "outlets": [
            "2号炉低压省煤器入口"
        ]
    },
    "lp2_economizer": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "2号炉低压省煤器入口"
        ],
        "water_outlets": [
            "2号炉低压省煤器出口"
        ]
    },
    "lp2_recycle_split": {
        "type": "Splitter",
        "inlets": [
            "2号炉低压省煤器出口"
        ],
        "outlets": [
            "2号炉低压汽包给水调节阀入口",
            "2号炉低压再循环泵入口母管",
            "2号炉低压水至余热回收"
        ]
    },
    "lp2_pump_split": {
        "type": "Splitter",
        "inlets": [
            "2号炉低压再循环泵入口母管"
        ],
        "outlets": [
            "2号炉低压再循环泵1入口",
            "2号炉低压再循环泵2入口"
        ]
    },
    "lp2_pump1": {
        "type": "Pump",
        "inlets": [
            "2号炉低压再循环泵1入口"
        ],
        "outlets": [
            "2号炉低压再循环泵1出口"
        ]
    },
    "lp2_pump2": {
        "type": "Pump",
        "inlets": [
            "2号炉低压再循环泵2入口"
        ],
        "outlets": [
            "2号炉低压再循环泵2出口"
        ]
    },
    "lp2_pump_merge": {
        "type": "Mixer",
        "inlets": [
            "2号炉低压再循环泵1出口",
            "2号炉低压再循环泵2出口"
        ],
        "outlets": [
            "2号炉低压再循环泵出口母管"
        ]
    },
    "lp2_feedwater_valve": {
        "type": "ThrottleValve",
        "inlets": [
            "2号炉低压汽包给水调节阀入口"
        ],
        "outlets": [
            "2号炉低压汽包入口"
        ]
    },
    "lp2_drum_evaporator": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "2号炉低压汽包入口"
        ],
        "water_outlets": [
            "2号炉低压汽包饱和蒸汽",
            "2号炉低压汽包水"
        ]
    },
    "lp2_water_split": {
        "type": "Splitter",
        "inlets": [
            "2号炉低压汽包水"
        ],
        "outlets": [
            "2号炉高压给水泵入口母管",
            "2号炉中压给水泵入口母管"
        ]
    },
    "lp2_superheater": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "2号炉低压汽包饱和蒸汽"
        ],
        "water_outlets": [
            "2号炉低压主蒸汽"
        ]
    },
    "lp2_main_split": {
        "type": "Splitter",
        "inlets": [
            "2号炉低压主蒸汽"
        ],
        "outlets": [
            "2号炉低压蒸汽至汽轮机",
            "2号炉低压蒸汽至供热"
        ]
    }
}
