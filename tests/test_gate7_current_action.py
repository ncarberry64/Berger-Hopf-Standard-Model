from pathlib import Path
import sys
import mpmath as mp
import pytest
from flint import arb, arb_mat, ctx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from bhsm.interface.gate7_current_action import (
    ActionBase, ActionSector, ImplicitAction, evaluate_gate7_current_action,
)
from bhsm.interface.arb_heat_pencil_contractions import HeatPencil, trace_product
from bhsm.interface.arb_zeta_contractions import zeta_first


def agrees(ball, value):
    return ball.overlaps(arb(mp.nstr(value, 90))+arb(0, arb('1e-88')))


def nonlinear_objective():
    # An exact small test, not BHSM data. F=n-x^2-y*p0-x*p1.
    # Gamma=n^2/2+x*n+x*y+p0*y^2/2, so Gamma_n is not zero.
    base = ActionBase('test-state', 'test-coeff', 'test-clock', 'test-F', 'test-contact', 'test-frame')
    x, y, p0, p1 = map(arb, ['1', '2', '.3', '-.4'])
    n = x*x+y*p0+x*p1
    def product(kind, direction, dn):
        if kind == 'H':
            xx = arb_mat([[0, 1], [1, p0]])
            a = xx*direction+arb_mat([[dn[0, 0]], [0]])
            b = arb_mat([[direction[0, 0]+dn[0, 0]]])
        else:
            a = arb_mat([[dn[0, 0]], [y*direction[0, 0]]])
            b = dn
        return a, b
    def residual(kind, direction, dn, eta):
        if kind == 'H':
            return arb_mat([[-2*eta[0, 0]*direction[0, 0]], [0]]), arb_mat(1, 1)
        return arb_mat([[-eta[0, 0]*direction[1, 0]],
                        [-eta[0, 0]*direction[0, 0]]]), arb_mat(1, 1)
    sector = ActionSector('action-and-residual-curvature', base,
                          arb_mat([[n+y], [x+p0*y]]), arb_mat([[n+x]]), product)
    return ImplicitAction(base, arb_mat([[1]]), arb_mat([[-2*x-p1, -p0]]),
                          lambda v: arb_mat([[-y*v[0, 0]-x*v[1, 0]]]),
                          (sector,), (sector.name,), 'algebraic test', {'uniform': None}, residual)


def test_products_equal_reduced_nonlinear_action_with_nonstationary_internal_objective():
    ctx.prec = 384
    query = nonlinear_objective()
    u = arb_mat([[2], [-1]])
    v = arb_mat(73, 1); v[0, 0] = -1; v[1, 0] = 2
    result = evaluate_gate7_current_action(query, dict(q66=True, H66_u=u, B66x73_v=v))
    with mp.workdps(100):
        def G(x, y, p, r):
            n = x*x+y*p+x*r
            return n*n/2+x*n+x*y+p*y*y/2
        p, r = mp.mpf('.3'), mp.mpf('-.4')
        for i in range(2):
            def gradient(t, w):
                a = [1+2*t, 2-t, p-w, r+2*w]
                return mp.diff(lambda z: G(*(a[:i]+[z]+a[i+1:])), a[i])
            assert agrees(result['q66'][i, 0], gradient(0, 0))
            assert agrees(result['H66_u'][i, 0], mp.diff(lambda t: gradient(t, 0), 0))
            assert agrees(result['B66x73_v'][i, 0], mp.diff(lambda w: gradient(0, w), 0))
    assert result['errors']['uniform'] is None
    for k, m in result.items():
        if k.endswith('replay'):
            assert all(v.contains(0) for v in m.entries())


def test_force_does_not_request_curvature_and_mixed_base_is_rejected():
    query = nonlinear_objective()
    query.sectors[0].objective_product = None
    assert 'q66' in evaluate_gate7_current_action(query, {'q66': True})
    with pytest.raises(ValueError, match='curvature missing'):
        evaluate_gate7_current_action(query, {'H66_u': arb_mat([[1], [0]])})
    query.sectors[0].base = ActionBase('other', 'c', 'd', 'n', 'w', 'r')
    with pytest.raises(ValueError, match='mixed-base'):
        evaluate_gate7_current_action(query, {'q66': True})


def test_signed_internal_sectors_combine_before_adjoint_and_norm():
    query = nonlinear_objective()
    s = query.sectors[0]
    query.sectors = (ActionSector('plus', s.base, s.gamma_xi, s.gamma_n),
                     ActionSector('minus', s.base, -s.gamma_xi, -s.gamma_n))
    query.required_sectors = ('plus', 'minus')
    result = evaluate_gate7_current_action(query, {'q66': True})
    assert all(v.contains(0) for v in result['q66'].entries())
    query.required_sectors += ('missing',)
    with pytest.raises(ValueError, match='omitted'):
        evaluate_gate7_current_action(query, {'q66': True})


