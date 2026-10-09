"""hrsg2_hp device definitions."""


DEVICE_DEFINITIONS = {
    "hp2_pump_split": {
        "type": "Splitter",
        "inlets": ["2号炉高压给水泵入口母管"],
        "outlets": ["2号炉高压给水泵1入口", "2号炉高压给水泵2入口"],
    },
    "hp2_pump1": {
        "type": "Pump",
        "inlets": ["2号炉高压给水泵1入口"],
        "outlets": ["2号炉高压给水泵1出口"],
    },
    "hp2_pump2": {
        "type": "Pump",
        "inlets": ["2号炉高压给水泵2入口"],
        "outlets": ["2号炉高压给水泵2出口"],
    },
    "hp2_pump_merge": {
        "type": "Mixer",
        "inlets": ["2号炉高压给水泵1出口", "2号炉高压给水泵2出口"],
        "outlets": ["2号炉低压汽包高压给水泵后"],
    },
    "hp2_feed_split": {
        "type": "Splitter",
        "inlets": ["2号炉低压汽包高压给水泵后"],
        "outlets": ["2号炉高压给水", "2号炉高压减温水", "2号炉高压旁路减温水", "2号炉高压给水泵回流"],
    },
    "hp2_economizer1": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉高压省煤器入口"],
        "water_outlets": ["2号炉高压省煤器1出口"],
    },
    "hp2_economizer2": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉高压省煤器1出口"],
        "water_outlets": ["2号炉高压省煤器2出口"],
    },
    "hp2_economizer3": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉高压省煤器2出口"],
        "water_outlets": ["2号炉高压汽包入口"],
    },
    "hp2_feed_valve": {
        "type": "ThrottleValve",
        "inlets": ["2号炉高压给水"],
        "outlets": ["2号炉高压省煤器入口"],
    },
    "hp2_drum_evaporator": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉高压汽包入口"],
        "water_outlets": ["2号炉高压汽包饱和蒸汽", "2号炉高压汽包排污"],
    },
    "hp2_superheater1": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉高压汽包饱和蒸汽"],
        "water_outlets": ["2号炉高压过热器1出口"],
    },
    "hp2_superheater2": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉高压过热器1出口"],
        "water_outlets": ["2号炉高压过热器2出口"],
    },
    "hp2_attemperator": {
        "type": "Mixer",
        "inlets": ["2号炉高压减温前蒸汽", "2号炉高压减温水"],
        "outlets": ["2号炉高压减温后蒸汽"],
    },
    "hp2_superheater3": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉高压过热器2出口"],
        "water_outlets": ["2号炉高压减温前蒸汽"],
    },
    "hp2_superheater4": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉高压减温后蒸汽"],
        "water_outlets": ["2号炉高压主蒸汽"],
    },
    "hp2_main_split": {
        "type": "Splitter",
        "inlets": ["2号炉高压主蒸汽"],
        "outlets": ["2号炉高压蒸汽至汽轮机", "2号炉高压旁路入口"],
    },
    "hp2_bypass_valve": {
        "type": "ThrottleValve",
        "inlets": ["2号炉高压旁路入口"],
        "outlets": ["2号炉高压旁路节流后"],
    },
    "hp2_bypass_spray": {
        "type": "Mixer",
        "inlets": ["2号炉高压旁路节流后", "2号炉高压旁路减温水"],
        "outlets": ["2号炉高压旁路出口"],
    },
}
