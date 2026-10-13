"""Read topology, source code and local point tables; write analysis evidence only.

Run from the repository root: python analysis/audit_parameter_sources.py
No model modules are imported and no source workbook/model file is modified.
"""

from __future__ import annotations

import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
EDGE = re.compile(r'^\s+(\w+) (-->|-\.->)\|([^|]+)\| (\w+)$', re.M)
NODE = re.compile(r'^\s+(\w+)\["([^\n]*)"\]|^\s+(\w+)\(\["([^\n]*)"\]\)', re.M)


def xlsx_rows(path):
    """Extract text metadata with sheet/row/cell provenance, without Excel edits."""
    with zipfile.ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared = ["".join(e.itertext()) for e in ET.fromstring(archive.read("xl/sharedStrings.xml")).findall("s:si", NS)]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        targets = {e.attrib["Id"]: e.attrib["Target"] for e in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        for sheet in workbook.findall("s:sheets/s:sheet", NS):
            target = targets[sheet.attrib[f"{{{REL}}}id"]]
            target = target.lstrip("/") if target.startswith("/") else "xl/" + target
            for row in ET.fromstring(archive.read(target)).findall("s:sheetData/s:row", NS):
                values = {}
                for cell in row.findall("s:c", NS):
                    v = cell.find("s:v", NS)
                    inline = cell.find("s:is", NS)
                    value = v.text if v is not None else "".join(inline.itertext()) if inline is not None else ""
                    if cell.attrib.get("t") == "s":
                        value = shared[int(value)]
                    values[re.sub(r"\d", "", cell.attrib["r"])] = value or ""
                yield sheet.attrib["name"], int(row.attrib["r"]), values


def literal(node):
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return literal(node.left) / literal(node.right)
    if isinstance(node, (ast.List, ast.Tuple)):
        return [literal(v) for v in node.elts]
    return ast.literal_eval(node)


def assignment(path, name):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return node.value
    raise ValueError(f"{path}: missing {name}")


def unit_kind(unit):
    value = unit.strip().lower().replace("°c", "℃")
    if value in {"pa", "kpa", "mpa", "kpa.a", "mpa.a", "pa.a", "kpa.g", "mpa.g"}:
        return "pressure"
    if value in {"℃", "c", "k"}:
        return "temperature"
    if value in {"t/h", "kg/s", "kg/h"}:
        return "mass_flow"
    if value in {"w", "kw", "mw"}:
        return "power"
    if value in {"m3/h", "m³/h", "nm3/h", "nm³/h"}:
        return "volume_flow"
    if value == "a":
        return "current"
    return "unknown"


def field_kind(field):
    if field.endswith(".current"):
        return "current"
    if field.endswith(".P") or field.endswith("_pressure"):
        return "pressure"
    if field.endswith(".T"):
        return "temperature"
    if field.endswith(".m_dot"):
        return "mass_flow"
    if "power" in field:
        return "power"
    return "unknown"


def topology():
    result = {}
    for path in sorted((ROOT / "gard/systems").glob("*/topology.md")):
        text = path.read_text(encoding="utf-8")
        nodes = {}
        for device, label, boundary, boundary_label in NODE.findall(text):
            nodes[device or boundary] = {"label": label or boundary_label, "external": bool(boundary)}
        edges = [{"source": a, "kind": k, "stream": s, "target": b} for a, k, s, b in EDGE.findall(text)]
        used = {e[k] for e in edges for k in ("source", "target")}
        undefined = sorted(used - nodes.keys())
        if undefined:
            raise ValueError(f"{path}: undefined nodes {undefined}")
        style_targets = {t for ids in re.findall(r'^\s+class ([\w,]+) \w+;', text, re.M) for t in ids.split(",")}
        result[path.parent.name] = {
            "path": path.relative_to(ROOT).as_posix(), "nodes": nodes, "edges": edges,
            "unused_nodes": sorted(nodes.keys() - used),
            "undefined_style_targets": sorted(style_targets - nodes.keys()),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    return result


def load_catalog():
    master_path = ROOT / "docs/点表-高安屯.xlsx"
    master = defaultdict(list)
    for sheet, row, cells in xlsx_rows(master_path):
        code = cells.get("B", "")
        if not code.startswith("GARD_"):
            continue
        master[code].append({
            "code": code, "plant_code": cells.get("A", ""), "point_type": cells.get("C", ""),
            "description": cells.get("D", ""), "unit": cells.get("E", ""), "note": cells.get("F", ""),
            "file": master_path.relative_to(ROOT).as_posix(), "sheet": sheet, "row": row,
            "code_cell": f"B{row}", "description_cell": f"D{row}", "unit_cell": f"E{row}",
        })
    selected = []
    for path in sorted((ROOT / "docs/点表").glob("*.xlsx")):
        for sheet, row, cells in xlsx_rows(path):
            code = cells.get("A", "")
            if code.startswith("GARD_"):
                selected.append({"code": code, "description": cells.get("C", ""), "note": cells.get("D", ""),
                                 "file": path.relative_to(ROOT).as_posix(), "sheet": sheet, "row": row,
                                 "code_cell": f"A{row}", "description_cell": f"C{row}"})
    return master, selected


def read_bindings(master):
    bindings = []
    references = defaultdict(list)
    for path in sorted((ROOT / "gard/systems").glob("*/streams.py")):
        for stream, spec in literal(assignment(path, "STREAM_DEFINITIONS")).items():
            for key, value in spec.items():
                if isinstance(value, str) and key not in {"method", "type", "note"}:
                    references[value].append({"system": path.parent.name, "stream": stream, "parameter": key})
    for path in sorted((ROOT / "gard/systems").glob("*/data.py")):
        try:
            overrides = literal(assignment(path, "UNIT_OVERRIDES"))
        except ValueError:
            overrides = {}
        expr = assignment(path, "POINT_BINDINGS")
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr == "astype":
            expr = expr.func.value
        if not isinstance(expr, ast.Call):
            raise ValueError(f"Unexpected POINT_BINDINGS expression: {path}")
        for node in expr.args[0].elts:
            field, code, expected, declared, scale, offset, basis = literal(node)
            records = master.get(code, [])
            problems = []
            if not records:
                problems.append("not_in_master_point_table")
            actual_units = {r["unit"].strip().lower().replace("°c", "℃") for r in records}
            override = overrides.get(field)
            override_applied = bool(override and override["code"] == code
                                    and override["original_unit"].lower() in actual_units
                                    and override["effective_unit"] == expected
                                    and declared == expected)
            if records and expected.strip().lower().replace("°c", "℃") not in actual_units and not override_applied:
                problems.append("source_unit_mismatch")
            if records and field_kind(field) != "unknown" and not any(unit_kind(r["unit"]) == field_kind(field) for r in records) and not override_applied:
                problems.append("field_dimension_mismatch")
            if records and not any(r["point_type"] == "AX" for r in records):
                problems.append("not_analog_measurement")
            pressure_basis_confirmed = field_kind(field) != "pressure" or any(
                r["unit"].lower().endswith((".a", ".g")) or "绝对压力" in r["description"] or "表压" in r["description"]
                for r in records)
            bindings.append({
                "system": path.parent.name, "field": field, "code": code, "expected_unit": expected,
                "declared_unit": declared, "scale": scale, "offset": offset, "pressure_basis": basis,
                "pressure_basis_confirmed_by_point_metadata": pressure_basis_confirmed,
                "source": {"file": path.relative_to(ROOT).as_posix(), "line": node.lineno},
                "master_records": records, "problems": problems,
                "unit_override": override if override_applied else None,
                "stream_references": references.get(field, []),
            })
    return bindings, references


def aliases(label):
    candidates = [label]
    transforms = [
        (r"([12])号炉高压给水泵出口母管", r"\1号炉低压汽包高压给水泵后"),
        (r"([12])号炉中压给水泵出口母管", r"\1号炉低压汽包中压给水泵后"),
        (r"([12])号炉再热减温后蒸汽", r"\1号炉再热减温后"),
        (r"([12])号炉低压汽包给水调节阀入口", r"\1号炉低压汽包调节阀前"),
        (r"([12])号炉低压汽包水", r"\1号炉低压汽包"),
        (r"([12])号炉热网水水换热器回水", r"\1号炉余热回收返回低压水"),
    ]
    for pattern, replacement in transforms:
        if re.fullmatch(pattern, label):
            candidates.append(re.sub(pattern, replacement, label))
    return candidates


def flow_observability(graphs, bindings, references):
    entries = []
    for system, graph in graphs.items():
        if system.startswith("gt") or system == "cooling":
            continue
        for edge in graph["edges"]:
            label = edge["stream"]
            if edge["kind"] != "-->" or label in {"供热系统回水", "供热系统供水", "冷却水供水", "冷却水回水"} or "热网侧" in label:
                continue
            entry = dict(edge, system=system)
            entries.append(entry)
    labels = sorted({e["stream"] for e in entries})
    rows = set()
    occurrences = defaultdict(list)
    def endpoint(entry, side):
        name = entry[side]
        if graphs[entry["system"]]["nodes"][name]["external"]:
            return None
        key = entry["system"] + ":" + name
        # A surface gland heater does not exchange mass between its two sides.
        if entry["system"] == "condenser" and name == "gland_heater":
            key += ":steam" if entry["stream"] in {"凝结水系统轴封加热器汽侧入口", "凝结水系统轴封加热器疏水出口"} else ":water"
        return key
    for entry in entries:
        source, target = endpoint(entry, "source"), endpoint(entry, "target")
        rows.update(k for k in (source, target) if k)
        occurrences[entry["stream"]].append({"system": entry["system"], "source": source, "target": target})
    rows = sorted(rows)
    rmap, cmap = {v:i for i,v in enumerate(rows)}, {v:i for i,v in enumerate(labels)}
    matrix = np.zeros((len(rows), len(labels)))
    topology_issues = []
    for label, uses in occurrences.items():
        sources = {e["source"] for e in uses if e["source"]}
        targets = {e["target"] for e in uses if e["target"]}
        if len(sources) > 1 or len(targets) > 1:
            topology_issues.append({"stream": label, "sources": sorted(sources), "targets": sorted(targets)})
        for source in sources:
            matrix[rmap[source], cmap[label]] -= 1
        for target in targets:
            matrix[rmap[target], cmap[label]] += 1
    rank = int(np.linalg.matrix_rank(matrix))
    stream_fields = defaultdict(set)
    for field, refs in references.items():
        for ref in refs:
            if ref["parameter"] == "m_dot":
                stream_fields[ref["stream"]].add(field)
    observations = []
    augmented = matrix.copy()
    for binding in bindings:
        if not binding["field"].endswith(".m_dot") or binding["problems"]:
            continue
        matches = [label for label in labels if any(binding["field"] in stream_fields[s] for s in aliases(label))]
        if not matches:
            continue
        # A single sensor is not counted as two independent measurements.
        chosen = matches[0]
        vector = np.zeros(len(labels)); vector[cmap[chosen]] = 1
        next_matrix = np.vstack((augmented, vector))
        new_rank = int(np.linalg.matrix_rank(next_matrix))
        observations.append({"field": binding["field"], "stream": chosen, "code": binding["code"],
                             "increases_rank": new_rank > int(np.linalg.matrix_rank(augmented))})
        augmented = next_matrix
    observed_rank = int(np.linalg.matrix_rank(augmented))
    def priority(label):
        if any(w in label for w in ("减温水", "冷再热", "至供热", "余热回收", "换热器回水", "再循环", "补水", "汽侧入口", "疏水出口")):
            return 0
        if re.search(r"泵[123](入口|出口)", label):
            return 1
        return 2
    additional = []
    for label in sorted(labels, key=lambda v:(priority(v), v)):
        vector = np.zeros(len(labels)); vector[cmap[label]] = 1
        next_matrix = np.vstack((augmented, vector))
        if int(np.linalg.matrix_rank(next_matrix)) > int(np.linalg.matrix_rank(augmented)):
            additional.append(label)
            augmented = next_matrix
        if int(np.linalg.matrix_rank(augmented)) == len(labels):
            break
    boundary_streams = [{"stream": label, "occurrences": uses} for label, uses in occurrences.items()
                        if not any(e["source"] for e in uses) or not any(e["target"] for e in uses)]
    return {
        "scope": "working-fluid water/steam sides only; excluded network/cooling water and all GT gas flows",
        "state_parameters_known": False,
        "method": "incidence matrix, gland heater sides separated; rank computed using NumPy SVD; no energy equations imposed",
        "mass_equations": len(rows), "stream_flow_variables": len(labels), "mass_rank": rank,
        "mass_only_degrees_of_freedom": len(labels)-rank,
        "current_mapped_flow_measurements": observations,
        "rank_with_current_unit_consistent_flow_bindings": observed_rank,
        "remaining_mass_only_degrees_of_freedom": len(labels)-observed_rank,
        "interpretation": "optimistic structural test: point location, availability and actual values are NOT validated by a unit match",
        "one_possible_additional_flow_anchor_set": additional,
        "anchor_set_note": "Not a request to install all these sensors. Independent enthalpy-mixing equations or verified pump operating constraints may replace anchors. Observed absolute flows inconsistent with mass equations still fail closure.",
        "external_working_fluid_streams": boundary_streams,
        "duplicate_endpoint_issues": topology_issues,
        "matrix_row_order": rows, "matrix_column_order": labels,
        "matrix": matrix.astype(int).tolist(),
    }


def main():
    master, selected = load_catalog()
    graphs = topology()
    bindings, references = read_bindings(master)
    flow = flow_observability(graphs, bindings, references)
    source_paths = sorted({ROOT/"docs/点表-高安屯.xlsx", *[(ROOT/g["path"]) for g in graphs.values()],
                           *list((ROOT/"gard").glob("**/*.py")), *list((ROOT/"src").glob("**/*.py")),
                           *list((ROOT/"docs/点表").glob("*.xlsx"))})
    evidence = {
        "snapshot_date": "2026-10-13", "scope": "read-only audit of current sources; audit itself modifies only analysis files",
        "binding_count": len(bindings), "bindings_with_metadata_errors": sum(bool(b["problems"]) for b in bindings),
        "problem_counts": dict(Counter(p for b in bindings for p in b["problems"])),
        "unconfirmed_pressure_basis_count": sum(not b["pressure_basis_confirmed_by_point_metadata"] for b in bindings),
        "master_point_record_count": sum(map(len,master.values())),
        "source_files": [{"file": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in source_paths],
        "bindings": bindings, "topologies": graphs, "water_flow_observability": flow,
        "selected_point_catalog": [dict(s, master_records=master.get(s["code"], [])) for s in selected],
        "code_drift": {
            "cooling_directory_present": (ROOT/"gard/systems/cooling").is_dir(),
            "registry_cooling_imports": [p.relative_to(ROOT).as_posix() for p in (ROOT/"gard/systems").glob("*registry.py") if "cooling" in p.read_text(encoding="utf-8")],
            "topology_is_not_automatically_loaded_by_build_system": True,
        },
    }
    OUT.mkdir(exist_ok=True)
    (OUT/"source_audit.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    lines = ["# 当前 data.py 测点绑定核对", "", "原始依据：`docs/点表-高安屯.xlsx`。只核对点表元数据，未读取实际运行时序；量纲一致不代表测点位置正确。", "",
             f"现有 {len(bindings)} 条绑定，{evidence['bindings_with_metadata_errors']} 条存在元数据问题；{evidence['unconfirmed_pressure_basis_count']} 个压力字段未能由点表证明绝压/表压基准。", "",
             "| 系统 | 字段 | 配置编码 | 原表描述 / 单位 | 判断 | 来源 |", "| --- | --- | --- | --- | --- | --- |"]
    for b in bindings:
        descriptions = "；".join(f"{r['description']} / {r['unit']}" for r in b["master_records"]) or "原始点表未找到"
        status = "、".join(b["problems"]) or "量纲一致，仍需核对位置"
        if b["unit_override"]:
            override=b['unit_override']
            conversion='，导入转K' if override['effective_unit']=='℃' else ''
            status = f"已解决：用户授权原单位{override['original_unit']}覆盖为{override['effective_unit']}{conversion}（原始证据保留）"
        sources = "；".join(f"{r['sheet']}!{r['description_cell']} / {r['unit_cell']}" for r in b["master_records"])
        lines.append(f"| {b['system']} | `{b['field']}` | `{b['code']}` | {descriptions.replace('|','/')} | {status} | {sources} |")
    (OUT/"data_binding_audit.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(json.dumps({k:evidence[k] for k in ("binding_count","bindings_with_metadata_errors","problem_counts","unconfirmed_pressure_basis_count")},ensure_ascii=False))
    print(json.dumps({k:flow[k] for k in ("mass_equations","stream_flow_variables","mass_rank","mass_only_degrees_of_freedom","rank_with_current_unit_consistent_flow_bindings","remaining_mass_only_degrees_of_freedom","one_possible_additional_flow_anchor_set")},ensure_ascii=False))


if __name__ == "__main__":
    main()
