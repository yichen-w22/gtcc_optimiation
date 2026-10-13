"""Read-only IP feedwater/source/history audit; writes evidence only in analysis/."""
import hashlib
from importlib import import_module
import json
from pathlib import Path
import sys

import openpyxl
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from audit_parameter_sources import load_catalog, assignment, literal
from gard.data_io import read_history, summarize_history, convert_values

def file_evidence(path):
    parquet = pq.ParquetFile(path)
    names = parquet.schema_arrow.names
    assert all(k in names for k in ('tbname','ts','col0')), (path, names)
    time_index, value_index = names.index('ts'), names.index('col0')
    time_stats = [parquet.metadata.row_group(i).column(time_index).statistics for i in range(parquet.num_row_groups)]
    value_stats = [parquet.metadata.row_group(i).column(value_index).statistics for i in range(parquet.num_row_groups)]
    available_time = [s for s in time_stats if s and s.has_min_max]
    available_value = [s for s in value_stats if s and s.has_min_max]
    return {'file':path.relative_to(ROOT).as_posix(), 'bytes':path.stat().st_size,
            'rows':parquet.metadata.num_rows, 'row_groups':parquet.num_row_groups,
            'min_time':pd.Timestamp(min(s.min for s in available_time),unit='ns',tz='UTC').tz_convert('Asia/Shanghai').isoformat() if available_time else None,
            'max_time':pd.Timestamp(max(s.max for s in available_time),unit='ns',tz='UTC').tz_convert('Asia/Shanghai').isoformat() if available_time else None,
            'metadata_value_min':min(s.min for s in available_value) if available_value else None,
            'metadata_value_max':max(s.max for s in available_value) if available_value else None}

