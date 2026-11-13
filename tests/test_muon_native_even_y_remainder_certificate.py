"""CONTROL_ONLY exact finite pencils; no physical state or cutoff selection."""
import numpy as np
import mpmath as mp
import pytest
from flint import arb, acb, acb_mat, ctx

from bhsm.interface.muon_native_even_y_remainder_certificate import (
    _frobenius_upper, _operator_norm_upper, certify_generalized_even_pencil,
    even_y_tail_bounds,
)


def fixture(gram_scale=1.):
    G = np.diag([gram_scale, 1.])
    K0 = np.diag([2. * gram_scale, 3.])
    K1 = np.array([[0., .4 * np.sqrt(gram_scale)], [.4 * np.sqrt(gram_scale), 0.]])
    K2 = np.diag([.2 * gram_scale, .3])
    V = np.diag([1. / np.sqrt(gram_scale), 1.])
    return (K0, K1, K2, G, V, np.array([2., 3.]), np.array([1, -1]))


def test_positive_generalized_gram_enclosed_without_diagonal_substitution():
    constants, cert = certify_generalized_even_pencil(*fixture(4.))
    assert constants['gap_lower'] <= 2
    assert constants['gap_lower'] > 1.99
    assert constants['C_norm_upper'] >= .4
    assert constants['C_norm_upper'] < .401
    assert constants['B_norm_upper'] >= .3
    assert cert['exact_stored_Hermitian_and_LR_parity']
    assert cert['approximate_diagonal_is_not_substituted_for_original_P0']


def test_reference_normalization_and_eigenvalue_defects_are_retained():
    f = list(fixture()); f[4] = f[4] * 1.01; f[5] = np.array([2.0001, 2.9999])
    constants, cert = certify_generalized_even_pencil(*f)
    assert cert['reference_Gram_defect']['upper_binary64'] > .02
    assert cert['reference_K0_diagonal_defect']['upper_binary64'] > .02
    assert constants['primitive_squared_norm_factor'] > 1
    assert constants['gap_lower'] < 2


def test_nonhermitian_not_silently_symmetrized():
    f = list(fixture()); f[1] = f[1].copy(); f[1][0, 1] += 1e-15
    with pytest.raises(ValueError, match='Hermitian'):
        certify_generalized_even_pencil(*f)


def test_tiny_parity_violation_is_not_deleted():
    f = list(fixture()); f[1] = f[1].copy(); f[1][0, 0] = 1e-30
    with pytest.raises(ValueError, match='grading'):
        certify_generalized_even_pencil(*f)


def test_indefinite_gram_and_incomplete_reference_fail_closed():
    f = list(fixture()); f[3] = np.diag([-1., 1.])
    with pytest.raises(ValueError, match='Gram'):
        certify_generalized_even_pencil(*f)
    f = list(fixture()); f[4] = np.zeros((2, 2))
    with pytest.raises(ValueError, match='Gram'):
        certify_generalized_even_pencil(*f)


def test_zero_centred_ball_norm_remains_finite_and_outward():
    old = ctx.prec
    try:
        ctx.prec = 128
        A = acb_mat([[acb(arb(0, '1e-20'), arb(0, '2e-20'))]])
        bound = _frobenius_upper(A)
        assert bound.is_finite() and bound > arb('2e-20')
    finally:
        ctx.prec = old


def test_operator_norm_bound_handles_nonhermitian_stored_matrix():
    A = np.array([[1., 2j], [.5j, -2.]])
    old = ctx.prec
    try:
        ctx.prec = 128
        bound, _ = _operator_norm_upper(acb_mat(A.tolist()), A)
        assert float(bound.upper()) >= np.linalg.norm(A, 2)
    finally:
        ctx.prec = old


def test_even_difference_tail_encloses_independent_full_matrix_remainder():
    # Analytic eigenvalues of a two-by-two Hermitian polynomial, not the
    # Cauchy majorant's own implementation.
    c = .7; ym = .05; yl = .004
    constants, _ = certify_generalized_even_pencil(*fixture())
    bound = even_y_tail_bounds(constants, c, ym, yl)
    with mp.workdps(70):
        def trace(y):
            a = mp.mpf(2) + mp.mpf('.2') * y*y
            b = mp.mpf(3) + mp.mpf('.3') * y*y
            spread = mp.sqrt((a-b)**2 + 4 * mp.mpf('.4')**2 * y*y)
            return mp.e1(mp.mpf(c)*(a+b-spread)/2)+mp.e1(mp.mpf(c)*(a+b+spread)/2)
        coefficient = mp.diff(trace, 0, 2)/2
        error = trace(mp.mpf(ym))-trace(mp.mpf(yl))-(mp.mpf(ym)**2-mp.mpf(yl)**2)*coefficient
        assert abs(error) < bound['value_tail_upper']['upper_binary64']
        r = bound['circle_radius_exact_binary64']
        sum_tail = (ym/r)**4/(1-(ym/r)**2)+(yl/r)**4/(1-(yl/r)**2)
        assert bound['paired_even_tail_factor']['upper_binary64'] < sum_tail


