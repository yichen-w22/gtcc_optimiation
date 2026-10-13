# 两台余热锅炉高压汽水回路模型、来源与验证

更新日期：2026-10-13。以 `gard/systems/hrsg1_hp/topology.md` 和二号炉对应文件为连接依据。保留用户此前修改；本轮未修改中压、低压、供热等其他系统模型，未恢复已删除的 cooling 文件。

## 已落实的状态与流量

两台高压共用 `gard/systems/hrsg_hp.py`，由 `gard.systems.build_system('hrsg1_hp', row)` / `hrsg2_hp` 或各炉包的 `build_system` 进入。每台炉活动图为10个设备：入口分流、两泵、出口汇流、给水与喷水分流、省煤器组、汽包、过热器组、减温器和第四级过热器。滤网、滤网压差、旁路及排污等不进入此活动图。旧流股定义保留用于定位其他系统，不能据此要求采集这些活动图之外的高压字段。

| 位置 | 当前状态 / 流量来源 | 性质 |
| --- | --- | --- |
| 给水泵入口母管、两泵入口 | 对应低压汽包P，x=0，`from_Px` | 用户确认的饱和液相近似；省略静压头、吸入管损及散热 |
| 高压泵组总量 | 高压主汽质量流量 | 简化图稳态、无其他质量出口与蓄积；包含省煤器给水和减温水 |
| 逐泵流量 | 唯一运行泵承担总量，另一泵0 | 运行判断有效才分配，不均分 |
| 运行泵出口 | 实测出口P，入口s求理想h，再按指定η修正 | 默认η=1理想等熵基准；计算出口T |
| 停运泵端口 | 流量0，热力状态占位采用入口状态 | 不声称测得停运支路出口压力/温度；不计功率和效率 |
| 泵出口母管 | 唯一运行泵出口P/h | 派生状态 |
| 减温水 | 出口母管P/h，流量=主汽量−省煤器给水量 | 喷水节流前供水；负差值变为None并标记异常 |
| 省煤器组出口 / 汽包进水 | 原“高压汽包进水温度”，P暂取高压汽包P | 用户确认的接口近似，不换测点 |
| 汽包出口 | 高压汽包P，x=1；流量等于省煤器给水量 | 简化饱和蒸汽端口 |
| 减温前后 | 后P=主汽P；前P=主汽P+配置压降，默认0 | 实测前后T保留；不按汽包压力任意插值 |
| 主汽边界 | 实测主汽P/T/流量 | 活动图出口；汽机侧另测P/T是接口校核，不额外串入HP图 |

入口基准编码：一号炉 `GARD_11HBK11CM001BP02XQ01`；二号炉 `GARD_12HAG11CM001BP02XQ01`，不机械替换成12HBK11。

输入row为SI：Pa、K、kg/s、J/kg、J/(kg·K)、W。输入字典不被修改。prepared row保留 `hrsg{i}.hp_source_inputs` 原始输入副本，重复构建读取原始副本，避免把备用泵占位压力、上一次派生功率/热量及旧运行标记当成测量；需改变工况时修改原始输入后重新准备。原有喷水流量、出口T/h、入口分流及派生P字段均重新计算。

### 用户后续确认（2026-10-13）

高压给水继续采用当前 `hp_feed.P/T` 组合：压力为“高压省煤器进水调节阀前压力”，温度为“高压省煤器进水温度”。这是用户明确接受的当前建模近似，不再作为本轮待确认的取点问题，不另加阀压降。

用户将后续补充缺失历史文件。目前缺少两炉低压汽包压力（`GARD_11HBK11CM001BP02XQ01`、`GARD_12HAG11CM001BP02XQ01`）和两炉泵2电流（`GARD_11LAC72GP001BC01XQ01`、`GARD_12LAC72GP001BC01XQ01`）的对应历史文件；继续保留缺失值，不补零。压力基准确认按用户指示留待后续，当前沿用既有压力配置；该安排不代表已核实真实绝压/表压。

## 电流运行识别

`HPPreparationConfig.current_threshold_A=1.0`，判据为电流严格大于阈值；约±0.5 A停泵噪声不判为运行。电流只用于运行与工作强度的定性判断。保持其他热力输入不变，运行电流30 A改为70 A不会改变模型泵功。

| 电流证据 | 状态 | 流量处理 |
| --- | --- | --- |
| 一泵>阈值，另一泵≤阈值 | pump1 / pump2 | 全量给运行泵，停运泵0 |
| 只存在一路历史，已知泵运行 | pumpN_assumed_standby | 按两泵互备推断缺失泵备用，显式标记assumed |
| 只存在一路历史，已知泵停运且总流量>0 | 另一泵_assumed_running | 按互备推断另一泵运行，显式标记assumed |
| 两泵均运行 | both_running | 逐泵流量None |
| 两泵均停运，总流量>0 | stopped并记录异常 | 不分配正流量 |
| 两路缺失、覆盖不足或证据不够 | unknown | 逐泵流量None，缺失不当零 |
| 窗口中任一电流跨阈值或运行状态变化 | unstable | 不使用平均电流分配 |
| 两泵停运且主汽/给水均为0 | stopped | 全部流量、模型流体功率0，效率None |

