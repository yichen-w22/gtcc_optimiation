"""Build a proposed input/derived-parameter manifest from the audited snapshot.

This is a selection proposal in analysis/, not a replacement for data.py.
"""

from collections import Counter
import json
from pathlib import Path

from audit_parameter_sources import ROOT, aliases, assignment, literal, load_catalog, unit_kind


OUT = Path(__file__).resolve().parent


def existing_role(binding):
    system, field = binding["system"], binding["field"]
    if system.endswith("_hp"):
        if ".hp_pump" in field or ".hp_to_drum." in field or ".hp_before_spray." in field or ".hp_after_spray." in field:
            return "component"
        if ".hp_to_st." in field:
            return "validation"
    if system.endswith("_ip"):
        if any(s in field for s in (".ip_pump", ".ip_to_drum.", ".reheat_mixed.", ".rh_after_spray.")):
            return "component"
        if ".rh_to_st." in field:
            return "validation"
    if system.endswith("_lp"):
        if any(s in field for s in (".lp_economizer_out.", ".lp_drum_valve_in.", ".lp_recirc_pump")):
            return "component"
        if any(s in field for s in (".lp_to_drum.", ".lp_to_st.")):
            return "validation"
    if system == "condenser" and any(s in field for s in ("cond.pre_pump", "cond.pump1_", "cond.pump2_", "cond.pump3_", "cond.filter_in.")):
        return "component"
    return "core"


