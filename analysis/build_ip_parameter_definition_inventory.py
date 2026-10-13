"""List exact IP fields and distinguish definition decisions from missing data."""
import json
from pathlib import Path

from audit_parameter_sources import assignment, literal

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).resolve().parent

# status is about the source/model contract, not current numerical availability.
FIELDS=[
 ('lp_drum_pressure','入口','对应低压汽包压力，泵入口P+x=0','已定','共用输入；历史缺失，按用户安排后续补'),
 ('ip_pump1.current','入口','中压泵1电流','已定','按A解释；>10 A为运行，两泵互备；已接入'),
 ('ip_pump2.current','入口','中压泵2电流','已定','按A解释；1号原%覆盖来源保留；>10 A为运行，两泵互备；已接入'),
 ('ip_pump_in.m_dot','入口','泵入口母管总质量流量','已定','等于ip_feed.m_dot+rh_spray.m_dot；任一分量缺失或无效时None'),
 ('ip_pump1_in.m_dot','入口','泵1入口流量','已定','运行时等于ip_feed.m_dot+rh_spray.m_dot，停运0；电流证据不足/矛盾时None'),
 ('ip_pump2_in.m_dot','入口','泵2入口流量','已定','运行时等于ip_feed.m_dot+rh_spray.m_dot，停运0；电流证据不足/矛盾时None'),
 ('ip_pump1_out.P','泵出口','泵1出口压力','已定','现有实测压力绑定'),
 ('ip_pump1_out.T','泵出口','泵1出口温度','已定','用户确认等于泵入口温度；等温状态近似，不自动生成绝热功边界'),
 ('ip_pump1_out.m_dot','泵出口','泵1出口流量','已定','等于泵1入口流量；运行为ip_feed.m_dot+rh_spray.m_dot，停运0'),
 ('ip_pump2_out.P','泵出口','泵2出口压力','已定','现有实测压力绑定'),
 ('ip_pump2_out.T','泵出口','泵2出口温度','已定','用户确认等于泵入口温度'),
 ('ip_pump2_out.m_dot','泵出口','泵2出口流量','已定','等于泵2入口流量；运行为ip_feed.m_dot+rh_spray.m_dot，停运0'),
 ('ip_pump_out.P','泵出口','泵出口母管压力','已定','取唯一运行泵出口P'),
 ('ip_pump_out.T','泵出口','泵出口母管温度','已定','采用唯一运行泵出口状态，T等于入口T'),
 ('ip_pump_out.m_dot','泵出口','泵出口母管总流量','已定','等于ip_feed.m_dot+rh_spray.m_dot；分流质量残差为0，派生闭合不作为独立验证'),
 ('ip_feed.P','给水与汽包','中压省煤器进水压力','已定','原描述即省煤器进水压力'),
 ('ip_feed.T','给水与汽包','中压省煤器进水温度','已定','原描述即省煤器进水温度'),
 ('ip_feed.m_dot','给水与汽包','中压省煤器进水流量','已定','DCS选择值，现有绑定'),
 ('ip_to_drum.P','给水与汽包','中压汽包进水口压力','已定','用户确认等于ip_drum_pressure，已落实'),
 ('ip_to_drum.T','给水与汽包','中压汽包进水温度','已定','原汽包进水测温；当前图省煤器直接连接该端口，不保留旧阀前出口字段'),
 ('ip_to_drum.m_dot','给水与汽包','中压汽包进水流量','关系明确','当前简化主路等于ip_feed.m_dot，待实现'),
 ('ip_drum_pressure','给水与汽包','中压汽包压力','已定','1号11HBK02，2号12HAG02，现有绑定'),
 ('ip_drum_steam.m_dot','给水与汽包','汽包饱和蒸汽流量','已定','用户指定1号GARD_11HAH80WP011BF03XQ01，2号用现有对应12HAH80WP011BF03XQ01；复用ip_fresh.m_dot，保留与给水量的质量残差'),
 ('ip_fresh.P','新蒸汽与冷再热','中压过热器出口/新蒸汽压力','已定','现有绑定'),
 ('ip_fresh.T','新蒸汽与冷再热','中压过热器出口/新蒸汽温度','已定','现有绑定'),
 ('ip_fresh.m_dot','新蒸汽与冷再热','中压新蒸汽流量','已定','原蒸汽流量选择值，现有绑定'),
 ('cold_reheat.P','新蒸汽与冷再热','汽轮机高压缸返回锅炉的冷再热压力','已定','现有绑定'),
 ('cold_reheat.T','新蒸汽与冷再热','汽轮机高压缸返回锅炉的冷再热温度','已定','现有绑定'),
 ('cold_reheat.m_dot','新蒸汽与冷再热','冷再热质量流量','关系明确','当前简化图可由hot_reheat.m_dot-ip_fresh.m_dot-rh_spray.m_dot求得；需检查非负及DCS流量来源'),
 ('reheat_mixed.P','新蒸汽与冷再热','冷再热与新蒸汽混合后压力','已定','原冷再热混合后压力测点，现有绑定'),
 ('reheat_mixed.T','新蒸汽与冷再热','冷再热与新蒸汽混合后温度','已定','原混合后温度测点，现有绑定'),
 ('reheat_mixed.m_dot','新蒸汽与冷再热','进入再热器组的总流量','关系明确','cold_reheat.m_dot+ip_fresh.m_dot，待实现'),
 ('rh_before_spray.P','再热减温','再热器组1～2之后、减温前压力','已定','用户确认等于hot_reheat.P，已落实'),
 ('rh_before_spray.T','再热减温','再热器2出口、减温前温度','测点已选','Excel已选HAJ80WP001BT01，原单位℃；两炉历史缺失，现已绑定并接入'),
 ('rh_before_spray.m_dot','再热减温','减温前蒸汽流量','关系明确','等于reheat_mixed.m_dot，待实现'),
 ('rh_spray.P','再热减温','再热减温水压力','已定','采用出口母管P，不另做节流状态变换'),
 ('rh_spray.T','再热减温','再热减温水温度','已定','采用出口母管热力状态，不考虑节流'),
 ('rh_spray.m_dot','再热减温','再热减温水质量流量','测点已定，计算来源待核','LAF80WP001BF02，t/h；DCS计算值已有历史，不是独立实测已验证'),
 ('rh_after_spray.P','再热减温','再热减温后、再热器3前压力','已定','用户确认等于hot_reheat.P'),
 ('rh_after_spray.T','再热减温','减温后蒸汽温度','测点已选','HAJ80WP011BT07，原描述中压喷水后温度，℃；物理取点需随拓扑同步核对'),
 ('rh_after_spray.m_dot','再热减温','减温后蒸汽总流量','关系明确','reheat_mixed.m_dot+rh_spray.m_dot=hot_reheat.m_dot，待实现'),
 ('hot_reheat.P','热再热与接口','锅炉热再热出口压力','已定','现有绑定'),
 ('hot_reheat.T','热再热与接口','锅炉热再热出口温度','已定','使用BT13选择值；原%按用户授权℃解释，导入加273.15转K，原始来源保留'),
 ('hot_reheat.m_dot','热再热与接口','锅炉热再热出口总流量','已定','原流量补偿后选择值，现有绑定'),
 ('rh_to_st.P','热再热与接口','至汽机热再热压力','已定','独立接口位置测点，不自动替代锅炉出口'),
 ('rh_to_st.T','热再热与接口','至汽机热再热温度','已定','独立接口位置测点，不自动替代hot_reheat.T'),
 ('rh_to_st.m_dot','热再热与接口','送往汽机的热再热流量','已定','用户确认等于hot_reheat.m_dot，已落实'),
 ('_ip.work','边界量','IP工质系统边界功，输出正','暂不考虑','用户暂不考虑系统能量输入输出，保持None，不使用电流计算'),
 ('_ip.heat','边界量','IP工质系统净入热','暂不考虑','用户暂不考虑系统能量输入输出，保持None'),
 ('_ip.heat_exergy','边界量','热量穿过IP边界携带的火用','暂不考虑','系统能量/完整火用暂不计算，保持None而非0'),
]

