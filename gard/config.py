"""GARD reference conditions; fixed pressure is the user's current approximation."""
from src.base.stream import create_ref_env

DEFAULT_ENVIRONMENT_PRESSURE = 101375.0  # Pa, absolute
DEFAULT_REFERENCE_TEMPERATURE = 298.15  # K, declared fixed reference


def reference_environment(T0=DEFAULT_REFERENCE_TEMPERATURE, P0=DEFAULT_ENVIRONMENT_PRESSURE):
    return create_ref_env(T0, P0)
