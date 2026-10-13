"""Prepare both HP water circuits, keeping qualitative current separate from power.

The default pump is an ideal isentropic reference, not a measured-efficiency claim.
Single-current inference explicitly relies on the user-specified exclusive duty.
"""
from dataclasses import dataclass, replace
from importlib import import_module
import math

from gard.config import reference_environment
from src.base.system import System
from src.working_fluid.steam_water import WaterSteamState


@dataclass(frozen=True)
class HPPreparationConfig:
    current_threshold_A: float = 1.0
    pump_model: str = "isentropic"
    pump_efficiencies: tuple[float, float] = (1.0, 1.0)
    allow_single_current_inference: bool = True
    attemperator_pressure_drop: float = 0.0  # Pa, declared ignored without design data

    def __post_init__(self):
        if not math.isfinite(self.current_threshold_A) or self.current_threshold_A < 0:
            raise ValueError("current_threshold_A must be finite and nonnegative")
        if self.pump_model not in {"isentropic", "isothermal"}:
            raise ValueError("pump_model must be isentropic or isothermal")
        if len(self.pump_efficiencies) != 2 or any(not math.isfinite(v) or not 0 < v <= 1 for v in self.pump_efficiencies):
            raise ValueError("two pump_efficiencies in (0, 1] are required")
        if self.pump_model == "isothermal" and self.pump_efficiencies != (1.0, 1.0):
            raise ValueError("isentropic efficiencies cannot be combined with isothermal outlet states")
        if not math.isfinite(self.attemperator_pressure_drop) or self.attemperator_pressure_drop < 0:
            raise ValueError("attemperator_pressure_drop must be finite and nonnegative")


def _number(value):
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return value if math.isfinite(value) else None


def _positive(value):
    value = _number(value)
    return value if value is not None and value > 0 else None


def _flow(value):
    value = _number(value)
    return value if value is not None and value >= 0 else None


_UNSET = object()


def classify_operation(currents, flow, config):
    """For a steady snapshot; missing currents are not replaced by zero."""
    flags = tuple(None if _number(v) is None else float(v) > config.current_threshold_A for v in currents)
    if flags == (True, True):
        return "both_running"
    if flags == (False, False):
        return "stopped"
    if flags == (True, False):
        return "pump1"
    if flags == (False, True):
        return "pump2"
    if config.allow_single_current_inference and flags.count(None) == 1:
        known = 0 if flags[0] is not None else 1
        if flags[known]:
            return f"pump{known+1}_assumed_standby"
        if _flow(flow) is not None and flow > 0:
            return f"pump{2-known}_assumed_running"
    return "unknown"


def qualify_current_history(raw, start, end, codes, total_flow, config=None, timezone="Asia/Shanghai"):
    """Classify held current intervals before averaging, excluding pump switches.

Require jointly usable intervals for at least 80% of the window. When only one
channel exists, classify it using the declared exclusive-duty assumption.
"""
    import numpy as np
    from gard.data_io import MAX_HOLD, _window, clean_history

    config = config or HPPreparationConfig()
    start, end = _window(start, end, timezone)
    frame = clean_history(raw[raw.code.isin(codes)])
    # A dropout in a channel that exists is missing evidence, not a standby pump.
    if all((frame.code == code).any() for code in codes):
        config = replace(config, allow_single_current_inference=False)
    signals = []
    boundaries = [start.value, end.value]
    for code in codes:
        channel = frame[frame.code == code]
        times = channel.time.array.asi8
        values = channel.value.to_numpy(dtype=float)
        signals.append((times, values))
        boundaries.extend(times[(times > start.value) & (times < end.value)])
        expiry = times + MAX_HOLD.value
        boundaries.extend(expiry[(expiry > start.value) & (expiry < end.value)])
    boundaries = np.unique(boundaries)
    statuses = set()
    channel_flags = [set(), set()]
    coverage = 0
    for left, right in zip(boundaries[:-1], boundaries[1:]):
        current = []
        for times, values in signals:
            i = np.searchsorted(times, left, side="right") - 1
            value = values[i] if i >= 0 and left - times[i] < MAX_HOLD.value else None
            current.append(value)
        status = classify_operation(current, total_flow, config)
        for j, value in enumerate(current):
            if _number(value) is not None:
                channel_flags[j].add(float(value) > config.current_threshold_A)
        if status != "unknown":
            statuses.add(status)
            coverage += int(right-left)
    if len(statuses) > 1 or any(len(flags) > 1 for flags in channel_flags):
        return "unstable"
    if coverage < 0.8 * (end-start).value or not statuses:
        return "unknown"
    return next(iter(statuses))


