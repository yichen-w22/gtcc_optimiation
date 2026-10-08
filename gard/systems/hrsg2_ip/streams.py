"""hrsg2_ip owned streams."""
from src.working_fluid.stream import StreamBook

# 2. 流股
def build_streams(row, ref_env):
    row = dict(row)
    row.setdefault("hrsg2.ip_drum_steam.P", row.get("hrsg2.ip_drum_pressure"))
    row.setdefault("hrsg2.ip_drum_steam.x", 1.0)
    streams = StreamBook(row, ref_env)
    streams.add("hrsg2.ip_pump_in")
    streams.add("hrsg2.ip_pump1_in")
    streams.add("hrsg2.ip_pump2_in")
    streams.add("hrsg2.ip_pump1_out")
    streams.add("hrsg2.ip_pump2_out")
    streams.add("hrsg2.ip_pump_out")
    streams.add("hrsg2.ip_feed")
    streams.add("hrsg2.ip_economizer_out")
    streams.add("hrsg2.ip_to_drum")
    streams.add("hrsg2.ip_drum_steam")
    streams.add("hrsg2.ip_drum_drain")
    streams.add("hrsg2.ip_fresh")
    streams.add("hrsg2.cold_reheat")
    streams.add("hrsg2.cold_reheat_with_bypass")
    streams.add("hrsg2.reheat_mixed")
    streams.add("hrsg2.rh1_out")
    streams.add("hrsg2.rh_spray")
    streams.add("hrsg2.rh_after_spray")
    streams.add("hrsg2.rh2_out")
    streams.add("hrsg2.hot_reheat")
    streams.add("hrsg2.rh_to_st")
    streams.add("hrsg2.ip_bypass_in")
    streams.add("hrsg2.ip_bypass_throttled")
    streams.add("hrsg2.ip_bypass_spray")
    streams.add("hrsg2.ip_bypass_out")
    streams.add("hrsg2.ip_bypass_to_heat")
    streams.add("hrsg2.ip_bypass_to_condenser")
    streams.add("hrsg2.ip_pump_return", "含反冲洗等其他用水，不能默认为零")
    return streams


