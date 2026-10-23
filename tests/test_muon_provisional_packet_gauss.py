"""Independent checks of the restricted original source/continuation application."""
import numpy as np
import pytest

from bhsm.interface.muon_provisional_packet_gauss import (
    HAAR_VOLUME, electron_family_lift, sign_projected_constant_sections,
    evaluate_constant_packet, evolve_constant_sections, solve_temporal_difference,
    temporal_indices,
)
from bhsm.interface.muon_native_dirac_hamiltonian import canonical_lepton_hamiltonian_maps
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_prepared_weak_gauss_dressing import _annihilators4


def control_hamiltonian():
    # Supplied finite original-action comparison, not physical preparation.
    H = np.array([.17+.02j, .71-.03j])
    generators = lepton_unit_trace_gauge_representation()['generators']
    fields = np.array([[.03, -.01, .02, .04], [-.8, 0., 0., .02],
                       [0., -1.1, 0., .03], [0., 0., -.9, -.01]])
    connection = np.einsum('mc,cij->mij', fields, generators)[None]
    h = canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],
        spatial_derivative_map=np.zeros((1, 3, 18, 18)), H=H[None], R4=.9,
        gauge_connection=connection)['hamiltonian_map'][0]
    return h, H


def exact_pair():
    rho = np.zeros((16, 16), complex)
    for s in range(2):
        for t in range(2):
            index = (1 << s) | (1 << (2+t)); rho[index, index] = .25
    return rho


def test_full_family_sign_trial_has_global_CAR_and_original_Dirac_evolution():
    h, H = control_hamiltonian()
    a = sign_projected_constant_sections(h, H)
    np.testing.assert_allclose(a['complete_Haar_Cauchy_Gram'], np.eye(4), atol=4e-15)
    for key in ('original_family_reduction_rows', 'original_positive_boundary_rows',
                'original_negative_boundary_rows', 'original_Dirac_first_rows'):
        np.testing.assert_allclose(a[key], 0, atol=3e-15)
    C = electron_family_lift()
    # General weak background mixes the charged seeds with the neutral weak
    # direction: imposing charged4 would change the original action problem.
    Hunit = H/np.linalg.norm(H)
    neutral = np.zeros((6, 2), complex)
    neutral[:2] = Hunit[1].conjugate()*np.eye(2)
    neutral[2:4] = -Hunit[0].conjugate()*np.eye(2)
    assert np.linalg.norm(neutral.conj().T@a['electron_Hamiltonian']
        @a['balanced_charged_spin_seeds6']) > .01
    evolution = evolve_constant_sections(a, np.array([0., .19, .63]))
    np.testing.assert_allclose(evolution['original_Dirac_rows'], 0, atol=2e-15)
    np.testing.assert_allclose(evolution['complete_Haar_Cauchy_Gram'],
        np.broadcast_to(np.eye(4), (3, 4, 4)), atol=4e-15)
    assert a['physical_admission'] is False


def test_source_is_original_iG_contraction_with_exact_half_spin_weights():
    h, H = control_hamiltonian(); a = sign_projected_constant_sections(h, H)
    source = evaluate_constant_packet(a, pair_density=exact_pair(),
        annihilators=_annihilators4(), normalization_owner='declared constant Haar control')
    U, V = a['particle_modes'][0], a['antiparticle_modes'][0]
    G = lepton_unit_trace_gauge_representation()['generators']
    independent = .5*np.array([np.trace(U.conj().T@(1j*g)@U)
        - np.trace(V.conj().T@(1j*g)@V) for g in G])
    np.testing.assert_allclose(source['lepton_material_At_action_source_density'][0],
        independent.real, atol=2e-18)
    np.testing.assert_allclose(source['integrated_material_At_source4'],
        HAAR_VOLUME*independent.real, atol=4e-17)
    assert np.linalg.norm(independent) > 1e-4


def test_trial_rejects_lost_seed_rank_and_unbound_family():
    h, H = control_hamiltonian()
    C = electron_family_lift(); broken = h.copy()
    broken[0, 4] = .01; broken[4, 0] = .01
    with pytest.raises(ValueError, match='does not reduce'):
        sign_projected_constant_sections(broken, H)
    with pytest.raises(ValueError, match='lose rank'):
        sign_projected_constant_sections(np.eye(18), H)
    assert C.shape == (18, 6)


