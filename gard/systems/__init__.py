"""按名称构建单个完整系统。"""

__all__ = ["build_system"]


def build_system(name, row, ref_env):
    """预处理指定系统的数据，从统一定义目录构建系统。"""
    from src.base.system_builder import build_system as build_from_definition
    from .system_registry import SYSTEM_DEFINITIONS, SYSTEM_INPUT_PREPARERS
    from .device_registry import DEVICE_DEFINITIONS
    from .stream_registry import STREAM_DEFINITIONS

    inputs = SYSTEM_INPUT_PREPARERS[name](row)
    return build_from_definition(
        name, SYSTEM_DEFINITIONS, DEVICE_DEFINITIONS,
        STREAM_DEFINITIONS, inputs, ref_env,
    )
