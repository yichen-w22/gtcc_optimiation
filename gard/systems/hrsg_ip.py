"""Confirmed IP topology and preparation; unresolved sources remain unavailable.

Pump outlet T equals inlet T by the user's current IP approximation. This
temperature constraint is not an adiabatic/isentropic pump-work model.
"""
from dataclasses import dataclass
from importlib import import_module
import math

from gard.config import reference_environment
from src.base.device_builder import DEVICE_TYPES
from src.base.stream_builder import build_stream
from src.ST_model.pump import Pump
from src.working_fluid.steam_water import WaterSteamState
from .hrsg_hp import HPSystem, classify_operation


@dataclass(frozen=True)
class IPPreparationConfig:
    current_threshold_A: float = 10.0
    allow_single_current_inference: bool = True

    def __post_init__(self):
        if not math.isfinite(self.current_threshold_A) or self.current_threshold_A<0:
            raise ValueError('current_threshold_A must be finite and nonnegative')


def _value(value, *, nonnegative=False, positive=False):
    try:
        value=float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(value) or (nonnegative and value<0) or (positive and value<=0):
        return None
    return value


@dataclass
class IPPreparation:
    row: dict
    states: dict
    raw_inputs: dict
    issues: list[str]
    operation_status: str = 'unknown'
    active_pump: int | None = None
    pump_model: str = 'outlet_temperature_equals_inlet'
    work_basis: str = 'deferred_by_user'


@dataclass
class TemperatureSpecifiedPump(Pump):
    @property
    def isentropic_efficiency(self):
        """No physical isentropic efficiency is inferred from fixed outlet T."""
        return None


@dataclass
class IPSystem(HPSystem):
    preparation: IPPreparation | None = None

    def energy_balance(self):
        return None  # System energy accounting is deferred by the user.

    def exergy_balance(self):
        return None


