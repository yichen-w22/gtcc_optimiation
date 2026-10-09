from dataclasses import dataclass
from src.base.device import Device


@dataclass
class Splitter(Device):
    """A junction with one inlet and multiple outlets."""
