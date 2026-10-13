"""The authorized unit override remains traceable and narrowly scoped."""
from copy import deepcopy
import importlib.util
from pathlib import Path

def test_user_override_resolves_dimension_but_retains_original_evidence():
    path = Path(__file__).resolve().parents[1]/'analysis/audit_parameter_sources.py'
    spec = importlib.util.spec_from_file_location('hp_source_audit', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    master, _ = module.load_catalog()
    bindings, _ = module.read_bindings(master)
    binding = next(b for b in bindings if b['field'] == 'hrsg2.hp_before_spray.T')
    assert binding['code'] == 'GARD_12HBK11WP021BT02XQ01'
    assert binding['problems'] == []
    assert binding['master_records'][0]['unit'] == '%'
    assert binding['unit_override']['effective_unit'] == '℃'
    assert '用户' in binding['unit_override']['authority']
    assert binding['master_records'][0]['unit_cell'] == 'E12071'
    changed = deepcopy(master)
    changed[binding['code']][0]['unit'] = 'A'  # Override must not excuse unrelated source drift.
    other, _ = module.read_bindings(changed)
    bad = next(b for b in other if b['field'] == binding['field'])
    assert 'source_unit_mismatch' in bad['problems']
    assert bad['unit_override'] is None
