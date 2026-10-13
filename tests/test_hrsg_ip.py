"""Only confirmed IP rules are applied; stale topology and fields cannot reappear."""
from copy import deepcopy
from importlib import import_module
from pathlib import Path
import re

import pandas as pd
import pytest

from gard.data_io import prepare_inputs, load_inputs
from gard.systems import build_system
from gard.systems.hrsg_ip import IPPreparationConfig, prepare_ip_inputs
from src.working_fluid.steam_water import WaterSteamState


def inputs(unit):
    p=f'hrsg{unit}'
    return {f'{p}.{key}':value for key,value in {
        'lp_drum_pressure':0.5e6,'ip_pump1_out.P':4e6,'ip_pump2_out.P':4.1e6,
        'ip_pump1.current':60,'ip_pump2.current':0,
        'ip_feed.P':3.9e6,'ip_feed.T':435,'ip_feed.m_dot':12,
        'ip_to_drum.T':490,'ip_drum_pressure':3.5e6,
        'ip_fresh.P':3.2e6,'ip_fresh.T':630,'ip_fresh.m_dot':11.7,
        'cold_reheat.P':3e6,'cold_reheat.T':590,
        'reheat_mixed.P':2.9e6,'reheat_mixed.T':615,
        'rh_before_spray.T':780,'rh_spray.m_dot':2,'rh_after_spray.T':745,
        'hot_reheat.P':2.8e6,'hot_reheat.T':795,'hot_reheat.m_dot':100,
        'rh_to_st.P':2.7e6,'rh_to_st.T':790,
    }.items()}


@pytest.mark.parametrize('unit',[1,2])
def test_confirmed_single_pump_states_and_energy_deferred(unit):
    row=inputs(unit)
    original=deepcopy(row)
    system=build_system(f'hrsg{unit}_ip',row)
    p=system.preparation
    prefix=f'hrsg{unit}'
    inlet=WaterSteamState.from_Px(P=0.5e6,x=0)
    assert row==original
    assert len(system.devices)==12
    for j in (1,2):
        out=p.states[f'{unit}号炉中压给水泵{j}出口']
        assert out.T==inlet.T
        assert out.P==row[f'{prefix}.ip_pump{j}_out.P']
        assert out.h is not None
        assert out.m_dot==(14 if j==1 else 0)
        assert system.device[f'ip{unit}_pump{j}'].isentropic_efficiency is None
    assert p.states[f'{unit}号炉中压汽包入口'].P==3.5e6
    assert p.states[f'{unit}号炉中压汽包饱和蒸汽'].m_dot==11.7
    assert p.states[f'{unit}号炉中压汽包饱和蒸汽'].m_dot!=12
    assert p.states[f'{unit}号炉再热减温前蒸汽'].P==2.8e6
    assert p.states[f'{unit}号炉再热蒸汽至汽轮机'].m_dot==100
    assert p.row[f'{prefix}.ip_pump_in.m_dot']==14
    assert p.row[f'{prefix}.cold_reheat.m_dot']==pytest.approx(86.3)
    assert p.row[f'{prefix}.rh_before_spray.m_dot']==98
    assert 'drum_feed_steam_mass_mismatch' in p.issues
    assert system.mass_balance()==pytest.approx(0.3,abs=1e-8)
    assert system.energy_balance() is None and system.exergy_balance() is None
    assert system.work is None and system.heat is None and system.heat_exergy is None
    assert p.row[f'{prefix}.ip_feed_split_mass_residual']==0
    assert p.row[f'{prefix}.ip_pump_out.P']==4e6
    assert p.row[f'{prefix}.rh_spray.P']==4e6
    assert p.row[f'{prefix}.rh_spray.T']==inlet.T
    assert p.row[f'{prefix}.rh_after_spray.P']==2.8e6
    assert system.device[f'ip{unit}_feed_split'].mass_balance()==0
    assert not any(s.startswith('unconfirmed_source:') for s in p.issues)


