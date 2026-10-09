"""按设备定义构建所需流股，返回一个设备。"""

from src.base.device import Device
from src.base.stream_builder import build_stream
from src.ST_model.condenser import Condenser
from src.ST_model.heat_exchanger import HeatExchanger, GasWaterHeatExchanger
from src.ST_model.mixer import Mixer
from src.ST_model.pump import Pump
from src.ST_model.splitter import Splitter
from src.ST_model.throttle_valve import ThrottleValve
from src.ST_model.turbine import Turbine


DEVICE_TYPES = {
    "Device": Device,
    "Condenser": Condenser,
    "HeatExchanger": HeatExchanger,
    "GasWaterHeatExchanger": GasWaterHeatExchanger,
    "Mixer": Mixer,
    "Pump": Pump,
    "Splitter": Splitter,
    "ThrottleValve": ThrottleValve,
    "Turbine": Turbine,
}


def build_device(name, device_definitions, stream_definitions, row, ref_env):
    """只构建指定设备所需的流股，不缓存流股对象。"""
    definition = device_definitions[name].copy()
    constructor = DEVICE_TYPES[definition.pop("type")]
    parameters = {}

    for port, stream_names in definition.items():
        parameters[port] = [
            build_stream(stream_name, stream_definitions, row, ref_env)
            for stream_name in stream_names
        ]

    return constructor(name=name, **parameters)
