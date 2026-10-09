"""统一汇集各系统的流股定义，不构建流股对象。"""

from .gt1.streams import STREAM_DEFINITIONS as GT1
from .gt2.streams import STREAM_DEFINITIONS as GT2
from .hrsg1_hp.streams import STREAM_DEFINITIONS as HP1
from .hrsg1_ip.streams import STREAM_DEFINITIONS as IP1
from .hrsg1_lp.streams import STREAM_DEFINITIONS as LP1
from .hrsg2_hp.streams import STREAM_DEFINITIONS as HP2
from .hrsg2_ip.streams import STREAM_DEFINITIONS as IP2
from .hrsg2_lp.streams import STREAM_DEFINITIONS as LP2
from .st.streams import STREAM_DEFINITIONS as ST
from .condenser.streams import STREAM_DEFINITIONS as CONDENSER
from .cooling.streams import STREAM_DEFINITIONS as COOLING
from .heating.streams import STREAM_DEFINITIONS as HEATING


STREAM_DEFINITIONS = {
    **GT1, **GT2,
    **HP1, **IP1, **LP1,
    **HP2, **IP2, **LP2,
    **ST, **CONDENSER, **COOLING, **HEATING,
}
