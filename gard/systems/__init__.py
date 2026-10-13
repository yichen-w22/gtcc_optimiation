"""按名称构建单个完整系统。"""

__all__ = ["build_system"]


def build_system(name, row, ref_env=None, *, config=None):
    """使用已准备好的 SI 数据，从统一定义目录构建系统。"""
    from gard.config import reference_environment
    if name in {"hrsg1_hp", "hrsg2_hp"}:
        from .hrsg_hp import build_hp_system
        return build_hp_system(int(name[4]), row, ref_env, config)
    if name in {"hrsg1_ip", "hrsg2_ip"}:
        from .hrsg_ip import build_ip_system
        return build_ip_system(int(name[4]), row, ref_env, config)
    if name in {"hrsg1_lp", "hrsg2_lp"}:
        from .hrsg_lp import build_lp_system
        return build_lp_system(int(name[4]), row, ref_env, config)
    ref_env = ref_env if ref_env is not None else reference_environment()
    if name in {'st', 'heating'}:
        from .hrsg_lp import prepare_lp_steam_interfaces
        row = prepare_lp_steam_interfaces(row, ref_env)
    from src.base.system_builder import build_system as build_from_definition
    from .system_registry import SYSTEM_DEFINITIONS
    from .device_registry import DEVICE_DEFINITIONS
    from .stream_registry import STREAM_DEFINITIONS

    return build_from_definition(
        name, SYSTEM_DEFINITIONS, DEVICE_DEFINITIONS,
        STREAM_DEFINITIONS, row, ref_env,
    )
