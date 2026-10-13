"""Audit all active LP fields, raw points and histories without changing sources."""
from collections import Counter
import hashlib
from importlib import import_module
import json
from pathlib import Path
import sys

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from audit_parameter_sources import load_catalog
from audit_ip_feedwater_sources import file_evidence
from gard.data_io import load_inputs

INDEPENDENT_GAPS = {
    'lp_feed.P': ('余热回收返回混合前低压给水压力', '原HAA70压力已按用户指定移至混合后；混合前需独立测点或明确近似'),
    'lp_feed.T': ('余热回收返回混合前低压给水温度', '原HAA70温度已按用户指定移至混合后；不能把同一测温当作混合前实测'),
    'lp_to_heat_recovery.m_dot': ('水水换热器工质侧循环总流量', '用户明确暂留空；闭合循环返回量等于送出量，但不能由给水量推得循环量'),
    'lp_to_heat.m_dot': ('本炉低压蒸汽至供热流量', '每炉需要一个独立分流依据；全厂供热总流量不能唯一分配到两炉'),
}

INTERFACE_GAPS = {
    'heat.lp_steam_header.P': ('两炉低压供热支路汇合后母管压力', '新确认汇合节点；尚未选定测点或混合压力近似'),
    'heat.lp_steam_header.T': ('两炉低压供热支路汇合后母管温度', '尚未选定测点；两炉温度不同时不能直接复制任一炉温度'),
}

DERIVED = {
    'lp_from_heat_recovery.m_dot': '默认稳态无泄漏工质侧闭合循环，等于lp_to_heat_recovery.m_dot；配置可关闭此近似',
    'lp_feed_after_recovery.m_dot': 'lp_feed.m_dot+lp_from_heat_recovery.m_dot',
    'lp_economizer_in.P': '用户确认等于lp_feed_after_recovery.P（HAA70WP021BP01）',
    'lp_economizer_out.P': '用户确认等于lp_feed_after_recovery.P（HAA70WP021BP01）',
    'lp_to_drum.P': '用户确认给水阀后压力等于lp_drum_pressure',
    'lp_to_heat.P': '简单分叉出口取lp_main.P；不代表下游共同母管压力',
    'lp_to_heat.T': '简单分叉出口取lp_main.T；不代表下游共同母管温度',
    'lp_economizer_in.m_dot': 'lp_feed_after_recovery.m_dot+lp_recirc_in.m_dot',
    'lp_economizer_out.m_dot': 'lp_economizer_in.m_dot',
    'lp_drum_valve_in.T': '当前无旁路分流节点，取lp_economizer_out.T',
    'lp_drum_valve_in.m_dot': '闭合循环默认等于lp_feed.m_dot，循环量缺失仍可确定；非闭合时为给水+返回-送出',
    'lp_to_drum.m_dot': '等于lp_drum_valve_in.m_dot，不强制与汽包出口总量相等',
    'lp_recirc_out.P': '唯一运行再循环泵出口P；运行状态不可判定时None',
    'lp_recirc_out.T': '运行泵出口T，按已确认的泵出口T等于入口T近似',
    'lp_recirc_out.m_dot': 'lp_recirc_in.m_dot',
    'lp_water.m_dot': 'hp_main.m_dot+ip_feed.m_dot+rh_spray.m_dot',
    'lp_saturated_steam.m_dot': 'lp_main.m_dot（简化稳态过热器无额外分流）',
    'lp_to_st.m_dot': 'lp_main.m_dot-lp_to_heat.m_dot，负差值None',
    'hp_pump_in.m_dot': 'hp_main.m_dot（已确认高压供水总量）',
    'ip_pump_in.m_dot': 'ip_feed.m_dot+rh_spray.m_dot（已确认中压供水总量）',
}
for stem in ('lp_recirc_in', 'lp_to_heat_recovery'):
    for quantity in ('P', 'T'):
        DERIVED[f'{stem}.{quantity}'] = f'当前分流节点取lp_economizer_out.{quantity}，暂不增加管路压降/散热'
for pump in (1, 2):
    for side in ('in', 'out'):
        DERIVED[f'lp_recirc_pump{pump}_{side}.m_dot'] = '唯一运行泵承担再循环总量，备用0；原始时序切泵/矛盾时None'
        DERIVED[f'lp_recirc_pump{pump}_{side}.T'] = 'lp_economizer_out.T（泵出口T等于入口T近似）'
    DERIVED[f'lp_recirc_pump{pump}_in.P'] = 'lp_economizer_out.P，来自省煤器而非汽包饱和水'


