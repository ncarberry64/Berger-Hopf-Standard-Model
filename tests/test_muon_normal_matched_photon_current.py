import numpy as np
from bhsm.interface.muon_normal_matched_photon_current import (
    complete_normal_current_gaunt, normal_matched_field_adjoint,
    constant_right_bridge_embedding, normal_matched_adjoint_sources,
    normal_matched_left_current_moments)


def test_complete_real_gaunt_reach_and_nonzero_n3_return():
    g = complete_normal_current_gaunt()
    n4 = np.flatnonzero(g['internal_degrees'] == 4)
    n1 = np.flatnonzero(g['external_degrees'] == 1)
    n3 = np.flatnonzero(g['external_degrees'] == 3)
    assert np.max(abs(g['gaunt'][n4][:, :, n3])) > .1
    assert np.array_equal(g['gaunt'][n4][:, :, n1], np.zeros((25, 4, 4)))
    rng = np.random.default_rng(199)
    b = rng.normal(size=(3, 120, 48))+1j*rng.normal(size=(3, 120, 48))
    embedded = constant_right_bridge_embedding(b)
    ii = embedded['retained_even02_indices']
    assert np.array_equal(embedded['original_current_magnetic_internal_bridge'][:, ii], b)
    assert np.array_equal(np.delete(embedded['original_current_magnetic_internal_bridge'], ii, axis=1),
                          np.zeros((3, 300, 48)))


def test_literal_c_before_transpose_inverse_preserves_pairing():
    rng = np.random.default_rng(12)
    nb = 5
    k = rng.normal(size=(nb, nb))+1j*rng.normal(size=(nb, nb))
    k += 4*np.eye(nb)
    c = np.array([[1., 0., 0., 0., 0.]])
    left = rng.normal(size=(120, 420, nb))+1j*rng.normal(size=(120, 420, nb))
    tests = rng.normal(size=(3, 6, 120))+1j*rng.normal(size=(3, 6, 120))
    result = normal_matched_field_adjoint(dict(original_Hessian=k, frame_rows=c), left, tests)
    assert np.max(abs(result['original_adjoint_residual'])) < 2e-12
    assert np.max(abs(result['frame_residual'])) < 2e-12
    force = rng.normal(size=nb)+1j*rng.normal(size=nb)
    saddle = np.block([[k, c.T], [c, np.zeros((1, 1))]])
    right = np.linalg.solve(saddle, np.r_[force, 0])[:nb]
    lhs = np.einsum('aij,i->aj', result['field_adjoint'], force)
    rhs = np.einsum('aij,i->aj', result['literal_adjoint_source'], right)
    np.testing.assert_allclose(lhs, rhs, rtol=2e-13, atol=2e-12)


def test_direct_source_equals_full_literal_current_integration():
    rng = np.random.default_rng(65)
    nodes = dict(proper_time=np.array([.2, .8]), weight=np.array([.4, .6]),
                 R=np.array([.9+.01j, 1.1-.02j]), N=np.array([.7+.02j, .8+.01j]),
                 total_proper_clock=1.)
    p = rng.normal(size=(96, 2))
    h = np.array([[.1, .8, .05, .02], [.2, .9, .1, -.03]])
    tests = rng.normal(size=(3, 6, 120))+1j*rng.normal(size=(3, 6, 120))
    full = normal_matched_left_current_moments(nodes, p, h, temporal_cells=2, family=1)
    soft = np.einsum('ado,ofb->adfb', tests, full['literal_left_current'])
    expected = soft.transpose(0, 3, 1, 2).reshape(3, 4, 2520)
    direct = normal_matched_adjoint_sources(nodes, p, h, tests, temporal_cells=2, family=1)
    np.testing.assert_allclose(direct, expected, atol=5e-15, rtol=2e-13)
