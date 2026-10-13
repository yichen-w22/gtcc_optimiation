from copy import deepcopy
from importlib import import_module
from pathlib import Path
import re

import pandas as pd
import pytest

from gard.data_io import load_inputs, prepare_inputs
from gard.systems import build_system
from gard.systems.hrsg_lp import LPPreparationConfig, prepare_lp_inputs, prepare_lp_steam_interfaces


def inputs(unit):
    return {f'hrsg{unit}.{key}': val for key, val in {
        'lp_feed.P': 0.8e6, 'lp_feed.T': 350, 'lp_feed.m_dot': 30,
        'lp_from_heat_recovery.P': 0.8e6, 'lp_from_heat_recovery.T': 380,
        'lp_to_heat_recovery.m_dot': 4, 'lp_feed_after_recovery.P': 0.8e6,
        'lp_feed_after_recovery.T': 355,
        'lp_economizer_in.P': 0.8e6, 'lp_economizer_out.P': 0.7e6,
        'lp_economizer_out.T': 410, 'lp_drum_valve_in.P': 0.7e6,
        'lp_to_drum.P': 0.5e6, 'lp_to_drum.T': 410, 'lp_drum_pressure': 0.5e6,
        'lp_recirc_in.m_dot': 6, 'lp_recirc_pump1.current': 50, 'lp_recirc_pump2.current': 0,
        'lp_recirc_pump1_out.P': 0.9e6, 'lp_recirc_pump2_out.P': 0.9e6,
        'lp_main.P': 0.48e6, 'lp_main.T': 500, 'lp_main.m_dot': 5,
        'lp_to_st.P': 0.46e6, 'lp_to_st.T': 498,
        'lp_to_heat.P': 0.48e6, 'lp_to_heat.T': 500, 'lp_to_heat.m_dot': 2,
        'hp_main.m_dot': 12, 'ip_feed.m_dot': 11, 'rh_spray.m_dot': 2,
    }.items()}


@pytest.mark.parametrize('unit', [1, 2])
def test_current_graph_and_shared_interfaces(unit):
    module = import_module(f'gard.systems.hrsg{unit}_lp')
    text = (Path(__file__).resolve().parents[1] / f'gard/systems/hrsg{unit}_lp/topology.md').read_text(encoding='utf-8')
    edges = re.findall(r'^\s+(\w+) -->\|([^|]+)\| (\w+)$', text, re.M)
    devices = module.DEVICE_DEFINITIONS
    assert len(devices) == 13
    assert module.SYSTEM_DEFINITIONS[f'hrsg{unit}_lp']['devices'] == list(devices)
    assert set(module.STREAM_DEFINITIONS) == {s for _, s, _ in edges}
    for source, stream, target in edges:
        if source in devices:
            assert stream in devices[source].get('outlets', []) + devices[source].get('water_outlets', [])
        if target in devices:
            assert stream in devices[target].get('inlets', []) + devices[target].get('water_inlets', [])
    for level, label in [('hp', '高压'), ('ip', '中压')]:
        name = f'{unit}号炉{label}给水泵入口母管'
        assert module.STREAM_DEFINITIONS[name] == import_module(f'gard.systems.hrsg{unit}_{level}').STREAM_DEFINITIONS[name]


@pytest.mark.parametrize('unit', [1, 2])
def test_mass_relations_mixing_and_existing_input_preservation(unit):
    row = inputs(unit)
    original = deepcopy(row)
    system = build_system(f'hrsg{unit}_lp', row)
    p = system.preparation
    prefix = f'hrsg{unit}'
    assert row == original
    expected = {'lp_feed_after_recovery.m_dot': 34, 'lp_economizer_in.m_dot': 40,
                'lp_economizer_out.m_dot': 40, 'lp_to_drum.m_dot': 30,
                'hp_pump_in.m_dot': 12, 'ip_pump_in.m_dot': 13, 'lp_water.m_dot': 25,
                'lp_saturated_steam.m_dot': 5, 'lp_to_st.m_dot': 3, 'lp_drum_mass_residual': 0}
    for stem, val in expected.items():
        assert p.row[f'{prefix}.{stem}'] == val
    assert p.row[f'{prefix}.lp_feed_after_recovery.T'] == 355
    assert p.row[f'{prefix}.lp_feed_after_recovery.T'] < p.row[f'{prefix}.lp_economizer_in.T'] < 410
    assert system.mass_balance() == pytest.approx(0, abs=1e-8)
    assert system.energy_balance() is None and system.exergy_balance() is None
    assert system.device[f'lp{unit}_pump2'].power_input == 0
    assert system.device[f'lp{unit}_pump1'].isentropic_efficiency is None
    assert prepare_lp_inputs(unit, p.row).row == p.row
    for d in system.devices:
        assert d.mass_balance() == pytest.approx(0, abs=1e-8)


