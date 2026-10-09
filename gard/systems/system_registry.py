"""统一汇集完整系统定义及各系统的数据预处理入口。"""

from . import gt1, gt2, hrsg1_hp, hrsg1_ip, hrsg1_lp, hrsg2_hp, hrsg2_ip, hrsg2_lp
from . import st, condenser, cooling, heating


SYSTEM_DEFINITIONS = {
    **gt1.SYSTEM_DEFINITIONS, **gt2.SYSTEM_DEFINITIONS,
    **hrsg1_hp.SYSTEM_DEFINITIONS, **hrsg1_ip.SYSTEM_DEFINITIONS, **hrsg1_lp.SYSTEM_DEFINITIONS,
    **hrsg2_hp.SYSTEM_DEFINITIONS, **hrsg2_ip.SYSTEM_DEFINITIONS, **hrsg2_lp.SYSTEM_DEFINITIONS,
    **st.SYSTEM_DEFINITIONS, **condenser.SYSTEM_DEFINITIONS,
    **cooling.SYSTEM_DEFINITIONS, **heating.SYSTEM_DEFINITIONS,
}


SYSTEM_INPUT_PREPARERS = {
    "gt1": gt1.prepare_system_inputs,
    "gt2": gt2.prepare_system_inputs,
    "hrsg1_hp": hrsg1_hp.prepare_system_inputs,
    "hrsg1_ip": hrsg1_ip.prepare_system_inputs,
    "hrsg1_lp": hrsg1_lp.prepare_system_inputs,
    "hrsg2_hp": hrsg2_hp.prepare_system_inputs,
    "hrsg2_ip": hrsg2_ip.prepare_system_inputs,
    "hrsg2_lp": hrsg2_lp.prepare_system_inputs,
    "st": st.prepare_system_inputs,
    "condenser": condenser.prepare_system_inputs,
    "cooling": cooling.prepare_system_inputs,
    "heating": heating.prepare_system_inputs,
}
