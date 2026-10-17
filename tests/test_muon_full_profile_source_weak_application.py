from types import SimpleNamespace

import numpy as np
import pytest

import bhsm.interface.muon_full_profile_source_weak_application as owner
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP


def _fixture(monkeypatch):
    rng = np.random.default_rng(71392)
    rho = np.array([.2, .6])
    rep = dict(rho=rho, radial_quadrature=np.array([.4, .6]), cap_points=3,
        scalar_matching=dict(lambda_H=.13),
        gauge_basis=rng.normal(size=(2, 80, 1, 5, 4))*.03,
        gauge_radial_basis=rng.normal(size=(2, 80, 1, 5, 4))*.04,
        wall_trace_map=rng.normal(size=(5, 4, 80))*.03)
    pg = rng.normal(size=(3, 100))*.015 + .004j*rng.normal(size=(3, 100))
    dg = rng.normal(size=(5, 100))*.01 + .003j*rng.normal(size=(5, 100))
    wg = rng.normal(size=(3, 100))*.012 + .002j*rng.normal(size=(3, 100))
    p0 = np.array([1.03+.01j, .02-.003j, -.01+.004j])
    d0 = np.array([1.1+.02j, .9+.01j, .8-.01j, 1.2+.03j, .07+.02j])
    w0 = np.array([.9+.01j, 1.1-.02j, .7+.005j])

    def geometry(raw, points, **kwargs):
        p, d = p0+pg@raw, d0+dg@raw
        rows = []
        for point in points:
            row = {}
            for i, key in enumerate(('connection_lambda', 'lambda_tau', 'lambda_rho')):
                row[key] = SimpleNamespace(value=p[i]+.001*point,
                    gradient=pg[i].copy())
            for i, key in enumerate(('electric', 'radial', 'angular', 'electric_radial', 'shift')):
                row[key] = SimpleNamespace(value=d[i]+.002*point,
                    gradient=dg[i].copy())
            rows.append(row)
        return dict(rows=rows)

    def cap(raw, **kwargs):
        return {key:SimpleNamespace(value=w0[i]+wg[i]@raw,
                    gradient=wg[i].copy())
                for i, key in enumerate(('wT', 'wS', 'wV'))}

    monkeypatch.setattr(owner, 'holomorphic_geometry_rows', geometry)
    monkeypatch.setattr(owner, 'holomorphic_cap_and_weights', cap)
    lift = np.zeros((536, 504), complex)
    lift[:504] = np.eye(504)
    lift[504:] = np.eye(504)[:32]*(.6+.1j)

    def action(raw):
        parent = geometry(raw[0, :100], rho)['rows']
        eff = np.array([[p[k].value for k in
                        ('connection_lambda', 'lambda_tau', 'lambda_rho')]
                        for p in parent])
        gb = rep['gauge_basis'][:, :, 0].reshape(2, 80, 20)
        gr = rep['gauge_radial_basis'][:, :, 0].reshape(2, 80, 20)
        A = np.einsum('rjc,j->rc', gb, raw[1, 100:180]).reshape(2, 5, 4)
        At = np.einsum('rjc,j->rc', gb, raw[1, 180:260]).reshape(2, 5, 4)
        Ar = np.einsum('rjc,j->rc', gr, raw[1, 100:180]).reshape(2, 5, 4)
        A[:, 2:] += M[None]*(eff[:, 0]-1)[:, None, None]
        At[:, 2:] += M[None]*eff[:, 1, None, None]
        Ar[:, 2:] += M[None]*eff[:, 2, None, None]
        wall = np.einsum('fcj,j->fc', rep['wall_trace_map'], raw[1, 100:180])
        wall[2:] += M*(geometry(raw[0, :100], [owner.WALL])['rows'][0]
                          ['connection_lambda'].value-1)
        return dict(master_lift=lift, branch_fields=[{},
                    dict(A=A, At=At, Ar=Ar, wall=wall)])

    def literal_value(raw, source, wall_source, epsilon):
        fields = action(raw)['branch_fields'][1]
        density = np.array([[r[k].value for k in
                    ('electric', 'radial', 'angular', 'electric_radial', 'shift')]
                    for r in geometry(raw[1, :100], rho)['rows']])
        # Only literal action VALUE owners are used in this independent
        # polynomial derivative; no Hessian or weak source map is reused.
        local = owner.analytic_constant_maxwell_batch(
            fields['A']+epsilon*source[0],
            fields['At']+epsilon*source[1],
            fields['Ar']+epsilon*source[2], density)['value']
        scalar = owner.analytic_intrinsic_n0_jet(
            fields['wall']+epsilon*wall_source[0],
            raw[1, 260:264], raw[1, 264:],
            np.array([x.value for x in cap(raw[1, :100]).values()]),
            lambda_H=.13, nu_squared_action=4)['value']
        return MAXWELL_TO_CAP*(rep['radial_quadrature']@local)+scalar

    return rng, rep, action, literal_value, lift


