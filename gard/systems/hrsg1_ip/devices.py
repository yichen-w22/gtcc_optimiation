"""hrsg1_ip device definitions."""


DEVICE_DEFINITIONS = {
    "ip1_pump_split": {
        "type": "Splitter",
        "inlets": [
            "1号炉中压给水泵入口母管"
        ],
        "outlets": [
            "1号炉中压给水泵1入口",
            "1号炉中压给水泵2入口"
        ]
    },
    "ip1_pump1": {
        "type": "Pump",
        "inlets": [
            "1号炉中压给水泵1入口"
        ],
        "outlets": [
            "1号炉中压给水泵1出口"
        ]
    },
    "ip1_pump2": {
        "type": "Pump",
        "inlets": [
            "1号炉中压给水泵2入口"
        ],
        "outlets": [
            "1号炉中压给水泵2出口"
        ]
    },
    "ip1_pump_merge": {
        "type": "Mixer",
        "inlets": [
            "1号炉中压给水泵1出口",
            "1号炉中压给水泵2出口"
        ],
        "outlets": [
            "1号炉中压给水泵出口母管"
        ]
    },
    "ip1_feed_split": {
        "type": "Splitter",
        "inlets": [
            "1号炉中压给水泵出口母管"
        ],
        "outlets": [
            "1号炉中压给水",
            "1号炉再热减温水"
        ]
    },
    "ip1_economizer": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "1号炉中压给水"
        ],
        "water_outlets": [
            "1号炉中压汽包入口"
        ]
    },
    "ip1_drum_evaporator": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "1号炉中压汽包入口"
        ],
        "water_outlets": [
            "1号炉中压汽包饱和蒸汽"
        ]
    },
    "ip1_superheater": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "1号炉中压汽包饱和蒸汽"
        ],
        "water_outlets": [
            "1号炉中压新蒸汽"
        ]
    },
    "ip1_fresh_steam_mix": {
        "type": "Mixer",
        "inlets": [
            "1号炉中压新蒸汽",
            "1号炉冷再热蒸汽"
        ],
        "outlets": [
            "1号炉再热器入口混合蒸汽"
        ]
    },
    "ip1_reheater_group": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "1号炉再热器入口混合蒸汽"
        ],
        "water_outlets": [
            "1号炉再热减温前蒸汽"
        ]
    },
    "ip1_attemperator": {
        "type": "Mixer",
        "inlets": [
            "1号炉再热减温前蒸汽",
            "1号炉再热减温水"
        ],
        "outlets": [
            "1号炉再热减温后蒸汽"
        ]
    },
    "ip1_reheater3": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "1号炉再热减温后蒸汽"
        ],
        "water_outlets": [
            "1号炉热再热蒸汽"
        ]
    }
}
