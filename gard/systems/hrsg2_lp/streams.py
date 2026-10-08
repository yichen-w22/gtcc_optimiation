"""hrsg2_lp owned streams."""
from src.working_fluid.stream import StreamBook

# 2. 流股
def build_streams(row, ref_env):
    row = dict(row)
    row.setdefault("hrsg2.lp_saturated_steam.P", row.get("hrsg2.lp_drum_pressure"))
    row.setdefault("hrsg2.lp_saturated_steam.x", 1.0)
    row.setdefault("hrsg2.lp_water.P", row.get("hrsg2.lp_drum_pressure"))
    row.setdefault("hrsg2.lp_water.x", 0.0)
    streams = StreamBook(row, ref_env)
    streams.add("hrsg2.lp_feed")
    streams.add("hrsg2.lp_economizer_in")
    streams.add("hrsg2.lp_economizer_out")
    streams.add("hrsg2.lp_economizer_bypass")
    streams.add("hrsg2.lp_feed_to_mix")
    streams.add("hrsg2.lp_feed_mixed")
    streams.add("hrsg2.lp_drum_valve_in")
    streams.add("hrsg2.lp_to_drum")
    streams.add("hrsg2.lp_to_heat_recovery")
    streams.add("hrsg2.lp_from_heat_recovery")
    streams.add("hrsg2.lp_feed_after_recovery")
    streams.add("hrsg2.lp_recirc_in")
    streams.add("hrsg2.lp_recirc_pump1_in")
    streams.add("hrsg2.lp_recirc_pump2_in")
    streams.add("hrsg2.lp_recirc_pump1_out")
    streams.add("hrsg2.lp_recirc_pump2_out")
    streams.add("hrsg2.lp_recirc_out")
    streams.add("hrsg2.lp_water")
    streams.add("hrsg2.lp_saturated_steam", "汽包蒸汽出口；不采用饱和液体代替")
    streams.add("hrsg2.lp_drum_drain")
    streams.add("hrsg2.lp_main")
    streams.add("hrsg2.lp_to_st")
    streams.add("hrsg2.lp_to_heat")
    streams.add("hrsg2.lp_bypass_in")
    streams.add("hrsg2.lp_bypass_throttled")
    streams.add("hrsg2.lp_bypass_spray")
    streams.add("hrsg2.lp_bypass_out")
    return streams