@dataclass
class HPPreparation:
    row: dict
    states: dict
    raw_inputs: dict
    operation_status: str
    active_pump: int | None
    issues: list[str]
    pump_model: str
    modeled_pump_power: float | None
    ideal_pump_power: float | None
    work_basis: str


def prepare_hp_inputs(unit, row, ref_env=None, config=None):
    """Input row uses SI. All derived fields overwrite stale preparation fields.

    No current-to-power conversion is performed. A measured boundary work, if
    explicitly supplied, remains independent of the theoretical pump estimate.
    """
    if unit not in (1, 2):
        raise ValueError("unit must be 1 or 2")
    prefix = f"hrsg{unit}"
    system = f"{prefix}_hp"
    # Prepared rows retain their original inputs so a second build cannot treat
    # inferred flow, standby pressure or modeled boundary work as measurements.
    row = dict(row.get(f"{prefix}.hp_source_inputs", row))
    operation_parameters = row.get(f"{prefix}.hp_operation_parameters", {})
    config = config or HPPreparationConfig(**operation_parameters)
    ref_env = ref_env if ref_env is not None else reference_environment()
    raw = dict(row)
    prepared = dict(row)
    prepared[f"{prefix}.hp_source_inputs"] = dict(raw)
    issues = []
    states = {}
    lp_pressure = _positive(row.get(f"{prefix}.lp_drum_pressure"))
    m_main = _flow(row.get(f"{prefix}.hp_main.m_dot"))
    m_feed = _flow(row.get(f"{prefix}.hp_feed.m_dot"))
    m_spray = m_main-m_feed if m_main is not None and m_feed is not None else None
    if m_spray is not None and m_spray < 0:
        issues.append("main_steam_flow_below_feedwater_flow")
        m_spray = None
    if lp_pressure is None:
        issues.append("missing_lp_drum_pressure")
    if m_main is None or m_feed is None:
        issues.append("missing_boundary_mass_flow")

    currents = tuple(row.get(f"{prefix}.hp_pump{j}.current") for j in (1, 2))
    status = row.get(f"{prefix}.hp_operation_status") if row.get(f"{prefix}.hp_operation_source") == "raw_history" else None
    if status is not None and operation_parameters and any(
            getattr(config, key) != value for key, value in operation_parameters.items()):
        status = "unknown"
        issues.append("operation_config_changed_reload_raw_history")
    if status is None:
        status = classify_operation(currents, m_main, config)
    valid_statuses = {"pump1", "pump2", "pump1_assumed_standby", "pump2_assumed_standby", "pump1_assumed_running", "pump2_assumed_running"}
    active = int(status[4]) if status in valid_statuses else None
    if active is None and not (status == "stopped" and m_main == 0):
        issues.append(f"pump_operation_{status}")
    if "assumed" in status:
        issues.append("pump_selection_uses_exclusive_duty_assumption")
    prepared[f"{prefix}.hp_operation_status"] = status
    prepared[f"{prefix}.hp_operation_source"] = row.get(f"{prefix}.hp_operation_source", "snapshot")
    prepared[f"{prefix}.hp_active_pump"] = active

    def emit(name, stem, state):
        states[name] = state
        for key in ("P", "T", "h", "s", "x", "m_dot"):
            prepared[f"{prefix}.{stem}.{key}"] = getattr(state, key, None)
        return state

    def liquid(name, stem, flow):
        return emit(name, stem, WaterSteamState.from_Px(P=lp_pressure, x=0, m_dot=flow, name=name, ref=ref_env))

    def pt(name, stem, flow, pressure=_UNSET, temperature=_UNSET):
        pressure = _positive(row.get(f"{prefix}.{stem}.P")) if pressure is _UNSET else pressure
        temperature = _positive(row.get(f"{prefix}.{stem}.T")) if temperature is _UNSET else temperature
        return emit(name, stem, WaterSteamState.from_PT(P=pressure, T=temperature, m_dot=flow, name=name, ref=ref_env))

    liquid(f"{unit}号炉高压给水泵入口母管", "hp_pump_in", m_main)
    pump_outlets = []
    ideal_power = None
    modeled_power = None
    for j in (1, 2):
        flow = (m_main if j == active else 0.0) if active is not None else (0.0 if status == "stopped" and m_main == 0 else None)
        inlet = liquid(f"{unit}号炉高压给水泵{j}入口", f"hp_pump{j}_in", flow)
        prepared[f"{prefix}.hp_pump{j}.running"] = j == active if active is not None else (False if status == "stopped" else None)
        outlet_name = f"{unit}号炉高压给水泵{j}出口"
        if flow == 0:
            outlet = WaterSteamState.from_Px(P=lp_pressure, x=0, m_dot=0.0, name=outlet_name, ref=ref_env)
        elif j == active:
            pressure = _positive(row.get(f"{prefix}.hp_pump{j}_out.P"))
            if pressure is None or lp_pressure is None or pressure <= lp_pressure:
                issues.append(f"invalid_pump{j}_outlet_pressure")
                outlet = WaterSteamState(name=outlet_name, P=pressure, m_dot=flow, ref=ref_env)
            else:
                ideal = WaterSteamState.from_Ps(P=pressure, s=inlet.s, m_dot=flow, name=outlet_name, ref=ref_env)
                if config.pump_model == "isothermal":
                    outlet = WaterSteamState.from_PT(P=pressure, T=inlet.T, m_dot=flow, name=outlet_name, ref=ref_env)
                    issues.append("isothermal_pump_is_not_an_adiabatic_exergy_model")
                else:
                    h = inlet.h+(ideal.h-inlet.h)/config.pump_efficiencies[j-1] if ideal.h is not None and inlet.h is not None else None
                    outlet = ideal if config.pump_efficiencies[j-1] == 1.0 else WaterSteamState.from_Ph(P=pressure, h=h, m_dot=flow, name=outlet_name, ref=ref_env)
                if flow is not None and ideal.h is not None and inlet.h is not None:
                    ideal_power = flow*(ideal.h-inlet.h)
                if flow is not None and outlet.h is not None and inlet.h is not None:
                    modeled_power = flow*(outlet.h-inlet.h)
        else:
            outlet = WaterSteamState(name=outlet_name, m_dot=flow, ref=ref_env)
        pump_outlets.append(emit(outlet_name, f"hp_pump{j}_out", outlet))
    if (active is not None or status == "stopped") and m_main == 0:
        ideal_power = modeled_power = 0.0
    selected = pump_outlets[active-1] if active is not None else states[f"{unit}号炉高压给水泵入口母管"] if status == "stopped" and m_main == 0 else None
    header_name = f"{unit}号炉高压给水泵出口母管"
    header = WaterSteamState.from_Ph(P=getattr(selected,"P",None), h=getattr(selected,"h",None), m_dot=m_main, name=header_name, ref=ref_env)
    emit(header_name, "hp_pump_out", header)
    pt(f"{unit}号炉高压给水", "hp_feed", m_feed)
    spray_name = f"{unit}号炉高压减温水"
    emit(spray_name,"hp_spray",WaterSteamState.from_Ph(P=header.P,h=header.h,m_dot=m_spray,name=spray_name,ref=ref_env))
    # The user's measured drum-inlet temperature is the economizer-group outlet proxy.
    drum_pressure = _positive(row.get(f"{prefix}.hp_drum_pressure"))
    pt(f"{unit}号炉高压汽包入口","hp_to_drum",m_feed,pressure=drum_pressure)
    name = f"{unit}号炉高压汽包饱和蒸汽"
    emit(name,"hp_drum_steam",WaterSteamState.from_Px(P=drum_pressure,x=1,m_dot=m_feed,name=name,ref=ref_env))
    main_pressure = _positive(row.get(f"{prefix}.hp_main.P"))
    before_pressure = main_pressure+config.attemperator_pressure_drop if main_pressure is not None else None
    pt(f"{unit}号炉高压减温前蒸汽","hp_before_spray",m_feed,pressure=before_pressure)
    pt(f"{unit}号炉高压减温后蒸汽","hp_after_spray",m_main,pressure=main_pressure)
    main = pt(f"{unit}号炉高压主蒸汽","hp_main",m_main)
    pt(f"{unit}号炉高压蒸汽至汽轮机","hp_to_st",m_main)
    incoming = states[f"{unit}号炉高压给水泵入口母管"]
    work = _number(raw.get(f"{system}.work"))
    work_basis = "explicit_boundary_work" if work is not None else "isentropic_reference" if config.pump_efficiencies == (1.0,1.0) and config.pump_model == "isentropic" else "declared_pump_model"
    if work is None and config.pump_model != "isothermal" and modeled_power is not None:
        work = -modeled_power
    heat = _number(raw.get(f"{system}.heat"))
    if heat is None and work is not None and m_spray is not None and m_main is not None and main.h is not None and incoming.h is not None:
        heat = m_main*(main.h-incoming.h)+work
    prepared[f"{system}.work"] = work
    prepared[f"{system}.heat"] = heat
    prepared[f"{system}.heat_exergy"] = _number(raw.get(f"{system}.heat_exergy"))
    prepared[f"{prefix}.hp_ideal_pump_power"] = ideal_power
    prepared[f"{prefix}.hp_modeled_pump_power"] = modeled_power
    for name,state in states.items():
        if state.m_dot != 0 and (state.h is None or state.s is None):
            issues.append(f"missing_state:{name}")
    return HPPreparation(prepared,states,raw,status,active,issues,config.pump_model,modeled_power,ideal_power,work_basis)