def test_generalized_pencil_mixed_matches_actual_action_with_moving_mass():
    ctx.prec = 384
    K = arb_mat([[3, 1], [1, 4]]); M = arb_mat([[2, 0], [0, 1]])
    Kb = arb_mat([[1, 2], [2, -1]]); Kp = arb_mat([[2, -1], [-1, 3]])
    Mb = arb_mat([[1, 1], [1, 0]]); Mp = arb_mat([[0, -1], [-1, 2]])
    Kbp = arb_mat([[0, 1], [1, 2]]); Mbp = arb_mat([[1, 0], [0, -1]])
    pencil = HeatPencil(K, M)
    mixed = pencil.mixed(Kb, Mb, Kp, Mp, Kbp, Mbp)
    reverse = pencil.mixed(Kp, Mp, Kb, Mb, Kbp, Mbp)
    assert (mixed['value']-reverse['value']).contains(0)
    with mp.workdps(100):
        mats = [mp.matrix([[int(float(v[i, j])) for j in range(2)] for i in range(2)])
                for v in (K, M, Kb, Kp, Mb, Mp, Kbp, Mbp)]
        k, m, kb, kp, mb, mp_, kbp, mbp = mats
        def gamma(b, p):
            A = (m+b*mb+p*mp_+b*p*mbp)**-1*(k+b*kb+p*kp+b*p*kbp)
            tr = A[0, 0]+A[1, 1]; det = mp.det(A)
            disc = mp.sqrt(tr*tr-4*det)
            return -(mp.e1((tr-disc)/2)+mp.e1((tr+disc)/2))/2
        assert agrees(pencil.first(Kb, Mb), mp.diff(lambda b: gamma(b, 0), 0))
        assert agrees(mixed['value'], mp.diff(lambda b: mp.diff(lambda p: gamma(b, p), 0), 0))
    # Keeping only K jets changes the same-action derivative.
    assert not pencil.first(Kb, Mb).overlaps(pencil.first(Kb, arb_mat(2, 2)))


def test_pencil_basis_covariance_and_common_scale_ward_identity():
    ctx.prec = 384
    K = arb_mat([[3, 1], [1, 4]]); M = arb_mat([[2, 0], [0, 1]])
    E = arb_mat([[1, 2], [2, -1]]); D = arb_mat([[1, 0], [0, -1]])
    S = arb_mat([[1, 2], [0, 1]])
    a = HeatPencil(K, M)
    b = HeatPencil(S.transpose()*K*S, S.transpose()*M*S)
    assert (a.first(E, D)-b.first(S.transpose()*E*S, S.transpose()*D*S)).contains(0)
    ward = -sum((a.exponential[i, i] for i in range(2)), arb(0))
    # K -> exp(-t)K and M -> exp(t)M under a joint length scale.
    assert (a.first(-K, M)-ward).contains(0)


def test_interior_heat_information_survives_equal_boundary_schur_response():
    ctx.prec = 384
    M = arb_mat([[1, 0], [0, 1]])
    first = HeatPencil(arb_mat([[2, 0], [0, 3]]), M)
    second = HeatPencil(arb_mat([[4, 0], [0, 3]]), M)
    jet = arb_mat([[1, 0], [0, 0]])
    # Boundary node 1 has identical Schur response; the interior force differs.
    assert not first.first(jet, arb_mat(2, 2)).overlaps(second.first(jet, arb_mat(2, 2)))


def test_nonpositive_pencil_rejected():
    with pytest.raises(ValueError, match='positive form'):
        HeatPencil(arb_mat([[0]]), arb_mat([[1]]))


def test_zeta_streaming_has_moving_duration_and_preserves_action_constant():
    ctx.prec = 384
    c = arb(float(59/30))
    x = [arb('.1'), arb('.15')]; h = [arb('.4')]
    z = zeta_first(x, h, arb_mat([[2], [-1]]), arb_mat([[3]]), coefficient=c)
    with mp.workdps(100):
        cf = mp.mpf(float(59/30))
        def action(t):
            return -cf*(mp.mpf('.4')+3*t)*mp.quad(
                lambda u: mp.exp(-mp.mpf('.1')-2*t-u*(mp.mpf('.05')-3*t)), [0, 1])
        assert agrees(z['value'], action(0))
        assert agrees(z['first'][0, 0], mp.diff(action, 0))
    rational = zeta_first(x, h, arb_mat([[2], [-1]]), arb_mat([[3]]), coefficient=arb(59)/30)
    assert not z['value'].overlaps(rational['value'])