def prepare_ip_inputs(unit, row, ref_env=None, config=None):
    if unit not in (1,2):
        raise ValueError('unit must be 1 or 2')
    prefix=f'hrsg{unit}'
    name=f'{prefix}_ip'
    ref_env=ref_env if ref_env is not None else reference_environment()
    definitions=import_module(f'gard.systems.{name}.streams').STREAM_DEFINITIONS
    bindings=import_module(f'gard.systems.{name}.data').POINT_BINDINGS
    raw=dict(row.get(f'{prefix}.ip_source_inputs',row))
    operation_parameters=raw.get(f'{prefix}.ip_operation_parameters',{})
    config=config or IPPreparationConfig(**operation_parameters)
    # Retain only current circuit inputs. Deleted legacy fields cannot leak back
    # into preparation, and old computed outlet temperatures cannot be reused.
    allowed=set(bindings.field)
    allowed.update(v for d in definitions.values() for k,v in d.items()
                   if k in {'P','T','m_dot'} and isinstance(v,str))
    allowed.update(f'{name}.{k}' for k in ('work','heat','heat_exergy'))
    allowed.update(f'{prefix}.ip_operation_{key}' for key in ('status','source','parameters'))
    raw={k:v for k,v in raw.items() if k in allowed}
    prepared=dict(raw)
    prepared[f'{prefix}.ip_source_inputs']=dict(raw)
    issues=[]
    flow=lambda field: _value(raw.get(f'{prefix}.{field}'),nonnegative=True)
    feed=flow('ip_feed.m_dot')
    spray=flow('rh_spray.m_dot')
    fresh=flow('ip_fresh.m_dot')
    hot=flow('hot_reheat.m_dot')
    # The running pump supplies both the economizer and the spray branch.
    total=feed+spray if feed is not None and spray is not None else None
    cold=hot-fresh-spray if all(v is not None for v in (hot,fresh,spray)) else None
    if cold is not None and cold<0:
        issues.append('negative_cold_reheat_flow')
        cold=None
    mixed=cold+fresh if cold is not None and fresh is not None else None
    derived={
        'ip_pump_in.m_dot':total,'ip_pump_out.m_dot':total,
        'ip_to_drum.m_dot':feed,'ip_drum_steam.m_dot':fresh,
        'cold_reheat.m_dot':cold,'reheat_mixed.m_dot':mixed,
        'rh_before_spray.m_dot':mixed,'rh_after_spray.m_dot':hot,
        'rh_to_st.m_dot':hot,
    }
    status=raw.get(f'{prefix}.ip_operation_status') if raw.get(f'{prefix}.ip_operation_source')=='raw_history' else None
    if status is not None and operation_parameters and any(getattr(config,key)!=value for key,value in operation_parameters.items()):
        status='unknown'
        issues.append('operation_config_changed_reload_raw_history')
    if status is None:
        status=classify_operation(tuple(raw.get(f'{prefix}.ip_pump{j}.current') for j in (1,2)),total,config)
    valid={'pump1','pump2','pump1_assumed_standby','pump2_assumed_standby','pump1_assumed_running','pump2_assumed_running'}
    active=int(status[4]) if status in valid else None
    if active is None and not (status=='stopped' and total==0):
        issues.append(f'ip_pump_operation_{status}')
    if 'assumed' in status:
        issues.append('pump_selection_uses_exclusive_duty_assumption')
    prepared[f'{prefix}.ip_operation_status']=status
    prepared[f'{prefix}.ip_operation_source']=raw.get(f'{prefix}.ip_operation_source','snapshot')
    prepared[f'{prefix}.ip_active_pump']=active
    for j in (1,2):
        branch=(total if j==active else 0.0) if active is not None else 0.0 if status=='stopped' and total==0 else None
        derived[f'ip_pump{j}_in.m_dot']=branch
        derived[f'ip_pump{j}_out.m_dot']=branch
    residual=total-feed-spray if all(v is not None for v in (total,feed,spray)) else None
    prepared[f'{prefix}.ip_feed_split_mass_residual']=residual
    if residual is not None and not math.isclose(residual,0,abs_tol=1e-8,rel_tol=0):
        issues.append('ip_feed_split_mass_mismatch')
    if feed is not None and fresh is not None and not math.isclose(feed,fresh,abs_tol=1e-8,rel_tol=0):
        issues.append('drum_feed_steam_mass_mismatch')
    pressure=_value(raw.get(f'{prefix}.lp_drum_pressure'),positive=True)
    inlet=WaterSteamState.from_Px(P=pressure,x=0,ref=ref_env)
    if inlet.T is None:
        issues.append('missing_lp_drum_state')
    for j in (1,2):
        derived[f'ip_pump{j}_out.T']=inlet.T
    selected_pressure=_value(raw.get(f'{prefix}.ip_pump{active}_out.P'),positive=True) if active is not None else pressure if status=='stopped' and total==0 else None
    derived['ip_pump_out.P']=selected_pressure
    derived['ip_pump_out.T']=inlet.T if active is not None or status=='stopped' and total==0 else None
    derived['rh_spray.P']=derived['ip_pump_out.P']
    derived['rh_spray.T']=derived['ip_pump_out.T']
    derived['ip_to_drum.P']=_value(raw.get(f'{prefix}.ip_drum_pressure'),positive=True)
    derived['rh_before_spray.P']=_value(raw.get(f'{prefix}.hot_reheat.P'),positive=True)
    derived['rh_after_spray.P']=_value(raw.get(f'{prefix}.hot_reheat.P'),positive=True)
    for field,value in derived.items():
        prepared[f'{prefix}.{field}']=value
    states={stream:build_stream(stream,definitions,prepared,ref_env) for stream in definitions}
    for stream,state in states.items():
        if state.m_dot != 0 and (state.h is None or state.s is None):
            issues.append(f'missing_state:{stream}')
    for term in ('work','heat','heat_exergy'):
        prepared[f'{name}.{term}']=None
    return IPPreparation(prepared,states,raw,issues,operation_status=status,active_pump=active)


def build_ip_system(unit,row,ref_env=None,config=None):
    preparation=prepare_ip_inputs(unit,row,ref_env,config)
    prefix=f'hrsg{unit}_ip'
    definitions=import_module(f'gard.systems.{prefix}.devices').DEVICE_DEFINITIONS
    devices=[]
    for name,definition in definitions.items():
        constructor=TemperatureSpecifiedPump if definition['type']=='Pump' else DEVICE_TYPES[definition['type']]
        ports={key:[preparation.states[s] for s in names] for key,names in definition.items() if key!='type'}
        devices.append(constructor(name=name,**ports))
    return IPSystem(name=prefix,devices=devices,preparation=preparation,
                    work=preparation.row[f'{prefix}.work'],heat=preparation.row[f'{prefix}.heat'],
                    heat_exergy=preparation.row[f'{prefix}.heat_exergy'])
