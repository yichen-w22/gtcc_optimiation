"""A bounded real-history integration check, without inventing missing measurements."""
import json
from importlib import import_module
from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gard.data_io import load_inputs
from gard.systems import build_system

def main():
    results = []
    for unit in (1, 2):
        name = f'hrsg{unit}_hp'
        prefix = f'hrsg{unit}'
        bindings = import_module(f'gard.systems.{name}.data').POINT_BINDINGS
        current_code = bindings.set_index('field').loc[f'{prefix}.hp_pump1.current', 'code']
        current_path = next((ROOT/'gard_raw_data').glob(f'*+{current_code}.parquet'))
        stats = pq.ParquetFile(current_path).metadata.row_group(0).column(1).statistics
        start = pd.Timestamp(stats.min, unit='ns', tz='UTC').tz_convert('Asia/Shanghai').ceil('30min')
        end = start + pd.Timedelta(minutes=30)
        row = load_inputs(name, ROOT/'gard_raw_data', start, end)
        system = build_system(name, row)
        assert row[f'{prefix}.hp_pump2.current'] is None
        results.append({'system': name, 'start': start.isoformat(), 'end': end.isoformat(),
                        'raw_si_inputs': row, 'operation_status': system.preparation.operation_status,
                        'active_pump': system.preparation.active_pump, 'issues': system.preparation.issues,
                        'modeled_fluid_power_W': system.preparation.modeled_pump_power,
                        'mass_residual_kg_s': system.mass_balance(), 'energy_residual_W': system.energy_balance(),
                        'exergy_destruction_W': system.exergy_balance(),
                        'interpretation': 'Integration check only; inferred flow/heat closure is not independent experimental validation; missing pump2 current is not zero.'})
    Path(__file__).with_name('hp_real_window_check.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps([{k:r[k] for k in ('system','start','operation_status','modeled_fluid_power_W','mass_residual_kg_s','energy_residual_W','exergy_destruction_W')} for r in results], ensure_ascii=False))
if __name__ == '__main__':
    main()
