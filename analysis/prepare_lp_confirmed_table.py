"""Plan a narrow workbook patch for the latest confirmed LP connections."""
import hashlib
from importlib import import_module
import json
from pathlib import Path
import shutil
import sys

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from audit_lp_sources import DERIVED, INDEPENDENT_GAPS, INTERFACE_GAPS
from audit_parameter_sources import load_catalog


def main():
    source = Path(r'C:\Users\32697\Desktop\全部原始编码.xlsx')
    support = ROOT / 'outputs/20261013_lp_confirmed/support'
    support.mkdir(parents=True, exist_ok=True)
    backup = support / 'previous_version.xlsx'
    assert not backup.exists(), 'Never overwrite the pre-delivery backup'
    shutil.copy2(source, backup)
    workbook = openpyxl.load_workbook(source, read_only=True)
    original = [list(r) for r in workbook.worksheets[0].iter_rows(min_row=2, max_col=6, values_only=True)]
    workbook.close()
    while original and not any(v is not None for v in original[-1]):
        original.pop()
    master, _ = load_catalog()
    rows, removed, added, updated = [], [], [], []
    existing = {r[1] for r in original}

    def bound_row(prefix, stem, meaning):
        module = import_module(f'gard.systems.{prefix}_lp.data')
        b = module.POINT_BINDINGS.set_index('field').loc[f'{prefix}.{stem}']
        note = '；'.join(f"点表-高安屯.xlsx：{r['sheet']}!{r['code_cell']}/{r['unit_cell']}" for r in master[b.code])
        note += '；用户确认工质侧返回口' if stem.startswith('lp_from_heat_recovery.') else '；用户确认余热回收返回混合后取点'
        if stem.startswith('lp_from_heat_recovery.'):
            note += '；历史文件待补'
        override = module.UNIT_OVERRIDES.get(f'{prefix}.{stem}')
        if override:
            note += f"；原单位{override['original_unit']}保留为证据，按用户约定{override['effective_unit']}导入"
        return [meaning, f'{prefix}.{stem}', b.code, b.expected_unit, f'{prefix}_lp', note]

    for i, row in enumerate(original):
        after = row.copy()
        if i == 0 or row[4] not in {'hrsg1_lp', 'hrsg2_lp'}:
            rows.append(after)
            continue
        prefix, stem = row[1].split('.', 1)
        if stem in DERIVED:
            removed.append(row)
            continue
        if stem in {'lp_feed.P', 'lp_feed.T'}:
            suffix = stem[-1]
            expected_code = f'GARD_1{prefix[-1]}HAA70WP021B{suffix}01XQ01'
            assert row[2] == expected_code, ('Unexpected existing user selection', row)
            meaning, note = INDEPENDENT_GAPS[stem]
            after = [f'{prefix[-1]}号炉{meaning}', row[1], None, None, row[4], note + '；原来源：' + (row[5] or '')]
        elif stem.startswith(('lp_from_heat_recovery.', 'lp_feed_after_recovery.')):
            after = bound_row(prefix, stem, row[0])
            assert row[2] in {None, '', after[2]}, ('Unexpected existing user selection', row)
        elif stem in {'lp_to_heat_recovery.m_dot', 'lp_to_heat.m_dot'}:
            after[5] = INDEPENDENT_GAPS[stem][1]
        if after != row:
            updated.append({'before': row, 'after': after})
        rows.append(after)
        if stem == 'lp_feed_after_recovery.P':
            field = f'{prefix}.lp_feed_after_recovery.T'
            if field not in existing:
                new = bound_row(prefix, 'lp_feed_after_recovery.T', f'{prefix[-1]}号炉低压给水余热回收后温度')
                rows.append(new)
                added.append(new)
    for field, (meaning, note) in INTERFACE_GAPS.items():
        if field not in existing:
            new = [meaning, field, None, None, 'heating', note]
            insert_at = next(i for i, r in enumerate(rows) if r[4] == 'heating')
            rows.insert(insert_at, new)
            added.append(new)
    for unit in (1, 2):
        prefix = f'hrsg{unit}'
        bindings = import_module(f'gard.systems.{prefix}_lp.data').POINT_BINDINGS
        expected = {b.field for b in bindings.itertuples(index=False) if b.field.startswith(prefix + '.lp_')}
        expected.update(f'{prefix}.{stem}' for stem in INDEPENDENT_GAPS)
        assert {r[1] for r in rows if r[4] == f'{prefix}_lp'} == expected
    assert rows[0] == original[0]
    assert all(r[0] and r[1] for r in rows)
    assert len({r[1] for r in rows}) == len(rows)
    hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (ROOT / 'docs').rglob('*.xlsx')}
    payload = {'source': str(source), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'template': str(backup), 'example': original[0], 'original_rows': original, 'rows': rows,
               'removed_rows': removed, 'added_rows': added, 'updated_rows': updated,
               'source_point_hashes': hashes, 'authorized_new_interface_fields': list(INTERFACE_GAPS),
               'counts': {'before': len(original), 'removed_LP_derived': len(removed),
                          'added_LP_mixed_T': 2, 'added_shared_header_states': 2,
                          'updated_LP_rows': len(updated), 'after': len(rows)}}
    (support / 'rows.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    shutil.copy2(ROOT / 'outputs/20261013_lp_review/support/edit_excel.mjs', support / 'edit_excel.mjs')
    print(json.dumps(payload['counts']))


if __name__ == '__main__':
    main()
