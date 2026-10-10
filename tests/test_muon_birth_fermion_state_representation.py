"""CAR algebra and supplied-input guards; no fixture selects a physical state.

All finite matrices below are CONTROL_ONLY unit-test inputs. The materialized
report never receives them and reads the frozen geometric reset without a new
action, trajectory, state-selection, or covariance-witness campaign.
"""
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

from bhsm.interface.muon_birth_fermion_state_representation import (
    NEXT_OPERAND,
    SCIENTIFIC_REFERENCE,
    STARTING_HEAD,
    charge_conjugate_family_projector,
    covariance_balance_defect,
    occupation_difference_contraction,
    representation_report,
    symbolic_matched_balance,
    transport_muon_covariance,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def supplied_car_inputs():
    """CONTROL_ONLY spin2 x family2 particle space with its CAR conjugate."""
    identity, zero = np.eye(4), np.zeros((4, 4))
    gamma = np.block([[zero, identity], [identity, zero]])
    positive = np.diag([1., 1., 0., 0.])
    covariance = np.block([[positive, zero], [zero, identity-positive]])
    spin_reset = np.array([[1, 1j], [1j, 1]], dtype=complex)/np.sqrt(2.)
    particle_reset = np.kron(spin_reset, np.eye(2))
    reset = np.block([[particle_reset, zero], [zero, particle_reset.conj()]])
    particle_family = np.kron(np.eye(2), np.diag([0., 1.]))
    sector = charge_conjugate_family_projector(particle_family)
    return dict(covariance_event=covariance, reset_lift=reset,
                conjugation_event=gamma, conjugation_child=gamma,
                family_sector=sector)


def test_complex_family_projector_includes_its_conjugate_charge_partner():
    particle = np.array([[1, -1j], [1j, 1]], dtype=complex)/2
    sector = charge_conjugate_family_projector(particle)
    np.testing.assert_array_equal(sector[:2, :2], particle)
    np.testing.assert_array_equal(sector[2:, 2:], particle.conj())
    np.testing.assert_array_equal(sector[:2, 2:], np.zeros((2, 2)))
    gamma = np.block([[np.zeros((2, 2)), np.eye(2)],
                      [np.eye(2), np.zeros((2, 2))]])
    np.testing.assert_array_equal(gamma @ sector.conj() @ gamma, sector)
    np.testing.assert_array_equal(sector @ sector, sector)
    assert np.linalg.matrix_rank(sector) == 2


def test_supplied_reset_preserves_car_and_the_restricted_family_covariance(supplied_car_inputs):
    result = transport_muon_covariance(**supplied_car_inputs)
    c, u, q, gamma = (supplied_car_inputs[name] for name in (
        'covariance_event', 'reset_lift', 'family_sector', 'conjugation_event'))
    child = result['covariance_child']
    np.testing.assert_allclose(child, u @ c @ u.conj().T, atol=2e-15, rtol=0)
    assert np.linalg.norm(child-c) > .5
    np.testing.assert_allclose(child+gamma @ child.conj() @ gamma, np.eye(8), atol=2e-15, rtol=0)
    np.testing.assert_allclose(result['muon_covariance_event'], q @ c @ q, atol=0, rtol=0)
    np.testing.assert_allclose(result['muon_covariance_child'], u @ q @ c @ q @ u.conj().T,
                               atol=2e-15, rtol=0)
    assert np.linalg.eigvalsh(child).min() >= -2e-15
    assert np.linalg.eigvalsh(child).max() <= 1+2e-15
    assert result['positivity_and_order_preserved']
    assert result['self_dual_CAR_constraint_preserved']
    assert result['purity_preserved']
    for name in ('restricted_CAR_residual', 'family_reset_commutator_residual',
                 'family_conjugation_residual', 'family_covariance_commutator_residual',
                 'family_transport_residual', 'sector_purity_residual'):
        assert result[name] < 2e-15
    assert not result['physical_state_selected']
    assert not result['hadamard_class_certified_by_finite_matrix']


def test_family_compression_has_car_identity_q_not_ambient_identity(supplied_car_inputs):
    result = transport_muon_covariance(**supplied_car_inputs)
    restricted = result['muon_covariance_child']
    gamma, q = supplied_car_inputs['conjugation_child'], supplied_car_inputs['family_sector']
    self_dual_sum = restricted+gamma @ restricted.conj() @ gamma.conj().T
    np.testing.assert_allclose(self_dual_sum, q, atol=2e-15, rtol=0)
    assert np.linalg.norm(self_dual_sum-np.eye(8), 2) == pytest.approx(1.)
    assert result['restricted_CAR_identity'] == 'Q on ambient space; I on Ran(Q)'


def test_noncommuting_family_compression_of_a_pure_state_can_be_mixed():
    # CONTROL_ONLY exact finite CAR data, not a BHSM family state choice.
    particle = np.full((2, 2), .5)
    zero, identity = np.zeros((2, 2)), np.eye(2)
    covariance = np.block([[particle, zero], [zero, identity-particle]])
    gamma = np.block([[zero, identity], [identity, zero]])
    q = charge_conjugate_family_projector(np.diag([0., 1.]))
    result = transport_muon_covariance(covariance, np.eye(4), gamma, gamma, q)
    assert result['event_purity_residual'] == 0.
    assert result['purity_preserved']
    assert result['family_covariance_commutator_residual'] == pytest.approx(.5)
    assert result['sector_purity_residual'] == pytest.approx(.25)
    assert result['restricted_CAR_residual'] == 0.
    np.testing.assert_array_equal(result['muon_covariance_child'], np.diag([0., .5, 0., .5]))
    assert not result['physical_state_selected']


def test_particle_only_family_sector_is_rejected(supplied_car_inputs):
    bad = dict(supplied_car_inputs)
    q = bad['family_sector'].copy()
    q[4:, 4:] = 0
    bad['family_sector'] = q
    with pytest.raises(ValueError, match='conjugate-charge partner'):
        transport_muon_covariance(**bad)


def test_nonunitary_reset_is_rejected(supplied_car_inputs):
    bad = dict(supplied_car_inputs, reset_lift=2*np.eye(8))
    with pytest.raises(ValueError, match='unitary'):
        transport_muon_covariance(**bad)


def test_reset_that_mixes_the_supplied_family_sector_is_rejected(supplied_car_inputs):
    family_swap = np.array([[0., 1.], [1., 0.]])
    particle_reset = np.kron(np.eye(2), family_swap)
    zero = np.zeros((4, 4))
    reset = np.block([[particle_reset, zero], [zero, particle_reset]])
    with pytest.raises(ValueError, match='preserve the supplied family sector'):
        transport_muon_covariance(**dict(supplied_car_inputs, reset_lift=reset))


def test_reset_must_intertwine_event_and_child_car_conjugations(supplied_car_inputs):
    with pytest.raises(ValueError, match='intertwine the CAR conjugations'):
        transport_muon_covariance(**dict(
            supplied_car_inputs, conjugation_child=-supplied_car_inputs['conjugation_child']))


@pytest.mark.parametrize('bad', [
    np.diag([.5, 0]), [[1, 1j], [0, 0]], np.zeros((2, 3)),
    np.empty((0, 0)), [[float('nan')]], [[float('inf')]],
])
def test_invalid_particle_projector_is_rejected(bad):
    with pytest.raises(ValueError):
        charge_conjugate_family_projector(bad)


@pytest.mark.parametrize('tolerance', [0, -1, float('nan'), float('inf')])
def test_invalid_tolerance_is_rejected(supplied_car_inputs, tolerance):
    with pytest.raises(ValueError, match='finite positive tolerance'):
        transport_muon_covariance(**supplied_car_inputs, tolerance=tolerance)
    with pytest.raises(ValueError, match='finite positive tolerance'):
        charge_conjugate_family_projector(np.diag([0., 1.]), tolerance=tolerance)


def test_covariance_transport_rejects_invalid_car_state_inputs(supplied_car_inputs):
    nonhermitian = supplied_car_inputs['covariance_event'].copy().astype(complex)
    nonhermitian[0, 1] = 1j
    with pytest.raises(ValueError, match='Hermitian'):
        transport_muon_covariance(**dict(supplied_car_inputs, covariance_event=nonhermitian))
    out_of_order = supplied_car_inputs['covariance_event'].copy()
    out_of_order[0, 0], out_of_order[4, 4] = 1.1, -.1
    with pytest.raises(ValueError, match='0 <= C <= I'):
        transport_muon_covariance(**dict(supplied_car_inputs, covariance_event=out_of_order))
    not_car = np.zeros((8, 8))
    with pytest.raises(ValueError, match='self-dual CAR constraint'):
        transport_muon_covariance(**dict(supplied_car_inputs, covariance_event=not_car))


def test_symbolic_opposite_normal_balance_vanishes_for_all_covariances():
    # C is an arbitrary matrix symbol, not a selected covariance or a sample.
    c, a, u = (sp.MatrixSymbol(name, 3, 3) for name in ('C', 'A', 'U'))
    ui = sp.Inverse(u)  # Equals U-dagger under the owned unitary reset law.
    child_operator = -u*a*ui
    kernel = (a+ui*child_operator*u).doit()
    assert kernel == sp.ZeroMatrix(3, 3)
    assert sp.Trace(c*kernel).doit() == 0
    delta_c = sp.MatrixSymbol('arbitrary_smooth_delta_C', 3, 3)
    assert sp.Trace(delta_c*kernel).doit() == 0
    proof = symbolic_matched_balance()
    assert proof['identically_zero']
    assert not proof['covariance_chosen']
    assert not proof['smooth_covariance_completion_needed_for_matched_zero']
    assert not proof['actual_full_E1_stress_Noether_kernel_match_proved']


def test_supplied_operator_balance_uses_the_owned_outward_normal_sign():
    operator = np.array([[2., 1j], [-1j, 3.]])
    reset = np.array([[0., 1.], [-1., 0.]])
    oriented_child = -reset @ operator @ reset.conj().T
    result = covariance_balance_defect(operator, oriented_child, reset)
    np.testing.assert_array_equal(result['kernel_defect'], np.zeros((2, 2)))
    assert result['defect_norm'] == 0
    assert result['supplied_matrix_zero_within_tolerance']
    assert not result['physical_E1_kernel_evaluated']
    wrong_sign = covariance_balance_defect(operator, -oriented_child, reset)
    np.testing.assert_array_equal(wrong_sign['kernel_defect'], 2*operator)
    assert not wrong_sign['supplied_matrix_zero_within_tolerance']
    assert not wrong_sign['physical_E1_kernel_evaluated']


def test_balance_and_state_difference_reject_invalid_or_mixed_shapes():
    with pytest.raises(ValueError, match='unitary'):
        covariance_balance_defect(np.eye(2), -np.eye(2), 2*np.eye(2))
    with pytest.raises(ValueError, match='dimensions must agree'):
        covariance_balance_defect(np.eye(2), -np.eye(3), np.eye(2))
    with pytest.raises(ValueError, match='dimensions must agree'):
        occupation_difference_contraction(np.eye(2), np.eye(3))
    with pytest.raises(ValueError, match='finite nonempty square'):
        occupation_difference_contraction(np.eye(2), [[float('nan'), 0], [0, 0]])


def test_particle_occupation_state_difference_has_the_opposite_c_plus_sign():
    operator = np.array([[1., 1j], [-1j, 2.]])
    delta_c_plus = np.array([[.25, 1j/3], [-1j/3, -.5]])
    delta_n = -delta_c_plus
    expected = np.trace(operator @ delta_n)
    assert expected != 0
    assert occupation_difference_contraction(operator, delta_c_plus) == expected
    assert occupation_difference_contraction(operator, -delta_c_plus) == -expected


def test_symbolic_ordered_bilinear_sign_uses_n_equals_i_minus_c_plus():
    a, c, dc = (sp.MatrixSymbol(name, 2, 2) for name in ('A', 'C_plus', 'delta_C_plus'))
    original = sp.Identity(2)-c
    varied = sp.Identity(2)-(c+dc)
    occupation_difference = (varied-original).doit()
    assert occupation_difference == -dc
    assert sp.Trace(a*occupation_difference).doit() == -sp.Trace(a*dc)


def test_symbolic_localization_transports_the_car_pairing_as_well_as_covariance():
    c, weight = sp.symbols('c weight', real=True)
    covariance = sp.diag(c, 1-c)
    gamma = sp.Matrix([[0, 1], [1, 0]])
    localization = weight*sp.eye(2)
    image = localization*covariance*localization.T
    self_dual_sum = sp.simplify(image+gamma*sp.conjugate(image)*gamma)
    assert self_dual_sum == localization*localization.T
    assert self_dual_sum != sp.eye(2)
    assert self_dual_sum == weight**2*sp.eye(2)


@pytest.fixture
def report(monkeypatch):
    def no_selected_covariance(*args, **kwargs):
        raise AssertionError('report must not choose or transport a numerical covariance')

    monkeypatch.setattr(
        'bhsm.interface.muon_birth_fermion_state_representation.transport_muon_covariance',
        no_selected_covariance,
    )
    return representation_report(ROOT)


def test_report_supersedes_the_vector_stop_without_promoting_zero_one_point(report):
    assert report['starting_head'] == STARTING_HEAD
    assert report['scientific_reference'] == SCIENTIFIC_REFERENCE
    assert report['representation'] == 'SELF_DUAL_CAR_CAUCHY_COVARIANCE'
    assert report['previous_vector_stop_superseded']
    assert not report['nonzero_one_point_required']
    assert not report['zero_one_point_implies_no_muon']
    assert not report['external_one_particle_ray_selected']
    assert not report['physical_covariance_selected']
    assert report['numerical_covariance'] is None


def test_report_unifies_the_incoming_and_current_c2_state_operand(report):
    operand = report['unified_state_operand']
    assert operand['id'] == NEXT_OPERAND == 'C_C1_E1_MINUS_BHSM'
    assert operand['value_name'] == 'C_C1,E1^-^BHSM'
    assert operand['value'] is None
    assert operand['independent_state_selection_problems'] == 1
    assert not operand['causal_reset_transport_selects_state']
    assert 'C_mu,Sigma^BHSM' in operand['existing_current_C2_operand']
    assert 'U_R' in operand['consumer'] and 'V_C2' in operand['consumer']
    assert 'not for the already proved matched internal-seam zero' in operand['qualification']


def test_retained_state_selector_candidates_supply_no_chosen_covariance(report):
    audit = report['selector_audit']
    assert audit['selected_candidate_count'] == 0
    assert not audit['retained_action_selects_unique_Feynman_state']
    assert all(not row['selects_state'] for row in audit['rows'])
    candidates = {row['candidate'] for row in audit['rows']}
    assert {'AE2_RESET_LIFT', 'CURRENT_C2_TIME_ORIENTATION',
            'HADAMARD_MICROLOCAL_CONDITION', 'INSTANTANEOUS_HAMILTONIAN_DIAGONALIZATION',
            'EUCLIDEAN_CAP_OR_REFLECTION_POSITIVITY', 'IN_OUT_ASYMPTOTIC_VACUUM'} <= candidates


def test_report_separates_state_uniform_matching_from_unmatched_physical_values(report):
    proof = report['exact_symbolic_matched_balance']
    assert proof['identically_zero']
    assert not proof['actual_full_E1_stress_Noether_kernel_match_proved']
    consumers = report['surviving_state_consumers']
    assert 'Pi_fin[C]' in consumers['finite_response']
    assert not consumers['blanket_native_KKT_or_Pauli_dependence_claimed']
    assert not consumers['full_birth_balance_covariance_dependence_proved']
    assert not consumers['covariance_selection_sufficient_for_all_remaining_values']
    assert not report['physical_I_phys_passed']
    assert all(value is None for value in report['downstream'].values())


def test_report_freezes_the_actual_geometric_reset_and_exact_convention(report):
    frozen = report['frozen_geometric_reset']
    assert frozen['norms']['l2_norm'] == 7.64107108345298e-15
    assert frozen['norms']['max_abs'] == 5.628594097932515e-15
    assert not frozen['newly_evaluated']
    assert not frozen['full_physical_birth_claimed']
    convention = report['convention']
    assert convention['finite_relative_state_difference'] == 'delta <chi_dagger*A*chi>=-Tr(A*delta C_plus)'
    assert not convention['absolute_local_Wick_prescription_owned']
    assert not convention['kinetic_action_half_is_quantum_doubling_half']
    assert not convention['blind_Tr_C_A_used']


def test_report_calls_are_detached_from_mutations(report):
    baseline = representation_report(ROOT)
    report['unified_state_operand']['value'] = [[1]]
    report['selector_audit']['rows'][0]['selects_state'] = True
    report['frozen_geometric_reset']['norms']['l2_norm'] = 1.
    assert representation_report(ROOT) == baseline
