"""Prepare a reviewable patch from existing IP definitions and confirmed topology."""
import difflib
import json
from pathlib import Path

from audit_parameter_sources import assignment, literal

ROOT=Path(__file__).resolve().parents[1]
REMOVED_STEMS={'ip_economizer_out','rh1_out','rh2_out','ip_drum_drain','cold_reheat_with_bypass',
               'ip_bypass_in','ip_bypass_throttled','ip_bypass_spray','ip_bypass_out',
               'ip_bypass_to_heat','ip_bypass_to_condenser','ip_pump_return'}

def main():
    pieces=['*** Begin Patch']
    for unit in (1,2):
        directory=ROOT/f'gard/systems/hrsg{unit}_ip'
        prefix=f'hrsg{unit}'
        streams=literal(assignment(directory/'streams.py','STREAM_DEFINITIONS'))
        streams={name:spec for name,spec in streams.items() if not any(
            isinstance(v,str) and v.startswith(f'{prefix}.{stem}.') for v in spec.values() for stem in REMOVED_STEMS)}
        old_header=f'{unit}号炉低压汽包中压给水泵后'
        header=f'{unit}号炉中压给水泵出口母管'
        streams={header if name==old_header else f'{unit}号炉再热减温后蒸汽' if name==f'{unit}号炉再热减温后' else name:spec for name,spec in streams.items()}
        streams[f'{unit}号炉中压汽包入口']['P']=f'{prefix}.ip_drum_pressure'
        streams[f'{unit}号炉中压汽包饱和蒸汽']['m_dot']=f'{prefix}.ip_fresh.m_dot'
        streams[f'{unit}号炉再热蒸汽至汽轮机']['m_dot']=f'{prefix}.hot_reheat.m_dot'
        streams[f'{unit}号炉再热减温前蒸汽']={'type':'WaterSteamState','method':'from_PT',
                                                   'P':f'{prefix}.hot_reheat.P','T':f'{prefix}.rh_before_spray.T',
                                                   'm_dot':f'{prefix}.rh_before_spray.m_dot'}
        devices=literal(assignment(directory/'devices.py','DEVICE_DEFINITIONS'))
        names=[f'ip{unit}_{s}' for s in ('pump_split','pump1','pump2','pump_merge','feed_split','economizer',
                                       'drum_evaporator','superheater','fresh_steam_mix','reheater_group','attemperator','reheater3')]
        retained={name:devices[name] for name in names if name in devices}
        retained[f'ip{unit}_pump_merge']['outlets']=[header]
        retained[f'ip{unit}_feed_split']['inlets']=[header]
        retained[f'ip{unit}_feed_split']['outlets']=[f'{unit}号炉中压给水',f'{unit}号炉再热减温水']
        retained[f'ip{unit}_economizer']['water_outlets']=[f'{unit}号炉中压汽包入口']
        retained[f'ip{unit}_drum_evaporator']['water_outlets']=[f'{unit}号炉中压汽包饱和蒸汽']
        retained[f'ip{unit}_fresh_steam_mix']['inlets']=[f'{unit}号炉中压新蒸汽',f'{unit}号炉冷再热蒸汽']
        retained[f'ip{unit}_reheater_group']={'type':'GasWaterHeatExchanger','water_inlets':[f'{unit}号炉再热器入口混合蒸汽'],
                                           'water_outlets':[f'{unit}号炉再热减温前蒸汽']}
        retained[f'ip{unit}_attemperator']['inlets']=[f'{unit}号炉再热减温前蒸汽',f'{unit}号炉再热减温水']
        retained[f'ip{unit}_attemperator']['outlets']=[f'{unit}号炉再热减温后蒸汽']
        retained[f'ip{unit}_reheater3']['water_inlets']=[f'{unit}号炉再热减温后蒸汽']
        devices={name:retained[name] for name in names}
        systems=literal(assignment(directory/'system.py','SYSTEM_DEFINITIONS'))
        systems[f'hrsg{unit}_ip']['devices']=names
        for filename, variable, definitions in [('streams.py','STREAM_DEFINITIONS',streams),('devices.py','DEVICE_DEFINITIONS',devices),('system.py','SYSTEM_DEFINITIONS',systems)]:
            path=directory/filename
            original=path.read_text(encoding='utf-8')
            start=original.index(variable+' = ')
            updated=original[:start]+variable+' = '+json.dumps(definitions,ensure_ascii=False,indent=4)+'\n'
            diff=list(difflib.unified_diff(original.splitlines(),updated.splitlines(),lineterm='',n=3))[2:]
            # apply_patch accepts bare @@ sections, not unified diff line numbers.
            pieces.append('*** Update File: '+path.as_posix())
            pieces.extend('@@' if line.startswith('@@') else line for line in diff)
    pieces.append('*** End Patch')
    print('\n'.join(pieces))
if __name__=='__main__':
    main()
