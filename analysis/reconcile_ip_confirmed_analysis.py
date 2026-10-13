"""Update current analysis manifests after the confirmed IP changes."""
from collections import Counter
import json
import re
from pathlib import Path
import numpy as np

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent

def main():
    payload=json.loads((ROOT/'outputs/20261013_ip_operation/support/rows.json').read_text(encoding='utf-8'))
    lp_payload_path=ROOT/'outputs/20261013_lp_review/support/rows.json'
    if lp_payload_path.exists():
        payload=json.loads(lp_payload_path.read_text(encoding='utf-8'))
    confirmed_path=ROOT/'outputs/20261013_lp_confirmed/support/rows.json'
    if confirmed_path.exists():
        payload=json.loads(confirmed_path.read_text(encoding='utf-8'))
    audit=json.loads((OUT/'source_audit.json').read_text(encoding='utf-8'))
    path=OUT/'raw_input_selection_review.json'
    review=json.loads(path.read_text(encoding='utf-8'))
    existing={r['field'] for r in review['removed']}
    for row in payload['removed_rows']:
        if row[1] not in existing:
            review['removed'].append({'field':row[1],'meaning':row[0],'reason':'当前低压派生状态，删除独立采集项' if '.lp_' in row[1] else '用户确认的中压派生状态，删除独立采集项'})
    if lp_payload_path.exists():
        lp_removed={r[1] for r in payload['removed_rows']}
        for item in review['removed']:
            if item['field'] in lp_removed:
                item['reason']='当前低压派生状态，删除独立采集项'
    review['retained']={row[1]:review['retained'].get(row[1],{}) for row in payload['rows']}
    review['removed']=[r for r in review['removed'] if r['field'] not in review['retained']]
    review['counts'].update({'retained_rows':len(payload['rows']),'confirmed_point_codes':sum(bool(row[2]) for row in payload['rows']),
                             'by_system':dict(Counter(row[4] for row in payload['rows'])),'latest_IP_operation_derived_removed':12,'latest_IP_currents_added':4})
    if lp_payload_path.exists():
        review['counts'].update({'latest_LP_derived_removed':payload['counts']['removed_LP_derived'],
                                'latest_LP_currents_added':payload['counts'].get('added_LP_currents',0),
                                'latest_LP_parameters_added':len(payload['added_rows'])})
        review['lp_implementation']={'date':'2026-10-13','active_devices_per_unit':13,'removed_legacy_fields':48,
                                     'pump_mass_flow':'lp_recirc_in.m_dot, standby0; raw history selection',
                                     'HP_IP_withdrawals':'hp_main.m_dot + ip_feed.m_dot + rh_spray.m_dot',
                                     'complete_missing_inputs':json.loads((OUT/'lp_source_audit.json').read_text(encoding='utf-8'))['counts'],
                                     'source_table_parameters':len(payload['rows'])}
    review['ip_implementation']={'date':'2026-10-13','active_devices_per_unit':12,'removed_legacy_fields':72,
                                 'pump_outlet_temperature':'equals inlet temperature; not automatic adiabatic work',
                                 'drum_inlet_pressure':'ip_drum_pressure',
                                 'drum_steam_flow':'ip_fresh.m_dot; unit1 user specified 11HAH80WP011BF03, unit2 existing corresponding12HAH80WP011BF03',
                                 'before_spray_pressure':'hot_reheat.P','turbine_interface_flow':'hot_reheat.m_dot',
                                 'current_threshold_A':10,'exclusive_duty':True,'pump_mass_flow':'ip_feed.m_dot + rh_spray.m_dot, standby0',
                                 'header_and_spray_state':'active pump outlet, no separate throttling',
                                 'after_spray_pressure':'hot_reheat.P','hot_reheat_temperature':'BT13 selector, user-authorized Celsius override',
                                 'energy_accounting':'deferred by user; work/heat/heat_exergy None',
                                 'definitions_confirmed':True,'remaining_source_validation':'history files, pressure basis, DCS spray flow provenance'}
    evidence={b['field']:b for b in audit['bindings']}
    for row in payload['rows']:
        b=evidence.get(row[1], {})
        review['retained'][row[1]].update({'code':row[2],'unit':row[3],
                                         'source_records':b.get('master_records',[]),
                                         'unit_override':b.get('unit_override'), 'current_note':row[5]})
    selection=review['mass_flow_selection']
    ip_fields=['hrsg1.ip_pump1_in.m_dot','hrsg2.ip_pump1_in.m_dot']
    selection['independent_fields']=[f for f in selection['independent_fields'] if f not in ip_fields]
    selection['conditional_IP_operation_constraints']=ip_fields
    lp_fields=['hrsg1.lp_recirc_pump1_in.m_dot','hrsg2.lp_recirc_pump1_in.m_dot'] if lp_payload_path.exists() else []
    lp_totals=['hrsg1.lp_recirc_in.m_dot','hrsg2.lp_recirc_in.m_dot'] if lp_payload_path.exists() else []
    selection['independent_fields']=[f for f in selection['independent_fields'] if f not in lp_fields]
    selection['measured_fields']=list(dict.fromkeys(selection['measured_fields']+lp_totals))
    selection['conditional_LP_operation_constraints']=lp_fields
    flow=audit['water_flow_observability']
    plan=json.loads((OUT/'parameter_plan.json').read_text(encoding='utf-8'))
    cols=flow['matrix_column_order']
    field_stream={next(x['field_or_constant'] for x in c['fields'] if x['parameter']=='m_dot'):c['topology_stream'] for c in plan['prepared_state_contracts']}
    _,sv,vt=np.linalg.svd(np.array(flow['matrix'],dtype=float),full_matrices=True)
    q=vt[:int(sum(sv>1e-9))].T
    def add(field):
        nonlocal q
        v=np.eye(len(cols))[cols.index(field_stream[field])]
        t=v-q@(q.T@v)
        if np.linalg.norm(t)>1e-8:
            q=np.column_stack([q,t/np.linalg.norm(t)])
    for f in selection['measured_fields']:
        add(f)
    selection['rank_with_measurements']=q.shape[1]
    for f in selection['conditional_operation_constraints']:
        add(f)
    selection['rank_with_valid_HP_operation_constraints']=q.shape[1]
    for f in ip_fields:
        add(f)
    selection['rank_with_valid_HP_IP_operation_constraints']=q.shape[1]
    for f in lp_fields:
        add(f)
    selection['rank_with_valid_HP_IP_LP_operation_constraints']=q.shape[1]
    for f in selection['independent_fields']:
        add(f)
    assert q.shape[1]==len(cols)
    selection['rank_after_independent_constraints']=q.shape[1]
    selection['operation_constraint_note']='仅稳定单泵运行证据有效时生效；结构秩不证明实测质量闭合。IP泵流量=省煤器给水量+减温水量，分流点按派生关系闭合，保留汽包给水与独立蒸汽测点的质量残差。'
    review['code_limitations']=[s.replace('两台高压内部流量与状态准备已接入并验证；其他系统仍保持原实现。',
                                         '两台高压及中压已确认的状态/流量准备已接入；中压未定来源保持None，其他系统保持原实现。') for s in review['code_limitations']]
    path.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    path=OUT/'raw_input_selection_review.md'
    text=path.read_text(encoding='utf-8').replace('当前清单294项','当前清单278项').replace('当前清单286项','当前清单278项')
    if lp_payload_path.exists():
        text=text.replace('当前清单278项',f"当前清单{len(payload['rows'])}项")
        text=re.sub(r'^当前清单.*$',f"当前清单{len(payload['rows'])}项；最新低压确认删除{len(payload['removed_rows'])}个派生采集项，新增{len(payload['added_rows'])}个外部状态需求，更新{len(payload['updated_rows'])}行来源或定义。保留原先高压、中压及用户已有修改。",text,flags=re.M)
        text=text.replace('两台高压及中压已确认的状态/流量准备已接入；中压规则已确认，缺数据保持None、系统能量暂缓，其余系统保留原实现。',
                          '两台高压、中压及低压当前拓扑和状态/流量准备已接入；缺数据保持None，中压系统能量暂缓，其余系统保留原实现。')
    text=text.replace('两台高压内部流量、状态及泵模型准备已接入；其他系统仍保留原实现，尚未逐个确认。',
                      '两台高压及中压已确认的状态/流量准备已接入；中压未定来源保持None，其余系统保留原实现。')
    text=text.replace('中压未定来源保持None','中压规则已确认，缺数据保持None、系统能量暂缓')
    text=text.replace('未确认测点编码留空；测点单位仅在来源一致时填写。','未确认测点编码留空；授权单位覆盖保留原始证据，其余单位按已核实来源填写。')
    text=text.replace('在两台HP稳定单泵运行约束有效时增至120，再保留14个其他独立分流需求后达到134。',
                      '在两台HP稳定单泵约束有效时增至120，再加入两台IP稳定单泵约束增至122，另保留12个其他分流需求后达到134。结构秩不证明数值闭合，IP泵流量=省煤器给水量+减温水量；分流点按派生关系闭合，保留汽包给水与独立蒸汽测点的质量残差。')
    text=text.replace('IP泵=给水且有喷水时保留质量残差。','IP泵流量=省煤器给水量+减温水量；分流点按派生关系闭合，保留汽包给水与独立蒸汽测点的质量残差。')
    if lp_payload_path.exists():
        rank_note=(f"{len(selection['measured_fields'])}个原选择流量约束与质量约束的组合秩为{selection['rank_with_measurements']}；"
                   f"依次加入有效HP、IP、LP稳定单泵约束后，秩为{selection['rank_with_valid_HP_operation_constraints']}、"
                   f"{selection['rank_with_valid_HP_IP_operation_constraints']}、{selection['rank_with_valid_HP_IP_LP_operation_constraints']}；"
                   f"再保留{len(selection['independent_fields'])}个其他独立流量需求后达到{selection['rank_after_independent_constraints']}。结构秩不证明实测数值闭合。")
        text=re.sub(r'^.*个原选择流量约束与质量约束的组合秩.*$',rank_note,text,flags=re.M)
        for f in lp_fields:
            text=text.replace(f'- {f}\n','')
        if 'lp_system_review.md' not in text:
            text+='\n低压拓扑、派生关系与全部缺测点见 [lp_system_review.md](lp_system_review.md)。当前桌面清单252项，保留原始来源和用户示例。\n'
    for f in ip_fields:
        text=text.replace(f'- {f}\n','')
    if 'ip_confirmed_model_review.md' not in text:
        text+='\n中压新约定、72项旧字段清理及8项采集删除见 [ip_confirmed_model_review.md](ip_confirmed_model_review.md)。\n'
    text=re.sub(r'当前桌面清单\d+项',f"当前桌面清单{len(payload['rows'])}项",text)
    path.write_text(text,encoding='utf-8')
    path=OUT/'parameter_selection.md'
    text=path.read_text(encoding='utf-8')
    text=text.replace('两台高压回路已按确认拓扑实现并进行行为测试和有界历史窗口检查；其他系统仍为原重选方案。',
                      '两台高压回路及中压已确认约定已接入；中压旧字段已删除，未定来源保留None；其他系统仍为原重选方案。')
    text=text.replace('131 条','141 条').replace('135 条','141 条').replace('61 个','63 个')
    text=text.replace('未定来源保留None','状态规则已确认，缺数据保留None且系统能量暂缓').replace('未定项保持None','缺失数据保持None，系统能量暂缓')
    for count in ('55','51'):
        text=text.replace(f'{count} 个字段','43 个字段').replace(f'{count} 台仪表','43 台仪表')
    text=text.replace('75 条','81 条').replace('79 条','81 条').replace('42 条','46 条').replace('高压推导已在 `gard/systems/hrsg_hp.py` 实现；其他系统仍需独立确认后接入。',
                      '高压推导在 `gard/systems/hrsg_hp.py`；中压已确认准备在 `gard/systems/hrsg_ip.py`，未定项保持None。')
    text=text.replace('HP活动设备与组合受热面已同步；其他系统和“再热器1/2→减温器→再热器3”仍待逐个确认。',
                      'HP/IP活动设备已同步；IP为“再热器组1～2→减温器→再热器3”，其他系统仍待逐个确认。')
    if 'ip_confirmed_model_review.md' not in text:
        text+='\n最新中压定义与剩余问题见 [ip_confirmed_model_review.md](ip_confirmed_model_review.md)。\n'
    if '用户已暂缓中压系统能量输入输出' not in text:
        text+='\n用户已暂缓中压系统能量输入输出：IP work/heat/heat_exergy保持None，系统能量及完整火用计算暂不启用；泵流量取省煤器给水量加减温水量，分流点按派生关系闭合，汽包给水与独立蒸汽流量的质量残差仍保留。\n'
    text=text.replace('泵流量取中压给水量，正喷水量保留分流质量残差。','泵流量取省煤器给水量加减温水量，分流点按派生关系闭合，汽包给水与独立蒸汽流量的质量残差仍保留。')
    if lp_payload_path.exists():
        text=text.replace('141 条','159 条').replace('63 个','65 个').replace('81 条','95 条').replace('46 条','50 条')
        text=text.replace('两台高压回路及中压已确认约定已接入；','两台高压、中压及低压当前拓扑和准备关系已接入；')
        text=text.replace('HP/IP活动设备已同步','HP/IP/LP活动设备已同步')
        text=text.replace('随后补足供热分流及锅炉水回收流量/状态。','这些已选测点中仍缺历史文件；随后补足供热分流及锅炉水回收流量/状态，全部缺项见低压专项检查。')
        if 'lp_system_review.md' not in text:
            text+='\n低压每炉13设备及派生关系已接入，当前原始参数表252项。完整缺项和源证据见 [lp_system_review.md](lp_system_review.md)。\n'
    # Reconcile figures against the freshly generated audit, not prior-phase
    # hardcoded counts. The LP header adds one stream and one mass equation.
    values={
        '现有 `POINT_BINDINGS`':f"{audit['binding_count']} 条",
        '主循环层 `core`':f"{plan['existing_binding_role_counts']['core']} 条",
        '设备分析层 `component`':f"{plan['existing_binding_role_counts']['component']} 条",
        '校核层 `validation`':f"{plan['existing_binding_role_counts']['validation']} 条",
        '元数据无冲突的现有绑定':f"{audit['binding_count']-audit['bindings_with_metadata_errors']} 条",
        '需隔离的现有绑定':f"{audit['bindings_with_metadata_errors']} 条",
        '未由点表确认绝压/表压的压力字段':f"{audit['unconfirmed_pressure_basis_count']} 个",
        '补充/替换需求':f"{len(plan['additional_or_replacement_parameters'])} 个字段",
        '独立流股质量流量变量':str(flow['stream_flow_variables']),
        '质量方程行数':str(flow['mass_equations']),
        '质量矩阵秩':str(flow['mass_rank']),
        '只有质量方程时的自由度':str(flow['mass_only_degrees_of_freedom']),
        '当前可映射、量纲一致的流量字段':str(len(flow['current_mapped_flow_measurements'])),
        '这些字段使质量约束增加的秩':str(flow['rank_with_current_unit_consistent_flow_bindings']-flow['mass_rank']),
        '尚余质量自由度':str(flow['remaining_mass_only_degrees_of_freedom']),
    }
    for label,value in values.items():
        text=re.sub(r'(?m)^(\| '+re.escape(label)+r' \| )[^|]+',lambda m:m[1]+value+' ',text)
    text=re.sub(r'不是要求新增 \d+ 台仪表',f"不是要求新增 {len(plan['additional_or_replacement_parameters'])} 台仪表",text)
    text=re.sub(r'(\[现有绑定核对表\]\(data_binding_audit.md\)：)\d+ 条',lambda m:m[1]+str(audit['binding_count'])+' 条',text)
    text=re.sub(r'因此 \d+ 是该假设下的剩余自由度，不能理解为必须新增 \d+ 个传感器',
                f"因此 {flow['remaining_mass_only_degrees_of_freedom']} 是该假设下的剩余自由度，不能理解为必须新增 {flow['remaining_mass_only_degrees_of_freedom']} 个传感器",text)
    text=re.sub(r'当前原始参数表\d+项',f"当前原始参数表{len(payload['rows'])}项",text)
    text=re.sub(r'现有 \d+ 条绑定自动生成',f"现有 {audit['binding_count']} 条绑定自动生成",text)
    text=re.sub(r'\d+ 条工质流股的状态准备合同',f"{len(plan['prepared_state_contracts'])} 条工质流股的状态准备合同",text)
    text=text.replace('中压仍需独立依据；高压用已确认互备与原始电流稳定资格，不单独采集逐泵流量',
                      '高中压均用已确认互备与原始电流稳定资格，不单独采集逐泵流量')
    text=text.replace('| 两炉低压再循环泵总量与分配 | 4 | 先增加已找到的再循环总流量，再按分析需要补逐泵分配 |',
                      '| 两炉低压再循环泵分配 | 2条件约束 | 总量已绑定；单泵互备与原始电流稳定资格决定逐泵分配 |')
    text=text.replace('若先合并所有并联泵组，可省去 10 个组内分配自由度，余下的 8 类循环/分流锚点仍需补足。',
                      '若先合并所有并联泵组，可省去10个组内分配自由度，当前已绑定再循环总量后仍余6个循环/分流锚点。')
    text=text.replace('阀后 P（汽包入口位置核对后可用汽包压力）', '阀后 P（用户已确认采用汽包压力）')
    text=text.replace('两股返回水入口/混合出口状态充分且独立时，可以增加焓混合方程求回流；若未测混合出口温度、返回水温或两支路同时未知，则不够。',
                      '两股返回水入口/混合出口状态充分且独立时，理论上可增加焓混合方程求回流。本轮已确认余热回收混合后P/T与返回水测点；混合前状态仍缺，且用户明确将水水换热器流量留空，不启用反算。')
    if confirmed_path.exists() and '低压本次确认' not in text:
        text+='\n低压本次确认：返回水P/T按指定HAA13/HAA11测点，HAA70测点迁移至混合后；省煤器进出口P取HAA70压力、给水阀后P取汽包压力。每炉先分流，两路各自跨炉合并；混合前给水P/T、供热分流量及热网低压补汽汇合母管P/T仍需定义，水水换热器流量按用户要求留空。详见低压专项审计。\n'
    path.write_text(text,encoding='utf-8')
    print(json.dumps({'parameters':len(payload['rows']),'IP_legacy_fields_removed':72,'latest_IP_derived_removed':12,'latest_IP_currents_added':4,'rank_with_HP_IP_operation':selection['rank_with_valid_HP_IP_operation_constraints']}))
if __name__=='__main__':
    main()
