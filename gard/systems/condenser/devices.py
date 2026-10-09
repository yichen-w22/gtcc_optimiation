"""condenser device definitions."""


DEVICE_DEFINITIONS = {
    "condenser": {
        "type": "HeatExchanger",
        "inlets": ["冷却水供水", "汽轮机低压缸排汽", "1号炉中压旁路至凝汽器", "2号炉中压旁路至凝汽器", "1号炉低压旁路出口", "2号炉低压旁路出口", "凝结水系统前置泵再循环", "凝结水系统主再循环", "凝结水系统溢流", "凝结水系统补水", "凝结水系统疏水汇集"],
        "outlets": ["冷却水回水", "凝结水系统热井", "凝结水系统真空抽气边界"],
    },
    "vacuum_pump1": {
        "type": "Device",
    },
    "vacuum_pump2": {
        "type": "Device",
    },
    "vacuum_pump3": {
        "type": "Device",
    },
    "hotwell_outlet_pipe": {
        "type": "ThrottleValve",
        "inlets": ["凝结水系统热井"],
        "outlets": ["凝结水系统前置泵入口母管"],
    },
    "pre_pump_split": {
        "type": "Splitter",
        "inlets": ["凝结水系统前置泵入口母管"],
        "outlets": ["凝结水系统前置泵1入口", "凝结水系统前置泵2入口", "凝结水系统前置泵3入口"],
    },
    "pre_pump1": {
        "type": "Pump",
        "inlets": ["凝结水系统前置泵1入口"],
        "outlets": ["凝结水系统前置泵1出口"],
    },
    "pre_pump2": {
        "type": "Pump",
        "inlets": ["凝结水系统前置泵2入口"],
        "outlets": ["凝结水系统前置泵2出口"],
    },
    "pre_pump3": {
        "type": "Pump",
        "inlets": ["凝结水系统前置泵3入口"],
        "outlets": ["凝结水系统前置泵3出口"],
    },
    "pre_pump_merge": {
        "type": "Mixer",
        "inlets": ["凝结水系统前置泵1出口", "凝结水系统前置泵2出口", "凝结水系统前置泵3出口"],
        "outlets": ["凝结水系统前置泵出口母管"],
    },
    "pre_recycle_split": {
        "type": "Splitter",
        "inlets": ["凝结水系统前置泵出口母管"],
        "outlets": ["凝结水系统前置泵向前输送", "凝结水系统前置泵再循环", "凝结水系统溢流"],
    },
    "cond_control_split": {
        "type": "Splitter",
        "inlets": ["凝结水系统前置泵向前输送"],
        "outlets": ["凝结水系统调节阀入口", "凝结水系统调节阀旁路入口"],
    },
    "cond_control": {
        "type": "ThrottleValve",
        "inlets": ["凝结水系统调节阀入口"],
        "outlets": ["凝结水系统调节阀出口"],
    },
    "cond_control_bypass": {
        "type": "ThrottleValve",
        "inlets": ["凝结水系统调节阀旁路入口"],
        "outlets": ["凝结水系统调节阀旁路出口"],
    },
    "cond_control_merge": {
        "type": "Mixer",
        "inlets": ["凝结水系统调节阀出口", "凝结水系统调节阀旁路出口"],
        "outlets": ["凝结水系统疏水混合前"],
    },
    "heating_drain_mix": {
        "type": "Mixer",
        "inlets": ["凝结水系统疏水混合前", "供热系统疏水返回"],
        "outlets": ["凝结水系统轴封加热器入口"],
    },
    "gland_heater": {
        "type": "HeatExchanger",
        "inlets": ["凝结水系统轴封加热器入口", "凝结水系统轴封加热器汽侧入口"],
        "outlets": ["凝结水系统轴封加热器出口", "凝结水系统轴封加热器疏水出口"],
    },
    "cond_pump_split": {
        "type": "Splitter",
        "inlets": ["凝结水系统轴封加热器出口"],
        "outlets": ["凝结水系统凝结水泵1入口", "凝结水系统凝结水泵2入口", "凝结水系统凝结水泵3入口"],
    },
    "cond_pump1": {
        "type": "Pump",
        "inlets": ["凝结水系统凝结水泵1入口"],
        "outlets": ["凝结水系统凝结水泵1出口"],
    },
    "cond_pump2": {
        "type": "Pump",
        "inlets": ["凝结水系统凝结水泵2入口"],
        "outlets": ["凝结水系统凝结水泵2出口"],
    },
    "cond_pump3": {
        "type": "Pump",
        "inlets": ["凝结水系统凝结水泵3入口"],
        "outlets": ["凝结水系统凝结水泵3出口"],
    },
    "cond_pump_merge": {
        "type": "Mixer",
        "inlets": ["凝结水系统凝结水泵1出口", "凝结水系统凝结水泵2出口", "凝结水系统凝结水泵3出口"],
        "outlets": ["凝结水系统凝结水泵出口母管"],
    },
    "cond_users_split": {
        "type": "Splitter",
        "inlets": ["凝结水系统凝结水泵出口母管"],
        "outlets": ["凝结水系统除铁过滤器入口", "凝结水系统主再循环", "1号炉中压旁路减温水", "2号炉中压旁路减温水", "1号炉低压旁路减温水", "2号炉低压旁路减温水", "凝结水系统其他用户"],
    },
    "iron_filter": {
        "type": "ThrottleValve",
        "inlets": ["凝结水系统除铁过滤器入口"],
        "outlets": ["凝结水系统至锅炉母管"],
    },
    "boiler_feed_split": {
        "type": "Splitter",
        "inlets": ["凝结水系统至锅炉母管"],
        "outlets": ["1号炉低压给水", "2号炉低压给水"],
    },
}
