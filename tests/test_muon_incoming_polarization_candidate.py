"""Conditional selector checks; none certifies a physical incoming state."""
import numpy as np
import pytest

from audits.bhsm_collider_incoming_field_current import apply_incoming_packet_current, current_algebra
from bhsm.interface.muon_incoming_polarization_candidate import (
    execute_boundary_transport_control, gapped_sign_subspaces,
)
from scripts.evaluate_muon_incoming_polarization_candidate import exact_saved_pair


def test_zero_modes_and_non_self_adjoint_boundary_rules_fail_closed():
    with pytest.raises(ValueError, match='zero/gap'):
        gapped_sign_subspaces(np.diag([-1., 0., 1.]))
    with pytest.raises(ValueError, match='self-adjoint'):
        gapped_sign_subspaces(np.array([[1., 1.], [0., -1.]]))


def test_stationary_past_transport_is_not_instantaneous_reselection():
    result, sections = execute_boundary_transport_control()
    r = result['residuals']
    assert r['original_full18_Dirac_Cauchy_five_point_max'] < 2e-10
    assert r['projector_transport_five_point_max'] < 2e-10
    assert r['full18_invariant_carrier_leakage_max'] < 2e-14
    assert r['finite_stationary_past_cutoff_projector_difference'] < 2e-14
    assert r['past_Cook_tail_bound'] == 0.
    assert r['instantaneous_projector_transport_defect_midpoint'] == pytest.approx(.32, abs=2e-10)
    assert r['transported_vs_instantaneous_projector_midpoint'] > .08
    assert not result['physical_incoming_realization']
    assert not result['physical_background_constraints_solved']
    assert not result['physical_derivative_admitted']
    assert result['adopted_Gaussian_preparation_residuals']['energy_MeV'] is None
    f = sections['transported']
    np.testing.assert_allclose(sections['Cauchy_quadrature'][0]*f.conj().T@f,
                               np.eye(4), atol=2e-12)


def test_ordered_current_channels_match_exact_Fock_trace():
    # Seven channels differs from four spin coefficients; the previous einsum
    # reused a label across those independent axes and could not execute.
    rho, annihilators = exact_saved_pair()
    rng = np.random.default_rng(20261018)
    modes, _ = np.linalg.qr(rng.normal(size=(18, 4))+1j*rng.normal(size=(18, 4)))
    z = rng.normal(size=(7, 18, 18))+1j*rng.normal(size=(7, 18, 18))
    vertices = (z+z.conj().swapaxes(-1, -2))[None]
    metadata = {key: 'ALGEBRAIC_REGRESSION_NOT_PHYSICAL_PACKET' for key in (
        'action_owner', 'background_owner', 'Cauchy_domain_owner',
        'particle_mode_owner', 'antiparticle_mode_owner', 'vertex_owner')}
    metadata['benchmark_id'] = 'BHSM_NEW_COLLIDER_ELECTRON_POSITRON_TO_MUON_ANTIMUON_V1'
    got = apply_incoming_packet_current(particle_modes=modes[None, :, :2],
        antiparticle_modes=modes[None, :, 2:], canonical_Hamiltonian_vertices=vertices,
        pair_density=rho, annihilators=annihilators, metadata=metadata)
    b = current_algebra(annihilators, rho)['bilinear_difference_operators4x4x16x16']
    j = np.einsum('aij,ijuv->auv', got['compressed_packet_vertices'][0], b)
    direct = np.array([[np.trace(rho@a@c) for c in j] for a in j])
    means = np.array([np.trace(rho@a) for a in j])
    assert got['ordered_Hamiltonian_vertex_product'].shape == (1, 7, 7)
    np.testing.assert_allclose(got['ordered_Hamiltonian_vertex_product'][0], direct,
                               rtol=2e-13, atol=2e-13)
    np.testing.assert_allclose(got['Hamiltonian_vertex_expectation'][0], means,
                               rtol=2e-13, atol=2e-13)
    np.testing.assert_allclose(got['connected_Hamiltonian_vertex_product'][0],
                               direct-means[:, None]*means[None, :], rtol=2e-13, atol=2e-13)
    assert not got['full_constraint_solution_admitted']