@dataclass
class HPSystem(System):
    preparation: HPPreparation | None = None
    electrical_power_input: None = None

    def _flow_balance(self, kind):
        total = 0.0
        for device in self.devices:
            inlets=device.inlets+getattr(device,"water_inlets",[])+getattr(device,"gas_inlets",[])
            outlets=device.outlets+getattr(device,"water_outlets",[])+getattr(device,"gas_outlets",[])
            for sign,streams in ((1,inlets),(-1,outlets)):
                for state in streams:
                    flow = _flow(state.m_dot)
                    if flow is None:
                        return None
                    value = 1.0 if kind == "mass" else getattr(state,kind,None)
                    if flow != 0 and value is None:
                        return None
                    total += sign*flow*(value if value is not None else 0.0)
        return total

    def mass_balance(self):
        return self._flow_balance("mass")

    def energy_balance(self):
        flows=self._flow_balance("h")
        return flows+self.heat-self.work if flows is not None and self.heat is not None and self.work is not None else None

    def exergy_balance(self):
        flows=self._flow_balance("exergy")
        return flows+self.heat_exergy-self.work if flows is not None and self.heat_exergy is not None and self.work is not None else None


def build_hp_system(unit, row, ref_env=None, config=None):
    from src.base.device_builder import DEVICE_TYPES
    config=config or row.get(f"hrsg{unit}_hp.config")
    ref_env=ref_env if ref_env is not None else reference_environment()
    preparation=prepare_hp_inputs(unit,row,ref_env,config)
    definitions=import_module(f"gard.systems.hrsg{unit}_hp.devices").DEVICE_DEFINITIONS
    devices=[]
    for name,definition in definitions.items():
        ports={k:[preparation.states[s] for s in names] for k,names in definition.items() if k != "type"}
        devices.append(DEVICE_TYPES[definition['type']](name=name,**ports))
    prefix=f'hrsg{unit}_hp'
    return HPSystem(name=prefix,devices=devices,work=preparation.row[f'{prefix}.work'],
                    heat=preparation.row[f'{prefix}.heat'],heat_exergy=preparation.row[f'{prefix}.heat_exergy'],preparation=preparation)
