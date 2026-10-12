"""Independent pointwise second variation of the complexified real action.

This control evaluates actual n1 fields on the owned Haar quadrature.  It
does not use the compiler's curvature maps or an adjoint of the continued
background.  It covers the source angular orientation E*a as well as the
complete original At/gauge/H layout and both mixed time placements.
"""
import numpy as np

from bhsm.interface.muon_chronological_harmonic_field_action import (
    analytic_homogeneous_original_field_forms,
)
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_matched_mechanical_source import epsilon
from bhsm.interface.muon_nonlinear_chronological_n0_action import chronological_n0_field_lifts
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP


def _fixture():
    rng = np.random.default_rng(20261012)
    phi, phir = rng.normal(size=(2, 3, 4))
    phi_wall = rng.normal(size=4)
    unit = np.eye(20).reshape(20, 5, 4)
    basis = np.array([np.concatenate([b * unit for b in p]) for p in phi])[:, :, None]
    radial = np.array([np.concatenate([b * unit for b in p]) for p in phir])[:, :, None]
    wall = np.concatenate([b * np.eye(20) for b in phi_wall], axis=1).reshape(5, 4, 80)
    labels = [dict(field=('A_tau', 'A_rho', 'A_1', 'A_2', 'A_3')[f], internal=c)
              for _ in range(4) for f in range(5) for c in range(4)]
    ids = np.r_[[j for j, l in enumerate(labels) if l['field'] == 'A_tau'],
                [j for j, l in enumerate(labels) if l['field'] != 'A_tau'], np.arange(80, 84)]
    rep = dict(gauge_basis=basis, gauge_radial_basis=radial, wall_trace_map=wall,
               gauge_labels=labels, radial_quadrature=np.array([.13, .2, .27]))
    def complex_array(shape, scale):
        return scale * (rng.normal(size=shape) + .2j * rng.normal(size=shape))
    row = dict(A=complex_array((3, 5, 4), .14), At=complex_array((3, 5, 4), .03),
               Ar=complex_array((3, 5, 4), .04), wall_A=complex_array((5, 4), .12),
               densities=np.tile([1.3, .8, .7, 1.1, .12], (3, 1)) + complex_array((3, 5), .05),
               H=np.array([.3, .8, .11, -.06]) + complex_array((4,), .02),
               Hdot=complex_array((4,), .03), weights=np.array([1.2, .7, .9]) + .03j,
               lambda_H=.129 + .007j, nu_squared_action=4.)
    directions = [complex_array((84, 4), .07) for _ in range(4)]
    return row, chronological_n0_field_lifts(rep, ids), directions


def _bracket(a, b):
    out = np.zeros(np.broadcast_shapes(a.shape, b.shape), complex)
    out[..., :3] = np.cross(a[..., :3], b[..., :3]) / np.sqrt(2)
    return out


def _curvature(a, at, ar, ea):
    spatial = a[..., 2:, :]
    x = at[..., 1, :] - ar[..., 0, :] + _bracket(a[..., 0, :], a[..., 1, :])
    ft = at[..., 2:, :] - ea[..., :, 0, :] + _bracket(a[..., 0, None, :], spatial)
    fr = ar[..., 2:, :] - ea[..., :, 1, :] + _bracket(a[..., 1, None, :], spatial)
    b = 2 * spatial + np.einsum('ijk,...jkc->...ic', epsilon(), ea[..., :, 2:, :])
    for i, j, k in np.argwhere(epsilon()):
        b[..., i, :] += .5 * epsilon()[i, j, k] * _bracket(spatial[..., j, :], spatial[..., k, :])
    return x, ft, fr, b


def _first_curvature(a, u, ut, ur, eu):
    # This is the literal derivative of the four pointwise curvature equations.
    x = ut[..., 1, :] - ur[..., 0, :] + _bracket(u[..., 0, :], a[..., 1, :]) + _bracket(a[..., 0, :], u[..., 1, :])
    ft = ut[..., 2:, :] - eu[..., :, 0, :] + _bracket(u[..., 0, None, :], a[..., 2:, :]) + _bracket(a[..., 0, None, :], u[..., 2:, :])
    fr = ur[..., 2:, :] - eu[..., :, 1, :] + _bracket(u[..., 1, None, :], a[..., 2:, :]) + _bracket(a[..., 1, None, :], u[..., 2:, :])
    b = 2 * u[..., 2:, :] + np.einsum('ijk,...jkc->...ic', epsilon(), eu[..., :, 2:, :])
    for i, j, k in np.argwhere(epsilon()):
        b[..., i, :] += epsilon()[i, j, k] * _bracket(a[..., 2+j, :], u[..., 2+k, :])
    return x, ft, fr, b


def _second_curvature(u, v):
    x = _bracket(u[..., 0, :], v[..., 1, :]) + _bracket(v[..., 0, :], u[..., 1, :])
    ft = _bracket(u[..., 0, None, :], v[..., 2:, :]) + _bracket(v[..., 0, None, :], u[..., 2:, :])
    fr = _bracket(u[..., 1, None, :], v[..., 2:, :]) + _bracket(v[..., 1, None, :], u[..., 2:, :])
    b = np.zeros_like(ft)
    for i, j, k in np.argwhere(epsilon()):
        b[..., i, :] += epsilon()[i, j, k] * _bracket(u[..., 2+j, :], v[..., 2+k, :])
    return x, ft, fr, b


