# 参数筛选明细

高压及中压已确认约定、低压拓扑及派生关系已实现；缺失数据保持None，低压全部缺项见 [lp_system_review.md](lp_system_review.md)。完整候选测点来源与推导条件见 [parameter_plan.json](parameter_plan.json)。

## 现有绑定

core 为主循环，component 为设备分配，validation 为独立校核；retain 不等于压力基准已确认。

| 系统 | 字段 | 采集层级 | 处理 | 原始点表依据 |
| --- | --- | --- | --- | --- |
| condenser | `cond.pre_header_in.P` | core | retain | DCS!D481 / E481 |
| condenser | `cond.pre_header_in.T` | core | retain | DCS!D482 / E482 |
| condenser | `cond.pre_pump1_out.P` | component | retain | DCS!D25 / E25 |
| condenser | `cond.pre_pump2_out.P` | component | retain | DCS!D261 / E261 |
| condenser | `cond.pre_pump3_out.P` | component | retain | DCS!D485 / E485 |
| condenser | `cond.pre_header_out.P` | core | retain | DCS!D491 / E491 |
| condenser | `cond.pre_header_out.T` | core | retain | DCS!D493 / E493 |
| condenser | `cond.gland_heater_in.P` | core | retain | DCS!D492 / E492 |
| condenser | `cond.gland_heater_in.m_dot` | core | retain | DCS!D2783 / E2783 |
| condenser | `cond.gland_heater_out.P` | core | retain | DCS!D498 / E498 |
| condenser | `cond.gland_heater_out.T` | core | retain | DCS!D499 / E499 |
| condenser | `cond.pump1_out.P` | component | retain | DCS!D29 / E29 |
| condenser | `cond.pump2_out.P` | component | retain | DCS!D265 / E265 |
| condenser | `cond.pump3_out.P` | component | retain | DCS!D502 / E502 |
| condenser | `cond.pump_header_out.P` | core | retain | DCS!D504 / E504 |
| condenser | `cond.filter_in.P` | component | retain | DCS!D537 / E537 |
| condenser | `cond.filter_in.T` | component | retain | DCS!D538 / E538 |
| condenser | `cond.to_boilers.P` | core | retain | DCS!D505 / E505 |
| condenser | `cond.to_boilers.T` | core | retain | DCS!D506 / E506 |
| condenser | `cond.to_boilers.m_dot` | core | retain | DCS!D2784 / E2784 |
| condenser | `cond.main_recycle.m_dot` | core | retain | DCS!D2840 / E2840 |
| condenser | `cond.makeup.P` | core | retain | DCS!D697 / E697 |
| condenser | `cond.makeup.m_dot` | core | retain | DCS!D2782 / E2782 |
| heating | `heat.drain_return.m_dot` | core | retain | DCS!D7360 / E7360 |
| hrsg1_hp | `hrsg1.lp_drum_pressure` | core | retain | DCS!D2920 / E2920 |
| hrsg1_hp | `hrsg1.hp_pump1.current` | component | retain | DCS!D1582 / E1582 |
| hrsg1_hp | `hrsg1.hp_pump2.current` | component | retain | DCS!D1779 / E1779 |
| hrsg1_hp | `hrsg1.hp_pump1_out.P` | component | retain | DCS!D1562 / E1562 |
| hrsg1_hp | `hrsg1.hp_pump2_out.P` | component | retain | DCS!D1767 / E1767 |
| hrsg1_hp | `hrsg1.hp_feed.P` | core | retain | DCS!D1574 / E1574 |
| hrsg1_hp | `hrsg1.hp_feed.T` | core | retain | DCS!D1575 / E1575 |
| hrsg1_hp | `hrsg1.hp_feed.m_dot` | core | retain | DCS!D2709 / E2709 |
| hrsg1_hp | `hrsg1.hp_to_drum.T` | component | retain | DCS!D1492 / E1492 |
| hrsg1_hp | `hrsg1.hp_drum_pressure` | core | retain | DCS!D1497 / E1497 |
| hrsg1_hp | `hrsg1.hp_before_spray.T` | component | retain | DCS!D12762 / E12762 |
| hrsg1_hp | `hrsg1.hp_after_spray.T` | component | retain | DCS!D1542 / E1542 |
| hrsg1_hp | `hrsg1.hp_main.P` | core | retain | DCS!D2762 / E2762 |
| hrsg1_hp | `hrsg1.hp_main.T` | core | retain | DCS!D2760 / E2760 |
| hrsg1_hp | `hrsg1.hp_main.m_dot` | core | retain | DCS!D2704 / E2704 |
| hrsg1_hp | `hrsg1.hp_to_st.P` | validation | retain | DCS!D2699 / E2699 |
| hrsg1_hp | `hrsg1.hp_to_st.T` | validation | retain | DCS!D112 / E112 |
| hrsg1_ip | `hrsg1.lp_drum_pressure` | core | retain | DCS!D2920 / E2920 |
| hrsg1_ip | `hrsg1.ip_pump1.current` | component | retain | DCS!D1578 / E1578 |
| hrsg1_ip | `hrsg1.ip_pump2.current` | component | retain | DCS!D1770 / E1770 |
| hrsg1_ip | `hrsg1.ip_pump1_out.P` | component | retain | DCS!D1579 / E1579 |
| hrsg1_ip | `hrsg1.ip_pump2_out.P` | component | retain | DCS!D1771 / E1771 |
| hrsg1_ip | `hrsg1.ip_feed.P` | core | retain | DCS!D1776 / E1776 |
| hrsg1_ip | `hrsg1.ip_feed.T` | core | retain | DCS!D1777 / E1777 |
| hrsg1_ip | `hrsg1.ip_feed.m_dot` | core | retain | DCS!D2719 / E2719 |
| hrsg1_ip | `hrsg1.ip_to_drum.T` | component | retain | DCS!D1706 / E1706 |
| hrsg1_ip | `hrsg1.ip_drum_pressure` | core | retain | DCS!D2917 / E2917 |
| hrsg1_ip | `hrsg1.ip_fresh.P` | core | retain | DCS!D2770 / E2770 |
| hrsg1_ip | `hrsg1.ip_fresh.T` | core | retain | DCS!D2772 / E2772 |
| hrsg1_ip | `hrsg1.ip_fresh.m_dot` | core | retain | DCS!D2768 / E2768 |
| hrsg1_ip | `hrsg1.reheat_mixed.P` | component | retain | DCS!D1820 / E1820 |
| hrsg1_ip | `hrsg1.reheat_mixed.T` | component | retain | DCS!D1821 / E1821 |
| hrsg1_ip | `hrsg1.rh_spray.m_dot` | core | retain | DCS!D2787 / E2787 |
| hrsg1_ip | `hrsg1.rh_before_spray.T` | core | retain | DCS!D1742 / E1742 |
| hrsg1_ip | `hrsg1.rh_after_spray.T` | component | retain | DCS!D12781 / E12781 |
| hrsg1_ip | `hrsg1.hot_reheat.P` | core | retain | DCS!D2766 / E2766 |
| hrsg1_ip | `hrsg1.hot_reheat.T` | core | retain | DCS!D2764 / E2764 |
| hrsg1_ip | `hrsg1.hot_reheat.m_dot` | core | retain | DCS!D2756 / E2756 |
| hrsg1_ip | `hrsg1.cold_reheat.P` | core | retain | DCS!D157 / E157 |
| hrsg1_ip | `hrsg1.cold_reheat.T` | core | retain | DCS!D159 / E159 |
| hrsg1_ip | `hrsg1.rh_to_st.P` | validation | retain | DCS!D2697 / E2697 |
| hrsg1_ip | `hrsg1.rh_to_st.T` | validation | retain | DCS!D143 / E143 |
| hrsg1_lp | `hrsg1.lp_feed_after_recovery.P` | core | retain | DCS!D1473 / E1473 |
| hrsg1_lp | `hrsg1.lp_feed_after_recovery.T` | core | retain | DCS!D1474 / E1474 |
| hrsg1_lp | `hrsg1.lp_from_heat_recovery.P` | core | retain | DCS!D1640 / E1640 |
| hrsg1_lp | `hrsg1.lp_from_heat_recovery.T` | core | retain | DCS!D1823 / E1823 |
| hrsg1_lp | `hrsg1.lp_feed.m_dot` | core | retain | DCS!D2758 / E2758 |
| hrsg1_lp | `hrsg1.lp_economizer_out.T` | component | retain | DCS!D1478 / E1478 |
| hrsg1_lp | `hrsg1.lp_drum_valve_in.P` | component | retain | DCS!D1477 / E1477 |
| hrsg1_lp | `hrsg1.lp_to_drum.T` | validation | retain | DCS!D1479 / E1479 |
| hrsg1_lp | `hrsg1.lp_recirc_pump1_out.P` | component | retain | DCS!D1483 / E1483 |
| hrsg1_lp | `hrsg1.lp_recirc_pump2_out.P` | component | retain | DCS!D1693 / E1693 |
| hrsg1_lp | `hrsg1.lp_main.P` | core | retain | DCS!D2774 / E2774 |
| hrsg1_lp | `hrsg1.lp_main.m_dot` | core | retain | DCS!D2778 / E2778 |
| hrsg1_lp | `hrsg1.lp_to_st.P` | validation | retain | DCS!D119 / E119 |
| hrsg1_lp | `hrsg1.lp_to_st.T` | validation | retain | DCS!D122 / E122 |
| hrsg1_lp | `hrsg1.lp_drum_pressure` | core | retain | DCS!D2920 / E2920 |
| hrsg1_lp | `hrsg1.lp_economizer_in.T` | core | retain | DCS!D1475 / E1475 |
| hrsg1_lp | `hrsg1.lp_recirc_in.m_dot` | core | retain | DCS!D1482 / E1482 |
| hrsg1_lp | `hrsg1.lp_main.T` | core | retain | DCS!D2776 / E2776 |
| hrsg1_lp | `hrsg1.lp_recirc_pump1.current` | component | retain | DCS!D1481 / E1481 |
| hrsg1_lp | `hrsg1.lp_recirc_pump2.current` | component | retain | DCS!D1692 / E1692 |
| hrsg1_lp | `hrsg1.hp_main.m_dot` | core | retain | DCS!D2704 / E2704 |
| hrsg1_lp | `hrsg1.ip_feed.m_dot` | core | retain | DCS!D2719 / E2719 |
| hrsg1_lp | `hrsg1.rh_spray.m_dot` | core | retain | DCS!D2787 / E2787 |
| hrsg2_hp | `hrsg2.lp_drum_pressure` | core | retain | DCS!D2930 / E2930 |
| hrsg2_hp | `hrsg2.hp_pump1.current` | component | retain | DCS!D2084 / E2084 |
| hrsg2_hp | `hrsg2.hp_pump2.current` | component | retain | DCS!D2280 / E2280 |
| hrsg2_hp | `hrsg2.hp_pump1_out.P` | component | retain | DCS!D2064 / E2064 |
| hrsg2_hp | `hrsg2.hp_pump2_out.P` | component | retain | DCS!D2267 / E2267 |
| hrsg2_hp | `hrsg2.hp_feed.P` | core | retain | DCS!D2076 / E2076 |
| hrsg2_hp | `hrsg2.hp_feed.T` | core | retain | DCS!D2077 / E2077 |
| hrsg2_hp | `hrsg2.hp_feed.m_dot` | core | retain | DCS!D2708 / E2708 |
| hrsg2_hp | `hrsg2.hp_to_drum.T` | component | retain | DCS!D1997 / E1997 |
| hrsg2_hp | `hrsg2.hp_drum_pressure` | core | retain | DCS!D2002 / E2002 |
| hrsg2_hp | `hrsg2.hp_before_spray.T` | component | retain | DCS!D12071 / E12071 |
| hrsg2_hp | `hrsg2.hp_after_spray.T` | component | retain | DCS!D2047 / E2047 |
| hrsg2_hp | `hrsg2.hp_main.P` | core | retain | DCS!D2763 / E2763 |
| hrsg2_hp | `hrsg2.hp_main.T` | core | retain | DCS!D2761 / E2761 |
| hrsg2_hp | `hrsg2.hp_main.m_dot` | core | retain | DCS!D2705 / E2705 |
| hrsg2_hp | `hrsg2.hp_to_st.P` | validation | retain | DCS!D2698 / E2698 |
| hrsg2_hp | `hrsg2.hp_to_st.T` | validation | retain | DCS!D306 / E306 |
| hrsg2_ip | `hrsg2.lp_drum_pressure` | core | retain | DCS!D2930 / E2930 |
| hrsg2_ip | `hrsg2.ip_pump1.current` | component | retain | DCS!D2080 / E2080 |
| hrsg2_ip | `hrsg2.ip_pump2.current` | component | retain | DCS!D2271 / E2271 |
| hrsg2_ip | `hrsg2.ip_pump1_out.P` | component | retain | DCS!D2081 / E2081 |
| hrsg2_ip | `hrsg2.ip_pump2_out.P` | component | retain | DCS!D2272 / E2272 |
| hrsg2_ip | `hrsg2.ip_feed.P` | core | retain | DCS!D2277 / E2277 |
| hrsg2_ip | `hrsg2.ip_feed.T` | core | retain | DCS!D2278 / E2278 |
| hrsg2_ip | `hrsg2.ip_feed.m_dot` | core | retain | DCS!D2718 / E2718 |
| hrsg2_ip | `hrsg2.ip_to_drum.T` | component | retain | DCS!D2205 / E2205 |
| hrsg2_ip | `hrsg2.ip_drum_pressure` | core | retain | DCS!D2927 / E2927 |
| hrsg2_ip | `hrsg2.ip_fresh.P` | core | retain | DCS!D2771 / E2771 |
| hrsg2_ip | `hrsg2.ip_fresh.T` | core | retain | DCS!D2773 / E2773 |
| hrsg2_ip | `hrsg2.ip_fresh.m_dot` | core | retain | DCS!D2769 / E2769 |
| hrsg2_ip | `hrsg2.reheat_mixed.P` | component | retain | DCS!D2322 / E2322 |
| hrsg2_ip | `hrsg2.reheat_mixed.T` | component | retain | DCS!D2323 / E2323 |
| hrsg2_ip | `hrsg2.rh_spray.m_dot` | core | retain | DCS!D2788 / E2788 |
| hrsg2_ip | `hrsg2.rh_before_spray.T` | core | retain | DCS!D2241 / E2241 |
| hrsg2_ip | `hrsg2.rh_after_spray.T` | component | retain | DCS!D12090 / E12090 |
| hrsg2_ip | `hrsg2.hot_reheat.P` | core | retain | DCS!D2767 / E2767 |
| hrsg2_ip | `hrsg2.hot_reheat.T` | core | retain | DCS!D2765 / E2765 |
| hrsg2_ip | `hrsg2.hot_reheat.m_dot` | core | retain | DCS!D2757 / E2757 |
| hrsg2_ip | `hrsg2.cold_reheat.P` | core | retain | DCS!D353 / E353 |
| hrsg2_ip | `hrsg2.cold_reheat.T` | core | retain | DCS!D356 / E356 |
| hrsg2_ip | `hrsg2.rh_to_st.P` | validation | retain | DCS!D2696 / E2696 |
| hrsg2_ip | `hrsg2.rh_to_st.T` | validation | retain | DCS!D337 / E337 |
| hrsg2_lp | `hrsg2.lp_feed_after_recovery.P` | core | retain | DCS!D1976 / E1976 |
| hrsg2_lp | `hrsg2.lp_feed_after_recovery.T` | core | retain | DCS!D1977 / E1977 |
| hrsg2_lp | `hrsg2.lp_from_heat_recovery.P` | core | retain | DCS!D2141 / E2141 |
| hrsg2_lp | `hrsg2.lp_from_heat_recovery.T` | core | retain | DCS!D2361 / E2361 |
| hrsg2_lp | `hrsg2.lp_feed.m_dot` | core | retain | DCS!D2759 / E2759 |
| hrsg2_lp | `hrsg2.lp_economizer_out.T` | component | retain | DCS!D1984 / E1984 |
| hrsg2_lp | `hrsg2.lp_drum_valve_in.P` | component | retain | DCS!D1983 / E1983 |
| hrsg2_lp | `hrsg2.lp_to_drum.T` | validation | retain | DCS!D1985 / E1985 |
| hrsg2_lp | `hrsg2.lp_recirc_pump1_out.P` | component | retain | DCS!D1991 / E1991 |
| hrsg2_lp | `hrsg2.lp_recirc_pump2_out.P` | component | retain | DCS!D2192 / E2192 |
| hrsg2_lp | `hrsg2.lp_main.P` | core | retain | DCS!D2775 / E2775 |
| hrsg2_lp | `hrsg2.lp_main.m_dot` | core | retain | DCS!D2779 / E2779 |
| hrsg2_lp | `hrsg2.lp_to_st.P` | validation | retain | DCS!D312 / E312 |
| hrsg2_lp | `hrsg2.lp_to_st.T` | validation | retain | DCS!D315 / E315 |
| hrsg2_lp | `hrsg2.lp_drum_pressure` | core | retain | DCS!D2930 / E2930 |
| hrsg2_lp | `hrsg2.lp_economizer_in.T` | core | retain | DCS!D1978 / E1978 |
| hrsg2_lp | `hrsg2.lp_recirc_in.m_dot` | core | retain | DCS!D1990 / E1990 |
| hrsg2_lp | `hrsg2.lp_main.T` | core | retain | DCS!D2777 / E2777 |
| hrsg2_lp | `hrsg2.lp_recirc_pump1.current` | component | retain | DCS!D1989 / E1989 |
| hrsg2_lp | `hrsg2.lp_recirc_pump2.current` | component | retain | DCS!D2191 / E2191 |
| hrsg2_lp | `hrsg2.hp_main.m_dot` | core | retain | DCS!D2705 / E2705 |
| hrsg2_lp | `hrsg2.ip_feed.m_dot` | core | retain | DCS!D2718 / E2718 |
| hrsg2_lp | `hrsg2.rh_spray.m_dot` | core | retain | DCS!D2788 / E2788 |
| st | `st.hp_in.P` | core | retain | DCS!D6 / E6 |
| st | `st.hp_in.T` | core | retain | DCS!D9 / E9 |
| st | `st.hp_out.P` | core | retain | DCS!D20 / E20 |
| st | `st.hp_out.T` | core | retain | DCS!D2466 / E2466 |
| st | `st.ip_in.P` | core | retain | DCS!D14 / E14 |
| st | `st.ip_in.T` | core | retain | DCS!D17 / E17 |
| st | `st.ip_out.T` | core | retain | DCS!D258 / E258 |
| st | `st.generator_power` | core | retain | DCS!D2810 / E2810 |
| st | `st.lp_out.P` | core | retain | DCS!D549 / E549 |