def main():
    master, _ = load_catalog()
    desktop = Path(r'C:\Users\32697\Desktop\全部原始编码.xlsx')
    sources = [ROOT / 'docs/点表-高安屯.xlsx', desktop]
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    workbook = openpyxl.load_workbook(desktop, read_only=True)
    excel = {r[1]: {'row': i, 'values': list(r)} for i, r in enumerate(
        workbook.worksheets[0].iter_rows(min_row=2, max_col=6, values_only=True), 2) if r[1]}
    workbook.close()
    files = {}
    for path in (ROOT / 'gard_raw_data').glob('*.parquet'):
        files.setdefault(path.stem.rsplit('+', 1)[-1], []).append(path)
    bindings_report, inventory, gaps, summaries = [], [], [], []
    for unit in (1, 2):
        prefix, name = f'hrsg{unit}', f'hrsg{unit}_lp'
        module = import_module(f'gard.systems.{name}.data')
        bindings = module.POINT_BINDINGS
        by_field = {b.field: b for b in bindings.itertuples(index=False)}
        for b in by_field.values():
            references = master.get(b.code, [])
            assert references, (b.field, b.code)
            record = {'unit': unit, 'field': b.field, 'code': b.code, 'engineering_unit': b.expected_unit,
                      'master_records': references, 'unit_source_record': module.UNIT_OVERRIDES.get(b.field),
                      'history': [file_evidence(p) for p in files.get(b.code, [])], 'excel': excel.get(b.field),
                      'shared_with_HP_IP': b.field.endswith(('hp_main.m_dot', 'ip_feed.m_dot', 'rh_spray.m_dot'))}
            bindings_report.append(record)
            if not record['history']:
                gaps.append({'unit': unit, 'field': b.field, 'kind': 'history_missing', 'code': b.code,
                             'meaning': references[0]['description'], 'engineering_unit': b.expected_unit})
        definitions = import_module(f'gard.systems.{name}.streams').STREAM_DEFINITIONS
        seen = set()
        for stream, spec in definitions.items():
            for quantity in ('P', 'T', 'm_dot'):
                field = spec.get(quantity)
                if not isinstance(field, str) or field in seen:
                    continue
                seen.add(field)
                stem = field.removeprefix(prefix + '.')
                if field in by_field:
                    status, rule = 'raw_bound', '原始外部输入；缺文件与缺测点定义分开统计'
                elif stem == 'lp_economizer_in.T':
                    status, rule = 'raw_or_mixed', '已有测点；缺数据时可由混合焓及入口P计算'
                elif stem in DERIVED:
                    status, rule = 'derived', DERIVED[stem]
                elif stem in INDEPENDENT_GAPS:
                    status, rule = 'point_or_definition_missing', INDEPENDENT_GAPS[stem][1]
                else:
                    raise AssertionError(('Unclassified LP field', field))
                inventory.append({'unit': unit, 'field': field, 'stream': stream, 'quantity': quantity,
                                  'status': status, 'rule': rule})
        for stem, (meaning, note) in INDEPENDENT_GAPS.items():
            gaps.append({'unit': unit, 'field': f'{prefix}.{stem}', 'kind': 'point_or_definition_missing',
                         'code': None, 'meaning': meaning, 'note': note})
        row = load_inputs(name, ROOT / 'gard_raw_data', '2024-06-01 00:30', '2024-06-01 01:00')
        summaries.append({'unit': unit, 'active_devices': 13, 'bound_inputs': len(bindings),
                          'existing_histories': sum(b.code in files for b in by_field.values()),
                          'missing_histories': sum(b.code not in files for b in by_field.values()),
                          'unselected_independent_fields': len(INDEPENDENT_GAPS),
                          'bounded_window': {'start': '2024-06-01 00:30 Asia/Shanghai', 'end': '2024-06-01 01:00 Asia/Shanghai',
                                             'available_SI_inputs': sum(row.get(b.field) is not None for b in by_field.values()),
                                             'operation_status': row.get(f'{prefix}.lp_operation_status')}})
    for field, (meaning, note) in INTERFACE_GAPS.items():
        gaps.append({'unit': 'shared', 'field': field, 'kind': 'shared_interface_definition_missing',
                     'code': None, 'meaning': meaning, 'note': note})
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in hashes.items())
    candidates = [
        {'code': code, 'master_records': rs, 'history_exists': code in files,
         'status': 'location_candidate_only_not_bound'}
        for code, rs in master.items() if any(
            any(k in r['description'] for k in ('烟气热网', '烟气水水', '烟气换热器'))
            and any(k in r['description'] for k in ('凝水', '凝结水'))
            and r['unit'] in ('MPa', '℃', '%') for r in rs)
        and ('WP' in code or 'QN101BP' in code)
        and code not in {b['code'] for b in bindings_report}]
    verification_path = OUT / 'lp_parameter_table_verification.json'
    verification = json.loads(verification_path.read_text(encoding='utf-8')) if verification_path.exists() else None
    report = {'date': '2026-10-13', 'scope': 'two LP water/steam circuits, working-fluid side only',
              'units_review': '用户要求不考虑单位问题；使用工程单位，原标注仅作证据，单位不计缺项',
              'source_hashes': hashes, 'units': summaries, 'bindings': bindings_report,
              'current_field_inventory': inventory, 'missing_inputs': gaps, 'recovery_location_candidates': candidates,
              'counts': dict(Counter(g['kind'] for g in gaps)),
              'model_assumptions': ['每炉13设备，与当前拓扑一致；移除每炉24个旧字段',
                                    '沿用单泵互备、默认10 A阈值；此为可配置运行假设，电流不能计算电功',
                                    '泵出口温度等于入口温度；低压再循环泵入口为省煤器出口状态',
                                    '默认水水换热器工质侧稳态无泄漏，返回量等于送出量；不含热网循环水',
                                    '余热回收混合后P/T用HAA70WP021BP01/BT01；省煤器进出口P用同一压力，给水阀后P用汽包P',
                                    '省煤器入口T优先测点BT02；缺失时具备混合流量、状态和出口P才按焓流计算',
                                    '供热支路为主汽简单分叉出口，P/T取本炉主汽；两炉至汽机支路、至供热支路分别汇合，不均分流量',
                                    '热网低压补汽汇合母管P/T仍独立；本次仅连接该工质侧汇合节点，未重构其余热网设备',
                                    '保留独立低压给水与汽包总出口质量差；系统功/热量/热量火用缺失时不输出完整能量/火用结果'],
              'measurement_location_issue': 'HAA80QN102BP01原描述为低压汽包进水压力，保留既有lp_drum_valve_in.P绑定，阀前安装位置尚需核对；不影响已确认的省煤器P和阀后P规则',
              'parameter_table_verification': verification,
              'deferred': ['压力基准仍按用户安排后续确认', '无完整实测工况及热量火用边界，不能宣称完整火用已求得']}
    (OUT / 'lp_source_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# 两炉低压系统检查、修改与全部缺测点', '', '日期：2026-10-13。以当前topology.md为准；单位按用户要求不作为问题统计。', '',
             '每炉旧设备17→13，删除省煤器旁路、蒸汽旁路、排污和高压泵回流连接。低压回水及汽包水名称与当前拓扑对齐，补齐高中压供水母管定义，专用构建入口不依赖已删除cooling。', '',
             '## 本次确认的连接', '',
             '每台锅炉主汽经分叉后，一路至汽轮机、一路至热网；两炉按相同目的地分别汇合。代码保留至汽机支路的既有实测P/T；至热网支路按简单分叉出口取本炉主汽P/T，共同母管状态不跨位置复制。', '',
             '```mermaid', 'flowchart LR',
             '  LP1[1号炉低压补汽] --> ST1[1号炉至汽机支路]',
             '  LP1 --> HT1[1号炉至热网支路]',
             '  LP2[2号炉低压补汽] --> ST2[2号炉至汽机支路]',
             '  LP2 --> HT2[2号炉至热网支路]',
             '  ST1 --> STM[汽机补汽汇合]', '  ST2 --> STM', '  STM --> ST[汽轮机]',
             '  HT1 --> HTM[热网低压补汽汇合]', '  HT2 --> HTM', '  HTM --> HEAT[热网加热]', '```', '',
             '## 原始数据完整性', '', '| 炉号 | 绑定输入 | 有历史 | 缺历史 | 无选定测点/需状态定义 |', '| --- | --- | --- | --- | --- |']
    for summary in summaries:
        lines.append(f"| {summary['unit']} | {summary['bound_inputs']}（含3个复用HP/IP流量） | {summary['existing_histories']} | {summary['missing_histories']} | {summary['unselected_independent_fields']} |")
    lines += ['', '## 已选编码但缺历史文件（全部）', '', '| 算法字段 | 含义 | 原始编码 |', '| --- | --- | --- |']
    for g in gaps:
        if g['kind'] == 'history_missing':
            lines.append(f"| `{g['field']}` | {g['meaning']} | `{g['code']}` |")
    lines += ['', '## 还缺的独立测点或状态定义（全部）', '', '以下不是都必须新增仪表。可确认合适现有取点或明确状态近似；编码未核实的留空。每炉单列，不把派生字段作为采集点。', '',
              '| 算法字段 | 含义 | 需要的信息 |', '| --- | --- | --- |']
    for g in gaps:
        if g['kind'] in {'point_or_definition_missing', 'shared_interface_definition_missing'}:
            lines.append(f"| `{g['field']}` | {g['meaning']} | {g['note']} |")
    lines += ['', '## 派生规则与边界', ''] + ['- ' + s for s in report['model_assumptions']]
    lines += ['', '高压取水量=hp_main.m_dot；中压取水量=ip_feed.m_dot+rh_spray.m_dot；汽包水总量为两者之和。再循环是内部流量，不能等同低压总给水。低压供热量需要单炉分流依据，至汽机量取主汽减供热量，负差值保持None。', '',
              '低压汽包水x=0、饱和蒸汽x=1。余热回收混合后T按用户指定使用实测BT01，不再由混合焓替代。省煤器进水T测点BT02有编码但缺文件，具备混合流量、入口状态及P时可派生模型值，不宣称恢复了实测数据。', '',
              report['measurement_location_issue'], '',
              '用户称“热网疏水”的测点接在本低压图水水换热器工质侧返回口lp_from_heat_recovery，不替换供热蒸汽冷凝后的heat.drain_return。1号炉按指定11HAA11WP011BT02/11HAA13QN101BP02接入；2号炉已核实点表中12HAA11WP011BT02/12HAA13QN101BP02对应测点，按相同规则接入。原点表记录全部保留，单位不计未解决问题。', '',
              '原HAA70给水P/T重新定位到混合后；混合前lp_feed.P/T另需定义。BP04原描述是至汽机温度，保留绑定，不按编码字母换点。循环返回流量在闭合近似下派生；关闭该近似时lp_from_heat_recovery.m_dot另需输入。', '',
              '本轮实际窗口为2024-06-01 00:30–01:00（Asia/Shanghai），用于有限覆盖核查，不代表稳定运行工况。运行识别在原始时间序列上完成，均值不能掩盖切泵。具体覆盖、字段及原点表位置见JSON。', '',
              '## 全部活动字段', '', '| 算法字段 | 类型 | 定义 / 算法 |', '| --- | --- | --- |']
    for field in inventory:
        lines.append(f"| `{field['field']}` | {field['status']} | {field['rule']} |")
    lines += ['', '## 实现及参数表验证', '',
              '测试覆盖两炉运行识别、原始切泵、缺流量时实测状态保留、新压力定义覆盖旧值、混合前后测点分离、两路独立汇合、异常分流及输入不变。最新实际执行结果见lp_confirmed_validation.json。全厂旧注册表仍引用用户删除的cooling；本轮通过专用LP入口及独立汇合设备验证，未恢复cooling。', '']
    if verification:
        lines += [f"桌面表由{verification['before']}项调整为{verification['after']}项；已确认的派生状态不再独立采集，未确定测点编码留空。",
                  '', f"保留第一条用户示例、原有非目标行、行高、列宽、样式及空白工作表，不新增自动换行。修改前备份：`{verification['backup']}`。原始测点来源工作簿未改动。", '']
    lines += ['执行：`python -X utf8 analysis/audit_lp_sources.py`。详细证据：[lp_source_audit.json](lp_source_audit.json)。原始点表只读，执行前后哈希一致。']
    (OUT / 'lp_system_review.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'units': summaries, 'missing_counts': report['counts'], 'fields_classified': len(inventory)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