@pytest.mark.parametrize('unit', [1, 2])
@pytest.mark.parametrize('currents,active', [((50, 0), 1), ((0, 50), 2), ((50, None), 1),
                                           ((None, 0), 1), ((50, 50), None), ((None, None), None), ((0, 0), None)])
def test_exclusive_pump_duty_and_no_forced_allocation(unit, currents, active):
    row = inputs(unit)
    prefix = f'hrsg{unit}'
    row.update({f'{prefix}.lp_recirc_pump{j}.current': currents[j - 1] for j in (1, 2)})
    p = prepare_lp_inputs(unit, row)
    assert p.active_pump == active
    for j in (1, 2):
        assert p.row[f'{prefix}.lp_recirc_pump{j}_in.m_dot'] == (None if active is None else 6 if active == j else 0)
        assert p.row[f'{prefix}.lp_recirc_pump{j}_out.T'] == 410


@pytest.mark.parametrize('unit', [1, 2])
def test_missing_and_stale_fields_are_not_reused(unit):
    row = inputs(unit)
    prefix = f'hrsg{unit}'
    for stem in ('rh_spray.m_dot', 'lp_economizer_out.T', 'lp_feed_after_recovery.P', 'lp_recirc_pump1.current', 'lp_recirc_pump2.current'):
        del row[f'{prefix}.{stem}']
    row.update({f'{prefix}.ip_pump_in.m_dot': 999, f'{prefix}.lp_water.m_dot': 999,
                f'{prefix}.lp_recirc_pump1_out.T': 999, f'{prefix}.lp_recirc_pump1_in.m_dot': 999,
                f'{prefix}.lp_recirc_in.P': 2e6, f'{prefix}.lp_bypass_in.m_dot': 999})
    p = prepare_lp_inputs(unit, row)
    for stem in ('ip_pump_in.m_dot', 'lp_water.m_dot', 'lp_recirc_pump1_out.T', 'lp_recirc_pump1_in.m_dot', 'lp_recirc_in.P'):
        assert p.row[f'{prefix}.{stem}'] is None
    assert f'{prefix}.lp_bypass_in.m_dot' not in p.row
    assert build_system(f'{prefix}_lp', row).mass_balance() is None


@pytest.mark.parametrize('unit', [1, 2])
def test_bad_flows_zero_flow_and_independent_drum_mismatch(unit):
    row = inputs(unit)
    prefix = f'hrsg{unit}'
    row[f'{prefix}.lp_feed.m_dot'] = 31
    system = build_system(f'{prefix}_lp', row)
    assert system.mass_balance() == pytest.approx(1)
    assert 'lp_drum_feed_outlet_mass_mismatch' in system.preparation.issues
    row[f'{prefix}.lp_to_heat.m_dot'] = 8
    assert prepare_lp_inputs(unit, row).row[f'{prefix}.lp_to_st.m_dot'] is None
    row[f'{prefix}.lp_to_heat_recovery.m_dot'] = -4
    assert prepare_lp_inputs(unit, row).row[f'{prefix}.lp_economizer_out.m_dot'] is None
    row = inputs(unit)
    for field in row:
        if field.endswith('.m_dot') or field.endswith('.current'):
            row[field] = 0
    system = build_system(f'{prefix}_lp', row)
    assert system.mass_balance() == 0
    assert system.device[f'lp{unit}_pump1'].power_input == 0