@pytest.mark.parametrize('unit',[1,2])
def test_old_fields_and_stale_confirmed_outputs_are_discarded(unit):
    row=inputs(unit)
    prefix=f'hrsg{unit}'
    old=('ip_economizer_out','rh1_out','rh2_out','ip_drum_drain','cold_reheat_with_bypass',
         'ip_bypass_in','ip_bypass_throttled','ip_bypass_spray','ip_bypass_out',
         'ip_bypass_to_heat','ip_bypass_to_condenser','ip_pump_return')
    for stem in old:
        for key in ('P','T','m_dot'):
            row[f'{prefix}.{stem}.{key}']=999
    row.update({f'{prefix}.ip_pump1_out.T':999,f'{prefix}.ip_pump2_out.T':999,
                f'{prefix}.ip_to_drum.P':99e6,f'{prefix}.rh_before_spray.P':99e6,
                f'{prefix}.ip_drum_steam.m_dot':999,f'{prefix}.rh_to_st.m_dot':999})
    p=prepare_ip_inputs(unit,row)
    assert not any(k.startswith(f'{prefix}.{stem}.') for k in p.row for stem in old)
    assert p.row[f'{prefix}.ip_pump1_out.T']!=999
    assert p.row[f'{prefix}.ip_to_drum.P']==3.5e6
    assert p.row[f'{prefix}.rh_before_spray.P']==2.8e6
    assert p.row[f'{prefix}.ip_drum_steam.m_dot']==11.7
    assert p.row[f'{prefix}.rh_to_st.m_dot']==100
    rebuilt=prepare_ip_inputs(unit,p.row)
    assert rebuilt.row==p.row


@pytest.mark.parametrize('unit',[1,2])
def test_graph_is_exactly_current_topology(unit):
    directory=Path(__file__).resolve().parents[1]/f'gard/systems/hrsg{unit}_ip'
    edges=re.findall(r'^\s+(\w+) -->\|([^|]+)\| (\w+)$',(directory/'topology.md').read_text(encoding='utf-8'),re.M)
    module=import_module(f'gard.systems.hrsg{unit}_ip')
    definitions=module.DEVICE_DEFINITIONS
    assert module.SYSTEM_DEFINITIONS[f'hrsg{unit}_ip']['devices']==list(definitions)
    assert len(definitions)==12
    graph_streams={stream for _,stream,_ in edges}
    device_streams={stream for d in definitions.values() for key,values in d.items() if key!='type' for stream in values}
    assert graph_streams==device_streams
    for source,stream,target in edges:
        if source in definitions:
            d=definitions[source]
            assert stream in d.get('outlets',[])+d.get('water_outlets',[])
        if target in definitions:
            d=definitions[target]
            assert stream in d.get('inlets',[])+d.get('water_inlets',[])
    assert device_streams<=module.STREAM_DEFINITIONS.keys()
    assert len(module.STREAM_DEFINITIONS)==len(graph_streams)+1  # Explicit turbine-side P/T check.


@pytest.mark.parametrize('unit',[1,2])
def test_missing_inputs_do_not_reuse_stale_fields(unit):
    row=inputs(unit)
    p=f'hrsg{unit}'
    for key in ('lp_drum_pressure','ip_drum_pressure','ip_fresh.m_dot','hot_reheat.P','hot_reheat.m_dot'):
        del row[f'{p}.{key}']
    row.update({f'{p}.ip_pump1_out.T':444,f'{p}.ip_to_drum.P':3e6,
                f'{p}.ip_drum_steam.m_dot':12,f'{p}.rh_before_spray.P':3e6,
                f'{p}.rh_to_st.m_dot':100})
    prepared=prepare_ip_inputs(unit,row)
    for key in ('ip_pump1_out.T','ip_to_drum.P','ip_drum_steam.m_dot','rh_before_spray.P','rh_to_st.m_dot'):
        assert prepared.row[f'{p}.{key}'] is None


@pytest.mark.parametrize('unit',[1,2])
def test_drum_flow_point_is_shared_without_a_second_raw_measurement(unit):
    code=f'GARD_1{unit}HAH80WP011BF03XQ01'
    row=prepare_inputs(f'hrsg{unit}_ip',{code:36})
    assert row[f'hrsg{unit}.ip_fresh.m_dot']==10
    p=prepare_ip_inputs(unit,row)
    assert p.row[f'hrsg{unit}.ip_drum_steam.m_dot']==10
    bindings=import_module(f'gard.systems.hrsg{unit}_ip.data').POINT_BINDINGS
    assert not bindings.field.str.contains('ip_drum_steam').any()


@pytest.mark.parametrize('unit',[1,2])
def test_negative_cold_flow_and_energy_inputs_ignored_while_deferred(unit):
    row=inputs(unit)
    p=f'hrsg{unit}'
    row[f'{p}.hot_reheat.m_dot']=1
    system=build_system(f'{p}_ip',row)
    assert system.preparation.row[f'{p}.cold_reheat.m_dot'] is None
    assert 'negative_cold_reheat_flow' in system.preparation.issues
    row.update({f'{p}_ip.work':-100000,f'{p}_ip.heat':3000000,f'{p}_ip.heat_exergy':1000000})
    p2=prepare_ip_inputs(unit,row)
    assert p2.row[f'{p}_ip.work'] is None and p2.work_basis=='deferred_by_user'
    assert p2.row[f'{p}_ip.heat'] is None and p2.row[f'{p}_ip.heat_exergy'] is None


