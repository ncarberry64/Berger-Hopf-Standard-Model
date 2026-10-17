"""CONTROL_ONLY continuation/Green algebra and actual stored domain facts."""
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_literal_euclidean_higgs_green import (
    literal_proper_euclidean_forms, continued_action_polynomial,
    literal_higgs_weak_form, intrinsic_higgs_open_current_application)
from bhsm.interface.muon_euclidean_angular_weak_action import angular_weak_square


def test_literal_proper_clock_action_retains_imaginary_cross_and_correct_shift_sign():
    N, e, r, beta = 1.4, 1.2, 2.3, .4
    # A single transverse Maxwell coefficient with one radial derivative.
    # Its Lorentz L is (e*v²-2e*beta*x*v+(e*beta²-r)*x²)/2.
    M, B, K = [np.array([[x]]) for x in (e, -e*beta, e*beta**2-r)]
    out = literal_proper_euclidean_forms((M, B, K), N, 0)['forms']
    np.testing.assert_allclose([a[0, 0] for a in out], [N*e, 1j*e*beta, (r-e*beta**2)/N])
    x, v = .3-.2j, -.1+.6j
    literal = -.5/N*(M[0, 0]*(1j*N*v)**2+2*B[0, 0]*x*(1j*N*v)+K[0, 0]*x*x)
    continued = .5*(out[0][0, 0]*v*v+2*out[1][0, 0]*x*v+out[2][0, 0]*x*x)
    np.testing.assert_allclose(literal, continued, rtol=0, atol=2e-16)
    # The reflected modulus-square would erase/change the literal cross;
    # it cannot be silently used as the same scalar action.
    assert abs(out[1][0, 0].imag) > .4


def test_proper_temporal_one_form_rotation_and_no_unowned_algebraic_velocity():
    M = np.diag([0., 1., 2.]);B = np.array([[0., .2, -.3], [0., .1, .4], [0., -.1, .2]])
    K = np.array([[2., .1, .2], [.1, -.4, .3], [.2, .3, -.5]])
    N = 1.3+.1j
    x = np.array([.2+.5j, .1, -.3j]);v = np.array([0j, -.1+.3j, .4])
    out = literal_proper_euclidean_forms((M, B, K), N, 1)
    R = out['coordinate_rotation'];xl = x/R;vl = 1j*N*v/R
    original = -.5/N*(vl@M@vl+xl@B@vl+vl@B.T@xl+xl@K@xl)
    m, b, k = out['forms'];actual = .5*(v@m@v+x@b@v+v@b.T@x+x@k@x)
    np.testing.assert_allclose(actual, original, rtol=0, atol=2e-16)
    M[0, 0] = .2
    with pytest.raises(ValueError, match='velocity'):
        literal_proper_euclidean_forms((M, B, K), N, 1)


def _toy():
    times = np.linspace(0, 1, 5)
    M = np.zeros((5, 488, 488));B = M.copy();K = M.copy()
    K[:, :400, :400] = np.eye(400)*2
    M[:, 400:480, 400:480] = np.eye(80)
    K[:, 400:480, 400:480] = -np.eye(80)*.3
    B[:, 400, 420] = .2;B[:, 420, 400] = -.2
    z, w = np.polynomial.legendre.leggauss(20)
    t = (z+1)/2
    nodes = dict(proper_time=t,weight=w/2,total_proper_clock=1.,coordinate_anchor=t,
                 coordinate_offset=np.zeros(len(t),complex),
                 reflected_coordinate_offset=np.zeros(len(t),complex),N=np.ones(len(t)))
    return nodes, (M, B, K), times


def test_original_sectorial_higgs_action_inverse_and_literal_gaussian_ordering():
    nodes, forms, times = _toy()
    p = continued_action_polynomial(times, forms)
    h = literal_higgs_weak_form(nodes, p, temporal_cells=2, harmonics=np.array([0]))
    assert h['original_action_inverse_residual_max'] < 2e-14
    assert min(h['normalized_Hermitian_part_eigenvalues']) > 0
    assert h['operator_Hermiticity_defect'] > .01
    assert h['independent_branch_reflection_max'] == 0
    assert np.max(h['gauge_H_cross_max']) == 0
    hf = np.diag([.1, .2, .3, .4, .5, .6]).astype(complex)
    coeff = dict(forward=np.tile(hf,(len(times)*4,1,1)),reflected=np.tile(hf,(len(times)*4,1,1)))
    f = angular_weak_square(nodes, coeff, temporal_cells=2)
    rng = np.random.default_rng(62)
    V = rng.normal(size=(4,6,6))+1j*rng.normal(size=(4,6,6))
    result = intrinsic_higgs_open_current_application(nodes, coeff, f, h, V, temporal_cells=2)
    right = np.linalg.solve(f['K'],result['actual_A_sharp_source_numerator'].reshape(12,-1)).reshape(12,6,8)
    inverse = np.linalg.inv(h['Higgs_original_action_Hessian'])
    manual = np.zeros((6,6),complex)
    for a in range(8):
        for b in range(8):
            manual -= result['literal_left_current'][:,:,a]@right[:,:,b]*inverse[a,b]
    np.testing.assert_allclose(result['open_Gaussian_current'],manual,rtol=3e-15,atol=3e-12)
    assert result['native_Pauli_or_physical_a_mu'] is None
    assert result['original_fermion_source_rows_max'] < 1e-14


def test_actual_saved_dirichlet_internal_gauge_higgs_cross_is_exact_zero():
    root = Path(__file__).resolve().parents[1]
    folder = root/'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1'
    for side in ('incoming','outgoing'):
        for name in ('M','B','K'):
            with np.load(folder/f'{side}_operator_{name}.npz',allow_pickle=False) as a:
                x = a['raw_'+name]
                assert x.shape == (5,488,488)
                assert np.count_nonzero(x[:,:400,400:480]) == 0
                assert np.count_nonzero(x[:,400:480,:400]) == 0
    # This checks the literal finite trial domain, not an all-gauge cancellation.