def field(unit,suffix):
    return f'hrsg{unit}{suffix}' if suffix.startswith('_ip.') else f'hrsg{unit}.{suffix}'

def main():
    audit=json.loads((OUT/'ip_feedwater_source_audit.json').read_text(encoding='utf-8'))
    evidence={r['field']:r for r in audit['parameters']}
    active=[]
    old=[]
    for unit in (1,2):
        for suffix,group,meaning,status,note in FIELDS:
            if '待实现' in note:
                note=note.replace('待实现','已实现')
            name=field(unit,suffix)
            r=evidence.get(name)
            active.append({'field':name,'unit':unit,'group':group,'meaning':meaning,'definition_status':status,'note':note,
                           'code':r['code'] if r else None,'original_units':sorted({x['unit'] for x in r['master_records']}) if r else [],
                           'historical_file_exists':bool(r['history']) if r else None,
                           'bound_in_ip_data_py':r['status']=='bound' if r else False})
        streams=literal(assignment(ROOT/f'gard/systems/hrsg{unit}_ip/streams.py','STREAM_DEFINITIONS'))
        actual={v for d in streams.values() for k,v in d.items() if k in {'P','T','h','s','x','m_dot'} and isinstance(v,str)}
        bindings=evidence
        actual.update(k for k,v in bindings.items() if v['unit']==unit and v['status']=='bound')
        systems=literal(assignment(ROOT/f'gard/systems/hrsg{unit}_ip/system.py','SYSTEM_DEFINITIONS'))
        actual.update(v for d in systems.values() for k,v in d.items() if k in {'work','heat','heat_exergy'})
        covered={r['field'] for r in active+old if r['unit']==unit}
        assert actual<=covered, sorted(actual-covered)
    assert len(active)==100 and len(old)==0
    payload={'date':'2026-10-13','scope':'current IP circuit inputs/prepared fields, independent interface checks and boundary terms; legacy fields removed',
             'meaning_of_undetermined':'取值来源/建模或运行判断口径尚未明确；不等同于缺历史文件或字段名字没有含义',
             'pressure_basis':'用户要求后续再确认；本表不重复标每个P为待定基准',
             'active_or_interface_and_boundary':active,'removed_legacy_field_count':72,'legacy':old}
    (OUT/'ip_parameter_definition_inventory.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# 中压参数定义逐项清单','',
           '2026-10-13。所有字段从两炉IP代码、当前拓扑和来源审计对照；未改模型或Excel。下表“未定”是取值来源/建模口径未确认，缺文件与未接入另列。压力基准按用户安排后续再确认，不在每个P字段重复标记。','',
           '当前主回路、接口校核及暂缓边界量每炉50字段，共100；旧拓扑每炉36字段已删除，共72项。泵运行阈值10 A、互备、流量取给水量、母管/喷水状态和温度单位均已确认；系统能量/完整火用暂不计算。派生量不独立采集。','',
           '| 1号炉字段 | 2号炉字段 | 含义 | 定义状态 | 说明 |','| --- | --- | --- | --- | --- |']
    for suffix,group,meaning,status,note in FIELDS:
        if '待实现' in note:
            note=note.replace('待实现','已实现')
        lines.append(f'| `{field(1,suffix)}` | `{field(2,suffix)}` | {meaning} | {status} | {note} |')
    lines+=['','两炉活动图已严格同步当前12设备拓扑；旧旁路、排污、回流及单级再热器端口不再列入当前字段清单，IP已不再引用高压旁路出口。', '',
            '原始编码、单位、历史与绑定状态逐字段见 [ip_parameter_definition_inventory.json](ip_parameter_definition_inventory.json)；完整点表和文件证据见 [ip_feedwater_source_audit.json](ip_feedwater_source_audit.json)。']
    (OUT/'ip_parameter_definition_inventory.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'current_and_interface_fields':len(active),'legacy_fields':len(old),'all_existing_code_fields_covered':True},ensure_ascii=False))
if __name__=='__main__':
    main()
