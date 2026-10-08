"""condenser owned streams."""
from src.working_fluid.stream import StreamBook

# 2. 流股
def build_streams(row, ref_env):
    streams = StreamBook(row, ref_env)
    streams.add("cond.hotwell")
    streams.add("cond.pre_header_in")
    streams.add("cond.pre_pump1_in")
    streams.add("cond.pre_pump2_in")
    streams.add("cond.pre_pump3_in")
    streams.add("cond.pre_pump1_out")
    streams.add("cond.pre_pump2_out")
    streams.add("cond.pre_pump3_out")
    streams.add("cond.pre_header_out")
    streams.add("cond.pre_forward")
    streams.add("cond.pre_recycle")
    streams.add("cond.overflow")
    streams.add("cond.control_in")
    streams.add("cond.control_out")
    streams.add("cond.control_bypass_in")
    streams.add("cond.control_bypass_out")
    streams.add("cond.before_drain_mix")
    streams.add("cond.gland_heater_in")
    streams.add("cond.gland_heater_out")
    streams.add("cond.pump1_in")
    streams.add("cond.pump2_in")
    streams.add("cond.pump3_in")
    streams.add("cond.pump1_out")
    streams.add("cond.pump2_out")
    streams.add("cond.pump3_out")
    streams.add("cond.pump_header_out")
    streams.add("cond.filter_in")
    streams.add("cond.to_boilers")
    streams.add("cond.main_recycle")
    streams.add("cond.other_users", "凝结水其他用水边界未量化")
    streams.add("cond.makeup")
    streams.add("cond.drains")
    streams.add(
        "cond.vacuum_extraction",
        "汽气混合物，需另行提供非凝结气体模型；此处仅留汽侧端口",
    )
    return streams