def _polynomial_first(values, points):
    V = np.vander(points, N=len(points), increasing=True)
    target = np.zeros(len(points)); target[1] = 1
    return np.linalg.solve(V.T, target)@np.asarray(values)


def test_full_complex_source_weak_dual_matches_literal_mixed_action(monkeypatch):
    rng, rep, action, literal_value, lift = _fixture(monkeypatch)
    raw = .02*rng.normal(size=(2, 268))+.008j*rng.normal(size=(2, 268))
    source = .04*rng.normal(size=(3, 2, 5, 4))+.02j*rng.normal(size=(3, 2, 5, 4))
    wall = .03*rng.normal(size=(3, 5, 4))+.015j*rng.normal(size=(3, 5, 4))
    a = owner.full_profile_source_weak_application(raw, rep, action(raw), source, wall)
    eps = np.arange(-2., 3.)

    def source_value(x):
        # Maxwell and scalar are degree <=4 in the supplied source.
        return _polynomial_first([literal_value(x, source, wall, e) for e in eps], eps)

    np.testing.assert_allclose(a['value_clock_first'], source_value(raw), atol=2e-14, rtol=2e-11)
    for _ in range(2):
        d = .005*rng.normal(size=504)+.002j*rng.normal(size=504)
        draw = (lift@d).reshape(2, 268)
        t = np.arange(-3., 4.)
        # At most degree6 after one gauge-source derivative, including
        # the moving beta/density and scalar weight cross contacts.
        mixed = _polynomial_first([source_value(raw+s*draw) for s in t], t)
        np.testing.assert_allclose(a['gradient_clock_first']@d, mixed,
                                   atol=4e-14, rtol=4e-9)
    assert np.linalg.norm(a['raw_gradient_clock_first'][:100]) > 0
    assert np.linalg.norm(a['raw_gradient_clock_first'][268:368]) > 0
    assert np.linalg.norm(a['raw_gradient_clock_first'][528:]) > 0
    assert not a['source_coefficients_conjugated']
    assert not a['finite_coefficient_restriction_used']


def test_full_represented_complement_additivity_and_wall_slots(monkeypatch):
    rng, rep, action, _, _ = _fixture(monkeypatch)
    raw = .02*rng.normal(size=(2, 268))+.006j*rng.normal(size=(2, 268))
    s1 = rng.normal(size=(3, 2, 5, 4))*.03
    s2 = 1j*rng.normal(size=s1.shape)*.02
    w1 = rng.normal(size=(3, 5, 4))*.02
    w2 = 1j*rng.normal(size=w1.shape)*.03
    apply = lambda s, w:owner.full_profile_source_weak_application(raw, rep, action(raw), s, w)
    full, first, complement = apply(s1+s2, w1+w2), apply(s1, w1), apply(s2, w2)
    np.testing.assert_allclose(full['gradient_clock_first'],
        first['gradient_clock_first']+complement['gradient_clock_first'], atol=1e-16)
    np.testing.assert_allclose(full['value_clock_first'],
        first['value_clock_first']+complement['value_clock_first'], atol=1e-16)
    wout = w1.astype(complex); wout[1:] += 100+30j
    separate = apply(s1, wout)
    np.testing.assert_array_equal(separate['gradient_clock_first'], first['gradient_clock_first'])
    np.testing.assert_array_equal(separate['full_material_wall_source'], wout)
    with pytest.raises(ValueError, match='full three-slot'):
        apply(s1[0], w1)
