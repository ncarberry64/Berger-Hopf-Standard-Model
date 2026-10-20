"""Necessary prepared Gauss moments; no control is a physical packet."""
from pathlib import Path
import json
import numpy as np
import pytest

from bhsm.interface.muon_prepared_weak_gauss_dressing import (
    prepared_charge_moments, charge_test_twojet,
    physical_unit_moment_twojet, required_dressing_contractions,
)
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def prepared():
    preparation = json.loads((ROOT/'artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json').read_text())
    path = ROOT/'artifacts/muon_collider_common_state_constraint_family_20261014/retained_preparation/actual_frozen_family_and_exact_pair_spin_CAR_preparation.npz'
    with np.load(path, allow_pickle=False) as archive:
        rho = archive['pair_Fock_density16'].copy()
    return preparation, rho, prepared_charge_moments(preparation, rho)


def test_exact_pair_and_spatial_complement_are_required_for_second_moment(prepared):
    p, rho, result = prepared
    np.testing.assert_array_equal(result['pair_number_moments'], np.ones(5))
    assert result['required_physical_charge_mean'] == 0.
    assert result['exact_pair_charge_variance'] == 0.
    assert result['required_physical_dipole_mean_fm'] == 2000.
    assert result['reference_envelope_variance_fm_squared'] == 20000.
    assert result['reference_envelope_second_moment_fm_squared'] == 4020000.
    assert result['spatial_compression_defect_fm_squared'] == 20000.
    assert result['Gaussian_mean_identity_error'] < 1e-12
    assert result['Gaussian_second_identity_error'] < 3e-9
    assert not result['reference_second_moment_is_a_dressed_physical_result']
    assert result['achieved_physical_sections_or_moments'] is None
    # Same one-body mean as the exact pair is insufficient for its algebra.
    with pytest.raises(ValueError, match='exact one-electron'):
        prepared_charge_moments(p, np.eye(16)/16)


def test_gauss_determines_only_the_combined_dressing_contraction(prepared):
    result = required_dressing_contractions(prepared[2])
    assert result['required_K1_fm'] == 2000.
    assert 'Flux[lambda]-Bulk[D_i lambda]' in result['equation']
    assert result['reference_number_position_variance_fm_squared'] == 20000.
    assert result['physical_Var_D'] is None
    assert result['physical_Var_F'] is None
    assert result['achieved_J_pair_lambda1'] is None
    assert result['algebraic_target_substitution_Gauss_row_fm'] == 0.
    assert result['achieved_complete_Gauss_residual'] is None
    assert not result['quantum_dressing_or_reference_correlation_evaluated']
    assert not result['local_parent_incoming40_or_packet_selected']


def _control_theta():
    # CONTROL_ONLY: general H, connection and pairing-preserving chart.
    theta = np.r_[.9, .73, np.arange(16)*.03-.2, [.3, .8, -.2, .4]]
    gradient = np.zeros((22, 151));gradient[:, :22] = np.eye(22)
    hessian = np.zeros((22, 151, 151))
    return theta, gradient, hessian


def test_covariant_test_keeps_connection_even_when_H_is_angular_constant():
    t, g, h = _control_theta()
    result = charge_test_twojet(t, g, h)
    assert result['charge_reconstruction_error'] < 4e-16
    assert result['At_lapse_cancellation_error'] < 1e-16
    assert result['charge_mass_commutator_error'] < 1e-17
    assert result['spatial_covariant_derivative_nonzero']
    assert np.max(abs(result['proper_spatial_covariant_charge_derivative']['value'])) > .1
    # Gauge motion and normalized H motion have a nonzero mixed contact.
    mixed = result['proper_spatial_covariant_charge_derivative']['hessian'][:, 6:18, 18:22]
    assert np.max(abs(mixed)) > .1
    assert not result['ambient_lapse_substituted']
    assert not result['physical_collider_coordinate_or_dressing_selected']


def test_exact_twojet_matches_independent_variations_and_gauge_matrix_commutator():
    t, g, h = _control_theta()
    result = charge_test_twojet(t, g, h)
    v = np.linspace(-.3, .2, 22);step = 2e-6
    plus, minus = (charge_test_twojet(t+sign*step*v, g, h) for sign in (1, -1))
    direction = np.r_[v, np.zeros(129)]
    for key in ('charge_test', 'proper_spatial_covariant_charge_derivative',
                'proper_stationary_temporal_covariant_charge_derivative'):
        predicted = result[key]['gradient']@direction
        literal = (plus[key]['value']-minus[key]['value'])/(2*step)
        np.testing.assert_allclose(literal, predicted, rtol=3e-9, atol=5e-10)
        hessian_product = np.einsum('aij,j->ai', result[key]['hessian'], direction)
        gradient_change = (plus[key]['gradient']-minus[key]['gradient'])/(2*step)
        np.testing.assert_allclose(gradient_change, hessian_product, rtol=4e-9, atol=8e-10)
    # An independent original matrix representation checks the Lie bracket
    # sign and proper radial factor; this does not mirror the component code.
    G = lepton_unit_trace_gauge_representation()['generators']
    s = result['charge_test']['value'];s_matrix = np.einsum('c,cij->ij', s, G)
    expected = []
    for Ai in t[6:18].reshape(3, 4):
        A = np.einsum('c,cij->ij', Ai, G)
        expected.append((A@s_matrix-s_matrix@A)/t[0])
    reconstructed = np.einsum('ic,cjk->ijk', result['proper_spatial_covariant_charge_derivative']['value'].reshape(3, 4), G)
    np.testing.assert_allclose(reconstructed, expected, atol=2e-16)


def test_unit_jet_keeps_scale_free_and_has_both_chain_rule_terms(prepared):
    result = physical_unit_moment_twojet(prepared[2], -.4)
    d = result['required_dipole_chart'];v = result['reference_variance_chart']
    assert d['gradient'][0, 150] == d['value'][0]
    assert d['hessian'][0, 150, 150] == d['value'][0]
    assert v['gradient'][0, 150] == 2*v['value'][0]
    assert v['hessian'][0, 150, 150] == 4*v['value'][0]
    assert np.count_nonzero(d['gradient']) == 1
    assert result['scale_is_initializer_only']
    assert not result['physical_scale_equation_solved']


def test_zero_H_and_incomplete_chart_are_not_defaulted():
    t, g, h = _control_theta();t[18:] = 0.
    with pytest.raises(ValueError, match='nonzero actual H'):
        charge_test_twojet(t, g, h)
    with pytest.raises(ValueError, match='theta gradient'):
        charge_test_twojet(t, g[:, :10], h)