@pytest.mark.parametrize('unit',[1,2])
def test_old_derived_inputs_cannot_override_selection_and_zero_pump(unit):
    row=inputs(unit)
    p=f'hrsg{unit}'
    tin=WaterSteamState.from_Px(P=0.5e6,x=0).T
    row.update({f'{p}.ip_pump1_in.m_dot':999,f'{p}.ip_pump2_in.m_dot':0,
                f'{p}.ip_pump_out.P':4e6,f'{p}.ip_pump_out.T':tin,
                f'{p}.rh_spray.P':4e6,f'{p}.rh_spray.T':tin,
                f'{p}.rh_after_spray.P':2.8e6,f'{p}.hot_reheat.T':795})
    system=build_system(f'{p}_ip',row)
    assert system.mass_balance()==pytest.approx(0.3,abs=1e-8)
    assert system.preparation.row[f'{p}.ip_pump1_in.m_dot']==14
    assert system.device[f'ip{unit}_pump2'].power_input==0
    assert system.work is None and system.energy_balance() is None and system.exergy_balance() is None
    row.update({f'{p}_ip.work':-100000,f'{p}_ip.heat':3000000})
    system=build_system(f'{p}_ip',row)
    assert system.energy_balance() is None
    assert system.exergy_balance() is None


@pytest.mark.parametrize('unit',[1,2])
@pytest.mark.parametrize('currents,status,active',[
    ((60,0),'pump1',1),((0,60),'pump2',2),((60,None),'pump1_assumed_standby',1),
    ((None,60),'pump2_assumed_standby',2),((0,None),'pump2_assumed_running',2),
    ((None,0),'pump1_assumed_running',1),((60,60),'both_running',None),
    ((10,-5),'stopped',None),((None,None),'unknown',None),
])
def test_10A_exclusive_duty_selection_and_inference(unit,currents,status,active):
    row=inputs(unit)
    p=f'hrsg{unit}'
    row.update({f'{p}.ip_pump1.current':currents[0],f'{p}.ip_pump2.current':currents[1]})
    prepared=prepare_ip_inputs(unit,row)
    assert (prepared.operation_status,prepared.active_pump)==(status,active)
    for j in (1,2):
        expected=None if active is None else 14 if j==active else 0
        assert prepared.row[f'{p}.ip_pump{j}_in.m_dot']==expected
        assert prepared.row[f'{p}.ip_pump{j}_out.m_dot']==expected
    if active is not None:
        assert prepared.row[f'{p}.ip_pump_out.P']==row[f'{p}.ip_pump{active}_out.P']
    else:
        assert prepared.row[f'{p}.ip_pump_out.P'] is None


@pytest.mark.parametrize('unit',[1,2])
def test_zero_flow_and_current_magnitude_does_not_change_state(unit):
    row=inputs(unit)
    p=f'hrsg{unit}'
    before=prepare_ip_inputs(unit,row)
    row[f'{p}.ip_pump1.current']=120
    after=prepare_ip_inputs(unit,row)
    assert before.states[f'{unit}号炉中压给水泵1出口'].h==after.states[f'{unit}号炉中压给水泵1出口'].h
    row.update({f'{p}.ip_pump1.current':0,f'{p}.ip_pump2.current':0,
                f'{p}.ip_feed.m_dot':0,f'{p}.rh_spray.m_dot':0,
                f'{p}.ip_fresh.m_dot':0,f'{p}.hot_reheat.m_dot':0})
    system=build_system(f'{p}_ip',row)
    assert system.mass_balance()==0
    assert system.device[f'ip{unit}_pump1'].power_input==0
    assert system.energy_balance() is None


@pytest.mark.parametrize('unit',[1,2])
def test_user_authorized_current_and_hot_temperature_imports(unit):
    code=f'GARD_1{unit}LBB01WP001BT13XQ01'
    current=f'GARD_1{unit}LAB82QM003BC01XQ01'
    row=prepare_inputs(f'hrsg{unit}_ip',{code:500,current:70})
    assert row[f'hrsg{unit}.hot_reheat.T']==773.15
    assert row[f'hrsg{unit}.ip_pump2.current']==70
    overrides=import_module(f'gard.systems.hrsg{unit}_ip.data').UNIT_OVERRIDES
    assert overrides[f'hrsg{unit}.hot_reheat.T']['original_unit']=='%'
    if unit==1:
        assert overrides['hrsg1.ip_pump2.current']['original_unit']=='%'