def main():
    audit = json.loads((OUT/"source_audit.json").read_text(encoding="utf-8"))
    master, _ = load_catalog()
    inventory = []
    for b in audit["bindings"]:
        role = existing_role(b)
        item = {"system": b["system"], "field": b["field"], "role": role,
                "code": b["code"], "action": "quarantine" if b["problems"] else "retain",
                "source": b["source"], "point_metadata": b["master_records"], "issues": b["problems"],
                "pressure_basis_confirmed": b["pressure_basis_confirmed_by_point_metadata"],
                "unit_override": b.get("unit_override")}
        if role == "component":
            item["reason"] = "用于单设备/泵组/受热面火用分配；只做整循环边界计算时可转入扩展采集。"
        elif role == "validation":
            item["reason"] = "接口不同位置或阀后状态的校核通道；同一质量流量共享，P/T 不跨压降强制相等。"
        else:
            item["reason"] = "主循环流量、边界状态或独立功率输入/校核。"
        if "计算值" in " ".join(r["description"] for r in b["master_records"]):
            item["independence_note"] = "DCS 计算值；需要其原始输入及算法，不能自动视为新的独立观测。"
        inventory.append(item)

    additions = []
    def add(system, field, unit, role, why, codes=(), note=""):
        if any(b['system'] == system and b['field'] == field for b in audit['bindings']):
            return
        records = [r for code in codes for r in master.get(code, [])]
        if codes:
            assert all(code in master for code in codes), (field,codes)
            assert all(unit_kind(r["unit"]) == unit_kind(unit) for r in records), (field,records)
        additions.append({"system": system, "field": field, "unit": unit, "role": role,
                          "purpose": why, "candidate_codes": list(codes), "point_metadata": records,
                          "status": "source_candidate_requires_location_and_basis_confirmation" if codes else "no_verified_point_selected",
                          "note": note})
    for n in (1,2):
        prefix=f"hrsg{n}"
        low_drum="11HBK11CM001BP02" if n==1 else "12HAG11CM001BP02"
        add(f"hrsg{n}_lp",f"{prefix}.lp_drum_pressure","MPa","core","汽包饱和水/蒸汽状态；不能用省煤器进水压力代替。",[f"GARD_{low_drum}XQ01"])
        add(f"hrsg{n}_lp",f"{prefix}.lp_main.T","℃","core","低压主汽温度选择值，按工程温度单位导入。",note="已选BT03并接入；原标注只保留证据，用户要求不考虑单位问题。")
        add(f"hrsg{n}_lp",f"{prefix}.lp_recirc_in.m_dot","t/h","component","省煤器再循环总流量；若合并泵组只需总流量，逐泵还需分配依据。",[f"GARD_1{n}HAA85WP001BF01XQ01"])
        if not any(b['field']==f'{prefix}.rh_before_spray.T' for b in audit['bindings']):
            add(f"hrsg{n}_ip",f"{prefix}.rh_before_spray.T","℃","component","当前图减温器位于再热器 1、2 后；采用再热器 2 出口温度。",[f"GARD_1{n}HAJ80WP001BT01XQ01"],"新增规范字段。")
        # IP outlet selector T and spray P/T are now confirmed; no new sensors.
        from audit_lp_sources import INDEPENDENT_GAPS, INTERFACE_GAPS
        for stem, (meaning, note) in INDEPENDENT_GAPS.items():
            unit = 'MPa' if stem.endswith('.P') else '℃' if stem.endswith('.T') else 't/h'
            add(f"hrsg{n}_lp",f"{prefix}.{stem}",unit,"core",meaning,note=note)
    for field, (meaning, note) in INTERFACE_GAPS.items():
        add('heating', field, 'MPa' if field.endswith('.P') else '℃', 'component', meaning, note=note)
    add("st","st.ip_out.P","MPa","core","中压排汽、供热抽汽与低压连通管的焓熵状态。",["GARD_13LBS4400000BP01XQ01","GARD_13MAB5000000BP03XQ01","GARD_13MAB5000000BP04XQ01","GARD_13MAB5000000BP05XQ01"],"核对压力取点与供热抽汽截面；选择值/多个通道不是多份独立状态。")
    add("st","st.lp_in.P","MPa","core","补汽混合后的实际低压缸入口压力，不能由温度或质量平衡推出。",["GARD_13LBA1200000BT01XQ01"])
    add("st","st.lp_in.T","℃","validation","独立验证中压排汽和低压补汽的绝热混合焓。",["GARD_13LBA2000000BP01XQ01"])
    add("st","st.lp_out.h","J/kg","core","湿蒸汽状态；可用独立轴功及全汽轮机能量平衡推导，但该能量残差将不是独立检验。",note="h 或 x 二选一；出口 P、T 在饱和区不独立。")
    add("st","st.work","W","core","模型真实消耗字段；需明确轴功边界或包含发电机的电功边界。",note="现有 st.generator_power 是电功输入；不能在未定义效率/损失边界时直接当轴功。")
    add("heating","heat.drain_return.P","MPa","core","供热疏水回到机组的边界火用。",["GARD_00NDD80WP011BP01XQ01"])
    add("heating","heat.drain_return.T","℃","core","疏水焓；仅机组工质侧测点。",["GARD_00NDD80WP011BT01XQ01"])
    add("heating","heat.drain_before_pump.P","MPa","component","区分汽水换热器与疏水泵，正确计入泵功。",["GARD_00NDD70WP021BP01XQ01"])
    add("heating","heat.drain_before_pump.T","℃","component","疏水泵入口公共母管状态；单台加热器温度不能自动替代混合母管。")
    add("heating","heat.steam_header.P","MPa","component","供热母管混合后状态；不同压力蒸汽进入同一母管需节流/混合边界说明。")
    add("heating","heat.steam_header.T","℃","validation","独立校核母管混合；可由混合焓及实测 P 推导。")
    add("condenser","cond.makeup.T","℃","core","保留补水能量与火用项；补水非零时要有损失流或蓄水项解释。")
    add("condenser","cond.pre_recycle.m_dot","t/h","component","前置泵再循环；现有选取表 CAL 通道的 % 单位待核实，不直接绑定。")
    for variable,unit in (("P","MPa"),("T","℃"),("m_dot","t/h")):
        add("condenser",f"cond.gland_steam.{variable}",unit,"core","轴封加热器汽侧仍是当前图的外部输入，需要来源和状态。")
        add("condenser",f"cond.gland_drain.{variable}",unit,"core","轴封加热器疏水外部出口；汽侧质量独立守恒，不与主凝结水混合。")
    add("condenser","cond.gland_heater_in.T","℃","component","轴封加热器水侧入口焓，支撑加热器吸热与火用变化。")
    add("global","reference.T0","K","core","统一参考环境；不得用给水泵房或电气间温度替代室外参考环境。")
    add("global","reference.P0","Pa (absolute)","core","统一环境压力及表压转绝压；本次未选择到经核实的室外大气压力测点。")
    add("global","atmospheric_pressure","Pa (absolute)","core","DCS 表压转换；可与 reference.P0 同源，但定义与时间基准必须明确。")
    for item in additions:
        if item["field"].startswith("reference."):
            item["source_type"] = "declared_reference_configuration_or_verified_ambient"
            item["status"] = "declare_reference_choice_not_necessarily_a_new_sensor"
            item["note"] = "可以声明固定参考环境，也可以使用已核实室外环境；表压转绝压用的实际大气压与固定火用参考压力不是同一个概念。"

    definitions = {}
    for path in (ROOT/"gard/systems").glob("*/streams.py"):
        definitions.update(literal(assignment(path,"STREAM_DEFINITIONS")))
    existing_fields = {b["field"] for b in audit["bindings"] if not b["problems"]}
    proposed_candidates = {a["field"]:a["candidate_codes"] for a in additions if a["candidate_codes"]}
    state_contracts = []
    for stream in audit["water_flow_observability"]["matrix_column_order"]:
        import re
        choices = [name for name in aliases(stream) if name in definitions]
        spec = definitions[choices[0]] if choices else None
        proposal = {}
        if not spec:
            before = re.fullmatch(r"([12])号炉再热减温前蒸汽",stream)
            if before:
                stem = f"hrsg{before[1]}.rh_before_spray"
            else:
                stem = None
            if stem:
                proposal = {p:f"{stem}.{p}" for p in ("P","T","m_dot")}
        fields = {p:v for p,v in (spec or {}).items() if p in ("P","T","h","x","m_dot")}
        fields.update(proposal)
        phase = "single_phase_confirmed_before_using_PT"
        preparation = "from_PT when genuinely single phase; compute h/s/exergy in property layer"
        if spec and spec.get("method")=="from_Px":
            phase = "saturated_vapor" if spec.get("x")==1 else "saturated_liquid"
            preparation = "from_Px with measured drum pressure and physical outlet phase"
        if stream=="汽轮机低压缸排汽":
            phase="wet_steam_requires_independent_h_or_x"
            preparation="replace current from_PT with from_Ph or from_Px"
            fields.pop("T",None)
            fields["h"]="st.lp_out.h"
        field_records=[]
        for parameter,value in fields.items():
            record={"parameter":parameter,"field_or_constant":value}
            if isinstance(value,str):
                record["raw_binding_exists_and_metadata_consistent"]=value in existing_fields
                record["new_candidate_codes"]=proposed_candidates.get(value,[])
                record["acquisition_rule"]="existing raw input or declared reuse/derivation; missing binding is not automatically a request for a new sensor"
            field_records.append(record)
        state_contracts.append({"topology_stream":stream,"legacy_definition_candidates":choices,
                                "phase":phase,"preparation":preparation,"fields":field_records,
                                "position_note":"Current topology is authoritative. HP/IP feedwater-pump inlets use the corresponding LP drum liquid state. Other states do not cross valves, pumps or unmodelled pipe losses without an explicit rule."})

    derived = [
        {"field": "hrsg{i}.lp_economizer_in.P / lp_economizer_out.P / lp_to_drum.P", "equation": "lp_feed_after_recovery.P / lp_feed_after_recovery.P / lp_drum_pressure", "conditions": "用户已确认；HAA70WP021BP01/BT01为余热回收混合后P/T，混合前给水P/T另需定义。"},
        {"field": "hrsg{i}.lp_to_heat.P/T", "equation": "lp_main.P/T", "conditions": "用户确认简单分叉，取分叉出口状态；共同母管P/T另需定义。"},
        {"field": "st.lp_admission.m_dot / heat.lp_steam_header.m_dot", "equation": "sum(m_lp_to_st) / sum(m_lp_to_heat)", "conditions": "两炉分别分流后按目的地分别合流；分流未知时不均分，任一缺失不汇总。"},
        {"field": "hrsg{i}.hp_spray.m_dot", "equation": "m_hp_main - m_hp_feed", "conditions": "当前图稳态，无排污/旁路/漏汽；若实际损失非零必须增项。", "independent_check": "用独立喷水流量/焓混合残差校核；不能再把同一差值当独立闭合证据。"},
        {"field": "hrsg{i}.cold_reheat.m_dot", "equation": "m_hot_reheat - m_ip_fresh - m_rh_spray", "conditions": "图上无高压旁路；需确认 DCS 喷水计算值的输入独立性。"},
        {"field": "hrsg{i}.ip_pump_out.m_dot", "equation": "m_ip_feed + m_rh_spray", "conditions": "运行泵承担省煤器给水量加减温水量，备用0；任一分量缺失或无效时总量不可用。分流点派生闭合不作为独立检验，保留汽包给水与独立蒸汽测点的质量残差。"},
        {"field": "hrsg{i}.hp_pump_out.m_dot", "equation": "m_hp_feed + m_hp_spray = m_hp_main", "conditions": "稳态、无额外分流；用户确认两泵互备，原始电流识别唯一运行泵后分配全部流量，另一台为零；切泵、双运行或无法识别则不分配。"},
        {"field": "hrsg{i}.hp_spray.P/T/h", "equation": "state_of_unique_active_pump_outlet_header", "conditions": "减温水为节流前供水状态；不独立采集。"},
        {"field": "hrsg{i}.hp_before_spray.P / hp_after_spray.P / hp_to_drum.P", "equation": "P_main+configured_drop / P_main / P_hp_drum", "conditions": "用户确认的省略压降近似；省煤器组出口温度复用原高压汽包进水测温。"},
        {"field": "st.heat_extraction.m_dot", "equation": "m_heat_drain_return - sum(m_lp_to_heat)", "conditions": "供热蒸汽/疏水稳态且无其他蒸汽或补水输入。"},
        {"field": "hrsg{i}.lp_to_st.m_dot", "equation": "m_lp_main - m_lp_to_heat", "conditions": "不包含蒸汽旁路或其他去向。"},
        {"field": "hrsg{i}.lp_water.m_dot", "equation": "m_hp_pump_out + m_ip_pump_out", "conditions": "低压汽包水向高中压给水泵的两路分流。"},
        {"field": "hrsg{i}.lp_to_drum.m_dot", "equation": "m_lp_feed + m_lp_from_heat_recovery - m_lp_to_heat_recovery", "conditions": "默认水水换热器工质侧稳态无泄漏时等于m_lp_feed；保留与汽包总出口流量的独立质量残差，不用出口和反算给水来强制闭合。"},
        {"field": "hrsg{i}.lp_recirc_pump[12]_in/out.m_dot / lp_recirc_out.P/T", "equation": "10 A唯一运行泵承担m_lp_recirc，备用0；出口母管取运行泵状态", "conditions": "沿用两泵互备假设；原始时序切泵、双运行、停泵正流量或证据不足时不强行分配。"},
        {"field": "hrsg{i}.lp_recirc_pump[12]_out.T", "equation": "T_lp_economizer_out", "conditions": "再循环泵入口来自省煤器出口，出口T等于入口T；不按低压汽包饱和水替代。"},
        {"field": "heat.steam_header.m_dot", "equation": "m_st_heat_extraction + sum(m_lp_to_heat)", "conditions": "不包含已省略的中压旁路。"},
        {"field": "prepared_stream.h/s/exergy", "equation": "property_model(P,T or P,x or P,h) and (h-h0)-T0*(s-s0)", "conditions": "水物性及同一参考环境；湿蒸汽必须用额外独立状态。"},
        {"field": "valve.out.h", "equation": "h_in", "conditions": "稳态绝热节流，无轴功；还需要实际 P_out 计算 s_out。"},
        {"field": "hrsg{i}.hp_pump[12]_out.h", "equation": "h_in + (h_out_isentropic-h_in)/eta_pump", "conditions": "HP默认理想等熵；eta 为独立校准参数，不能把假设效率当实测。"},
        {"field": "hrsg{i}.ip_pump[12]_out.T/h", "equation": "T_out=T_sat(P_lp_drum); h_out=h(P_out,T_out)", "conditions": "用户确认的IP等温状态；不自动视为绝热泵功或真实效率。"},
        {"field": "hrsg{i}.ip_to_drum.P / ip_drum_steam.m_dot / rh_before_spray.P / rh_to_st.m_dot", "equation": "ip_drum_pressure / ip_fresh.m_dot / hot_reheat.P / hot_reheat.m_dot", "conditions": "用户明确确认并已落实；保留给水与独立蒸汽流量的质量残差。"},
        {"field": "hrsg{i}.ip_pump[12]_in/out.m_dot / ip_pump_out.P/T / rh_spray.P/T / rh_after_spray.P", "equation": "10 A单泵识别：运行泵m_ip_feed+m_rh_spray、备用0；母管和喷水取运行泵状态；减温后P_hot_reheat", "conditions": "用户已确认；喷水不单独节流，系统功/热量/热量火用暂不计算。"},
    ]
    boundary_terms = [
        {"fields":["hrsg{i}_hp.work","hrsg{i}_ip.work","hrsg{i}_lp.work","condenser.work","heating.work"],
         "preparation":"minus the mechanical pump power crossing the selected working-fluid boundary",
         "conditions":"Only pumps included in that boundary. IP system energy accounting is deferred by user, so IP work/heat/heat_exergy remain None. Electric power requires a matching motor boundary; water enthalpy rise is not an independent power check."},
        {"fields":["hrsg{i}_hp.heat","hrsg{i}_ip.heat","hrsg{i}_lp.heat"],
         "preparation":"for each water-side-only subsystem: H_out - H_in + W_out",
         "conditions":"This is inferred net heat into that water-side boundary, not an independent heat measurement. Do not also add it as external heat of the full gas+water HRSG."},
        {"fields":["condenser.heat","heating.heat"],
         "preparation":"negative heat export computed from complete working-fluid enthalpy balance and work",
         "conditions":"Heat input positive, work output positive. Export inferred from the same energy balance cannot independently validate that balance."},
        {"fields":["hrsg{i}.heat","hrsg{i}.heat_exergy"],
         "preparation":"only heat/heat-exergy exchanged with the external environment of the full gas+water HRSG",
         "conditions":"Exclude internal gas-to-water transfer. Zero needs an explicit external-adiabatic assumption; missing values remain unavailable."},
        {"fields":["hrsg{i}_hp.heat_exergy","hrsg{i}_ip.heat_exergy","hrsg{i}_lp.heat_exergy","condenser.heat_exergy","heating.heat_exergy"],
         "preparation":"independent integral of (1-T0/T_boundary) dQ, or a declared verified boundary model",
         "conditions":"Without an identified thermal boundary, leave unavailable and report stream-exergy change instead of destruction. Never copy a calculated destruction into a heat-exergy input to force closure."},
        {"fields":["st.work"],"preparation":"shaft work, or electrical output when the generator and corresponding losses are inside the selected boundary",
         "conditions":"Existing st.generator_power is a measured electrical quantity; raw data_io does not map it to st.work automatically."},
    ]
    excluded = [
        {"fields": ["heat.return_water.*","heat.supply_water.*","heat.recovery1_water_in.*","heat.recovery1_water_out.*","heat.recovery2_water_in.*","heat.recovery2_water_out.*"], "reason": "用户已排除热网循环水侧；不能用这些字段绑定机组锅炉水侧。"},
        {"fields": ["*.hp_bypass_*","*.ip_bypass_*","*.lp_bypass_*","*.cold_reheat_with_bypass.*","*.drum_drain.*","st.gland_leakage.*","st.ip_leakage.*"], "reason": "当前简化主路径不作为常规热力输入；仍需运行状态证明分支关闭，或补充实物流股/蓄能模型。"},
        {"fields": ["*.wall_temperature","*.bearing_temperature","*.valve_position","*.motor_current"], "reason": "不直接充当流股 P/T/m_dot；阀位、电流可用于工况筛选，功率不能仅凭电流计算。"},
        {"fields": ["*.heat","*.heat_exergy","*.exergy_destruction","*.efficiency"], "reason": "计算结果或已注明的边界模型输入，不作为伪造的原始测点；单侧热量火用需要额外边界条件。"},
    ]
    gas_extension = {
        "purpose": "只有要求 GT、完整 HRSG 或整厂火用时启用；汽水回路本身可先独立评估。",
        "systems": {
            f"gt{n}": {"measured_or_calibrated": [f"gt{n}.air_in.P/T/m_dot/composition",f"gt{n}.compressor_out.P/T",f"gt{n}.fuel.P/T/m_dot/composition",f"gt{n}.exhaust.P/T/composition",f"hrsg{n}.gas_out.P/T",f"gt{n}.power"],
                       "model_parameters": [f"gt{n}.config.compressor_bleeding_mass_fraction",f"gt{n}.config.compressor_bleeding_pressure_fraction",f"gt{n}.config.compressor_bleeding_energy_fraction",f"gt{n}.config.combustion_efficiency",f"gt{n}.total_pressure_recovery",f"gt{n}.fuel_chemical_exergy"],
                       "derived": ["m_exhaust = m_air + m_fuel; no bleed loss out of boundary", "m_gas_out = m_exhaust when no gas leakage/addition", "fuel_LHV from confirmed composition", "air composition from ambient RH/T/P", "flue composition from validated combustion model or measurement"],
                       "gaps": "当前 POINT_BINDINGS 为空。未验证标准体积流量的标准温压/湿干基、排气成分及燃料化学火用，不能输出已闭合整厂火用。"}
            for n in (1,2)
        },
        "chemical_exergy_limit": "当前 GasState.exergy 计算物理火用；燃料化学火用另加，烟气化学/混合火用尚未完整包含。",
    }
    plan = {
        "date": "2026-10-13", "scope_confirmed": "仅机组工质侧；排除热网循环水侧；以当前 Mermaid 主路径为依据；高中压给水泵入口直接采用低压汽包水状态",
        "is_applied_to_model_or_data_py": "HP/IP confirmed definitions and LP topology/preparation implemented; LP missing measurements and state definitions are listed separately; other systems remain proposals",
        "role_meaning": {"core":"循环/系统边界与主要流量锚点","component":"设备火用分配或泵组展开","validation":"冗余或不同位置的独立校核"},
        "existing_binding_role_counts": dict(Counter(x["role"] for x in inventory)),
        "existing_binding_action_counts": dict(Counter(x["action"] for x in inventory)),
        "existing_bindings": inventory, "additional_or_replacement_parameters": additions,
        "prepared_state_contracts": state_contracts,
        "derived_parameters": derived, "excluded_from_active_thermal_profile": excluded,
        "prepared_system_boundary_terms": boundary_terms,
        "gas_and_whole_plant_extension": gas_extension,
        "mass_only_flow_anchor_alternative": audit["water_flow_observability"]["one_possible_additional_flow_anchor_set"],
        "raw_binding_rule": "POINT_BINDINGS 放外部测点；授权单位覆盖保留原证据。只有明确表压才加环境压力；既有绝压默认不代表元数据已确认。推导量放 prepared row，缺失使用 None。",
    }
    (OUT/"parameter_plan.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# 参数筛选明细", "", "高压及中压已确认约定、低压拓扑及派生关系已实现；缺失数据保持None，低压全部缺项见 [lp_system_review.md](lp_system_review.md)。完整候选测点来源与推导条件见 [parameter_plan.json](parameter_plan.json)。", "",
           "## 现有绑定", "", "core 为主循环，component 为设备分配，validation 为独立校核；retain 不等于压力基准已确认。", "",
           "| 系统 | 字段 | 采集层级 | 处理 | 原始点表依据 |", "| --- | --- | --- | --- | --- |"]
    for item in inventory:
        refs="；".join(f"{r['sheet']}!{r['description_cell']} / {r['unit_cell']}" for r in item["point_metadata"])
        lines.append(f"| {item['system']} | `{item['field']}` | {item['role']} | {item['action']} | {refs} |")
    lines += ["", "## 需补充或替换的字段", "", "候选编码已核对原表的描述与单位；取点位置、基准和运行数据可用性仍需确认。没有选定编码的字段保留为缺口，不使用占位编码。", "",
              "| 系统 | 字段 | 单位 | 层级 | 候选编码 | 用途 / 条件 |", "| --- | --- | --- | --- | --- | --- |"]
    for item in additions:
        codes="、".join(f"`{c}`" for c in item["candidate_codes"]) or "未选定"
        lines.append(f"| {item['system']} | `{item['field']}` | {item['unit']} | {item['role']} | {codes} | {item['purpose']} {item['note']} |")
    (OUT/"parameter_plan.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"roles":plan["existing_binding_role_counts"],"actions":plan["existing_binding_action_counts"],"additional_parameters":len(additions)},ensure_ascii=False))


if __name__ == "__main__":
    main()
