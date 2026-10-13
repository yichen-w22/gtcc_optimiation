"""Reconcile earlier analysis with the implemented HP scope and verified Excel rows."""
import json
from collections import Counter
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent

def main():
    audit = json.loads((OUT/'source_audit.json').read_text(encoding='utf-8'))
    plan = json.loads((OUT/'parameter_plan.json').read_text(encoding='utf-8'))
    payload = json.loads((ROOT/'outputs/20261013_hp_validation/support/rows.json').read_text(encoding='utf-8'))
    review_path = OUT/'raw_input_selection_review.json'
    review = json.loads(review_path.read_text(encoding='utf-8'))
    review['removed'] = [r for r in review['removed'] if r['field'] not in {r[1] for r in payload['rows']}]
    old_removed = {r['field'] for r in review['removed']}
    for row in payload['removed_rows']:
        if row[1] not in old_removed:
            review['removed'].append({'field':row[1], 'meaning':row[0], 'reason':'默认环境配置' if row[1]=='atmospheric_pressure' else '用户确认的高压状态/运行流量派生，非外部采集参数'})
    review['retained'] = {r[1]:review['retained'].get(r[1], {}) for r in payload['rows']}
    for row in payload['added_rows'] + [x['after'] for x in payload['updated_rows']]:
        b = next(b for b in audit['bindings'] if b['field'] == row[1])
        review['retained'][row[1]].update({'code':row[2], 'unit':row[3], 'source_records':b['master_records'], 'unit_override':b['unit_override']})
    review['counts'].update({'retained_rows':len(payload['rows']), 'confirmed_point_codes':sum(bool(r[2]) for r in payload['rows']),
                             'by_system':dict(Counter(r[4] for r in payload['rows'])), 'latest_hp_removed':20, 'latest_current_added':4,
                             'latest_default_environment_removed':1})
    selection = review['mass_flow_selection']
    hp_fields = ['hrsg1.hp_pump1_in.m_dot','hrsg2.hp_pump1_in.m_dot']
    selection['independent_fields'] = [f for f in selection['independent_fields'] if f not in hp_fields]
    selection['conditional_operation_constraints'] = hp_fields
    flow = audit['water_flow_observability']
    cols = flow['matrix_column_order']
    field_stream = {next(x['field_or_constant'] for x in c['fields'] if x['parameter']=='m_dot'):c['topology_stream'] for c in plan['prepared_state_contracts']}
    _, singular, vt = np.linalg.svd(np.array(flow['matrix'],dtype=float), full_matrices=True)
    q = vt[:int(sum(singular>1e-9))].T
    def add(field):
        nonlocal q
        v = np.eye(len(cols))[cols.index(field_stream[field])]
        t = v-q@(q.T@v)
        if np.linalg.norm(t)>1e-8:
            q = np.column_stack([q,t/np.linalg.norm(t)])
    for field in selection['measured_fields']:
        add(field)
    selection['rank_with_measurements'] = q.shape[1]
    for field in hp_fields:
        add(field)
    selection['rank_with_valid_HP_operation_constraints'] = q.shape[1]
    for field in selection['independent_fields']:
        add(field)
    assert q.shape[1] == len(cols)
    selection['rank_after_independent_constraints'] = q.shape[1]
    selection['operation_constraint_note'] = '仅当HP稳定窗口确认唯一运行泵或标记单通道互备推断时生效；否则逐泵流量不可分配。'
    review['hp_implementation'] = {**review.get('hp_implementation', {}), 'status':'implemented and behavior-tested', 'default_pump_model':'isentropic eta=1 ideal reference',
                                    'current_threshold_A':1, 'environment_pressure_Pa':101375, 'temperature_override_code':'GARD_12HBK11WP021BT02XQ01'}
    review['code_limitations'] = [s.replace('汽水内部流量守恒准备尚未自动接入；只读检查并未修改算法代码。',
                                           '两台高压内部流量与状态准备已接入并验证；其他系统仍保持原实现。') for s in review['code_limitations']]
    review_path.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    path = OUT/'raw_input_selection_review.md'
    text = path.read_text(encoding='utf-8')
    text = text.replace('当前清单 311 项；本次将高中压泵入口 P/T 的24项独立采集需求改为复用低压汽包水状态。',
                         '当前清单294项；保留原先高中压入口复用低压汽包水的修改，本轮删除20项高压派生采集需求和1项环境压力采集需求，新增4项泵电流。')
    text = text.replace('行高、列宽、换行和冻结窗格恢复用户最初模板，不进行自动调整。', '本轮读取桌面当前版本，保留用户示例、已有改动、行高、列宽、换行、冻结窗格和空白工作表，不进行自动调整。')
    text = text.replace('汽水内部流量守恒准备尚未自动接入；只读检查并未修改算法代码。', '两台高压内部流量、状态及泵模型准备已接入；其他系统仍保留原实现，尚未逐个确认。')
    text = text.replace('23个已有流量绑定与质量约束的组合秩为 118；另保留 16 个独立分流需求后达到 134。',
                         f"23个原选择流量约束与质量约束的组合秩为{selection['rank_with_measurements']}；在两台HP稳定单泵运行约束有效时增至{selection['rank_with_valid_HP_operation_constraints']}，再保留14个其他独立分流需求后达到134。")
    text = text.replace('这是所选稳态拓扑的结构筛选，未考虑额外独立能量方程或已确认泵运行约束，不是新增仪表数量要求。', '这是条件性的结构筛选，HP运行约束失效时逐泵分配仍不可用；未使用额外独立能量方程，不是新增仪表数量要求。')
    for field in hp_fields:
        text = text.replace(f'- {field}\n','')
    text += '\n本轮高压单位覆盖和模型验证见 [hp_circuit_model_and_validation.md](hp_circuit_model_and_validation.md)。\n' if 'hp_circuit_model_and_validation.md' not in text else ''
    path.write_text(text,encoding='utf-8')

    path = OUT/'parameter_selection.md'
    text = path.read_text(encoding='utf-8')
    text = text.replace('本报告与清单是放在 `analysis` 中的重选方案，不是已应用到运行模型的配置。没有读取运行时序，也没有计算或宣称某个实际工况的平衡闭合。所有缺失参数、假设和测点问题均保留在清单中。',
        '两台高压回路已按确认拓扑实现并进行行为测试和有界历史窗口检查；其他系统仍为原重选方案。历史检查窗口数据不完整，不宣称实际工况已闭合。高压最新结论见 [hp_circuit_model_and_validation.md](hp_circuit_model_and_validation.md)。')
    for a,b in [('125 条','131 条'),('124 条','131 条'),('59 个','61 个'),('60 个字段','55 个字段'),('60 台仪表','55 台仪表'),('73 条','75 条'),('38 条','42 条')]:
        text = text.replace(a,b)
    text = text.replace('| 需隔离的现有绑定 | 1 条 | 二号炉高压喷水前温度所选通道的原表单位为 `%` |', '| 需隔离的现有绑定 | 0 条 | 二号炉高压减温前温度原%已由用户明确授权覆盖为℃，原始证据保留 |')
    text = text.replace('| 二号炉高压喷水前温度替换候选 | `GARD_12HBK11WP021BT06XQ01` | 高压喷水前温度 / ℃ | D12074、E12074 |', '| 二号炉高压喷水前温度授权覆盖 | `GARD_12HBK11WP021BT02XQ01` | 高压喷水前温度 / 原%按用户指定℃ | D12071、E12071 |')
    text = text.replace('现有需隔离项 `hrsg2.hp_before_spray.T -> GARD_12HBK11WP021BT02XQ01` 位于 DCS!D12071/E12071，描述为高压喷水前温度但单位为 `%`。在真实单位未核实前，不能在 `data.py` 强填 ℃ 使它通过转换。BT06 是有 ℃ 依据的候选，最终仍应确认选择器逻辑和取点。',
        '`hrsg2.hp_before_spray.T -> GARD_12HBK11WP021BT02XQ01` 保留原测点。DCS!D12071/E12071原表单位%按用户明确授权解释为℃，导入加273.15转K。`UNIT_OVERRIDES`及审计JSON保留编码、原单位、有效单位与授权来源；不改用BT06，也不继续作为未解决错误。')
    text = text.replace('新清单中的推导必须实现于单独的预处理层，不能只从 `data.py` 删除重复测点便期待模型自行补齐。', '高压推导已在 `gard/systems/hrsg_hp.py` 实现；其他系统仍需独立确认后接入。')
    text = text.replace('绝压基准不明确的压力不进入物性计算。', '既有MPa绑定仍沿用当前绝压默认，但并非点表已确认。默认环境绝压101375 Pa可配置；仅明确标记gauge的测点加环境压力，unknown仍为None。')
    text = text.replace('隔离单位冲突点，补确认所有压力基准。', '保留用户授权的单位覆盖及原证据，补确认压力基准。')
    text = text.replace('| 两炉高压/中压并联泵的分配 | 4 | 每个两泵组一个分配依据；只分析泵组时可合并 |',
                        '| 两炉中压泵分配及高压运行约束 | 2+2条件约束 | 中压仍需独立依据；高压用已确认互备与原始电流稳定资格，不单独采集逐泵流量 |')
    text = text.replace('| 高压 HP，两炉各一套 | 给水 P/T/m、汽包 P、主汽 P/T/m、给水泵组出口可用状态或独立功率 | 逐泵出口 P/流量/运行状态，省煤器出口状态，减温前后状态，喷水状态 | 泵入口直接采用低压汽包 P+x=0；无外流时饱和蒸汽量=省煤器给水量，喷水量=主汽量−给水量；泵后总量=主汽量 |',
                        '| 高压 HP，两炉各一套 | 低压汽包P、高压给水P/T/m、高压汽包P、主汽P/T/m、逐泵出口P与电流 | 原汽包进水T、减温前后T及汽机接口P/T；不采集派生流量/状态 | 入口饱和液水；稳定唯一运行泵全量、备用0；出口等熵/η模型；喷水状态复用泵出口母管；喷水量=主汽量−给水量 |')
    text = text.replace('组合受热面和“再热器1/2→减温器→再热器3”尚未完全同步。', 'HP活动设备与组合受热面已同步；其他系统和“再热器1/2→减温器→再热器3”仍待逐个确认。')
    path.write_text(text,encoding='utf-8')
    print(json.dumps({'parameters':len(payload['rows']), 'rank_with_measurements':selection['rank_with_measurements'], 'rank_with_HP_operation':selection['rank_with_valid_HP_operation_constraints']}))
if __name__ == '__main__':
    main()
