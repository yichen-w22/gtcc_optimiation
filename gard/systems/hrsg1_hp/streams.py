"""hrsg1_hp owned streams."""
from src.working_fluid.stream import StreamBook

# 2. 流股
def build_streams(row, ref_env):
    row = dict(row)
    row.setdefault("hrsg1.hp_drum_steam.P", row.get("hrsg1.hp_drum_pressure"))
    row.setdefault("hrsg1.hp_drum_steam.x", 1.0)
    streams = StreamBook(row, ref_env)
    streams.add("hrsg1.hp_pump_in")
    streams.add("hrsg1.hp_pump1_in")
    streams.add("hrsg1.hp_pump2_in")
    streams.add("hrsg1.hp_pump1_out")
    streams.add("hrsg1.hp_pump2_out")
    streams.add("hrsg1.hp_pump_out")
    streams.add("hrsg1.hp_feed")
    streams.add("hrsg1.hp_economizer1_out")
    streams.add("hrsg1.hp_economizer2_out")
    streams.add("hrsg1.hp_economizer_in")
    streams.add("hrsg1.hp_to_drum")
    streams.add("hrsg1.hp_drum_steam")
    streams.add("hrsg1.hp_drum_drain")
    streams.add("hrsg1.hp_sh1_out")
    streams.add("hrsg1.hp_before_spray")
    streams.add("hrsg1.hp_spray")
    streams.add("hrsg1.hp_after_spray")
    streams.add("hrsg1.hp_sh2_out")
    streams.add("hrsg1.hp_main")
    streams.add("hrsg1.hp_to_st")
    streams.add("hrsg1.hp_bypass_in")
    streams.add("hrsg1.hp_bypass_throttled")
    streams.add("hrsg1.hp_bypass_spray")
    streams.add("hrsg1.hp_bypass_out")
    streams.add("hrsg1.hp_pump_return", "泵回流去向和流量未闭合前作为待核对边界")
    return streams


