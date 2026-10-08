"""st owned streams."""
from src.working_fluid.stream import StreamBook

# 2. 流股
def build_streams(row, ref_env):
    streams = StreamBook(row, ref_env)
    streams.add("st.hp_in")
    streams.add("st.hp_out")
    streams.add("st.ip_in")
    streams.add("st.ip_out")
    streams.add("st.ip_to_lp")
    streams.add("st.heat_extraction")
    streams.add("st.lp_admission")
    streams.add("st.lp_in")
    streams.add("st.lp_out", "湿蒸汽需要实测/独立推导 h 或 x；不默认 x=0.97")
    streams.add("st.gland_leakage", "高压缸轴封等支路合计；不能默认为零")
    streams.add("st.ip_leakage")
    return streams


