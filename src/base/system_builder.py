"""按系统定义构建设备，返回一个系统。"""

from src.base.device_builder import build_device
from src.base.stream_builder import build_stream
from src.base.system import System
from src.GT_model.GT_model import GTModel


SYSTEM_TYPES = {
    "System": System,
    "GTModel": GTModel,
}


def build_system(
    name, system_definitions, device_definitions,
    stream_definitions, row, ref_env,
):
    """只构建指定系统包含的设备和所需流股。"""
    definition = system_definitions[name].copy()
    constructor = SYSTEM_TYPES[definition.pop("type", "System")]
    parameters = {}

    for parameter, source in definition.items():
        if parameter == "devices":
            parameters[parameter] = [
                build_device(
                    device_name, device_definitions,
                    stream_definitions, row, ref_env,
                )
                for device_name in source
            ]
        elif parameter == "streams":
            for argument, stream_name in source.items():
                parameters[argument] = build_stream(stream_name, stream_definitions, row, ref_env)
        elif isinstance(source, str):
            parameters[parameter] = row.get(source)
        else:
            parameters[parameter] = source

    return constructor(name=name, **parameters)
