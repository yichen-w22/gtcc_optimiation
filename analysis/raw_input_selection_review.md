# 原始测点清单复核

当前清单246项；最新低压确认删除10个派生采集项，新增4个外部状态需求，更新14行来源或定义。保留原先高压、中压及用户已有修改。

Excel只列采集侧所需字段；不再将模型属性、重复流量、参考环境和模型配置列为待采集测点。
保留所需外部P/T、燃料流量/组分、有功功率、湿度、真实汽水流量测点及无法由守恒唯一确定的分流。高中压泵入口直接用低压汽包压力和x=0构造，不另采集入口P/T。
未确认测点编码留空；授权单位覆盖保留原始证据，其余单位按已核实来源填写。
本轮读取桌面当前版本，保留用户示例、已有改动、行高、列宽、换行、冻结窗格和空白工作表，不进行自动调整。

## 代码依据

- `src/GT_model/components/compressor.py`：`state_2`、`bleeding` 计算支路流量和状态。
- `src/GT_model/components/chamber.py`：`_outlet_state` 计算燃烧室及混合出口状态。
- `src/working_fluid/gas.py`：已有 `build_air_composition`、`build_flue_gas_composition`。
- `src/base/stream_builder.py`：构造流股时使用 `row.get` 读取准备值，不意味着每个字段都应新设采集点。
- `src/working_fluid/steam_water.py`：存在混合流量反推函数，但未自动接入系统装配。
- `gard/systems/*/streams.py`：逐项核对PT、流量和组分的实际构造消费者。

## 尚未实现的准备步骤

- GTModel、GasState及build_stream目前消费已准备流量；没有自动反推空气/烟气流量的实现。
- Compressor.state_2/bleeding与Chamber._outlet_state确实计算内部支路状态和流量。
- build_air_composition/build_flue_gas_composition为已有函数；gard调用链尚未自动调用。
- 两台高压、中压及低压当前拓扑和状态/流量准备已接入；缺数据保持None，中压系统能量暂缓，其余系统保留原实现。
- 汽水质量约束使用当前Mermaid简化主回路；旧devices.py旁路不能混入推导。
- 高中压泵入口已直接复用低压汽包饱和水；其他设备的PT输入按已明确的规则处理。
- 逐泵分流不能由母管压力或总流量直接均分；非零补水需真实损失或库存项。

## 独立汽水流量需求

23个原选择流量约束与质量约束的组合秩为119；依次加入有效HP、IP、LP稳定单泵约束后，秩为121、123、125；再保留10个其他独立流量需求后达到135。结构秩不证明实测数值闭合。
这是条件性的结构筛选，HP运行约束失效时逐泵分配仍不可用；未使用额外独立能量方程，不是新增仪表数量要求。
采用这些推导仍须补齐预处理；实测值应通过守恒残差校核。

- cond.gland_steam.m_dot
- cond.pre_pump1_in.m_dot
- cond.pre_pump2_in.m_dot
- cond.pre_recycle.m_dot
- cond.pump1_in.m_dot
- cond.pump2_in.m_dot
- hrsg1.lp_to_heat.m_dot
- hrsg1.lp_to_heat_recovery.m_dot
- hrsg2.lp_to_heat.m_dot
- hrsg2.lp_to_heat_recovery.m_dot

本轮高压单位覆盖和模型验证见 [hp_circuit_model_and_validation.md](hp_circuit_model_and_validation.md)。

中压新约定、72项旧字段清理及8项采集删除见 [ip_confirmed_model_review.md](ip_confirmed_model_review.md)。

低压拓扑、派生关系与全部缺测点见 [lp_system_review.md](lp_system_review.md)。当前桌面清单246项，保留原始来源和用户示例。