def test_gram_measure_derivative_survives_zero_field_variations():
    constants, _ = certify_generalized_even_pencil(*fixture())
    p = dict(u=np.array([1.]), Au=np.array([2.]), Mu=np.array([.5]),
        deltaA=np.zeros((1, 2)), deltaMu=np.zeros((1, 2)),
        measure=np.array([[.1, 0.]]), weight=np.array([.2]))
    r = even_y_tail_bounds(constants, .7, .05, .004, p, grading_preserving_variations=True)
    assert r['weighted_directional_tail_upper'][0, 0] > 0
    assert r['weighted_directional_tail_upper'][0, 1] == 0
    assert r['Gram_measure_derivative_included_once']
    assert r['primitive_FE_Gram_normalization_factor_included']


def test_directional_tail_encloses_independent_mass_response_with_gram_motion():
    # This exact quadrature family has K=|A+yM|²/(1+t*mu), G=I,
    # equivalently Kfixed with Gram=(1+t*mu)I.  Construct the equivalent
    # primitive derivative: the measure moves and both A/M scale to cancel
    # its stiffness variation.  The remaining generalized-Gram response
    # is nonzero, and must be bounded together with the mass response.
    a, b, mass, dm, mu = 2., 3., .2, .1, .15
    A = np.diag(np.sqrt([a, b])); M = np.array([[0., mass], [mass, 0.]])
    C = A @ M + M @ A; B = M @ M
    constants, _ = certify_generalized_even_pencil(np.diag([a, b]), C, B,
        np.eye(2), np.eye(2), np.array([a, b]), np.array([1, -1]))
    dA = -mu/2*A; dM = np.array([[0., dm], [dm, 0.]])-mu/2*M
    norms = dict(u=[np.sqrt(2.)], Au=[np.linalg.norm(A)], Mu=[np.linalg.norm(M)],
        deltaA=[[np.linalg.norm(dA)]], deltaMu=[[np.linalg.norm(dM)]], measure=[[mu]], weight=[1.])
    bound = even_y_tail_bounds(constants, .7, .05, .004, norms, grading_preserving_variations=True)
    with mp.workdps(60):
        def value(y, t):
            off = (mp.sqrt(a)+mp.sqrt(b))*(mp.mpf(mass)+mp.mpf(dm)*t)*y
            aa = a+(mp.mpf(mass)+mp.mpf(dm)*t)**2*y*y
            bb = b+(mp.mpf(mass)+mp.mpf(dm)*t)**2*y*y
            disc = mp.sqrt((aa-bb)**2+4*off**2)
            eigen = [(aa+bb-disc)/2/(1+mp.mpf(mu)*t), (aa+bb+disc)/2/(1+mp.mpf(mu)*t)]
            return sum(mp.e1(mp.mpf('.7')*v) for v in eigen)
        def tail(t):
            coefficient = mp.diff(lambda y: value(y,t), 0, 2)/2
            return value(mp.mpf('.05'), t)-value(mp.mpf('.004'), t)-(mp.mpf('.05')**2-mp.mpf('.004')**2)*coefficient
        derivative = mp.diff(tail, 0)
        assert abs(derivative) > mp.mpf('1e-12')
        assert abs(derivative) < bound['weighted_directional_tail_upper'][0, 0]


@pytest.mark.parametrize('field,value', [('weight', [-1.]), ('Mu', [float('nan')]),
    ('deltaA', [[1., 2., 3.]])])
def test_bad_primitive_bounds_rejected(field, value):
    constants, _ = certify_generalized_even_pencil(*fixture())
    p = dict(u=[1.], Au=[2.], Mu=[.5], deltaA=[[0., 0.]], deltaMu=[[0., 0.]],
        measure=[[0., 0.]], weight=[.2]); p[field] = value
    with pytest.raises(ValueError):
        even_y_tail_bounds(constants, .7, .05, .004, p, grading_preserving_variations=True)


def test_norm_bounds_alone_cannot_certify_directional_evenness():
    constants, _ = certify_generalized_even_pencil(*fixture())
    p = dict(u=[1.], Au=[2.], Mu=[.5], deltaA=[[0.]], deltaMu=[[0.]],
        measure=[[0.]], weight=[.2])
    for unproved in (False, None, 'True', 1):
        with pytest.raises(ValueError, match='grading-preserving'):
            even_y_tail_bounds(constants, .7, .05, .004, p,
                grading_preserving_variations=unproved)


def test_coupling_outside_circle_and_reversed_order_rejected():
    constants, _ = certify_generalized_even_pencil(*fixture())
    with pytest.raises(ValueError, match='outside'):
        even_y_tail_bounds(constants, .7, 2., .004)
    with pytest.raises(ValueError, match='exceed'):
        even_y_tail_bounds(constants, .7, .004, .05)


def test_precision_restored_after_success_or_rejection():
    previous = ctx.prec
    certify_generalized_even_pencil(*fixture())
    assert ctx.prec == previous
    f = list(fixture()); f[3] = -f[3]
    with pytest.raises(ValueError):
        certify_generalized_even_pencil(*f)
    assert ctx.prec == previous
