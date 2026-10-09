"""使用已有流股装配 2 号燃机；锅炉烟气边界单独保存在 streams 中。"""

from src.GT_model.GT_model import GTModel
from .streams import HRSG_INLET_STREAM_NAME


SYSTEM_DEFINITIONS = {
    "gt2": {
        "type": "GTModel",
        "streams": {
            "state_1": "2号燃机进气",
            "compressor_outlet": "2号燃机压气机出口",
            "fuel": "2号燃机燃料",
            "state_4": "2号燃机排气",
            "hrsg_outlet": "2号余热锅炉出口烟气",
        },
        "actual_power": "gt2.power",
        "total_pressure_recovery": "gt2.total_pressure_recovery",
        "fuel_chemical_exergy": "gt2.fuel_chemical_exergy",
        "config": "gt2.config",
    },
}


def build_gt2(row, streams, ports=None, config=None):
    system_streams = streams.copy()
    if ports is not None:
        system_streams.update(ports)

    return GTModel(
        name="gt2",
        state_1=system_streams.get("2号燃机进气"),
        compressor_outlet=system_streams.get("2号燃机压气机出口"),
        fuel=system_streams.get("2号燃机燃料"),
        state_4=system_streams[HRSG_INLET_STREAM_NAME],
        hrsg_outlet=system_streams.get("2号余热锅炉出口烟气"),
        config=config,
        actual_power=row.get("gt2.power"),
        total_pressure_recovery=row.get("gt2.total_pressure_recovery"),
        fuel_chemical_exergy=row.get("gt2.fuel_chemical_exergy"),
    )