@pytest.mark.parametrize('unit', [1, 2])
def test_lp_sources_import_and_cross_level_codes_match(unit):
    bindings = import_module(f'gard.systems.hrsg{unit}_lp.data').POINT_BINDINGS
    for level, fields in [('hp', ['hp_main.m_dot']), ('ip', ['ip_feed.m_dot', 'rh_spray.m_dot'])]:
        other = import_module(f'gard.systems.hrsg{unit}_{level}.data').POINT_BINDINGS.set_index('field')
        for stem in fields:
            field = f'hrsg{unit}.{stem}'
            assert bindings.set_index('field').loc[field].to_dict() == other.loc[field].to_dict()
    row = prepare_inputs(f'hrsg{unit}_lp', {f'GARD_1{unit}LBA01WP001BT03XQ01': 220,
                                          f'GARD_1{unit}HAA85GP001BC01XQ01': 50,
                                          f'GARD_1{unit}HAA85WP001BF01XQ01': 21.6})
    assert row[f'hrsg{unit}.lp_main.T'] == 493.15
    assert row[f'hrsg{unit}.lp_recirc_pump1.current'] == 50
    assert row[f'hrsg{unit}.lp_recirc_in.m_dot'] == pytest.approx(6)


@pytest.mark.parametrize('unit', [1, 2])
def test_raw_current_switch_is_detected_before_mean(tmp_path, unit):
    prefix = f'hrsg{unit}'
    bindings = import_module(f'gard.systems.{prefix}_lp.data').POINT_BINDINGS.set_index('field')
    start = pd.Timestamp('2024-06-01 08:00:00', tz='Asia/Shanghai')
    end = start + pd.Timedelta(minutes=30)
    times = pd.date_range(start, end, freq='30s', inclusive='left').as_unit('ns').asi8
    for stem, vals in [('lp_recirc_pump1.current', [50] * 30 + [0] * 30),
                       ('lp_recirc_pump2.current', [0] * 30 + [50] * 30), ('lp_recirc_in.m_dot', [21.6] * 60)]:
        code = bindings.loc[f'{prefix}.{stem}', 'code']
        pd.DataFrame({'tbname': code, 'ts': times, 'col0': vals}).to_parquet(tmp_path / f'history+{code}.parquet')
    row = load_inputs(f'{prefix}_lp', tmp_path, start, end)
    assert row[f'{prefix}.lp_operation_status'] == 'unstable'
    assert prepare_lp_inputs(unit, row).active_pump is None


def test_config_and_open_recovery_loop_do_not_force_equal_return_flow():
    with pytest.raises(ValueError):
        LPPreparationConfig(current_threshold_A=-1)
    row = inputs(1)
    row['hrsg1.lp_from_heat_recovery.m_dot'] = 3
    p = prepare_lp_inputs(1, row, config=LPPreparationConfig(closed_heat_recovery_loop=False))
    assert p.row['hrsg1.lp_to_drum.m_dot'] == 29
    assert build_system('hrsg1_lp', row, config=LPPreparationConfig(closed_heat_recovery_loop=False)).mass_balance() == pytest.approx(-1)


@pytest.mark.parametrize('unit', [1, 2])
def test_confirmed_states_and_missing_recovery_circulation(unit):
    row = inputs(unit)
    prefix = f'hrsg{unit}'
    for stem in ('lp_to_heat_recovery.m_dot', 'lp_feed.P', 'lp_feed.T'):
        del row[f'{prefix}.{stem}']
    row.update({f'{prefix}.lp_to_drum.P': 999e6, f'{prefix}.lp_to_heat.T': 999})
    p = prepare_lp_inputs(unit, row).row
    for stem in ('lp_economizer_in.P', 'lp_economizer_out.P', 'lp_recirc_in.P'):
        assert p[f'{prefix}.{stem}'] == 0.8e6
    assert p[f'{prefix}.lp_to_drum.P'] == 0.5e6
    assert p[f'{prefix}.lp_feed_after_recovery.T'] == 355
    assert p[f'{prefix}.lp_to_drum.m_dot'] == 30
    assert p[f'{prefix}.lp_economizer_in.m_dot'] is None
    assert p[f'{prefix}.lp_from_heat_recovery.m_dot'] is None
    assert p[f'{prefix}.lp_to_heat.P'] == row[f'{prefix}.lp_main.P']
    assert p[f'{prefix}.lp_to_heat.T'] == row[f'{prefix}.lp_main.T']
    assert p.get(f'{prefix}.lp_feed.P') is None and p.get(f'{prefix}.lp_feed.T') is None
    del row[f'{prefix}.lp_feed_after_recovery.T']
    assert prepare_lp_inputs(unit, row).row[f'{prefix}.lp_feed_after_recovery.T'] is None