## 需补充或替换的字段

候选编码已核对原表的描述与单位；取点位置、基准和运行数据可用性仍需确认。没有选定编码的字段保留为缺口，不使用占位编码。

| 系统 | 字段 | 单位 | 层级 | 候选编码 | 用途 / 条件 |
| --- | --- | --- | --- | --- | --- |
| hrsg1_lp | `hrsg1.lp_feed.P` | MPa | core | 未选定 | 余热回收返回混合前低压给水压力 原HAA70压力已按用户指定移至混合后；混合前需独立测点或明确近似 |
| hrsg1_lp | `hrsg1.lp_feed.T` | ℃ | core | 未选定 | 余热回收返回混合前低压给水温度 原HAA70温度已按用户指定移至混合后；不能把同一测温当作混合前实测 |
| hrsg1_lp | `hrsg1.lp_to_heat_recovery.m_dot` | t/h | core | 未选定 | 水水换热器工质侧循环总流量 用户明确暂留空；闭合循环返回量等于送出量，但不能由给水量推得循环量 |
| hrsg1_lp | `hrsg1.lp_to_heat.m_dot` | t/h | core | 未选定 | 本炉低压蒸汽至供热流量 每炉需要一个独立分流依据；全厂供热总流量不能唯一分配到两炉 |
| hrsg2_lp | `hrsg2.lp_feed.P` | MPa | core | 未选定 | 余热回收返回混合前低压给水压力 原HAA70压力已按用户指定移至混合后；混合前需独立测点或明确近似 |
| hrsg2_lp | `hrsg2.lp_feed.T` | ℃ | core | 未选定 | 余热回收返回混合前低压给水温度 原HAA70温度已按用户指定移至混合后；不能把同一测温当作混合前实测 |
| hrsg2_lp | `hrsg2.lp_to_heat_recovery.m_dot` | t/h | core | 未选定 | 水水换热器工质侧循环总流量 用户明确暂留空；闭合循环返回量等于送出量，但不能由给水量推得循环量 |
| hrsg2_lp | `hrsg2.lp_to_heat.m_dot` | t/h | core | 未选定 | 本炉低压蒸汽至供热流量 每炉需要一个独立分流依据；全厂供热总流量不能唯一分配到两炉 |
| heating | `heat.lp_steam_header.P` | MPa | component | 未选定 | 两炉低压供热支路汇合后母管压力 新确认汇合节点；尚未选定测点或混合压力近似 |
| heating | `heat.lp_steam_header.T` | ℃ | component | 未选定 | 两炉低压供热支路汇合后母管温度 尚未选定测点；两炉温度不同时不能直接复制任一炉温度 |
| st | `st.ip_out.P` | MPa | core | `GARD_13LBS4400000BP01XQ01`、`GARD_13MAB5000000BP03XQ01`、`GARD_13MAB5000000BP04XQ01`、`GARD_13MAB5000000BP05XQ01` | 中压排汽、供热抽汽与低压连通管的焓熵状态。 核对压力取点与供热抽汽截面；选择值/多个通道不是多份独立状态。 |
| st | `st.lp_in.P` | MPa | core | `GARD_13LBA1200000BT01XQ01` | 补汽混合后的实际低压缸入口压力，不能由温度或质量平衡推出。  |
| st | `st.lp_in.T` | ℃ | validation | `GARD_13LBA2000000BP01XQ01` | 独立验证中压排汽和低压补汽的绝热混合焓。  |
| st | `st.lp_out.h` | J/kg | core | 未选定 | 湿蒸汽状态；可用独立轴功及全汽轮机能量平衡推导，但该能量残差将不是独立检验。 h 或 x 二选一；出口 P、T 在饱和区不独立。 |
| st | `st.work` | W | core | 未选定 | 模型真实消耗字段；需明确轴功边界或包含发电机的电功边界。 现有 st.generator_power 是电功输入；不能在未定义效率/损失边界时直接当轴功。 |
| heating | `heat.drain_return.P` | MPa | core | `GARD_00NDD80WP011BP01XQ01` | 供热疏水回到机组的边界火用。  |
| heating | `heat.drain_return.T` | ℃ | core | `GARD_00NDD80WP011BT01XQ01` | 疏水焓；仅机组工质侧测点。  |
| heating | `heat.drain_before_pump.P` | MPa | component | `GARD_00NDD70WP021BP01XQ01` | 区分汽水换热器与疏水泵，正确计入泵功。  |
| heating | `heat.drain_before_pump.T` | ℃ | component | 未选定 | 疏水泵入口公共母管状态；单台加热器温度不能自动替代混合母管。  |
| heating | `heat.steam_header.P` | MPa | component | 未选定 | 供热母管混合后状态；不同压力蒸汽进入同一母管需节流/混合边界说明。  |
| heating | `heat.steam_header.T` | ℃ | validation | 未选定 | 独立校核母管混合；可由混合焓及实测 P 推导。  |
| condenser | `cond.makeup.T` | ℃ | core | 未选定 | 保留补水能量与火用项；补水非零时要有损失流或蓄水项解释。  |
| condenser | `cond.pre_recycle.m_dot` | t/h | component | 未选定 | 前置泵再循环；现有选取表 CAL 通道的 % 单位待核实，不直接绑定。  |
| condenser | `cond.gland_steam.P` | MPa | core | 未选定 | 轴封加热器汽侧仍是当前图的外部输入，需要来源和状态。  |
| condenser | `cond.gland_drain.P` | MPa | core | 未选定 | 轴封加热器疏水外部出口；汽侧质量独立守恒，不与主凝结水混合。  |
| condenser | `cond.gland_steam.T` | ℃ | core | 未选定 | 轴封加热器汽侧仍是当前图的外部输入，需要来源和状态。  |
| condenser | `cond.gland_drain.T` | ℃ | core | 未选定 | 轴封加热器疏水外部出口；汽侧质量独立守恒，不与主凝结水混合。  |
| condenser | `cond.gland_steam.m_dot` | t/h | core | 未选定 | 轴封加热器汽侧仍是当前图的外部输入，需要来源和状态。  |
| condenser | `cond.gland_drain.m_dot` | t/h | core | 未选定 | 轴封加热器疏水外部出口；汽侧质量独立守恒，不与主凝结水混合。  |
| condenser | `cond.gland_heater_in.T` | ℃ | component | 未选定 | 轴封加热器水侧入口焓，支撑加热器吸热与火用变化。  |
| global | `reference.T0` | K | core | 未选定 | 统一参考环境；不得用给水泵房或电气间温度替代室外参考环境。 可以声明固定参考环境，也可以使用已核实室外环境；表压转绝压用的实际大气压与固定火用参考压力不是同一个概念。 |
| global | `reference.P0` | Pa (absolute) | core | 未选定 | 统一环境压力及表压转绝压；本次未选择到经核实的室外大气压力测点。 可以声明固定参考环境，也可以使用已核实室外环境；表压转绝压用的实际大气压与固定火用参考压力不是同一个概念。 |
| global | `atmospheric_pressure` | Pa (absolute) | core | 未选定 | DCS 表压转换；可与 reference.P0 同源，但定义与时间基准必须明确。  |
