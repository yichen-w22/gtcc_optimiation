"""hrsg1_hp device definitions."""


DEVICE_DEFINITIONS = {
    "hp1_pump_split": {
        "type": "Splitter",
        "inlets": ["1号炉高压给水泵入口母管"],
        "outlets": ["1号炉高压给水泵1入口", "1号炉高压给水泵2入口"],
    },
    "hp1_pump1": {
        "type": "Pump",
        "inlets": ["1号炉高压给水泵1入口"],
        "outlets": ["1号炉高压给水泵1出口"],
    },
    "hp1_pump2": {
        "type": "Pump",
        "inlets": ["1号炉高压给水泵2入口"],
        "outlets": ["1号炉高压给水泵2出口"],
    },
    "hp1_pump_merge": {
        "type": "Mixer",
        "inlets": ["1号炉高压给水泵1出口", "1号炉高压给水泵2出口"],
        "outlets": ["1号炉低压汽包高压给水泵后"],
    },
    "hp1_feed_split": {
        "type": "Splitter",
        "inlets": ["1号炉低压汽包高压给水泵后"],
        "outlets": ["1号炉高压给水", "1号炉高压减温水", "1号炉高压旁路减温水", "1号炉高压给水泵回流"],
    },
    "hp1_economizer1": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["1号炉高压省煤器入口"],
        "water_outlets": ["1号炉高压省煤器1出口"],
    },
    "hp1_economizer2": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["1号炉高压省煤器1出口"],
        "water_outlets": ["1号炉高压省煤器2出口"],
    },
    "hp1_economizer3": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["1号炉高压省煤器2出口"],
        "water_outlets": ["1号炉高压汽包入口"],
    },
    "hp1_feed_valve": {
        "type": "ThrottleValve",
        "inlets": ["1号炉高压给水"],
        "outlets": ["1号炉高压省煤器入口"],
    },
    "hp1_drum_evaporator": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["1号炉高压汽包入口"],
        "water_outlets": ["1号炉高压汽包饱和蒸汽", "1号炉高压汽包排污"],
    },
    "hp1_superheater1": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["1号炉高压汽包饱和蒸汽"],
        "water_outlets": ["1号炉高压过热器1出口"],
    },
    "hp1_superheater2": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["1号炉高压过热器1出口"],
        "water_outlets": ["1号炉高压过热器2出口"],
    },
    "hp1_attemperator": {
        "type": "Mixer",
        "inlets": ["1号炉高压减温前蒸汽", "1号炉高压减温水"],
        "outlets": ["1号炉高压减温后蒸汽"],
    },
    "hp1_superheater3": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["1号炉高压过热器2出口"],
        "water_outlets": ["1号炉高压减温前蒸汽"],
    },
    "hp1_superheater4": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["1号炉高压减温后蒸汽"],
        "water_outlets": ["1号炉高压主蒸汽"],
    },
    "hp1_main_split": {
        "type": "Splitter",
        "inlets": ["1号炉高压主蒸汽"],
        "outlets": ["1号炉高压蒸汽至汽轮机", "1号炉高压旁路入口"],
    },
    "hp1_bypass_valve": {
        "type": "ThrottleValve",
        "inlets": ["1号炉高压旁路入口"],
        "outlets": ["1号炉高压旁路节流后"],
    },
    "hp1_bypass_spray": {
        "type": "Mixer",
        "inlets": ["1号炉高压旁路节流后", "1号炉高压旁路减温水"],
        "outlets": ["1号炉高压旁路出口"],
    },
}
