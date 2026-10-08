"""hrsg1_ip owned streams."""
from src.working_fluid.stream import StreamBook

# 2. 流股
def build_streams(row, ref_env):
    row = dict(row)
    row.setdefault("hrsg1.ip_drum_steam.P", row.get("hrsg1.ip_drum_pressure"))
    row.setdefault("hrsg1.ip_drum_steam.x", 1.0)
    streams = StreamBook(row, ref_env)
    streams.add("hrsg1.ip_pump_in")
    streams.add("hrsg1.ip_pump1_in")
    streams.add("hrsg1.ip_pump2_in")
    streams.add("hrsg1.ip_pump1_out")
    streams.add("hrsg1.ip_pump2_out")
    streams.add("hrsg1.ip_pump_out")
    streams.add("hrsg1.ip_feed")
    streams.add("hrsg1.ip_economizer_out")
    streams.add("hrsg1.ip_to_drum")
    streams.add("hrsg1.ip_drum_steam")
    streams.add("hrsg1.ip_drum_drain")
    streams.add("hrsg1.ip_fresh")
    streams.add("hrsg1.cold_reheat")
    streams.add("hrsg1.cold_reheat_with_bypass")
    streams.add("hrsg1.reheat_mixed")
    streams.add("hrsg1.rh1_out")
    streams.add("hrsg1.rh_spray")
    streams.add("hrsg1.rh_after_spray")
    streams.add("hrsg1.rh2_out")
    streams.add("hrsg1.hot_reheat")
    streams.add("hrsg1.rh_to_st")
    streams.add("hrsg1.ip_bypass_in")
    streams.add("hrsg1.ip_bypass_throttled")
    streams.add("hrsg1.ip_bypass_spray")
    streams.add("hrsg1.ip_bypass_out")
    streams.add("hrsg1.ip_bypass_to_heat")
    streams.add("hrsg1.ip_bypass_to_condenser")
    streams.add("hrsg1.ip_pump_return", "含反冲洗等其他用水，不能默认为零")
    return streams


