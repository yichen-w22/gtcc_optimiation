"""st device definitions."""


DEVICE_DEFINITIONS = {
    "hp_main_merge": {
        "type": "Mixer",
        "inlets": ["1号炉高压蒸汽至汽轮机", "2号炉高压蒸汽至汽轮机"],
        "outlets": ["汽轮机高压缸入口"],
    },
    "hp_turbine": {
        "type": "Turbine",
        "inlets": ["汽轮机高压缸入口"],
        "outlets": ["汽轮机高压缸出口", "汽轮机轴封漏汽"],
    },
    "cold_reheat_split": {
        "type": "Splitter",
        "inlets": ["汽轮机高压缸出口"],
        "outlets": ["1号炉冷再热蒸汽", "2号炉冷再热蒸汽"],
    },
    "hot_reheat_merge": {
        "type": "Mixer",
        "inlets": ["1号炉再热蒸汽至汽轮机", "2号炉再热蒸汽至汽轮机"],
        "outlets": ["汽轮机中压缸入口"],
    },
    "ip_turbine": {
        "type": "Turbine",
        "inlets": ["汽轮机中压缸入口"],
        "outlets": ["汽轮机中压缸出口", "汽轮机中压缸漏汽"],
    },
    "ip_exhaust_split": {
        "type": "Splitter",
        "inlets": ["汽轮机中压缸出口"],
        "outlets": ["汽轮机中压至低压连通管", "汽轮机供热抽汽"],
    },
    "lp_admission_merge": {
        "type": "Mixer",
        "inlets": ["1号炉低压蒸汽至汽轮机", "2号炉低压蒸汽至汽轮机"],
        "outlets": ["汽轮机低压补汽"],
    },
    "lp_inlet_mix": {
        "type": "Mixer",
        "inlets": ["汽轮机中压至低压连通管", "汽轮机低压补汽"],
        "outlets": ["汽轮机低压缸入口"],
    },
    "lp_turbine": {
        "type": "Turbine",
        "inlets": ["汽轮机低压缸入口"],
        "outlets": ["汽轮机低压缸排汽"],
    },
}