@pytest.mark.parametrize('unit', [1, 2])
def test_confirmed_point_import_locations(unit):
    row = prepare_inputs(f'hrsg{unit}_lp', {
        f'GARD_1{unit}HAA11WP011BT02XQ01': 110,
        f'GARD_1{unit}HAA13QN101BP02XQ01': 0.9,
        f'GARD_1{unit}HAA70WP021BT01XQ01': 80,
        f'GARD_1{unit}HAA70WP021BP01XQ01': 0.8,
    })
    for stem, expected in {'lp_from_heat_recovery.T': 383.15, 'lp_from_heat_recovery.P': 0.9e6,
                           'lp_feed_after_recovery.T': 353.15, 'lp_feed_after_recovery.P': 0.8e6}.items():
        assert row[f'hrsg{unit}.{stem}'] == pytest.approx(expected)
    assert f'hrsg{unit}.lp_feed.P' not in row and f'hrsg{unit}.lp_feed.T' not in row


def test_two_separate_steam_merges_do_not_assume_equal_shares():
    row = {**inputs(1), **inputs(2), 'hrsg2.lp_main.m_dot': 9, 'hrsg2.lp_to_heat.m_dot': 3,
           'st.lp_admission.m_dot': 999, 'heat.lp_steam_header.m_dot': 999,
           'heat.lp_steam_header.P': 0.4e6, 'heat.lp_steam_header.T': 490}
    original = deepcopy(row)
    p = prepare_lp_steam_interfaces(row)
    assert row == original
    assert p['hrsg1.lp_to_st.m_dot'] == 3 and p['hrsg2.lp_to_st.m_dot'] == 6
    assert p['st.lp_admission.m_dot'] == 9
    assert p['heat.lp_steam_header.m_dot'] == 5
    assert p['heat.lp_steam_header.P'] == 0.4e6 and p['heat.lp_steam_header.T'] == 490
    assert prepare_lp_steam_interfaces(p) == p


@pytest.mark.parametrize('heat', [None, -1, 10])
def test_invalid_or_missing_branch_prevents_merge_allocation(heat):
    row = {**inputs(1), **inputs(2), 'hrsg2.lp_to_heat.m_dot': heat}
    p = prepare_lp_steam_interfaces(row)
    assert p['hrsg2.lp_to_st.m_dot'] is None
    assert p['hrsg2.lp_to_heat.m_dot'] is None
    assert p['st.lp_admission.m_dot'] is None
    assert p['heat.lp_steam_header.m_dot'] is None


def test_steam_merge_junctions_match_confirmed_topology():
    from gard.systems.heating.devices import DEVICE_DEFINITIONS as heating
    from gard.systems.st.devices import DEVICE_DEFINITIONS as st
    from src.base.device_builder import build_device
    from gard.config import reference_environment
    definitions = {}
    for system in ('hrsg1_lp', 'hrsg2_lp', 'st', 'heating'):
        definitions.update(import_module(f'gard.systems.{system}.streams').STREAM_DEFINITIONS)
    p = prepare_lp_steam_interfaces({**inputs(1), **inputs(2),
                                    'st.lp_admission.P': 0.45e6, 'st.lp_admission.T': 498,
                                    'heat.lp_steam_header.P': 0.47e6, 'heat.lp_steam_header.T': 500})
    assert heating['heating_lp_steam_merge']['inlets'] == ['1号炉低压蒸汽至供热', '2号炉低压蒸汽至供热']
    assert heating['heating_steam_merge']['inlets'] == ['汽轮机供热抽汽', '热网低压补汽母管']
    assert st['lp_admission_merge']['inlets'] == ['1号炉低压蒸汽至汽轮机', '2号炉低压蒸汽至汽轮机']
    # Build only the two authorized junctions; the old plant registry still
    # references user-deleted cooling and is outside this LP change.
    for name, devices in [('heating_lp_steam_merge', heating), ('lp_admission_merge', st)]:
        assert build_device(name, devices, definitions, p, reference_environment()).mass_balance() == pytest.approx(0)