`load_inputs`把**原始时序**传给 `qualify_current_history`，而不是传入平均电流。电流点值最多保持60秒，识别需覆盖窗口80%；只有一路通道整体缺失时才启用单通道互备推断，两路都存在的中途掉数不作为对方备用证据。原始电流启停变化即使缺失总流量仍判为unstable。其他输入仍按既有五分钟覆盖80%、半小时至少五个有效bin的时间加权规则汇总。输出 `hp_operation_source=raw_history`，系统构建保留该时间序列资格判断。

同时记录 `hp_operation_parameters` 的运行阈值与单通道推断开关；构建未另指定时沿用该资格判断的配置。显式更换识别配置则返回unknown并提示重新加载原始历史，不用旧阈值的运行状态冒充新配置结果。效率和减温压降的配置变化不需要重新识别电流。

四个原始A测点已接入两炉 `data.py` 及参数Excel：11LAC71、11LAC72、12LAC71、12LAC72对应的 `GP001BC01XQ01`。现有 `gard_raw_data` 只找到两台炉泵1历史；泵2编码存在于原点表，历史缺失保持None，可关闭 `allow_single_current_inference` 以禁止推断。

## 等熵加压近似是否合理

对稳定、接近绝热、单液相的泵，忽略动能和位能变化，可以用可逆绝热加压作为理论参照：

\[
s_{out,s}=s_{in},\qquad h_{out,s}=h(P_{out},s_{in}),\qquad
h_{out}=h_{in}+\frac{h_{out,s}-h_{in}}{\eta_s}.
\]

默认η=1给出理想基准，不意味着设备实际效率已知。若指定η，则它是模型输入的等熵效率，需要独立数据校准，不能直接把厂家水力效率或电机效率当成同一参数。实际出口温度由出口P/h得到，不能再添加 `T_out=T_in` 约束。对于液态水，`dh=T ds+v dP`，理想等熵增焓为积分 `∫v dP`，常密度近似为 `v ΔP`。使用IAPWS压力/熵状态计算，能保留液体压缩性和温升。

