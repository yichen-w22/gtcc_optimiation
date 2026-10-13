# 中压参数定义逐项清单

2026-10-13。所有字段从两炉IP代码、当前拓扑和来源审计对照；未改模型或Excel。下表“未定”是取值来源/建模口径未确认，缺文件与未接入另列。压力基准按用户安排后续再确认，不在每个P字段重复标记。

当前主回路、接口校核及暂缓边界量每炉50字段，共100；旧拓扑每炉36字段已删除，共72项。泵运行阈值10 A、互备、流量取给水量、母管/喷水状态和温度单位均已确认；系统能量/完整火用暂不计算。派生量不独立采集。

| 1号炉字段 | 2号炉字段 | 含义 | 定义状态 | 说明 |
| --- | --- | --- | --- | --- |
| `hrsg1.lp_drum_pressure` | `hrsg2.lp_drum_pressure` | 对应低压汽包压力，泵入口P+x=0 | 已定 | 共用输入；历史缺失，按用户安排后续补 |
| `hrsg1.ip_pump1.current` | `hrsg2.ip_pump1.current` | 中压泵1电流 | 已定 | 按A解释；>10 A为运行，两泵互备；已接入 |
| `hrsg1.ip_pump2.current` | `hrsg2.ip_pump2.current` | 中压泵2电流 | 已定 | 按A解释；1号原%覆盖来源保留；>10 A为运行，两泵互备；已接入 |
| `hrsg1.ip_pump_in.m_dot` | `hrsg2.ip_pump_in.m_dot` | 泵入口母管总质量流量 | 已定 | 等于ip_feed.m_dot+rh_spray.m_dot；任一分量缺失或无效时None |
| `hrsg1.ip_pump1_in.m_dot` | `hrsg2.ip_pump1_in.m_dot` | 泵1入口流量 | 已定 | 运行时等于ip_feed.m_dot+rh_spray.m_dot，停运0；电流证据不足/矛盾时None |
| `hrsg1.ip_pump2_in.m_dot` | `hrsg2.ip_pump2_in.m_dot` | 泵2入口流量 | 已定 | 运行时等于ip_feed.m_dot+rh_spray.m_dot，停运0；电流证据不足/矛盾时None |
| `hrsg1.ip_pump1_out.P` | `hrsg2.ip_pump1_out.P` | 泵1出口压力 | 已定 | 现有实测压力绑定 |
| `hrsg1.ip_pump1_out.T` | `hrsg2.ip_pump1_out.T` | 泵1出口温度 | 已定 | 用户确认等于泵入口温度；等温状态近似，不自动生成绝热功边界 |
| `hrsg1.ip_pump1_out.m_dot` | `hrsg2.ip_pump1_out.m_dot` | 泵1出口流量 | 已定 | 等于泵1入口流量；运行为ip_feed.m_dot+rh_spray.m_dot，停运0 |
| `hrsg1.ip_pump2_out.P` | `hrsg2.ip_pump2_out.P` | 泵2出口压力 | 已定 | 现有实测压力绑定 |
| `hrsg1.ip_pump2_out.T` | `hrsg2.ip_pump2_out.T` | 泵2出口温度 | 已定 | 用户确认等于泵入口温度 |
| `hrsg1.ip_pump2_out.m_dot` | `hrsg2.ip_pump2_out.m_dot` | 泵2出口流量 | 已定 | 等于泵2入口流量；运行为ip_feed.m_dot+rh_spray.m_dot，停运0 |
| `hrsg1.ip_pump_out.P` | `hrsg2.ip_pump_out.P` | 泵出口母管压力 | 已定 | 取唯一运行泵出口P |
| `hrsg1.ip_pump_out.T` | `hrsg2.ip_pump_out.T` | 泵出口母管温度 | 已定 | 采用唯一运行泵出口状态，T等于入口T |
| `hrsg1.ip_pump_out.m_dot` | `hrsg2.ip_pump_out.m_dot` | 泵出口母管总流量 | 已定 | 等于ip_feed.m_dot+rh_spray.m_dot；分流质量残差为0，派生闭合不作为独立验证 |
| `hrsg1.ip_feed.P` | `hrsg2.ip_feed.P` | 中压省煤器进水压力 | 已定 | 原描述即省煤器进水压力 |
| `hrsg1.ip_feed.T` | `hrsg2.ip_feed.T` | 中压省煤器进水温度 | 已定 | 原描述即省煤器进水温度 |
| `hrsg1.ip_feed.m_dot` | `hrsg2.ip_feed.m_dot` | 中压省煤器进水流量 | 已定 | DCS选择值，现有绑定 |
| `hrsg1.ip_to_drum.P` | `hrsg2.ip_to_drum.P` | 中压汽包进水口压力 | 已定 | 用户确认等于ip_drum_pressure，已落实 |
| `hrsg1.ip_to_drum.T` | `hrsg2.ip_to_drum.T` | 中压汽包进水温度 | 已定 | 原汽包进水测温；当前图省煤器直接连接该端口，不保留旧阀前出口字段 |
| `hrsg1.ip_to_drum.m_dot` | `hrsg2.ip_to_drum.m_dot` | 中压汽包进水流量 | 关系明确 | 当前简化主路等于ip_feed.m_dot，已实现 |
| `hrsg1.ip_drum_pressure` | `hrsg2.ip_drum_pressure` | 中压汽包压力 | 已定 | 1号11HBK02，2号12HAG02，现有绑定 |
| `hrsg1.ip_drum_steam.m_dot` | `hrsg2.ip_drum_steam.m_dot` | 汽包饱和蒸汽流量 | 已定 | 用户指定1号GARD_11HAH80WP011BF03XQ01，2号用现有对应12HAH80WP011BF03XQ01；复用ip_fresh.m_dot，保留与给水量的质量残差 |
| `hrsg1.ip_fresh.P` | `hrsg2.ip_fresh.P` | 中压过热器出口/新蒸汽压力 | 已定 | 现有绑定 |
| `hrsg1.ip_fresh.T` | `hrsg2.ip_fresh.T` | 中压过热器出口/新蒸汽温度 | 已定 | 现有绑定 |
| `hrsg1.ip_fresh.m_dot` | `hrsg2.ip_fresh.m_dot` | 中压新蒸汽流量 | 已定 | 原蒸汽流量选择值，现有绑定 |
| `hrsg1.cold_reheat.P` | `hrsg2.cold_reheat.P` | 汽轮机高压缸返回锅炉的冷再热压力 | 已定 | 现有绑定 |
| `hrsg1.cold_reheat.T` | `hrsg2.cold_reheat.T` | 汽轮机高压缸返回锅炉的冷再热温度 | 已定 | 现有绑定 |
| `hrsg1.cold_reheat.m_dot` | `hrsg2.cold_reheat.m_dot` | 冷再热质量流量 | 关系明确 | 当前简化图可由hot_reheat.m_dot-ip_fresh.m_dot-rh_spray.m_dot求得；需检查非负及DCS流量来源 |
| `hrsg1.reheat_mixed.P` | `hrsg2.reheat_mixed.P` | 冷再热与新蒸汽混合后压力 | 已定 | 原冷再热混合后压力测点，现有绑定 |
| `hrsg1.reheat_mixed.T` | `hrsg2.reheat_mixed.T` | 冷再热与新蒸汽混合后温度 | 已定 | 原混合后温度测点，现有绑定 |
| `hrsg1.reheat_mixed.m_dot` | `hrsg2.reheat_mixed.m_dot` | 进入再热器组的总流量 | 关系明确 | cold_reheat.m_dot+ip_fresh.m_dot，已实现 |
| `hrsg1.rh_before_spray.P` | `hrsg2.rh_before_spray.P` | 再热器组1～2之后、减温前压力 | 已定 | 用户确认等于hot_reheat.P，已落实 |
| `hrsg1.rh_before_spray.T` | `hrsg2.rh_before_spray.T` | 再热器2出口、减温前温度 | 测点已选 | Excel已选HAJ80WP001BT01，原单位℃；两炉历史缺失，现已绑定并接入 |
| `hrsg1.rh_before_spray.m_dot` | `hrsg2.rh_before_spray.m_dot` | 减温前蒸汽流量 | 关系明确 | 等于reheat_mixed.m_dot，已实现 |
| `hrsg1.rh_spray.P` | `hrsg2.rh_spray.P` | 再热减温水压力 | 已定 | 采用出口母管P，不另做节流状态变换 |
| `hrsg1.rh_spray.T` | `hrsg2.rh_spray.T` | 再热减温水温度 | 已定 | 采用出口母管热力状态，不考虑节流 |
| `hrsg1.rh_spray.m_dot` | `hrsg2.rh_spray.m_dot` | 再热减温水质量流量 | 测点已定，计算来源待核 | LAF80WP001BF02，t/h；DCS计算值已有历史，不是独立实测已验证 |
| `hrsg1.rh_after_spray.P` | `hrsg2.rh_after_spray.P` | 再热减温后、再热器3前压力 | 已定 | 用户确认等于hot_reheat.P |
| `hrsg1.rh_after_spray.T` | `hrsg2.rh_after_spray.T` | 减温后蒸汽温度 | 测点已选 | HAJ80WP011BT07，原描述中压喷水后温度，℃；物理取点需随拓扑同步核对 |
| `hrsg1.rh_after_spray.m_dot` | `hrsg2.rh_after_spray.m_dot` | 减温后蒸汽总流量 | 关系明确 | reheat_mixed.m_dot+rh_spray.m_dot=hot_reheat.m_dot，已实现 |
| `hrsg1.hot_reheat.P` | `hrsg2.hot_reheat.P` | 锅炉热再热出口压力 | 已定 | 现有绑定 |
| `hrsg1.hot_reheat.T` | `hrsg2.hot_reheat.T` | 锅炉热再热出口温度 | 已定 | 使用BT13选择值；原%按用户授权℃解释，导入加273.15转K，原始来源保留 |
| `hrsg1.hot_reheat.m_dot` | `hrsg2.hot_reheat.m_dot` | 锅炉热再热出口总流量 | 已定 | 原流量补偿后选择值，现有绑定 |
| `hrsg1.rh_to_st.P` | `hrsg2.rh_to_st.P` | 至汽机热再热压力 | 已定 | 独立接口位置测点，不自动替代锅炉出口 |
| `hrsg1.rh_to_st.T` | `hrsg2.rh_to_st.T` | 至汽机热再热温度 | 已定 | 独立接口位置测点，不自动替代hot_reheat.T |
| `hrsg1.rh_to_st.m_dot` | `hrsg2.rh_to_st.m_dot` | 送往汽机的热再热流量 | 已定 | 用户确认等于hot_reheat.m_dot，已落实 |
| `hrsg1_ip.work` | `hrsg2_ip.work` | IP工质系统边界功，输出正 | 暂不考虑 | 用户暂不考虑系统能量输入输出，保持None，不使用电流计算 |
| `hrsg1_ip.heat` | `hrsg2_ip.heat` | IP工质系统净入热 | 暂不考虑 | 用户暂不考虑系统能量输入输出，保持None |
| `hrsg1_ip.heat_exergy` | `hrsg2_ip.heat_exergy` | 热量穿过IP边界携带的火用 | 暂不考虑 | 系统能量/完整火用暂不计算，保持None而非0 |

两炉活动图已严格同步当前12设备拓扑；旧旁路、排污、回流及单级再热器端口不再列入当前字段清单，IP已不再引用高压旁路出口。

原始编码、单位、历史与绑定状态逐字段见 [ip_parameter_definition_inventory.json](ip_parameter_definition_inventory.json)；完整点表和文件证据见 [ip_feedwater_source_audit.json](ip_feedwater_source_audit.json)。
