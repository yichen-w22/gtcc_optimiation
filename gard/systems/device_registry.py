"""统一汇集汽水系统的设备定义，不构建设备对象。"""

from .hrsg1_hp.devices import DEVICE_DEFINITIONS as HP1
from .hrsg1_ip.devices import DEVICE_DEFINITIONS as IP1
from .hrsg1_lp.devices import DEVICE_DEFINITIONS as LP1
from .hrsg2_hp.devices import DEVICE_DEFINITIONS as HP2
from .hrsg2_ip.devices import DEVICE_DEFINITIONS as IP2
from .hrsg2_lp.devices import DEVICE_DEFINITIONS as LP2
from .st.devices import DEVICE_DEFINITIONS as ST
from .condenser.devices import DEVICE_DEFINITIONS as CONDENSER
from .cooling.devices import DEVICE_DEFINITIONS as COOLING
from .heating.devices import DEVICE_DEFINITIONS as HEATING


DEVICE_DEFINITIONS = {
    **HP1, **IP1, **LP1,
    **HP2, **IP2, **LP2,
    **ST, **CONDENSER, **COOLING, **HEATING,
}
