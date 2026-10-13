"""Prepare the current LP water/steam circuit without fabricating missing data."""
from dataclasses import dataclass
from importlib import import_module
import math

from gard.config import reference_environment
from src.base.device_builder import DEVICE_TYPES
from src.base.stream_builder import build_stream
from src.working_fluid.steam_water import WaterSteamState
from .hrsg_hp import HPSystem, classify_operation
from .hrsg_ip import TemperatureSpecifiedPump, _value


@dataclass(frozen=True)
class LPPreparationConfig:
    current_threshold_A: float = 10.0
    allow_single_current_inference: bool = True
    closed_heat_recovery_loop: bool = True

    def __post_init__(self):
        if not math.isfinite(self.current_threshold_A) or self.current_threshold_A < 0:
            raise ValueError('current_threshold_A must be finite and nonnegative')


@dataclass
class LPPreparation:
    row: dict
    states: dict
    raw_inputs: dict
    issues: list[str]
    operation_status: str
    active_pump: int | None


def prepare_lp_inputs(unit, row, ref_env=None, config=None):
    if unit not in (1, 2):
        raise ValueError('unit must be 1 or 2')
    prefix, name = f'hrsg{unit}', f'hrsg{unit}_lp'
    ref_env = ref_env if ref_env is not None else reference_environment()
    definitions = import_module(f'gard.systems.{name}.streams').STREAM_DEFINITIONS
    bindings = import_module(f'gard.systems.{name}.data').POINT_BINDINGS
    raw = dict(row.get(f'{prefix}.lp_source_inputs', row))
    operation_parameters = raw.get(f'{prefix}.lp_operation_parameters', {})
    config = config or LPPreparationConfig(**operation_parameters)
    allowed = set(bindings.field)
    allowed.update(v for spec in definitions.values() for k, v in spec.items()
                   if k in {'P', 'T', 'm_dot'} and isinstance(v, str))
    allowed.update(f'{name}.{k}' for k in ('work', 'heat', 'heat_exergy'))
    allowed.update(f'{prefix}.lp_operation_{k}' for k in ('status', 'source', 'parameters'))
    raw = {k: v for k, v in raw.items() if k in allowed}
    prepared = dict(raw)
    prepared[f'{prefix}.lp_source_inputs'] = dict(raw)
    issues = []
    for field in raw:
        if field.endswith('.m_dot'):
            prepared[field] = _value(raw[field], nonnegative=True)

    def value(stem, **kwargs):
        return _value(raw.get(f'{prefix}.{stem}'), **kwargs)

    def flow(stem):
        return value(stem + '.m_dot', nonnegative=True)

    def store(stem, val):
        prepared[f'{prefix}.{stem}'] = val
        return val

    def add(*vals):
        return sum(vals) if all(v is not None for v in vals) else None

    def difference(first, *rest):
        result = first - sum(rest) if all(v is not None for v in (first, *rest)) else None
        return result if result is None or result >= 0 else None

    feed, recirc, supply = (flow(s) for s in ('lp_feed', 'lp_recirc_in', 'lp_to_heat_recovery'))
    returned = supply if config.closed_heat_recovery_loop else flow('lp_from_heat_recovery')
    store('lp_from_heat_recovery.m_dot', returned)
    after_recovery = store('lp_feed_after_recovery.m_dot', add(feed, returned))
    economizer = store('lp_economizer_in.m_dot', add(after_recovery, recirc))
    store('lp_economizer_out.m_dot', economizer)
    # In the closed return loop the unmeasured circulating flow cancels.
    drum_feed = store('lp_drum_valve_in.m_dot', feed if config.closed_heat_recovery_loop else difference(after_recovery, supply))
    store('lp_to_drum.m_dot', drum_feed)
    main, heat = flow('lp_main'), flow('lp_to_heat')
    store('lp_saturated_steam.m_dot', main)
    store('lp_to_st.m_dot', difference(main, heat))
    if main is not None and heat is not None and heat > main:
        issues.append('heating_steam_flow_above_lp_main_flow')
        store('lp_to_heat.m_dot', None)
    hp = store('hp_pump_in.m_dot', flow('hp_main'))
    ip = store('ip_pump_in.m_dot', add(flow('ip_feed'), flow('rh_spray')))
    store('lp_water.m_dot', add(hp, ip))
    if all(v is not None for v in (drum_feed, main, hp, ip)):
        residual = drum_feed - main - hp - ip
        store('lp_drum_mass_residual', residual)
        if not math.isclose(residual, 0, abs_tol=1e-8):
            issues.append('lp_drum_feed_outlet_mass_mismatch')
    else:
        store('lp_drum_mass_residual', None)

    status = raw.get(f'{prefix}.lp_operation_status') if raw.get(f'{prefix}.lp_operation_source') == 'raw_history' else None
    if status is not None and operation_parameters and any(
            getattr(config, key) != val for key, val in operation_parameters.items()):
        status = 'unknown'
        issues.append('operation_config_changed_reload_raw_history')
    if status is None:
        status = classify_operation(tuple(raw.get(f'{prefix}.lp_recirc_pump{j}.current') for j in (1, 2)), recirc, config)
    valid = {'pump1', 'pump2', 'pump1_assumed_standby', 'pump2_assumed_standby',
             'pump1_assumed_running', 'pump2_assumed_running'}
    active = int(status[4]) if status in valid else None
    zero_stopped = status == 'stopped' and recirc == 0
    if active is None and not zero_stopped:
        issues.append(f'lp_recirc_operation_{status}')
    if 'assumed' in status:
        issues.append('pump_selection_uses_exclusive_duty_assumption')
    prepared[f'{prefix}.lp_operation_status'] = status
    prepared[f'{prefix}.lp_operation_source'] = raw.get(f'{prefix}.lp_operation_source', 'snapshot')
    prepared[f'{prefix}.lp_active_pump'] = active
    store('lp_recirc_out.m_dot', recirc)

    # User-confirmed pressure approximation; overwrite stale derived inputs.
    eco_p = value('lp_feed_after_recovery.P', positive=True)
    eco_t = value('lp_economizer_out.T', positive=True)
    store('lp_economizer_in.P', eco_p)
    store('lp_economizer_out.P', eco_p)
    store('lp_to_drum.P', value('lp_drum_pressure', positive=True))
    # These are the branch states immediately after the LP steam split.
    # Downstream common-header P/T are not assigned to either boiler branch.
    for quantity in ('P', 'T'):
        store('lp_to_heat.' + quantity, value('lp_main.' + quantity, positive=True))
    for stem in ('lp_recirc_in', 'lp_to_heat_recovery'):
        store(stem + '.P', eco_p)
        store(stem + '.T', eco_t)
    store('lp_drum_valve_in.T', eco_t)
    for j in (1, 2):
        branch = (recirc if j == active else 0.0) if active is not None else 0.0 if zero_stopped else None
        for side in ('in', 'out'):
            store(f'lp_recirc_pump{j}_{side}.m_dot', branch)
            store(f'lp_recirc_pump{j}_{side}.T', eco_t)
        store(f'lp_recirc_pump{j}_in.P', eco_p)
    header_p = value(f'lp_recirc_pump{active}_out.P', positive=True) if active is not None else eco_p if zero_stopped else None
    store('lp_recirc_out.P', header_p)
    store('lp_recirc_out.T', eco_t if active is not None or zero_stopped else None)

    # Mixer outlet temperatures follow inlet enthalpy, once their independent
    # outlet pressure is available. Never copy a temperature across a heater.
    def mixed_temperature(outlet, inlet_stems):
        pressure = _value(prepared.get(f'{prefix}.{outlet}.P'), positive=True)
        states = [WaterSteamState.from_PT(
            P=prepared.get(f'{prefix}.{s}.P'), T=prepared.get(f'{prefix}.{s}.T'),
            m_dot=prepared.get(f'{prefix}.{s}.m_dot'), ref=ref_env) for s in inlet_stems]
        total = prepared.get(f'{prefix}.{outlet}.m_dot')
        if total is None or total <= 0 or any(s.m_dot is None or (s.m_dot != 0 and s.h is None) for s in states):
            temperature = None
        else:
            enthalpy = sum(s.m_dot * s.h for s in states if s.m_dot != 0) / total
            temperature = WaterSteamState.from_Ph(P=pressure, h=enthalpy, ref=ref_env).T
        store(outlet + '.T', temperature)

    # HAA70WP021 P/T now belong to the measured recovery-mixed outlet.
    # Missing measured T is not silently replaced by an enthalpy calculation.
    store('lp_feed_after_recovery.T', value('lp_feed_after_recovery.T', positive=True))
    # A directly bound economizer-inlet thermometer is independent of mixing.
    if value('lp_economizer_in.T', positive=True) is None:
        mixed_temperature('lp_economizer_in', ('lp_feed_after_recovery', 'lp_recirc_out'))
    states = {stream: build_stream(stream, definitions, prepared, ref_env) for stream in definitions}
    for stream, state in states.items():
        if state.m_dot is None:
            issues.append(f'missing_flow:{stream}')
        if state.m_dot != 0 and (state.h is None or state.s is None):
            issues.append(f'missing_state:{stream}')
    return LPPreparation(prepared, states, raw, issues, status, active)


