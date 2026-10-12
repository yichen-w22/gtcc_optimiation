"""按名称构建单个完整系统。"""

__all__ = ["build_system"]


def build_system(name, row, ref_env):
    """使用已准备好的 SI 数据，从统一定义目录构建系统。"""
    from src.base.system_builder import build_system as build_from_definition
    from .system_registry import SYSTEM_DEFINITIONS
    from .device_registry import DEVICE_DEFINITIONS
    from .stream_registry import STREAM_DEFINITIONS

    return build_from_definition(
        name, SYSTEM_DEFINITIONS, DEVICE_DEFINITIONS,
        STREAM_DEFINITIONS, row, ref_env,
    )
