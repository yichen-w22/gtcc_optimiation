"""Preserve the current workbook while planning only confirmed LP row edits."""
import hashlib
from importlib import import_module
import json
from pathlib import Path
import shutil
import sys

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from audit_lp_sources import DERIVED, INDEPENDENT_GAPS
from audit_parameter_sources import load_catalog


def main():
    source = Path(r'C:\Users\32697\Desktop\全部原始编码.xlsx')
    support = ROOT / 'outputs/20261013_lp_review/support'
    support.mkdir(parents=True, exist_ok=True)
    backup = support / 'previous_version.xlsx'
    assert not backup.exists(), 'Keep the first backup; do not overwrite it'
    shutil.copy2(source, backup)
    workbook = openpyxl.load_workbook(source, read_only=True)
    original = [list(r) for r in workbook.worksheets[0].iter_rows(min_row=2, max_col=6, values_only=True)]
    workbook.close()
    while original and all(v is None for v in original[-1]):
        original.pop()
    master, _ = load_catalog()
    rows, removed, added, updated = [], [], [], []
    existing = {r[1] for r in original}
    for index, row in enumerate(original):
        after = row.copy()
        if index == 0 or row[4] not in {'hrsg1_lp', 'hrsg2_lp'}:
            rows.append(after)
            continue
        prefix, stem = row[1].split('.', 1)
        if stem in DERIVED:
            removed.append(row)
            continue
        unit = int(prefix[-1])
        bindings = import_module(f'gard.systems.{prefix}_lp.data').POINT_BINDINGS.set_index('field')
        if stem in {'lp_main.T', 'lp_economizer_in.T'}:
            b = bindings.loc[row[1]]
            refs = master[b.code]
            assert after[2] in {None, '', b.code}, ('Existing user code conflicts', after)
            after[2], after[3] = b.code, b.expected_unit
            after[5] = '；'.join(f"点表-高安屯.xlsx：{r['sheet']}!{r['code_cell']}/{r['unit_cell']}" for r in refs)
            after[5] += '；原标注保留，按工程温度单位导入' if stem == 'lp_main.T' else '；历史文件缺失；可另用混合焓模型温度'
        elif stem == 'lp_drum_valve_in.P':
            after[5] = (after[5] or '') + '；原描述低压汽包进水压力，阀前/阀后安装位置待核对'
        if after != row:
            updated.append({'before': row, 'after': after})
        rows.append(after)
        if stem == 'lp_recirc_in.m_dot':
            for pump in (1, 2):
                field = f'{prefix}.lp_recirc_pump{pump}.current'
                if field in existing:
                    continue
                b = bindings.loc[field]
                r = master[b.code][0]
                new = [f'{unit}号炉低压省煤器再循环泵{pump}电流', field, b.code, 'A', f'{prefix}_lp',
                       f"点表-高安屯.xlsx：{r['sheet']}!{r['code_cell']}/{r['unit_cell']}；原标注保留，按电流A导入；运行默认阈值10 A"]
                rows.append(new)
                added.append(new)
    for unit in (1, 2):
        prefix = f'hrsg{unit}'
        bindings = import_module(f'gard.systems.{prefix}_lp.data').POINT_BINDINGS
        expected = {b.field for b in bindings.itertuples(index=False) if b.field.startswith(prefix + '.lp_')}
        expected.update(f'{prefix}.{stem}' for stem in INDEPENDENT_GAPS)
        assert {r[1] for r in rows if r[4] == f'{prefix}_lp'} == expected
    assert rows[0] == original[0]
    assert all(r[0] and r[1] for r in rows)
    hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (ROOT / 'docs').glob('*.xlsx')}
    payload = {'source': str(source), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'template': str(backup), 'example': original[0], 'original_rows': original, 'rows': rows,
               'removed_rows': removed, 'added_rows': added, 'updated_rows': updated, 'source_point_hashes': hashes,
               'counts': {'before': len(original), 'removed_LP_derived': len(removed), 'added_LP_currents': len(added),
                          'updated_LP_rows': len(updated), 'after': len(rows)}}
    (support / 'rows.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(payload['counts']))


if __name__ == '__main__':
    main()
