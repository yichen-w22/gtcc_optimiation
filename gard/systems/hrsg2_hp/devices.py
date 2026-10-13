"""hrsg2_hp active graph, matching topology.md."""

DEVICE_DEFINITIONS = {
    "hp2_pump_split": {
        "type": "Splitter",
        "inlets": [
            "2号炉高压给水泵入口母管"
        ],
        "outlets": [
            "2号炉高压给水泵1入口",
            "2号炉高压给水泵2入口"
        ]
    },
    "hp2_pump1": {
        "type": "Pump",
        "inlets": [
            "2号炉高压给水泵1入口"
        ],
        "outlets": [
            "2号炉高压给水泵1出口"
        ]
    },
    "hp2_pump2": {
        "type": "Pump",
        "inlets": [
            "2号炉高压给水泵2入口"
        ],
        "outlets": [
            "2号炉高压给水泵2出口"
        ]
    },
    "hp2_pump_merge": {
        "type": "Mixer",
        "inlets": [
            "2号炉高压给水泵1出口",
            "2号炉高压给水泵2出口"
        ],
        "outlets": [
            "2号炉高压给水泵出口母管"
        ]
    },
    "hp2_feed_split": {
        "type": "Splitter",
        "inlets": [
            "2号炉高压给水泵出口母管"
        ],
        "outlets": [
            "2号炉高压给水",
            "2号炉高压减温水"
        ]
    },
    "hp2_economizer_group": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "2号炉高压给水"
        ],
        "water_outlets": [
            "2号炉高压汽包入口"
        ]
    },
    "hp2_drum_evaporator": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "2号炉高压汽包入口"
        ],
        "water_outlets": [
            "2号炉高压汽包饱和蒸汽"
        ]
    },
    "hp2_superheater_group": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "2号炉高压汽包饱和蒸汽"
        ],
        "water_outlets": [
            "2号炉高压减温前蒸汽"
        ]
    },
    "hp2_attemperator": {
        "type": "Mixer",
        "inlets": [
            "2号炉高压减温前蒸汽",
            "2号炉高压减温水"
        ],
        "outlets": [
            "2号炉高压减温后蒸汽"
        ]
    },
    "hp2_superheater4": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": [
            "2号炉高压减温后蒸汽"
        ],
        "water_outlets": [
            "2号炉高压主蒸汽"
        ]
    }
}
