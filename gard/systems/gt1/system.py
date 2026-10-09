"""使用已有流股装配 1 号燃机；锅炉烟气边界单独保存在 streams 中。"""

from src.GT_model.GT_model import GTModel
from .streams import HRSG_INLET_STREAM_NAME


SYSTEM_DEFINITIONS = {
    "gt1": {
        "type": "GTModel",
        "streams": {
            "state_1": "1号燃机进气",
            "compressor_outlet": "1号燃机压气机出口",
            "fuel": "1号燃机燃料",
            "state_4": "1号燃机排气",
            "hrsg_outlet": "1号余热锅炉出口烟气",
        },
        "actual_power": "gt1.power",
        "total_pressure_recovery": "gt1.total_pressure_recovery",
        "fuel_chemical_exergy": "gt1.fuel_chemical_exergy",
        "config": "gt1.config",
    },
}


def build_gt1(row, streams, ports=None, config=None):
    system_streams = streams.copy()
    if ports is not None:
        system_streams.update(ports)

    return GTModel(
        name="gt1",
        state_1=system_streams.get("1号燃机进气"),
        compressor_outlet=system_streams.get("1号燃机压气机出口"),
        fuel=system_streams.get("1号燃机燃料"),
        state_4=system_streams[HRSG_INLET_STREAM_NAME],
        hrsg_outlet=system_streams.get("1号余热锅炉出口烟气"),
        config=config,
        actual_power=row.get("gt1.power"),
        total_pressure_recovery=row.get("gt1.total_pressure_recovery"),
        fuel_chemical_exergy=row.get("gt1.fuel_chemical_exergy"),
    )
