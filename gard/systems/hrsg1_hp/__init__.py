"""hrsg1_hp system public interface."""

from importlib import import_module

from .streams import STREAM_DEFINITIONS
from .devices import DEVICE_DEFINITIONS

__all__ = [
    "prepare_row",
    "build_system",
    "STREAM_DEFINITIONS",
    "DEVICE_DEFINITIONS",
    "POINT_BINDINGS",
    "SYSTEM_DEFINITIONS",
]


def __getattr__(name):
    # 读取流股定义无需加载数据、设备和系统模块。
    if name == "POINT_BINDINGS":
        module = import_module(".data", __name__)
    elif name == "SYSTEM_DEFINITIONS":
        module = import_module(".system", __name__)
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    value = getattr(module, name)
    globals()[name] = value
    return value


def prepare_row(row, ref_env=None, config=None):
    """Prepare SI state/flow values from raw SI inputs."""
    from ..hrsg_hp import prepare_hp_inputs
    return prepare_hp_inputs(1, row, ref_env, config).row


def build_system(row, ref_env=None, config=None):
    from ..hrsg_hp import build_hp_system
    return build_hp_system(1, row, ref_env, config)