def test_difference_continuation_recomputes_load_and_preserves_absolute_remainder():
    rng = np.random.default_rng(42); n = 84
    diagonal = np.linspace(1., 2., n); seed = rng.normal(size=n)/20
    offset = np.linspace(-.4, .6, n)
    def evaluate(c):
        return dict(gradient=diagonal*c+offset, hessian=np.diag(diagonal))
    feedback = np.diag([.03, -.02, .01, .04]); base = np.array([.2, -.3, .4, -.1])
    calls = []
    def load(c):
        calls.append(c[60:64].copy())
        return base+feedback@c[60:64]
    result = solve_temporal_difference(dict(evaluate=evaluate), seed, load)
    expected_wall = np.linalg.solve(np.diag(diagonal[60:64])+feedback,
        diagonal[60:64]*seed[60:64]-base)
    np.testing.assert_allclose(result['coefficients'][60:64], expected_wall, atol=1e-13)
    np.testing.assert_allclose(result['temporal_original_difference_rows'], 0, atol=2e-13)
    # The seed absolute remainder is still present after difference convergence.
    np.testing.assert_allclose(result['full_known_absolute_rows'], evaluate(seed)['gradient'], atol=2e-13)
    frozen = np.setdiff1d(np.arange(n), temporal_indices(n))
    np.testing.assert_array_equal(result['coefficients'][frozen], seed[frozen])
    assert result['status'] == 'CONTINUATION_CONVERGED'
    assert len(calls) > 100 and result['physical_admission'] is False


def test_singular_difference_keeps_cokernel_instead_of_silent_pseudoinverse():
    def evaluate(c):
        return dict(gradient=np.zeros(84), hessian=np.zeros((84, 84)))
    result = solve_temporal_difference(dict(evaluate=evaluate), np.zeros(84),
        lambda c: np.ones(4), continuation_steps=1)
    assert result['status'] == 'JACOBIAN_RANK_DEFICIENT'
    assert np.linalg.norm(result['left_cokernel_projected_residual']) > 0
    np.testing.assert_array_equal(result['coefficients'], 0)
    np.testing.assert_array_equal(result['full_known_absolute_rows'][60:64], 1)


def test_packet_difference_shrinks_to_its_valid_domain_and_keeps_failures():
    def evaluate(c):
        return dict(gradient=c.copy(), hessian=np.eye(84))
    def load(c):
        if np.max(abs(c)) > 3e-7:
            raise ValueError('declared trial sign-domain boundary')
        return np.full(4, 1e-7)
    result = solve_temporal_difference(dict(evaluate=evaluate), np.zeros(84), load,
        continuation_steps=1)
    assert result['status'] == 'CONTINUATION_CONVERGED'
    assert result['achieved_continuation_strength'] == 1
    assert len(result['packet_derivative_failures']) == 20
    assert all(item['admissible_neighborhood_found'] for item in result['packet_derivative_failures'])
    np.testing.assert_allclose(result['temporal_original_difference_rows'], 0, atol=1e-20)


def test_unresolved_packet_derivative_exports_reached_and_full_strength_rows():
    def evaluate(c):
        return dict(gradient=c.copy(), hessian=np.eye(84))
    def load(c):
        if np.any(c != 0):
            raise ValueError('no supplied admissible packet neighborhood')
        return np.ones(4)
    result = solve_temporal_difference(dict(evaluate=evaluate), np.zeros(84), load,
        continuation_steps=4)
    assert result['status'] == 'PACKET_DERIVATIVE_UNRESOLVED'
    assert result['achieved_continuation_strength'] == 0
    assert result['last_attempted_continuation_strength'] == .25
    assert len(result['packet_derivative_failures'][0]['attempts']) == 21
    np.testing.assert_array_equal(result['full_last_attempted_difference_rows'][60:64], .25)
    np.testing.assert_array_equal(result['full_original_difference_rows'][60:64], 1)
    np.testing.assert_array_equal(result['coefficients'], 0)


def test_explicit_strengths_keep_last_completed_problem_at_domain_limit():
    def evaluate(c):
        return dict(gradient=c.copy(), hessian=np.eye(84))
    def load(c):
        if np.max(abs(c)) > .2:
            raise ValueError('declared continuation domain limit')
        return np.ones(4)
    result = solve_temporal_difference(dict(evaluate=evaluate), np.zeros(84), load,
        continuation_strengths=(.125, 1.), max_iterations=4)
    assert result['status'] != 'CONTINUATION_CONVERGED'
    assert result['achieved_continuation_strength'] == .125
    assert result['last_attempted_continuation_strength'] == 1
    np.testing.assert_allclose(result['last_converged_coefficients'][60:64], -.125, atol=1e-15)
    assert np.max(abs(result['coefficients'])) > .125
    for invalid in ((0., 1.), (.5, .25, 1.), (.25, .5), (np.nan, 1.), (1.1, 1.)):
        with pytest.raises(ValueError, match='strengths must increase'):
            solve_temporal_difference(dict(evaluate=evaluate), np.zeros(84), load,
                continuation_strengths=invalid)
