"""Generate a targeted patch from existing LP definitions and current topology."""
import difflib
import json
from pathlib import Path

from audit_parameter_sources import assignment, literal

ROOT = Path(__file__).resolve().parents[1]
REMOVED_STEMS = {
    'lp_economizer_bypass', 'lp_feed_to_mix', 'lp_feed_mixed', 'lp_drum_drain',
    'lp_bypass_in', 'lp_bypass_throttled', 'lp_bypass_spray', 'lp_bypass_out',
}


def main():
    pieces = ['*** Begin Patch']
    for unit in (1, 2):
        directory = ROOT / f'gard/systems/hrsg{unit}_lp'
        prefix = f'hrsg{unit}'
        streams = literal(assignment(directory / 'streams.py', 'STREAM_DEFINITIONS'))
        streams = {name: spec for name, spec in streams.items() if not any(
            isinstance(v, str) and v.startswith(f'{prefix}.{stem}.')
            for v in spec.values() for stem in REMOVED_STEMS)}
        rename = {
            f'{unit}号炉余热回收返回低压水': f'{unit}号炉热网水水换热器回水',
            f'{unit}号炉低压汽包调节阀前': f'{unit}号炉低压汽包给水调节阀入口',
            f'{unit}号炉低压汽包': f'{unit}号炉低压汽包水',
        }
        streams = {rename.get(name, name): spec for name, spec in streams.items()}
        for level, label in [('hp', '高压'), ('ip', '中压')]:
            other = literal(assignment(ROOT / f'gard/systems/{prefix}_{level}/streams.py', 'STREAM_DEFINITIONS'))
            name = f'{unit}号炉{label}给水泵入口母管'
            streams[name] = other[name]
        devices = literal(assignment(directory / 'devices.py', 'DEVICE_DEFINITIONS'))
        names = [f'lp{unit}_{s}' for s in (
            'heat_recovery_return', 'recycle_mix', 'economizer', 'recycle_split',
            'pump_split', 'pump1', 'pump2', 'pump_merge', 'feedwater_valve',
            'drum_evaporator', 'water_split', 'superheater', 'main_split')]
        devices[f'lp{unit}_feedwater_valve'] = devices.pop(f'lp{unit}_drum_feed_valve')
        devices = {name: devices[name] for name in names}
        for definition in devices.values():
            for key, values in definition.items():
                if key != 'type':
                    definition[key] = [rename.get(v, v) for v in values]
        devices[f'lp{unit}_recycle_mix']['inlets'][0] = f'{unit}号炉低压给水余热回收后'
        devices[f'lp{unit}_recycle_split']['outlets'][0] = f'{unit}号炉低压汽包给水调节阀入口'
        devices[f'lp{unit}_drum_evaporator']['water_inlets'] = [f'{unit}号炉低压汽包入口']
        devices[f'lp{unit}_drum_evaporator']['water_outlets'] = [f'{unit}号炉低压汽包饱和蒸汽', f'{unit}号炉低压汽包水']
        devices[f'lp{unit}_main_split']['outlets'] = [f'{unit}号炉低压蒸汽至汽轮机', f'{unit}号炉低压蒸汽至供热']
        systems = literal(assignment(directory / 'system.py', 'SYSTEM_DEFINITIONS'))
        systems[f'{prefix}_lp']['devices'] = names
        for filename, variable, definitions in [
            ('streams.py', 'STREAM_DEFINITIONS', streams),
            ('devices.py', 'DEVICE_DEFINITIONS', devices),
            ('system.py', 'SYSTEM_DEFINITIONS', systems),
        ]:
            path = directory / filename
            original = path.read_text(encoding='utf-8')
            updated = original[:original.index(variable + ' = ')] + variable + ' = ' + json.dumps(definitions, ensure_ascii=False, indent=4) + '\n'
            diff = list(difflib.unified_diff(original.splitlines(), updated.splitlines(), lineterm='', n=3))[2:]
            pieces.append('*** Update File: ' + path.as_posix())
            pieces.extend('@@' if line.startswith('@@') else line for line in diff)
    pieces.append('*** End Patch')
    print('\n'.join(pieces))


if __name__ == '__main__':
    main()
