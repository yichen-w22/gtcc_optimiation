"""A system contains devices; shared internal streams cancel at its boundary."""

from dataclasses import dataclass, field

from .device import Device

@dataclass
class System:
    """稳态开口系统；忽略动能、位能及系统蓄能变化。

    流股按系统外边界统计，内部流股抵消。热量流入为正，功输出为正，
    功、热量及热量火用只记录穿过本系统边界的部分。
    """

    name: str
    devices: list[Device] = field(default_factory=list)
    work: float | None = 0.0 # 系统对外做功：work > 0
    heat: float | None = 0.0 # 热量流入系统：heat > 0
    heat_exergy: float | None = 0.0 # 热量携带的火用净流入
    subsystems: dict[str, "System"] = field(default_factory=dict)

    @property
    def device(self):
        """按名称索引设备。"""
        return {device.name: device for device in self.devices}

    def add_device(self, device):
        self.devices.append(device)

    def mass_balance(self):
        return sum(d.mass_balance() for d in self.devices)

    def energy_balance(self):
        return sum(d.energy_balance() for d in self.devices) + self.heat - self.work

    def exergy_balance(self):
        """系统火用损失；不可逆过程通常大于零。"""
        return sum(d.exergy_balance() for d in self.devices) + self.heat_exergy - self.work

