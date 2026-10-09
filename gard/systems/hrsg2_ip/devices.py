"""hrsg2_ip device definitions."""


DEVICE_DEFINITIONS = {
    "ip2_pump_split": {
        "type": "Splitter",
        "inlets": ["2号炉中压给水泵入口母管"],
        "outlets": ["2号炉中压给水泵1入口", "2号炉中压给水泵2入口"],
    },
    "ip2_pump1": {
        "type": "Pump",
        "inlets": ["2号炉中压给水泵1入口"],
        "outlets": ["2号炉中压给水泵1出口"],
    },
    "ip2_pump2": {
        "type": "Pump",
        "inlets": ["2号炉中压给水泵2入口"],
        "outlets": ["2号炉中压给水泵2出口"],
    },
    "ip2_pump_merge": {
        "type": "Mixer",
        "inlets": ["2号炉中压给水泵1出口", "2号炉中压给水泵2出口"],
        "outlets": ["2号炉低压汽包中压给水泵后"],
    },
    "ip2_feed_split": {
        "type": "Splitter",
        "inlets": ["2号炉低压汽包中压给水泵后"],
        "outlets": ["2号炉中压给水", "2号炉再热减温水", "2号炉中压给水泵回流"],
    },
    "ip2_economizer": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉中压给水"],
        "water_outlets": ["2号炉中压省煤器出口"],
    },
    "ip2_feed_valve": {
        "type": "ThrottleValve",
        "inlets": ["2号炉中压省煤器出口"],
        "outlets": ["2号炉中压汽包入口"],
    },
    "ip2_drum_evaporator": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉中压汽包入口"],
        "water_outlets": ["2号炉中压汽包饱和蒸汽", "2号炉中压汽包排污"],
    },
    "ip2_superheater": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉中压汽包饱和蒸汽"],
        "water_outlets": ["2号炉中压新蒸汽"],
    },
    "ip2_cold_reheat_bypass_mix": {
        "type": "Mixer",
        "inlets": ["2号炉冷再热蒸汽", "2号炉高压旁路出口"],
        "outlets": ["2号炉冷再热与高旁混合蒸汽"],
    },
    "ip2_fresh_steam_mix": {
        "type": "Mixer",
        "inlets": ["2号炉冷再热与高旁混合蒸汽", "2号炉中压新蒸汽"],
        "outlets": ["2号炉再热器入口混合蒸汽"],
    },
    "ip2_reheater1": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉再热器入口混合蒸汽"],
        "water_outlets": ["2号炉再热器1出口"],
    },
    "ip2_attemperator": {
        "type": "Mixer",
        "inlets": ["2号炉再热器1出口", "2号炉再热减温水"],
        "outlets": ["2号炉再热减温后"],
    },
    "ip2_reheater2": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉再热减温后"],
        "water_outlets": ["2号炉再热器2出口"],
    },
    "ip2_reheater3": {
        "type": "GasWaterHeatExchanger",
        "water_inlets": ["2号炉再热器2出口"],
        "water_outlets": ["2号炉热再热蒸汽"],
    },
    "ip2_main_split": {
        "type": "Splitter",
        "inlets": ["2号炉热再热蒸汽"],
        "outlets": ["2号炉再热蒸汽至汽轮机", "2号炉中压旁路入口"],
    },
    "ip2_bypass_valve": {
        "type": "ThrottleValve",
        "inlets": ["2号炉中压旁路入口"],
        "outlets": ["2号炉中压旁路节流后"],
    },
    "ip2_bypass_spray": {
        "type": "Mixer",
        "inlets": ["2号炉中压旁路节流后", "2号炉中压旁路减温水"],
        "outlets": ["2号炉中压旁路出口"],
    },
    "ip2_bypass_destination": {
        "type": "Splitter",
        "inlets": ["2号炉中压旁路出口"],
        "outlets": ["2号炉中压旁路至供热", "2号炉中压旁路至凝汽器"],
    },
}