@pytest.mark.parametrize('unit',[1,2])
def test_raw_history_switch_is_not_hidden_by_mean_current(tmp_path,unit):
    p=f'hrsg{unit}'
    bindings=import_module(f'gard.systems.{p}_ip.data').POINT_BINDINGS.set_index('field')
    start=pd.Timestamp('2024-06-01 08:00:00',tz='Asia/Shanghai')
    end=start+pd.Timedelta(minutes=30)
    times=pd.date_range(start,end,freq='30s',inclusive='left').as_unit('ns').asi8
    for field,values in [('ip_pump1.current',[60]*30+[0]*30),('ip_pump2.current',[0]*30+[60]*30),('ip_feed.m_dot',[36]*60)]:
        code=bindings.loc[f'{p}.{field}','code']
        pd.DataFrame({'tbname':code,'ts':times,'col0':values}).to_parquet(tmp_path/f'history+{code}.parquet')
    row=load_inputs(f'{p}_ip',tmp_path,start,end)
    assert row[f'{p}.ip_pump1.current']==30
    assert row[f'{p}.ip_pump2.current']==30
    assert row[f'{p}.ip_operation_status']=='unstable'
    assert prepare_ip_inputs(unit,row).active_pump is None


def test_threshold_validation_and_history_config_provenance():
    with pytest.raises(ValueError):
        IPPreparationConfig(current_threshold_A=-1)
    row=inputs(1)
    row.update({'hrsg1.ip_operation_status':'pump1','hrsg1.ip_operation_source':'raw_history',
                'hrsg1.ip_operation_parameters':{'current_threshold_A':10,'allow_single_current_inference':True}})
    p=prepare_ip_inputs(1,row,config=IPPreparationConfig(current_threshold_A=20))
    assert p.active_pump is None
    assert 'operation_config_changed_reload_raw_history' in p.issues


@pytest.mark.parametrize('unit',[1,2])
@pytest.mark.parametrize('missing',['ip_feed.m_dot','rh_spray.m_dot'])
def test_missing_component_does_not_use_partial_or_stale_pump_total(unit,missing):
    row=inputs(unit)
    p=f'hrsg{unit}'
    del row[f'{p}.{missing}']
    row[f'{p}.ip_pump_in.m_dot']=999
    prepared=prepare_ip_inputs(unit,row)
    assert prepared.row[f'{p}.ip_pump_in.m_dot'] is None
    assert prepared.row[f'{p}.ip_pump1_in.m_dot'] is None
    assert prepared.row[f'{p}.ip_pump2_in.m_dot']==0
    assert prepared.row[f'{p}.ip_feed_split_mass_residual'] is None


@pytest.mark.parametrize('unit',[1,2])
def test_spray_only_flow_is_still_pump_duty(unit):
    row=inputs(unit)
    p=f'hrsg{unit}'
    row.update({f'{p}.ip_feed.m_dot':0,f'{p}.ip_pump1.current':0,f'{p}.ip_pump2.current':None})
    prepared=prepare_ip_inputs(unit,row)
    assert prepared.active_pump==2
    assert prepared.row[f'{p}.ip_pump2_in.m_dot']==2
    assert prepared.row[f'{p}.ip_feed_split_mass_residual']==0


@pytest.mark.parametrize('unit',[1,2])
@pytest.mark.parametrize('spray,status',[(7.2,'pump2_assumed_running'),(None,'unknown'),(-7.2,'unknown')])
def test_raw_history_inference_uses_complete_nonnegative_pump_total(tmp_path,unit,spray,status):
    p=f'hrsg{unit}'
    bindings=import_module(f'gard.systems.{p}_ip.data').POINT_BINDINGS.set_index('field')
    start=pd.Timestamp('2024-06-01 08:00:00',tz='Asia/Shanghai')
    end=start+pd.Timedelta(minutes=30)
    times=pd.date_range(start,end,freq='30s',inclusive='left').as_unit('ns').asi8
    values={'ip_pump1.current':0,'ip_feed.m_dot':0}
    if spray is not None:
        values['rh_spray.m_dot']=spray
    for field,value in values.items():
        code=bindings.loc[f'{p}.{field}','code']
        pd.DataFrame({'tbname':code,'ts':times,'col0':[value]*len(times)}).to_parquet(tmp_path/f'history+{code}.parquet')
    row=load_inputs(f'{p}_ip',tmp_path,start,end)
    assert row[f'{p}.ip_operation_status']==status
    prepared=prepare_ip_inputs(unit,row)
    if spray is not None and spray>0:
        assert prepared.active_pump==2
        assert prepared.row[f'{p}.ip_pump2_in.m_dot']==pytest.approx(2)
        assert prepared.row[f'{p}.ip_pump1_in.m_dot']==0
    else:
        assert prepared.active_pump is None
        assert prepared.row[f'{p}.ip_pump_out.m_dot'] is None
