"""整厂模型：两台燃机、两台完整锅炉及汽轮机和公用系统。"""

from src.base.device import Device
from src.base.plant import Plant
from src.base.system import System
from gard.systems import build_system


def build_hrsg(name, row, ref_env, gt):
    """复用燃机中的锅炉烟气边界，装配完整锅炉。

    heat/heat_exergy 只记录锅炉整体对外传热；子系统的水侧吸热属于内部传热。
    """
    subsystems = {
        f"{name}_hp": build_system(f"{name}_hp", row, ref_env),
        f"{name}_ip": build_system(f"{name}_ip", row, ref_env),
        f"{name}_lp": build_system(f"{name}_lp", row, ref_env),
    }
    devices = [device for system in subsystems.values() for device in system.devices]
    devices.append(
        Device(
            name=f"{name}_gas_boundary",
            inlets=[gt.hrsg_inlet],
            outlets=[gt.hrsg_outlet],
        )
    )

    return System(
        name=name,
        devices=devices,
        subsystems=subsystems,
        work=sum(system.work for system in subsystems.values()),
        heat=row.get(f"{name}.heat"),
        heat_exergy=row.get(f"{name}.heat_exergy"),
    )


def build_plant(row, ref_env, name="gard"):
    """构建整厂；所有系统和流股共用传入的参考环境。"""
    gt1 = build_system("gt1", row, ref_env)
    gt2 = build_system("gt2", row, ref_env)
    hrsg1 = build_hrsg("hrsg1", row, ref_env, gt1)
    hrsg2 = build_hrsg("hrsg2", row, ref_env, gt2)
    st = build_system("st", row, ref_env)
    condenser = build_system("condenser", row, ref_env)
    cooling = build_system("cooling", row, ref_env)
    heating = build_system("heating", row, ref_env)

    return Plant(
        name=name,
        systems=[gt1, gt2, hrsg1, hrsg2, st, condenser, cooling, heating],
    )
