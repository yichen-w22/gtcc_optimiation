"""cooling owned streams."""
from src.working_fluid.stream import StreamBook

# 2. 流股
def build_streams(row, ref_env):
    streams = StreamBook(row, ref_env)
    streams.add("cooling.supply")
    streams.add("cooling.return")
    streams.add("cooling.external_in")
    streams.add("cooling.external_out")
    return streams


