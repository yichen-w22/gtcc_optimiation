"""hrsg1_hp active graph, matching topology.md."""

DEVICE_DEFINITIONS = {
    "hp1_pump_split": {
        "type": "Splitter",
        "inlets": [
            "1号炉高压给水泵入口母管"
        ],
        "outlets": [
            "1号炉高压给水泵1入口",
            "1号炉高压给水泵2入口"
        ]
    },
    "hp1_pump1": {
        "type": "Pump",
        "inlets": [
            "1号炉高压给水泵1入口"
        ],
        "outlets": [
            "1号炉高压给水泵1出口"
        ]
    },
    "hp1_pump2": {
        "type": "Pump",
        "inlets": [
            "1号炉高压给水泵2入口"
        ],
        "outlets": [
            "1号炉高压给水泵2出口"
        ]
    },
    "hp1_pump_merge": {
        "type": "Mixer",
        "inlets": [
            "1号炉高压给水泵1出口",
            "1号炉高压给水泵2出口"
        ],
        "outlets": [
            "1号炉高压给水泵出口母管"
        ]
    },
    "hp1_feed_split": {
        "type": "Splitter",
        "inlets": [
            "1号炉高压给水泵出口母管"
        ],
        "outlets": [
            "1号炉高压给水",
            "1号炉高压减温水"
        ]
    },
    "hp1_economizer_group": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "1号炉高压给水"
        ],
        "water_outlets": [
            "1号炉高压汽包入口"
        ]
    },
    "hp1_drum_evaporator": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "1号炉高压汽包入口"
        ],
        "water_outlets": [
            "1号炉高压汽包饱和蒸汽"
        ]
    },
    "hp1_superheater_group": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "1号炉高压汽包饱和蒸汽"
        ],
        "water_outlets": [
            "1号炉高压减温前蒸汽"
        ]
    },
    "hp1_attemperator": {
        "type": "Mixer",
        "inlets": [
            "1号炉高压减温前蒸汽",
            "1号炉高压减温水"
        ],
        "outlets": [
            "1号炉高压减温后蒸汽"
        ]
    },
    "hp1_superheater4": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "1号炉高压减温后蒸汽"
        ],
        "water_outlets": [
            "1号炉高压主蒸汽"
        ]
    }
}
