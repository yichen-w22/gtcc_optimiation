"""auxiliary owned streams."""
from src.working_fluid.stream import StreamBook

# 2. 流股
def build_streams(row, ref_env):
    streams = StreamBook(row, ref_env)
    streams.add("aux.gland_exhaust")
    streams.add("aux.gland_drain")
    streams.add("aux.external_steam")
    streams.add("aux.external_drain")
    return streams


