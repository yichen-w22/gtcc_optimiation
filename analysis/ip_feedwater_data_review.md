# 两炉中压给水原始数据完整性检查

检查日期2026-10-13。读取现有IP拓扑、代码、原始点表、Parquet元数据与桌面参数表；不改模型或Excel。低压汽包缺失文件及压力基准按用户已有安排留待后续。

| 项目 | 1号炉 | 2号炉 |
| --- | --- | --- |
| 当前data.py绑定历史文件 | 23/25存在：缺低压汽包P、减温前T | 23/25存在：缺低压汽包P、减温前T |
| 两台中压泵出口P、省煤器进水P/T/流量、汽包进水T和汽包P | 均有点表及历史 | 均有点表及历史 |
| 低压汽包P历史（泵入口共用） | 缺失，后续补 | 缺失，后续补 |
| 泵1电流 | 有历史、按A已接入 | 有历史、按A已接入 |
| 泵2电流 | 有历史、原%按用户授权A已接入 | 有历史、按A已接入 |
| 再热喷水流量 | 有历史、t/h，DCS计算值 | 有历史、t/h，DCS计算值 |
| 再热器2出口 / 减温前T扩展输入 | 已选点表编码，历史缺失 | 已选点表编码，历史缺失 |

## 给水原始来源

中压给水P与T的原点表名称分别为“中压省煤器进水压力”和“中压省煤器进水温度”。与HP压力为调节阀前测点的描述不同，本轮未发现同类跨阀位置描述问题；真实安装位置仍以现场资料为准。

| 字段 | 原始编码 | 原单位 | 原点表位置 | 历史文件 | 接入情况 |
| --- | --- | --- | --- | --- | --- |
| `hrsg1.lp_drum_pressure` | `GARD_11HBK11CM001BP02XQ01` | MPa | DCS!B2920/E2920 | 缺失 | data.py已绑定 |
| `hrsg1.ip_pump1.current` | `GARD_11LAB81QM003BC01XQ01` | A | DCS!B1578/E1578 | 存在 | data.py已绑定 |
| `hrsg1.ip_pump2.current` | `GARD_11LAB82QM003BC01XQ01` | % | DCS!B1770/E1770 | 存在 | data.py已绑定 |
| `hrsg1.ip_pump1_out.P` | `GARD_11LAB81WP011BP01XQ01` | MPa | DCS!B1579/E1579 | 存在 | data.py已绑定 |
| `hrsg1.ip_pump2_out.P` | `GARD_11LAB82WP012BP01XQ01` | MPa | DCS!B1771/E1771 | 存在 | data.py已绑定 |
| `hrsg1.ip_feed.P` | `GARD_11HAC02WP001BP01XQ01` | MPa | DCS!B1776/E1776 | 存在 | data.py已绑定 |
| `hrsg1.ip_feed.T` | `GARD_11HAC02WP001BT01XQ01` | ℃ | DCS!B1777/E1777 | 存在 | data.py已绑定 |
| `hrsg1.ip_feed.m_dot` | `GARD_11HAC02WP001BF03XQ01` | t/h | DCS!B2719/E2719 | 存在 | data.py已绑定 |
| `hrsg1.ip_to_drum.T` | `GARD_11LAF80WP002BT01XQ01` | ℃ | DCS!B1706/E1706 | 存在 | data.py已绑定 |
| `hrsg1.ip_drum_pressure` | `GARD_11HBK02CM001BP02XQ01` | MPa | DCS!B2917/E2917 | 存在 | data.py已绑定 |
| `hrsg1.rh_spray.m_dot` | `GARD_11LAF80WP001BF02XQ01` | t/h | DCS!B2787/E2787 | 存在 | data.py已绑定 |
| `hrsg2.lp_drum_pressure` | `GARD_12HAG11CM001BP02XQ01` | MPa | DCS!B2930/E2930 | 缺失 | data.py已绑定 |
| `hrsg2.ip_pump1.current` | `GARD_12LAB81QM003BC01XQ01` | A | DCS!B2080/E2080 | 存在 | data.py已绑定 |
| `hrsg2.ip_pump2.current` | `GARD_12LAB82QM003BC01XQ01` | A | DCS!B2271/E2271 | 存在 | data.py已绑定 |
| `hrsg2.ip_pump1_out.P` | `GARD_12LAB81WP011BP01XQ01` | MPa | DCS!B2081/E2081 | 存在 | data.py已绑定 |
| `hrsg2.ip_pump2_out.P` | `GARD_12LAB82WP012BP01XQ01` | MPa | DCS!B2272/E2272 | 存在 | data.py已绑定 |
| `hrsg2.ip_feed.P` | `GARD_12HAC02WP001BP01XQ01` | MPa | DCS!B2277/E2277 | 存在 | data.py已绑定 |
| `hrsg2.ip_feed.T` | `GARD_12HAC02WP001BT01XQ01` | ℃ | DCS!B2278/E2278 | 存在 | data.py已绑定 |
| `hrsg2.ip_feed.m_dot` | `GARD_12HAC02WP001BF03XQ01` | t/h | DCS!B2718/E2718 | 存在 | data.py已绑定 |
| `hrsg2.ip_to_drum.T` | `GARD_12LAF80WP002BT01XQ01` | ℃ | DCS!B2205/E2205 | 存在 | data.py已绑定 |
| `hrsg2.ip_drum_pressure` | `GARD_12HAG02CM001BP02XQ01` | MPa | DCS!B2927/E2927 | 存在 | data.py已绑定 |
| `hrsg2.rh_spray.m_dot` | `GARD_12LAF80WP001BF02XQ01` | t/h | DCS!B2788/E2788 | 存在 | data.py已绑定 |