def prepare_lp_steam_interfaces(row, ref_env=None):
    """Prepare the two distinct LP steam merges; never infer a branch split.

    The turbine merge consumes only each boiler's turbine branch. The heating
    merge consumes only each boiler's heating branch, before other heat sources.
    Common-header P/T remain independent downstream states.
    """
    prepared = dict(row)
    branches = [prepare_lp_inputs(unit, row, ref_env).row for unit in (1, 2)]
    for destination, stem in (('st.lp_admission.m_dot', 'lp_to_st.m_dot'),
                              ('heat.lp_steam_header.m_dot', 'lp_to_heat.m_dot')):
        values = [_value(p.get(f'hrsg{unit}.{stem}'), nonnegative=True)
                  for unit, p in enumerate(branches, 1)]
        prepared[destination] = sum(values) if all(v is not None for v in values) else None
    for unit, branch in enumerate(branches, 1):
        for stem in ('lp_to_st.m_dot', 'lp_to_heat.m_dot', 'lp_to_heat.P', 'lp_to_heat.T'):
            prepared[f'hrsg{unit}.{stem}'] = branch.get(f'hrsg{unit}.{stem}')
    return prepared


def build_lp_system(unit, row, ref_env=None, config=None):
    preparation = prepare_lp_inputs(unit, row, ref_env, config)
    name = f'hrsg{unit}_lp'
    definitions = import_module(f'gard.systems.{name}.devices').DEVICE_DEFINITIONS
    devices = []
    for device_name, spec in definitions.items():
        constructor = TemperatureSpecifiedPump if spec['type'] == 'Pump' else DEVICE_TYPES[spec['type']]
        ports = {k: [preparation.states[s] for s in names] for k, names in spec.items() if k != 'type'}
        devices.append(constructor(name=device_name, **ports))
    return HPSystem(name=name, devices=devices, preparation=preparation,
                    **{k: preparation.row.get(f'{name}.{k}') for k in ('work', 'heat', 'heat_exergy')})
