"""hrsg1_hp system public interface."""

from importlib import import_module

from .streams import STREAM_DEFINITIONS
from .devices import DEVICE_DEFINITIONS

__all__ = [
    "STREAM_DEFINITIONS",
    "DEVICE_DEFINITIONS",
    "POINT_BINDINGS",
    "read_bindings",
    "load_raw_data",
    "prepare_inputs",
    "load_inputs",
    "SYSTEM_DEFINITIONS",
    "prepare_system_inputs",
]


def __getattr__(name):
    # 读取流股定义无需加载数据、设备和系统模块。
    if name in (
        "POINT_BINDINGS",
        "read_bindings",
        "load_raw_data",
        "prepare_inputs",
        "load_inputs",
        "prepare_system_inputs",
    ):
        module = import_module(".data", __name__)
    elif name == "SYSTEM_DEFINITIONS":
        module = import_module(".system", __name__)
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    value = getattr(module, name)
    globals()[name] = value
    return value