def main():
    master, _ = load_catalog()
    source = ROOT/'docs/点表-高安屯.xlsx'
    desktop = Path(r'C:\Users\32697\Desktop\全部原始编码.xlsx')
    before = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (source, desktop)}
    workbook = openpyxl.load_workbook(desktop, read_only=True)
    sheet = workbook.worksheets[0]
    excel_rows = {r[1]:{'row':i,'values':list(r)} for i,r in enumerate(sheet.iter_rows(min_row=2,max_col=6,values_only=True),2) if r[1]}
    workbook.close()
    files = {}
    for path in (ROOT/'gard_raw_data').glob('*.parquet'):
        files.setdefault(path.stem.rsplit('+',1)[-1], []).append(path)
    records = []
    unit_results = []
    for unit in (1,2):
        name, prefix = f'hrsg{unit}_ip', f'hrsg{unit}'
        bindings = import_module(f'gard.systems.{name}.data').POINT_BINDINGS
        overrides=getattr(import_module(f'gard.systems.{name}.data'),'UNIT_OVERRIDES',{})
        relevant = set(bindings.field)
        extras = [(f'{prefix}.lp_drum_pressure','GARD_11HBK11CM001BP02XQ01' if unit==1 else 'GARD_12HAG11CM001BP02XQ01','MPa','shared_input')]
        extras += [(f'{prefix}.ip_pump{j}.current',f'GARD_1{unit}LAB8{j}QM003BC01XQ01','A','unbound_current_candidate') for j in (1,2)]
        before_field = f'{prefix}.rh_before_spray.T'
        extras += [(before_field, excel_rows[before_field]['values'][2], '℃','excel_selected_not_bound')]
        extras = [item for item in extras if item[0] not in relevant]
        all_inputs = [(b.field,b.code,b.expected_unit,'bound') for b in bindings.itertuples(index=False)] + extras
        for field, code, expected_unit, status in all_inputs:
            references = master.get(code, [])
            paths = files.get(code, [])
            row = excel_rows.get(field)
            problems = []
            override=overrides.get(field)
            applied=bool(override and override['code']==code and override['effective_unit']==expected_unit
                         and any(r['unit']==override['original_unit'] for r in references))
            if not references:
                problems.append('not_in_source_point_table')
            if references and not any(r['unit'].lower() == expected_unit.lower() for r in references) and not applied:
                problems.append('source_unit_mismatch')
            if not paths:
                problems.append('history_file_missing')
            if len(paths)>1:
                problems.append('duplicate_history_files')
            if row is None:
                problems.append('excel_row_missing')
            elif row['values'][2] != code:
                problems.append('excel_code_mismatch')
            records.append({'unit':unit, 'system':name, 'field':field, 'code':code,
                            'status':status, 'expected_unit':expected_unit, 'master_records':references,
                            'excel':row, 'history':[file_evidence(p) for p in paths], 'unit_override':override if applied else None,'problems':problems})
        # Bounded integration check uses the same 30-minute window as the HP check.
        # A file's existence does not imply coverage or physical validity in this window.
        start=pd.Timestamp('2024-06-01 00:30:00',tz='Asia/Shanghai')
        end=start+pd.Timedelta(minutes=30)
        raw=read_history(ROOT/'gard_raw_data', start, end, bindings)
        raw_means=summarize_history(raw,start,end)
        converted=convert_values(raw_means,bindings,atmospheric_pressure=101375)
        system=literal(assignment(ROOT/f'gard/systems/{name}/system.py','SYSTEM_DEFINITIONS'))[name]
        unit_results.append({'unit':unit,'bound_inputs':len(bindings),'bound_inputs_with_history':sum(b.code in files for b in bindings.itertuples(index=False)),
                             'window':{'start':start.isoformat(),'end':end.isoformat()},
                             'raw_means_with_sufficient_coverage':sum(raw_means.get(b.code) is not None for b in bindings.itertuples(index=False)),
                             'si_values_available':sum(v is not None for v in converted.values()), 'raw_point_means':raw_means,'si_inputs':converted,
                             'legacy_active_device_count':len(system['devices']),
                             'legacy_extra_devices':[s for s in system['devices'] if any(k in s for k in ('bypass','feed_valve','main_split'))],
                             'feedwater_pressure_description':master[bindings.set_index('field').loc[f'{prefix}.ip_feed.P','code']][0]['description'],
                             'feedwater_temperature_description':master[bindings.set_index('field').loc[f'{prefix}.ip_feed.T','code']][0]['description']})
    temperature_candidates=[]
    for unit in (1,2):
        for channel in (10,14,15,13):
            code=f'GARD_1{unit}LBB01WP001BT{channel:02d}XQ01'
            temperature_candidates.append({'unit':unit,'field':f'hrsg{unit}.hot_reheat.T','code':code,
                                           'master_records':master.get(code,[]),'history_exists':code in files,
                                           'is_selected_or_authorized':channel==13})
    report={'date':'2026-10-13','scope':'two IP feedwater circuits and connected reheat source prerequisites; read-only audit, no model/Excel edits',
            'user_deferred_items':['missing LP drum history files to be supplied later','pressure basis confirmation deferred'],
            'units':unit_results,'parameters':records,'supplementary_temperature_candidates':temperature_candidates,'source_hashes':before,
            'interpretation':'File presence and metadata unit match do not prove independent measurement, stable window coverage or valid thermodynamic states. HP exclusive-duty, pump efficiency and pressure approximations are not automatically applied to IP.'}
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items())
    (OUT/'ip_feedwater_source_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# 两炉中压给水原始数据完整性检查','',
           '检查日期2026-10-13。读取现有IP拓扑、代码、原始点表、Parquet元数据与桌面参数表；不改模型或Excel。低压汽包缺失文件及压力基准按用户已有安排留待后续。','',
           '| 项目 | 1号炉 | 2号炉 |','| --- | --- | --- |',
           '| 当前data.py绑定历史文件 | 23/25存在：缺低压汽包P、减温前T | 23/25存在：缺低压汽包P、减温前T |',
           '| 两台中压泵出口P、省煤器进水P/T/流量、汽包进水T和汽包P | 均有点表及历史 | 均有点表及历史 |',
           '| 低压汽包P历史（泵入口共用） | 缺失，后续补 | 缺失，后续补 |',
           '| 泵1电流 | 有历史、按A已接入 | 有历史、按A已接入 |',
           '| 泵2电流 | 有历史、原%按用户授权A已接入 | 有历史、按A已接入 |',
           '| 再热喷水流量 | 有历史、t/h，DCS计算值 | 有历史、t/h，DCS计算值 |',
           '| 再热器2出口 / 减温前T扩展输入 | 已选点表编码，历史缺失 | 已选点表编码，历史缺失 |','',
           '## 给水原始来源','',
           '中压给水P与T的原点表名称分别为“中压省煤器进水压力”和“中压省煤器进水温度”。与HP压力为调节阀前测点的描述不同，本轮未发现同类跨阀位置描述问题；真实安装位置仍以现场资料为准。','',
           '| 字段 | 原始编码 | 原单位 | 原点表位置 | 历史文件 | 接入情况 |','| --- | --- | --- | --- | --- | --- |']
    for r in records:
        if not any(s in r['field'] for s in ('ip_pump','ip_feed','ip_to_drum','ip_drum_pressure','lp_drum_pressure','rh_spray.m_dot')):
            continue
        refs='；'.join(f"{x['sheet']}!{x['code_cell']}/{x['unit_cell']}" for x in r['master_records'])
        units='、'.join(sorted({x['unit'] for x in r['master_records']}))
        lines.append(f"| `{r['field']}` | `{r['code']}` | {units} | {refs} | {'存在' if r['history'] else '缺失'} | {'data.py已绑定' if r['status']=='bound' else '共用低压输入' if r['status']=='shared_input' else '未绑定'} |")
    lines += ['', '## 原始输入与候选派生量', '',
              '运行泵及母管流量等于省煤器给水流量 `ip_feed.m_dot` 加减温水流量 `rh_spray.m_dot`。喷水流量仍用 `GARD_11LAF80WP001BF02XQ01` / `GARD_12LAF80WP001BF02XQ01` 的t/h DCS计算值；任一分量缺失或无效时不使用部分流量代替总量。分流点按派生关系闭合，不能作为独立实测验证；汽包给水与新蒸汽流量不一致的质量残差仍保留。DCS计算来源/独立性尚未核验。', '',
              '中压泵出口T等于入口T、汽包进水P等于汽包P、饱和蒸汽量复用指定新蒸汽测点、减温前后P等于热再热P、至汽机流量等于热再热量。运行泵流量等于省煤器给水量加减温水量，备用0；母管及喷水采用运行泵状态，无独立节流。以上已接入 `gard/systems/hrsg_ip.py`，系统能量/完整火用暂不计算。', '',
              '四路 `hrsg{i}.ip_pump{j}.current` 按A绑定并加入Excel。一号泵2原DCS!E1770的%保留为原始证据，用户已授权按A。用户指定10 A阈值、两泵互备；使用简单>10 A判据，切泵或矛盾窗口保持不可分配。', '',
              '四路电流全记录元数据范围包含约−2.13至−5的负值，不当作实际负电功；使用用户指定10 A阈值而非HP的1 A阈值。', '',
              '## 完整中压/再热回路的额外接入问题', '',
              '当前 `data.py` 两炉各25条绑定、23个文件存在。低压汽包P和再热减温前T历史仍缺失；电流和热再热T已接入，授权覆盖保留原单位。IP活动图为12设备，旧字段不恢复；专用入口不依赖旧cooling注册表。', '',
              '两炉 `rh_before_spray.T`（`GARD_11HAJ80WP001BT01XQ01` / `GARD_12HAJ80WP001BT01XQ01`）原描述为再热器2出口温度；两个历史文件均缺失，现已绑定并由活动流股消费。', '',
              '锅炉出口 `hot_reheat.T` 已选两炉 `LBB01WP001BT13XQ01`。选择值原%按用户授权℃导入并转K，历史均存在；不改用BT10/14/15或至汽机取点。候选及原始证据保留在JSON。', '',
              '## 文件存在与窗口数据可用性', '',
              '读取2024-06-01 00:30–01:00（Asia/Shanghai）窗口，沿用原数据准备的60秒保持、五分钟覆盖80%、半小时五个有效bin规则。此为停机附近的有界检查，不是已确认稳定运行窗口：','']
    for u in unit_results:
        lines.append(f"- {u['unit']}号炉：{u['bound_inputs_with_history']}/{u['bound_inputs']}个输入有文件，原始时间加权均值覆盖合格{u['raw_means_with_sufficient_coverage']}项，SI转换后可用{u['si_values_available']}项；具体None、数值和文件总时间范围见JSON。")
    lines += ['', '压力基准延后核对；系统能量输入输出和完整火用按用户安排暂不考虑，保持None。电流不用于电功。', '',
              '复核脚本：`python analysis/audit_ip_feedwater_sources.py`。详细原始证据：[ip_feedwater_source_audit.json](ip_feedwater_source_audit.json)。原始点表与桌面表哈希在执行前后相同。']
    (OUT/'ip_feedwater_data_review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'bound_files':[{'unit':u['unit'],'existing':u['bound_inputs_with_history'],'total':u['bound_inputs'],'window_raw_covered':u['raw_means_with_sufficient_coverage'],'window_si_available':u['si_values_available']} for u in unit_results],
                      'problems':[{'field':r['field'],'code':r['code'],'problems':r['problems']} for r in records if r['problems']]},ensure_ascii=False))
if __name__=='__main__':
    main()