## 原始输入与候选派生量

运行泵及母管流量等于省煤器给水流量 `ip_feed.m_dot` 加减温水流量 `rh_spray.m_dot`。喷水流量仍用 `GARD_11LAF80WP001BF02XQ01` / `GARD_12LAF80WP001BF02XQ01` 的t/h DCS计算值；任一分量缺失或无效时不使用部分流量代替总量。分流点按派生关系闭合，不能作为独立实测验证；汽包给水与新蒸汽流量不一致的质量残差仍保留。DCS计算来源/独立性尚未核验。

中压泵出口T等于入口T、汽包进水P等于汽包P、饱和蒸汽量复用指定新蒸汽测点、减温前后P等于热再热P、至汽机流量等于热再热量。运行泵流量等于省煤器给水量加减温水量，备用0；母管及喷水采用运行泵状态，无独立节流。以上已接入 `gard/systems/hrsg_ip.py`，系统能量/完整火用暂不计算。

四路 `hrsg{i}.ip_pump{j}.current` 按A绑定并加入Excel。一号泵2原DCS!E1770的%保留为原始证据，用户已授权按A。用户指定10 A阈值、两泵互备；使用简单>10 A判据，切泵或矛盾窗口保持不可分配。

四路电流全记录元数据范围包含约−2.13至−5的负值，不当作实际负电功；使用用户指定10 A阈值而非HP的1 A阈值。

## 完整中压/再热回路的额外接入问题

当前 `data.py` 两炉各25条绑定、23个文件存在。低压汽包P和再热减温前T历史仍缺失；电流和热再热T已接入，授权覆盖保留原单位。IP活动图为12设备，旧字段不恢复；专用入口不依赖旧cooling注册表。

两炉 `rh_before_spray.T`（`GARD_11HAJ80WP001BT01XQ01` / `GARD_12HAJ80WP001BT01XQ01`）原描述为再热器2出口温度；两个历史文件均缺失，现已绑定并由活动流股消费。

锅炉出口 `hot_reheat.T` 已选两炉 `LBB01WP001BT13XQ01`。选择值原%按用户授权℃导入并转K，历史均存在；不改用BT10/14/15或至汽机取点。候选及原始证据保留在JSON。

## 文件存在与窗口数据可用性

读取2024-06-01 00:30–01:00（Asia/Shanghai）窗口，沿用原数据准备的60秒保持、五分钟覆盖80%、半小时五个有效bin规则。此为停机附近的有界检查，不是已确认稳定运行窗口：

- 1号炉：23/25个输入有文件，原始时间加权均值覆盖合格11项，SI转换后可用10项；具体None、数值和文件总时间范围见JSON。
- 2号炉：23/25个输入有文件，原始时间加权均值覆盖合格12项，SI转换后可用11项；具体None、数值和文件总时间范围见JSON。

压力基准延后核对；系统能量输入输出和完整火用按用户安排暂不考虑，保持None。电流不用于电功。

复核脚本：`python analysis/audit_ip_feedwater_sources.py`。详细原始证据：[ip_feedwater_source_audit.json](ip_feedwater_source_audit.json)。原始点表与桌面表哈希在执行前后相同。
