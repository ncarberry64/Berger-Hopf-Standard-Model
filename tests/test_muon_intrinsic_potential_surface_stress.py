"""New coefficient and boundary readouts checked against literal functionals."""
from decimal import Decimal
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]


def evaluate(name, output):
    spec = spec_from_file_location(name, ROOT / 'audits' / (name + '.py'))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    module.evaluate(ROOT, output)
    return json.loads((output / 'result.json').read_bytes())


@pytest.fixture(scope='module')
def readouts(tmp_path_factory):
    folder = tmp_path_factory.mktemp('intrinsic_potential_surface_stress')
    return folder, {
        'cutoff': evaluate('bhsm_saved_c2_scalar_cutoff_jets_20261015', folder / 'cutoff'),
        'stress': evaluate('bhsm_c2_vertical_stress_contrast_20261015', folder / 'stress'),
        'outgoing': evaluate('bhsm_saved_outgoing_boundary_subspace_sensitivity_20261015', folder / 'outgoing'),
        'potential': evaluate('bhsm_intrinsic_neutral_background_potential_20261015', folder / 'potential'),
    }


def test_cutoff_source_chain_rule_against_direct_heat_and_differences(readouts):
    for channel in readouts[1]['cutoff']['channels'].values():
        for row in channel['rows']:
            assert Decimal(row['direct_heat_first_absolute_error']) < Decimal('1e-60')
            assert Decimal(row['direct_heat_second_absolute_error']) < Decimal('1e-60')
            assert Decimal(row['centered_logc_FD_relative_error']) < Decimal('2e-10')
            assert Decimal('3.9') < Decimal(row['centered_logc_FD_error_step_improvement']) < Decimal('4.1')
        assert Decimal(channel['rows'][4]['Gamma_u']) < 0
        assert Decimal(channel['rows'][4]['Gamma_u_logc']) > 0


def test_vertical_stress_against_literal_surface_value_difference(readouts):
    from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    folder, data = readouts
    with np.load(folder / 'stress/vertical_stress_contrast.npz') as saved:
        states = saved['actual_real_raw268']
        directions = saved['coordinate_directions']
        for raw, direction, row in zip(states, directions, data['stress']['records']):
            assert abs(row['partial_log_radius_direction']) < 2e-10
            assert abs(row['partial_log_lapse_direction']) < 2e-10
            assert row['partial_log_fibre_direction'] > .09

            def geometry(state):
                weights = intrinsic_m4_weight_jet(12, state[:37], state[37:74], state[74:98],
                                                  source_value=state[98], source_rate=state[99])
                return (weights['fields']['A'].value, weights['fields']['B'].value,
                        weights['R4'].value, weights['induced_lapse'].value)

            a, b, radius, lapse = geometry(raw)
            k4 = 5 / (16 * np.pi**2)
            held_gamma = k4 / (2 * np.pi**2 * (a*a + b*b)**1.5)

            def literal(step):
                trial = raw.copy()
                trial[:100] += step * direction
                a, b, radius, lapse = geometry(trial)
                return np.array([-k4*lapse*radius**3/(2*np.pi**2),
                                 -held_gamma*lapse*(a*b)**3])

            step = 1e-4
            fd = (literal(step) - literal(-step)) / (2*step)
            expected = np.array([row['directional_C2_volume_action_per_ell_star_minus4'],
                                 row['directional_matched_constant_ambient_area_per_ell_star_minus4']])
            assert np.max(abs(fd - expected)) < 2e-10
            assert abs(expected[1]) > 2e-4
            assert abs(expected[0]) < 2e-10


def test_saved_outgoing_subspace_transport_keeps_nonzero_spin_terms(readouts):
    result = readouts[1]['outgoing']
    assert result['finite_phase_E_derivative_five_point_relative_discrepancy'] < 2e-10
    gains = result['invariant_terminal_projector_tangent_gain_bounds']
    assert max(abs(value - 1) for value in gains.values()) < 1e-12
    assert min(result['midpoint_spin_commutator_norms']) > 2
    assert min(result['saved_transfer_spin_commutator_norms']) > 1e-5
    assert result['temporal_connection_norm'] > 0
    assert result['actual_terminal_annihilator_or_allowed_subspace_selected'] is False
    assert result['full_physical_outgoing_derivative_passed'] is False


def test_intrinsic_neutral_potential_against_literal_e1_fourth_difference(readouts):
    result = readouts[1]['potential']
    assert len(result['records']) == 12
    for row in result['records']:
        assert row['actual_H_norm'] > 1
        assert row['temporal_connection_antiHermitian_factor_norm'] > 0
        assert row['literal_E1_fd_checks'][-1]['fourth_relative_error'] < 2e-10
        assert row['analytic_fourth_u_remainder_upper'] < 1e-20 * abs(row['dimensionless_u_derivatives_real'][4])
        assert max(c['matrix_series_absolute_discrepancy'] for c in row['literal_eigenaction_checks']) < 1e-11
    for side in ('incoming', 'outgoing'):
        rows = [row for row in result['records'] if row['side'] == side]
        assert sum(row['matrix_dimension'] for row in rows) == 990
    assert result['temporal_connection_not_removed'] is True
    assert result['physical_lambda_H'] is None
    assert result['coupled_matching_corrections_applied'] == 0