[IDAES Pressure Changer](https://idaes-pse.readthedocs.io/en/stable/reference_guides/model_libraries/generic/unit_models/pressure_changer.html)分别提供等熵、等温与不可压缩泵假设。其等熵参照以入口熵及出口压力确定，再用效率关联理论功与机械功；不可压缩泵近似采用体积流量乘压升。本项目采用等熵状态路线，是有成熟实现依据的初始近似，并非本机组实际性能已验证。

数值示例只用于说明：入口0.5 MPa饱和水，出口12 MPa。IAPWS97算得入口151.836 ℃，等熵出口153.102 ℃，理想增焓12.528 kJ/kg；入口比容乘压升约12.564 kJ/kg，相差约0.29%。因此液体温升虽小也不为零。该示例不写入实测参数或设备效率。

[KSB Pump efficiency](https://www.ksb.com/en-global/centrifugal-pump-lexicon/article/pump-efficiency-1116510)区分泵输出与轴输入的效率；[KSB Power input](https://www.ksb.com/en-global/centrifugal-pump-lexicon/article/power-input-1117260)说明泵输入功位于轴/联轴器边界；[KSB Efficiency class](https://www.ksb.com/en-global/centrifugal-pump-lexicon/article/efficiency-class-1116446)将电机轴输出与电输入用电机效率区分。由此，本项目 `m_dot*(h_out-h_in)`命名为**模型估计的流体功率**。只有在声明绝热、忽略动位能并采用一致流体边界时，才能用其作为该边界所需模型功；不能称实测电功，也不能代表含轴承、电机和变频器损失的整个泵组耗电。

零流量时本模型流体功率为0。真实转泵在零外送流量下仍可能耗轴功或电功，KSB明确列有零流量输入功；因此零模型流体功不等于真实设备耗电为0。源码保留的显式等温对比选项不自动生成绝热功边界，也不能据其焓差直接解释真实火用毁灭。

热量传递显著、内部再循环、汽蚀、启动/切泵、并联双运行、实际质量损失及库存变化等超出当前简化闭合条件。当前饱和吸入状态本身不包含NPSH校核，不能据此判断实际汽蚀裕度。

## 质量、能量与火用边界

只统计HP活动图的工质边界，内部共享流股抵消。质量残差为入口总量−主汽量；未知逐泵流量或负喷水差值不强行得到0。功输出为正、流入热量为正：

\[
R_E=\sum\dot m h_{in}-\sum\dot m h_{out}+\dot Q-\dot W_{out}.
\]

未提供独立边界功时，默认 `work=-modeled_pump_power`。未提供净热量时，按 `heat=m_main*(h_main-h_in)+work`计算，仅作为**推导吸热**；由同一方程回算的能量残差为0，不是独立验证。显式给定work/heat时保留它们，可产生非零残差。泵电流不参与边界功的数值计算。

\[
I=\sum\dot m e_{in}-\sum\dot m e_{out}+\dot E_Q-\dot W_{out},\qquad
\dot E_Q=\int(1-T_0/T_b)\,d\dot Q.
\]

默认 `heat_exergy=None`，因此 `exergy_balance()`返回None。补齐热量传递边界的温度或受验证的火用输入模型之后才能讨论完整边界火用毁灭。流股净火用变化、能量闭合、假设等熵效率分别不能替代热量火用。`Pump.exergy_balance()`继承设备的流股差值，**不独立包含泵轴功**，不能直接把该差值叫泵火用损失。

参考环境默认T0=298.15 K、P0=101375 Pa，均为配置；`atmospheric_pressure`默认101375 Pa。只有明确标记gauge的点才加环境压力，absolute不加，unknown仍保留None。既有MPa绑定沿用目前绝压默认，但原始点表未明确61个压力字段的基准，审计仍保留这一证据差距；环境默认不能证明它们是表压。

## 温度单位覆盖与原始证据

二号炉 `hrsg2.hp_before_spray.T` 保留 `GARD_12HBK11WP021BT02XQ01`。原表 `docs/点表-高安屯.xlsx` 的DCS!D12071/E12071记录“高压喷水前温度 / %”。用户明确授权按℃解释，导入加273.15转K；`UNIT_OVERRIDES`保留原单位%、有效单位℃、编码及授权说明。

`audit_parameter_sources.py`只对精确匹配编码、原单位和有效单位的授权覆盖消除单位/量纲错误，不掩盖其他元数据变化。原始工作簿不改写，审计仍列出原始单位和单元格。中压新增共用输入、电流和温度选择值后，当前141条绑定的元数据错误计数为0，压力基准未确认计数为63；“无单位错误”不意味着所有位置和压力基准实测已确认。

## 验证与交付

执行：

```text
python -m pytest tests/test_hrsg_hp.py tests/test_hp_parameter_audit.py tests/test_data_io.py tests/test_model_layers.py tests/test_stream_builder.py tests/test_gt_systems.py tests/test_system_stream_definitions.py -q -k "not cooling"
```

结果：115 passed，1 skipped（既有跳过项），2 deselected（已删除cooling的旧参数化测试）。新增高压/来源测试59项，覆盖两炉和任一运行泵、单通道推断、双运行、停泵正流量、缺失状态、切泵、时序掉数、零流量、负喷水、两泵效率修正、电流不改变功率、输入不变、重复准备和旧派生字段、质量/能量/火用边界、配置阈值及其历史来源、来源覆盖及拓扑端口一致性。

全量 `python -m pytest -q`在收集阶段仍报两个 `ModuleNotFoundError: gard.systems.cooling`，来自旧device/stream注册表的导入。此为用户删除cooling后已存在的问题，HP专用入口不依赖它；本轮不恢复文件、不扩展修改全厂注册表。

`analysis/check_hp_history_window.py`对两炉2024-06-01 00:30–01:00（Asia/Shanghai）做有界真实历史加载。两炉泵1电流均接近停泵噪声，泵2历史缺失，且低压汽包P、主汽流量等关键量缺失；结果为unknown，模型功、质量/能量残差、完整火用损失均None。此检查证明缺失路径可用，不证明任何实际运行工况已闭合。详细输入及问题见 `hp_real_window_check.json`。

桌面Excel本轮读取的当前版本为311条：删除20条已派生高压字段、删除1条环境压力外部采集要求、增加4条泵电流，最终294条。保留第一条用户示例及全部非HP系统行；二号炉指定温度填写原编码及℃并记录覆盖说明。两炉低压汽包压力行已有正确编码，保留作为共用输入，不重复新增。

交付前备份位于 `outputs/20261013_hp_validation/support/previous_version.xlsx`；输出位于 `outputs/20261013_hp_validation/全部原始编码.xlsx`，核验后交付到 `C:/Users/32697/Desktop/全部原始编码.xlsx`。检查了全部含义和内部编码、唯一性、行值、字体/边框/样式、行高、列宽、无新增换行、空白Sheet2/Sheet3及源点表SHA-256；原参数表固有窄列文字裁切按用户保留间距要求不重排。`hp_parameter_table_verification.json`保存核验与交付路径。

仍需实测或设计资料支持：泵2原始电流历史、完整稳定工况中的流量/压力/温度覆盖、压力基准、实际效率或性能曲线、实际电压/有功功率及其电机边界、热量传递温度/热量火用边界、真实安装高度/NPSH及实际损失。上述缺口不新增伪测点，不用电流替代电功。

公开来源核验日期2026-10-13，URL、HTTP状态、章节关键词及页面哈希见 `hp_pump_source_checks.json`，可由 `research_hp_pump_sources.py`重跑。
