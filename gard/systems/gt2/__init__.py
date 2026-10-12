"""2 号燃机系统接口。"""

from .data import INPUT_UNITS, POINT_BINDINGS
from .streams import HRSG_INLET_STREAM_NAME, STREAM_DEFINITIONS
from .system import SYSTEM_DEFINITIONS, build_gt2

build_system = build_gt2

__all__ = ["INPUT_UNITS", "STREAM_DEFINITIONS", "SYSTEM_DEFINITIONS", "HRSG_INLET_STREAM_NAME", "POINT_BINDINGS", "build_gt2", "build_system"]
