# 汽包平衡假设与给水泵入口状态调研

调研日期：2026-10-13。针对当前 GARD 稳态质量、能量和火用分析，以及低压汽包向高压给水泵供水的状态准备。

## 结论与适用范围

汽包采用集中参数的汽水饱和平衡模型有明确的文献和成熟模型依据，可作为本项目稳态计算的初始近似。但真实汽包不是任意位置都具有相同温度和压力的容器。液相与汽相可以接近压力平衡而不处于完全热平衡，较冷给水混合可使液相或出水过冷。

应区分两种“过冷”：

1. 以汽包汽空间压力为基准，液相温度确实低于该压力对应的饱和温度。这可能来自给水混合、散热及有限速率相间换热，需要液相温度/焓或足够的能量与混合模型依据。
2. 水温接近汽空间压力对应的饱和温度，但汽包底部或较低位置的管道压力因静压头而增大。相对于该位置更高的局部压力，水属于过冷液态水；这不需要先假定液相温度下降。

目前没有本机组的独立液相测温、泵入口压力或安装高度证据，不能为了使物性构造成功而人为设定液相低于饱和温度若干摄氏度。

## 既有研究与公开实现

| 路线 | 核验到的处理 | 对本项目的意义 |
|---|---|---|
| Åström–Bell（2000）经典自然循环汽包锅炉研究及 Modelica 的 EquilibriumDrumBoiler 实现 | 论文研究汽包、下降管和上升管的动态；Modelica 明确采用两相平衡，蒸汽出口为饱和蒸汽，并引用该论文 | 说明汽水饱和平衡是成熟的简化路线，而不是未经依据的默认值 |
| ThermoPower.Water.DrumEquilibrium | 假设液体、蒸汽、金属壁处于热力学平衡；以压力和液体体积为两个状态变量 | 平衡模型可用压力确定饱和液相、汽相物性；不能据此证明真实设备完全均匀 |
| ThermoPower.Water.Drum | 不假设液相和汽相热力学平衡；两相分别动态质量、能量守恒，含凝结、沸腾和相间传热；下降管口压力包含液柱静压 | 非平衡模型需要更多状态和闭合关系；汽包汽空间压力与下降管/泵入口压力应区分 |
| ThermoSysPro.DynamicDrum | 两相保持压力平衡，但不强制热平衡；液相、汽相、壁温分别作为状态；底部压力加入液柱静压 | 压力平衡不等于温度必然相同；底部液相的局部压力也不等于汽空间压力 |
| IDAES Drum 1D | 采用相分离器、混合器和水箱组合；饱和循环水与较冷给水混合，允许过冷水经下降管排出；计算水位静压及出口收缩压差 | 过冷出水可以由能量、流量、混合关系得到，不宜用任意固定温差代替 |

核验范围：经典论文的出版信息及摘要已核对；饱和平衡与非平衡的具体假设直接核对了上述公开模型文档。未取得经典论文 PDF 全文，不把未读正文作为已核验的详细方程来源。

汽水处于纯水两相界面局部平衡时，界面温度取相应压力下的饱和温度。开放、持续进出工质的实际汽包可以出现较冷液相区域和进水温度分布；两相界面局部平衡并不强制全部液相瞬时均匀。饱和水入口、较冷给水入口及实际出水口的位置因此影响所选代表状态。

## 当前算法采用了什么

`gard/systems/hrsg1_lp/streams.py` 与二号炉对应文件将“低压汽包水”定义为 `WaterSteamState.from_Px`，压力来源为 `hrsg{i}.lp_drum_pressure`，`x=0`。这已经是饱和液相的端口近似。

现有定义是端口物性构造；汽包设备是包含进出口流股的通用设备。它没有显式求解汽包内部空间温度场，也没有实现液相、汽相分开的动态储能、相间换热与相变速率模型。不能据当前代码反推真实汽包液相的过冷度。

`src/working_fluid/steam_water.py` 会拒绝只用 P/T 构造恰好位于饱和线的完整汽水状态。因此，汽包饱和液相应继续用 P+x=0；饱和汽相用 P+x=1。

## 泵入口状态的建议

当前执行口径（2026-10-13）：高中压给水路径直接连接低压汽包与给水泵，母管及各泵入口统一采用对应低压汽包饱和液水状态，由 `lp_drum_pressure` 与 `x=0` 构造，不额外采集入口 P/T。

这是用户明确指定的集中参数简化。以下水力关系保留为真实入口状态的研究依据，不作为当前简化模型的附加输入需求。

忽略速度头变化、取代表液体密度时：

\[
P_{\mathrm{suction},j}=P_{\mathrm{drum,abs}}+
\rho g\left(z_{\mathrm{water\ surface}}-z_{\mathrm{pump},j}\right)
-\Delta P_{\mathrm{pipe},j}.
\]

这里的高度差从汽包自由液面到泵入口中心线计算。汽包液位会影响高度差；稳定工况下采用固定正常液位，应将其写明为几何近似。管道散热可忽略时，泵入口温度可近似为汽包代表液相温度。

至少校核 `P_suction > P_sat(T_suction)` 以保持入口为过冷液相。这个条件只说明状态没有越过饱和线；实际防汽蚀还需要可用 NPSH 满足泵要求及相应裕度，不能仅凭此条件认定实际入口安全。

若以后需要校核真实入口水力状态，优先使用已有泵入口压力；没有时，需安装高度、正常液位和管路压降的依据。若后续实测证实液相过冷，则可使用实测 P/T 或 P/h，或者经验证的混合模型。

## 物性示例：仅为说明，不是本机组工况

