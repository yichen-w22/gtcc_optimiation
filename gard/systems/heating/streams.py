"""heating owned streams."""
from src.working_fluid.stream import StreamBook

# 2. 流股
def build_streams(row, ref_env):
    streams = StreamBook(row, ref_env)
    streams.add("heat.drain_return")
    streams.add("heat.return_water")
    streams.add("heat.supply_water")
    streams.add("heat.steam_header")
    streams.add("heat.drain_before_pump")
    streams.add("heat.recovery1_water_in")
    streams.add("heat.recovery1_water_out")
    streams.add("heat.recovery2_water_in")
    streams.add("heat.recovery2_water_out")
    return streams