def _literal_pair(row, lifts, Y, EY, haar, u, ud, v, vd):
    count, points = len(lifts['P']), len(Y)
    def gauge_image(x, xt):
        coef = np.einsum('ria,ah->rih', lifts['P'], x).reshape(count, 5, 4, 4)
        value = np.einsum('rfch,ph->rpfc', coef, Y)
        rate = np.einsum('ria,ah,ph->rpi', lifts['Pt'], xt, Y).reshape(count, points, 5, 4)
        radial = np.einsum('ria,ah,ph->rpi', lifts['Pr'], x, Y).reshape(count, points, 5, 4)
        angular = np.einsum('rfch,pih->rpifc', coef, EY)
        return value, rate, radial, angular
    gu, gv = gauge_image(u, ud), gauge_image(v, vd)
    A, At, Ar = [np.broadcast_to(row[k][:, None], (count, points, 5, 4)) for k in ('A', 'At', 'Ar')]
    f = _curvature(A, At, Ar, np.zeros((count, points, 3, 5, 4)))
    fu, fv, fuv = _first_curvature(A, *gu), _first_curvature(A, *gv), _second_curvature(gu[0], gv[0])
    e, r, d, k, beta = np.asarray(row['densities']).T
    def shifted(curvature):
        return (curvature[0], curvature[1] - beta[:, None, None, None] * curvature[2], curvature[2], curvature[3])
    weights = (k, e, -r, -d)
    answer = 0j
    for background, du, dv, second, weight in zip(shifted(f), shifted(fu), shifted(fv), shifted(fuv), weights):
        pointwise = np.sum(du*dv + background*second, axis=tuple(range(2, background.ndim)))
        answer += MAXWELL_TO_CAP * np.einsum('r,p,rp,r->', lifts['radial_weights'], haar, pointwise, weight)
    T = higgs_u2_real_representation()['real_generators']
    def scalar_image(x, xt):
        return (np.einsum('ia,ah,ph->pi', lifts['hv'], x, Y),
                np.einsum('ia,ah,ph->pi', lifts['hv'], xt, Y),
                np.einsum('ia,ah,pjh->pji', lifts['hv'], x, EY),
                np.einsum('ia,ah,ph->pi', lifts['W'], x, Y).reshape(points, 5, 4))
    hu, htu, ehu, au = scalar_image(u, ud)
    hv, htv, ehv, av = scalar_image(v, vd)
    H, Hd = row['H'], row['Hdot']
    O = np.einsum('fc,cij->fij', row['wall_A'], T)
    for f, w in zip((0, 2, 3, 4), (row['weights'][0], *[-row['weights'][1]]*3)):
        Ou, Ov = np.einsum('pc,cij->pij', au[:, f], T), np.einsum('pc,cij->pij', av[:, f], T)
        dh = (Hd if f == 0 else 0) + O[f]@H
        du = (htu if f == 0 else ehu[:, f-2]) + hu@O[f].T + np.einsum('pij,j->pi', Ou, H)
        dv = (htv if f == 0 else ehv[:, f-2]) + hv@O[f].T + np.einsum('pij,j->pi', Ov, H)
        second = np.einsum('pij,pj->pi', Ou, hv) + np.einsum('pij,pj->pi', Ov, hu)
        answer += 2*w/(2*np.pi**2) * np.einsum('p,pi,pi->', haar, du, dv)
        answer += 2*w/(2*np.pi**2) * np.einsum('p,i,pi->', haar, dh, second)
    potential = row['lambda_H'] * (8*np.outer(H, H) + 4*(H@H-row['nu_squared_action'])*np.eye(4))
    answer -= row['weights'][2]/(2*np.pi**2) * np.einsum('p,pi,ij,pj->', haar, hu, potential, hv)
    return answer


def test_complex_n1_full_original_action_pair_matches_literal_haar_curvature_and_higgs():
    row, lifts, (u, ud, v, vd) = _fixture()
    angular = scalar_s3_discretization(1)
    ids = np.flatnonzero([label[0] == 1 for label in angular['real_basis_labels']])
    Y = angular['real_basis_values'][:, ids]
    EY = angular['real_basis_derivative_values'][:, :, ids]
    E = angular['real_angular_derivative_matrices'][:, ids][:, :, ids]
    form = analytic_homogeneous_original_field_forms(row, np.zeros(84), np.zeros(84), lifts, E)
    actual = (u.ravel()@form['K']@v.ravel() + u.ravel()@form['B_forward']@vd.ravel()
              + ud.ravel()@form['B_reverse']@v.ravel() + ud.ravel()@form['M']@vd.ravel())
    expected = _literal_pair(row, lifts, Y, EY, angular['haar_weights'], u, ud, v, vd)
    np.testing.assert_allclose(actual, expected, rtol=3e-12, atol=3e-13)
    # A Hilbert dagger of complexified real field coefficients changes the action.
    dagger_pair = (u.ravel().conj()@form['K']@v.ravel() + u.ravel().conj()@form['B_forward']@vd.ravel()
                   + ud.ravel().conj()@form['B_reverse']@v.ravel() + ud.ravel().conj()@form['M']@vd.ravel())
    assert abs(dagger_pair-expected) > 1e-4