采用项目所用 IAPWS97：汽空间绝对压力 0.5 MPa 时，饱和水温约 151.836 ℃。

- 若直接保持该温度并将压力降至 0.48 MPa，用 P/T 构造会得到汽相，已不符合给水泵液相入口。
- 真实绝热降压应近似等焓；由 P/h 构造会出现少量闪蒸，而不是凭保持温度将全部液体变成蒸汽。
- 假设自由液面比泵入口高 20 m，忽略管损，泵入口压力约 0.680 MPa（按饱和水密度估算）；入口温度仍可接近 151.836 ℃，相对于局部压力已是过冷液体。

20 m 及上述降压示例都是演示条件，不能填入机组配置。

## 高压部分已讨论规则的状态

- 两台高压给水泵按互为备用处理；运行泵承担全部高压给水总流量（等于主汽流量，包含减温水分支）。四个电流编码已接入 `data.py`，默认可配置阈值为1 A；±0.5 A停泵噪声不判为运行。
- 识别应在原始时间序列上进行，再选取稳定工况窗口；不得仅用半小时平均电流判泵切换过程。
- 两泵同时运行、都停运但主回路有正流量、两路电流缺失或切泵时，不分配逐泵流量。仅一路电流历史存在时，可按互备假设推断另一泵，输出 `assumed` 标记；通道中途掉数不直接等同于备用泵。
- 最新确认模型为默认理想等熵加压：由出口P和入口s求出口h/T；若给定η，则 `h_out=h_in+(h_out,s-h_in)/η`。不再同时强制出口温度等于入口温度。η=1只是基准，`m_dot Δh`只是估计流体功率；电流不会直接改变功率。详见 [高压泵模型与验证](hp_circuit_model_and_validation.md)。等温选项只保留为显式对比，不自动赋予绝热功或完整火用边界。
- 泵出口母管由唯一运行泵的出口状态生成；高压减温水取该母管状态时，代表喷水节流之前的供水侧状态。若以喷嘴之后为混合边界，需另做等焓节流到蒸汽压力。
- 高压汽包入口取高压汽包压力可作为忽略末段管路、给水阀及液柱差的接口近似。
- 用户已明确采用原“高压汽包进水温度”作为省煤器组出口温度，`hp_to_drum.T`继续使用这一测点，P暂取高压汽包压力。这是已确认的接口近似，原始点表名称保留，不再作为未解决的选点错误。
- 减温前压力严格满足 `P_before=P_main+ΔP_superheater4+ΔP_attemperator`（暂不计其他连接管损）。用户已取 `P_after=P_main`，相当于忽略第四级过热器及后段管损；若再忽略减温器汽侧压降，则一致的初始近似为 `P_before=P_after=P_main`。后续有实测或设计压降时再修正，不能仅由汽包、主汽两端压力任意插值得出。

当前已按用户的直接连接口径更新高中压入口流股定义；实际静压头及过冷度仍属于研究信息，不加入当前简化模型的测点清单。

## 已核验的给水泵电流来源

下列电流测点均在原始点表找到，可用于运行泵识别。

| 设备 | 参数 | 内部输入建议 | 原始测点编码 | 原始单位 |
|---|---|---|---|---|
| 1号炉泵1 | 电流 | hrsg1.hp_pump1.current | GARD_11LAC71GP001BC01XQ01 | A |
| 1号炉泵2 | 电流 | hrsg1.hp_pump2.current | GARD_11LAC72GP001BC01XQ01 | A |
| 2号炉泵1 | 电流 | hrsg2.hp_pump1.current | GARD_12LAC71GP001BC01XQ01 | A |
| 2号炉泵2 | 电流 | hrsg2.hp_pump2.current | GARD_12LAC72GP001BC01XQ01 | A |

上述字段已绑定。`gard_raw_data`目前仅两台炉泵1有历史文件，泵2缺失保持None；单通道运行识别明确标记互备推断，不把缺失当零电流。

## 来源

1. Åström, K. J.; Bell, R. D. (2000). *Drum-boiler dynamics*. Automatica, 36(3), 363–378. DOI: https://doi.org/10.1016/S0005-1098(99)00171-5 。出版信息：https://portal.research.lu.se/en/publications/drum-boiler-dynamics-2/ 。
2. Modelica 官方 EquilibriumDrumBoiler 文档：https://doc.modelica.org/om/Modelica.Fluid.Examples.DrumBoiler.BaseClasses.EquilibriumDrumBoiler.html 。
3. ThermoPower.Water.DrumEquilibrium：https://build.openmodelica.org/Documentation/ThermoPower.Water.DrumEquilibrium.html 。
4. ThermoPower.Water.Drum：https://build.openmodelica.org/Documentation/ThermoPower.Water.Drum.html ，Information 段特别说明相间非平衡及下降管口静压。
5. ThermoSysPro DynamicDrum：https://thermosyspro.gitlab.io/documentation/src/WaterSteam/Volumes/DynamicDrum.html ，Assumptions 及底部压力定义。
6. IDAES Drum 1D：https://idaes-pse.readthedocs.io/en/stable/reference_guides/model_libraries/power_generation/unit_models/drum1D.html ，Introduction、Constraints。
7. Spirax Sarco，The Feedtank and Feedwater Conditioning：https://www.spiraxsarco.com/learn-about-steam/the-boiler-house/the-feedtank-and-feedwater-conditioning ，Cavitation of the boiler feedpump 段。

以上网页核验日期为 2026-10-13。本记录中的计算关系、项目建议和物性演示与来源陈述分别列出，未将普通模型假设当作本机组实测事实。
