"""统一汇集完整系统定义。"""

from . import gt1, gt2, hrsg1_hp, hrsg1_ip, hrsg1_lp, hrsg2_hp, hrsg2_ip, hrsg2_lp
from . import st, condenser, cooling, heating


SYSTEM_DEFINITIONS = {
    **gt1.SYSTEM_DEFINITIONS, **gt2.SYSTEM_DEFINITIONS,
    **hrsg1_hp.SYSTEM_DEFINITIONS, **hrsg1_ip.SYSTEM_DEFINITIONS, **hrsg1_lp.SYSTEM_DEFINITIONS,
    **hrsg2_hp.SYSTEM_DEFINITIONS, **hrsg2_ip.SYSTEM_DEFINITIONS, **hrsg2_lp.SYSTEM_DEFINITIONS,
    **st.SYSTEM_DEFINITIONS, **condenser.SYSTEM_DEFINITIONS,
    **cooling.SYSTEM_DEFINITIONS, **heating.SYSTEM_DEFINITIONS,
}
