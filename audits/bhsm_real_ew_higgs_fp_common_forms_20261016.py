"""Actual saved-real EW4/Higgs/FP coefficient-cell test complex.

The existing positive-ADM constituent forms are bound to the same frozen
real D5 midpoint coefficients. These classical forms are not P_strat.
Potential coefficients remain polynomial; no matching value is selected.
The eight color directions, physical reset and global BRST quotient are
explicitly outside this EW4 component, rather than counted or set to zero.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import cho_factor, cho_solve
from scipy.sparse import csr_matrix

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm.interface.muon_birth_trace_enriched_action import trace_enriched_radial_basis
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_matched_mechanical_source import epsilon
from bhsm.interface.muon_moving_geometric_action import _fields
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
from bhsm.interface.muon_parent_maxwell_corrected_retarded import constant_angular_curvatures
from bhsm.interface.muon_parent_maxwell_full_weak import FIELD_ORDER, M
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
from bhsm.interface.muon_parent_positive_brst_ghost import (
    ghost_radial_values, smooth_ghost_temporal_values, ghost_temporal_moments,
    _ghost_form_row, covariant_ghost_gradient_images)
from bhsm.interface.muon_parent_positive_coupled_field import coupled_wall_maps, VOLUME
from bhsm.interface.muon_parent_positive_coupled_temporal import (
    one_form_point_row, paired_scalar_orbit_maps, intrinsic_coupled_point_form)
from bhsm.interface.muon_parent_positive_gauge_form import one_form_cell_row, one_form_temporal_moments
from bhsm.interface.muon_parent_retarded_hypercharge import WALL

SOURCE = 'artifacts/muon_real_coupled_open_operator_20261016/source_first_run_1'
SOURCE_JSON_SHA = 'd15def102e329c38f35b62c137d8398aa72eeda626924498a426246d66c88df1'
SOURCE_NPZ_SHA = '7da8ddd5fa4bda397aa6a2d50e845338a3ef92fb3f0e837a5a6d0d166915e177'
BASE = 'artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1'
BASE_JSON_SHA = '06867e31959910ec21385e8491bd5b794060c68e8404ae0524e3d0c9b544faa6'
BASE_NPZ_SHA = 'c67363c17adfb519f399614463d5a13dbcd019aa53246d452421eea8ba982455'


def norm(a):
    return float(np.linalg.norm(a))


def maximum(a):
    return float(np.max(np.abs(a)))


def real(a, name):
    a = np.asarray(a)
    if not np.isfinite(a).all() or np.any(a.imag != 0):
        raise ValueError('Exact real saved operand required: ' + name)
    return np.asarray(a.real, float)


def save_sparse(arrays, name, value):
    s = csr_matrix(value)
    arrays[name + '_data'] = s.data
    arrays[name + '_indices'] = s.indices
    arrays[name + '_indptr'] = s.indptr
    arrays[name + '_shape'] = np.asarray(s.shape, np.int64)


def positive_geometry(c, raw):
    """Existing YM pushforward pairing, not bare fermion NCR^3 pairing."""
    q, v, m = ([Jet.constant(float(x), 0) for x in a]
               for a in (raw[:37], raw[37:74], raw[74:98]))
    metric, density, common = [], [], []
    for j, rho in enumerate(c['radial_points']):
        f = _fields(12, q, v, m, rho * c['material_wall'][j] / WALL)
        LF = np.sqrt(f['A'].value ** 2 + f['B'].value ** 2)
        # Both factors are retained, avoiding a second subtraction of squares.
        w = (1 - 2 * c['sigma'][j]) * (1 + 2 * c['sigma'][j])
        push = 2 * np.pi ** 4 * LF ** 5 * w
        N, C, R, z = (c[k][j] for k in ('lapse', 'radial_coframe', 'radius', 'coordinate_shift'))
        e, r, d, k = push * np.array([C * R / N, N * R / C, N * C / R, R ** 3 / (N * C)])
        if min(push, N, C, R, e, r, d, k) <= 0:
            raise ValueError('Positive regular source constituent pairing required')
        metric.append((d * R ** 4, e * R ** 2, r * R ** 2, d * R ** 2, z, R))
        density.append((e, r, d, k, z))
        common.append(push)
    return np.array(metric), np.array(density), np.array(common)


def scalar_point(weights, H, Hd, A, E, W, hs):
    """Exact coefficient polynomial Kkin + lambda*K4 + lambda*nu²*K2."""
    wt, ws, wv = weights
    T = higgs_u2_real_representation()['real_generators']
    O = np.einsum('fc,cij->fij', A, T)
    U = np.einsum('cij,j->ci', T, H)
    dt, ds = Hd + O[0] @ H, O[2:] @ H
    h, ht = hs['value'], hs['time']
    wr = W.reshape(5, 80, 1200)
    K = np.zeros((1200, 1200))
    derivatives = []
    for f, mu in ((0, wt), (2, ws), (3, ws), (4, ws)):
        ordinary = ht if f == 0 else np.kron(np.eye(4), E[f - 2]) @ h
        derivative = ordinary + np.kron(O[f], np.eye(20)) @ h + np.kron(U.T, np.eye(20)) @ wr[f]
        base = dt if f == 0 else ds[f - 2]
        cross = wr[f].T @ np.kron(np.einsum('i,cij->cj', base, T), np.eye(20)) @ h
        K += 2 * mu / VOLUME * (derivative.T @ derivative + cross + cross.T)
        derivatives.append(derivative)
    K4 = 2 * wv / VOLUME * h.T @ np.kron(4 * np.outer(H, H) + 2 * (H @ H) * np.eye(4), np.eye(20)) @ h
    K2 = -4 * wv / VOLUME * h.T @ h
    G = 2 * wv / VOLUME * h.T @ h
    return K, K4, K2, G, np.array(derivatives), dt, ds


def trial_maps(A, At, Ar, E, radial, temporal):
    """Literal same one-form functions and all their first coordinate jets."""
    t = temporal
    I = np.eye(400).reshape(5, 80, 400)
    value = np.zeros((5, 80, 1120))
    time, rho = value.copy(), value.copy()
    value[:, :, :800] = t[0] * np.concatenate([r[0] * I for r in radial], axis=2)
    time[:, :, :800] = t[1] * np.concatenate([r[0] * I for r in radial], axis=2)
    rho[:, :, :800] = t[0] * np.concatenate([r[1] * I for r in radial], axis=2)
    Ef = np.array([np.kron(np.eye(4), e) for e in E])
    angle = np.einsum('aij,fjz->afiz', Ef, value)
    g = covariant_ghost_gradient_images(A, At, Ar, E,
        np.array([[t[2], t[3], t[6]], [t[4], t[5], t[7]]]), radial)
    value[:, :, 800:] = g['value']
    time[:, :, 800:] = g['time']
    rho[:, :, 800:] = g['radial']
    angle[:, :, :, 800:] = g['angular']
    return (value, time, rho, angle), g


def bracket(a, b):
    out = np.zeros(np.broadcast_shapes(a.shape, b.shape))
    out[..., :3] = np.einsum('ijk,...j,...k->...i', epsilon(), a[..., :3], b[..., :3]) / np.sqrt(2)
    return out


def literal_curvatures(A, At, Ar, Ea):
    X = At[:, 1] - Ar[:, 0] + bracket(A[:, 0], A[:, 1])
    Ft = np.array([At[:, 2 + i] - Ea[i, :, 0] + bracket(A[:, 0], A[:, 2 + i]) for i in range(3)])
    Fr = np.array([Ar[:, 2 + i] - Ea[i, :, 1] + bracket(A[:, 1], A[:, 2 + i]) for i in range(3)])
    B = 2 * A[:, 2:].transpose(1, 0, 2).copy()
    for i, j, k in np.argwhere(epsilon()):
        B[i] += epsilon()[i, j, k] * (Ea[j, :, 2 + k] + .5 * bracket(A[:, 2 + j], A[:, 2 + k]))
    return X, Ft, Fr, B


def literal_first_curvatures(A, a, at, ar, ea):
    X = at[:, 1] - ar[:, 0] + bracket(A[:, 0], a[:, 1]) - bracket(A[:, 1], a[:, 0])
    Ft = np.array([at[:, 2 + i] - ea[i, :, 0] + bracket(A[:, 0], a[:, 2 + i]) - bracket(A[:, 2 + i], a[:, 0]) for i in range(3)])
    Fr = np.array([ar[:, 2 + i] - ea[i, :, 1] + bracket(A[:, 1], a[:, 2 + i]) - bracket(A[:, 2 + i], a[:, 1]) for i in range(3)])
    B = 2 * a[:, 2:].transpose(1, 0, 2).copy()
    for i, j, k in np.argwhere(epsilon()):
        B[i] += epsilon()[i, j, k] * (ea[j, :, 2 + k] + bracket(A[:, 2 + j], a[:, 2 + k]))
    return X, Ft, Fr, B


def curved_pair(F, G, density, haar):
    e, r, d, k, z = density
    X, T, R, B = F
    x, t, rr, b = G
    return float(k * np.einsum('p,pc,pc', haar, X, x)
        + e * np.einsum('p,ipc,ipc', haar, T - z * R, t - z * rr)
        + r * np.einsum('p,ipc,ipc', haar, R, rr) + d * np.einsum('p,ipc,ipc', haar, B, b))


def point_controls(A, At, Ar, E, Y, haar, radial, density, metric, H, Hd, weights, length):
    """Unprojected Haar action and independent off-shell Euler contact."""
    u = .37 * length
    tg = smooth_ghost_temporal_values([u], length)[0]
    t = np.r_[2 * u / length, 2 / length, tg[0, :2], tg[1, :2], tg[:, 2]]
    maps, g = trial_maps(A, At, Ar, E, radial, t)
    rp = one_form_point_row(A, At, Ar, E, radial, metric, density, t[:6])
    W = np.zeros((400, 1200))
    W[:, :1120] = rp['value_map']
    hs = paired_scalar_orbit_maps(H, Hd, t[:6], radial)
    K, K4, K2, G, deriv, dt, ds = scalar_point(weights, H, Hd, A, E, W, hs)
    owner = intrinsic_coupled_point_form(weights, H, Hd, A, E, W, hs['value'], hs['time'],
        lambda_H=1., nu_squared_action=0.)
    rows = np.arange(1, 1201)
    z = (np.cos(rows * .173) + np.sin(rows * .119)) / np.sqrt(1200)
    z[800:] *= length
    eta_coordinate = (np.cos(np.arange(1, 321) * .131) + .3 * np.sin(np.arange(1, 321) * .157)) / np.sqrt(320) * length
    d = np.zeros(1200)
    d[800:1120] = eta_coordinate
    ac = [np.einsum('fiz,z->fi', m, z[:1120]).reshape(5, 4, 20) for m in maps[:3]]
    a, at, ar = [np.einsum('ph,fch->pfc', Y, m) for m in ac]
    ea = np.einsum('ph,afch->apfc', Y, np.einsum('afiz,z->afi', maps[3], z[:1120]).reshape(3, 5, 4, 20))
    hc, htc = [(m @ z).reshape(4, 20) for m in (hs['value'], hs['time'])]
    h, ht = Y @ hc.T, Y @ htc.T
    eh = np.array([Y @ (hc @ e.T).T for e in E])
    ec = [(g[k] @ eta_coordinate).reshape(4, 20) for k in ('eta', 'eta_time', 'eta_radial')]
    eta, etat, etar = [Y @ m.T for m in ec]
    eeta = np.array([Y @ (ec[0] @ e.T).T for e in E])
    T = higgs_u2_real_representation()['real_generators']
    O = lambda f: np.einsum('pfc,cij->pfij', f, T)
    baseA = np.broadcast_to(A, (len(Y), 5, 4))
    baseAt, baseAr = [np.broadcast_to(m, baseA.shape) for m in (At, Ar)]
    zeroEa = np.zeros((3,) + baseA.shape)
    F = literal_curvatures(baseA, baseAt, baseAr, zeroEa)
    # Literal independent first variation of R_eta(z): ([a,eta],-eta*h).
    xi = bracket(a, eta[:, None])
    xit = bracket(at, eta[:, None]) + bracket(a, etat[:, None])
    xir = bracket(ar, eta[:, None]) + bracket(a, etar[:, None])
    exi = np.array([bracket(ea[i], eta[:, None]) + bracket(a, eeta[i, :, None]) for i in range(3)])
    dFxi = literal_first_curvatures(baseA, xi, xit, xir, exi)
    eulerYM = curved_pair(F, dFxi, density, haar)
    omega_eta = np.einsum('pc,cij->pij', eta, T)
    omega_etat = np.einsum('pc,cij->pij', etat, T)
    xih = -np.einsum('pij,pj->pi', omega_eta, h)
    xiht = -np.einsum('pij,pj->pi', omega_etat, h) - np.einsum('pij,pj->pi', omega_eta, ht)
    exih = np.array([-np.einsum('pij,pj->pi', np.einsum('pc,cij->pij', eeta[i], T), h)
                    - np.einsum('pij,pj->pi', omega_eta, eh[i]) for i in range(3)])
    oxi = O(xi)
    obase = O(baseA)
    dxih = np.empty((4, len(Y), 4))
    dxih[0] = xiht + np.einsum('pij,pj->pi', obase[:, 0], xih) + oxi[:, 0] @ H
    for i in range(3):
        dxih[i + 1] = exih[i] + np.einsum('pij,pj->pi', obase[:, 2 + i], xih) + oxi[:, 2 + i] @ H
    eulerKin = 2 / VOLUME * (weights[0] * np.einsum('p,i,pi', haar, dt, dxih[0])
        + weights[1] * np.einsum('p,ai,api', haar, ds, dxih[1:]))
    hxi = np.einsum('i,pi->p', H, xih)
    euler4 = 4 * weights[2] / VOLUME * (H @ H) * (haar @ hxi)
    euler2 = -4 * weights[2] / VOLUME * (haar @ hxi)
    ward = dict(YM=dict(Hessian=float(z[:1120] @ rp['Hessian'] @ d[:1120]), Euler=eulerYM),
        intrinsic_kinetic=dict(Hessian=float(z @ K @ d), Euler=float(eulerKin)),
        lambda_coefficient=dict(Hessian=float(z @ K4 @ d), Euler=float(euler4)),
        lambda_nu_squared_coefficient=dict(Hessian=float(z @ K2 @ d), Euler=float(euler2)))
    for w in ward.values():
        w['sum'] = w['Hessian'] + w['Euler']
        w['relative_to_nonzero_contact'] = abs(w['sum']) / max(abs(w['Hessian']), abs(w['Euler']), np.finfo(float).tiny)
    def value(s):
        curv = literal_curvatures(baseA + s * a, baseAt + s * at, baseAr + s * ar, s * ea)
        YM = .5 * curved_pair(curv, curv, density, haar)
        hh = H + s * h
        oo = O(baseA + s * a)
        dht = Hd + s * ht + np.einsum('pij,pj->pi', oo[:, 0], hh)
        dhs = np.array([s * eh[i] + np.einsum('pij,pj->pi', oo[:, 2 + i], hh) for i in range(3)])
        kin = (weights[0] * np.einsum('p,pi,pi', haar, dht, dht)
            + weights[1] * np.einsum('p,api,api', haar, dhs, dhs)) / VOLUME
        h2 = np.sum(hh ** 2, axis=1)
        return np.array([YM, kin, weights[2] / VOLUME * (haar @ (h2 ** 2)),
                         -2 * weights[2] / VOLUME * (haar @ h2)])
    target = np.array([z[:1120] @ rp['Hessian'] @ z[:1120], z @ K @ z, z @ K4 @ z, z @ K2 @ z])
    zero = value(0.)
    sweep = []
    for step in (.08, .04, .02):
        sec = (16 * (value(step) + value(-step) - 2 * zero)
               - (value(2 * step) + value(-2 * step) - 2 * zero)) / (12 * step ** 2)
        sweep.append(dict(step=step, literal=sec.tolist(), target=target.tolist(),
            absolute_error=np.abs(sec - target).tolist(),
            relative_to_nonzero=[float(abs(a - b) / abs(b)) if b else None for a, b in zip(sec, target)]))
    # A separate well-scaled intrinsic-scalar direction checks the actual
    # potential coefficients. It does not replace the unfavorable mixed
    # sweep above, whose h direction was scaled by the tiny cell length.
    zh = np.zeros(1200)
    zh[1120:] = np.cos(np.arange(1, 81) * .193) / np.sqrt(80)
    hh = Y @ (hs['value'] @ zh).reshape(4, 20).T
    target_h = np.array([zh @ K4 @ zh, zh @ K2 @ zh])
    def potential_value(s):
        h2 = np.sum((H + s * hh) ** 2, axis=1)
        return weights[2] / VOLUME * np.array([haar @ (h2 ** 2), -2 * (haar @ h2)])
    zero_h = potential_value(0.)
    potential_sweep = []
    for step in (.08, .04, .02):
        sec = (16 * (potential_value(step) + potential_value(-step) - 2 * zero_h)
               - (potential_value(2 * step) + potential_value(-2 * step) - 2 * zero_h)) / (12 * step ** 2)
        potential_sweep.append(dict(step=step, literal=sec.tolist(), target=target_h.tolist(),
            relative_to_nonzero=[float(abs(a - b) / abs(b)) if b else None for a, b in zip(sec, target_h)]))
    Hh = hh @ H
    hh2 = np.sum(hh ** 2, axis=1)
    direct_coefficients = weights[2] / VOLUME * np.array([
        haar @ (8 * Hh ** 2 + 4 * (H @ H) * hh2), -4 * (haar @ hh2)])
    return dict(scalar_polynomial_against_existing_owner_absolute=maximum(K + K4 - owner['Hessian']),
        scalar_polynomial_against_existing_owner_scaled=maximum(K + K4 - owner['Hessian']) / max(1., maximum(owner['Hessian'])),
        offshell_Ward_Euler_contacts=ward, literal_unprojected_Haar_action_second_sweep=sweep,
        separate_intrinsic_scalar_potential_second_sweep=potential_sweep,
        independent_Haar_potential_coefficient_relative=(abs(direct_coefficients - target_h) / abs(target_h)).tolist(),
        nonlinear_product_projected_back_to_n1_n3=False, potential_values_selected_for_physics=False)


def execute(output):
    out = Path(output)
    if out.exists():
        raise FileExistsError('Preserve independent readouts')
    pins = {}
    def pin(path, expected=None):
        p = ROOT / path
        h = sha256(p.read_bytes()).hexdigest()
        if expected is not None and h != expected:
            raise ValueError('Pinned bytes changed: ' + path)
        pins[path] = h
        return p
    pin(SOURCE + '/result.json', SOURCE_JSON_SHA)
    source_path = pin(SOURCE + '/application.npz', SOURCE_NPZ_SHA)
    base_receipt = json.loads(pin(BASE + '/result.json', BASE_JSON_SHA).read_text())
    with np.load(pin(BASE + '/application.npz', BASE_NPZ_SHA), allow_pickle=False) as z:
        rep = {k: z[k].copy() for k in ('affine_profile_reference_states', 'affine_interior_projection')}
    rep.update(affine_wall_coefficient=base_receipt['affine_profile_enrichment']['wall_coefficient'],
        affine_complement_norm=base_receipt['affine_profile_enrichment']['boundary_anchored_complement_norm'])
    with np.load(source_path, allow_pickle=False) as z:
        saved = {k: z[k].copy() for k in z.files if '_input_' in k}
    angular = scalar_s3_discretization(3)
    ids = np.array([i for i, row in enumerate(angular['real_basis_labels']) if row[0] in (1, 3)])
    E = angular['real_angular_derivative_matrices'][:, ids][:, :, ids]
    Y, haar = angular['real_basis_values'][:, ids], angular['haar_weights']
    x, w = np.polynomial.legendre.leggauss(4)
    rho, rw = (x + 1) * WALL / 2, w * WALL / 2
    allrho = np.r_[rho, WALL]
    basis, basisr = trace_enriched_radial_basis(rep, allrho)
    radial = ghost_radial_values(allrho)
    arrays = dict(radial_points=allrho, core_coordinate_weights=rw,
        exact_frozen_background_radial_basis=basis, exact_frozen_background_radial_basis_derivative=basisr,
        ghost_radial_value_rate_second=radial, EW_real_angular_derivatives=E)
    records = []
    for side, phase in (('incoming', 'artifacts/muon_finite_normal_phase_20261011/incoming_run_1'),
                        ('outgoing', 'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')):
        phase_receipt = json.loads(pin(phase + '/result.json').read_text())
        length = abs(float(phase_receipt['span']) / int(phase_receipt['steps']))
        prefix = side + '_input_'
        raw = real(saved[prefix + 'raw'], side + ' raw')
        c = {k[len(prefix):]: real(v, k) for k, v in saved.items() if k.startswith(prefix)
             and k not in (prefix + 'raw', prefix + 'rawtime')}
        if not np.array_equal(c['radial_points'], allrho):
            raise ValueError('Same frozen core4 plus separate wall required')
        A = np.einsum('ri,ifc->rfc', basis, raw[100:180].reshape(4, 5, 4))
        Ar = np.einsum('ri,ifc->rfc', basisr, raw[100:180].reshape(4, 5, 4))
        A[:, 2:] += M * (c['mechanical_profile'][:, 0, None, None] - 1)
        Ar[:, 2:] += M * c['mechanical_profile'][:, 2, None, None]
        At = c['gauge_connection_material_first'][0]
        Adefect = maximum(A - c['gauge_connection_material'])
        if Adefect > 1e-13:
            raise ValueError('Wrong original trace-enriched source basis')
        A = c['gauge_connection_material'].copy()
        metric, density, common = positive_geometry(c, raw)
        H, Hd = c['intrinsic_H_realified'], c['intrinsic_H_realified_first'][0]
        R, ell = c['radius'][-1], c['surface_proper_clock_rate'][-1]
        weights = np.array([R ** 3 / ell, ell * R, ell * R ** 3])
        moments = one_form_temporal_moments(length)
        gmoments = ghost_temporal_moments(length)
        K, G, contact = [np.zeros((1120, 1120)) for _ in range(3)]
        ghostK, ghostG = [np.zeros((320, 320)) for _ in range(2)]
        for j in range(4):
            k, g, cc = one_form_cell_row(A[j], At[j], Ar[j], E, radial[j], metric[j], density[j], moments)
            kg, gg = _ghost_form_row(A[j], E, radial[j], metric[j], gmoments)
            K += rw[j] * k
            G += rw[j] * g
            contact += rw[j] * cc
            ghostK += rw[j] * kg
            ghostG += rw[j] * gg
        B = np.zeros((320, 1200))
        B[:, :1120] = G[800:, :]
        F = cho_solve(cho_factor(ghostG, lower=True), B)
        remove = cho_solve(cho_factor(ghostK, lower=True), B)
        Pi = np.eye(1200)
        Pi[800:1120] -= remove
        Kkin, K4, K2, scalarG = [np.zeros((1200, 1200)) for _ in range(4)]
        nodes, tw = np.polynomial.legendre.leggauss(8)
        # Split at the tent corner. Polynomial point-image products are
        # integrated exactly in this frozen coefficient-first-germ reference.
        times = np.r_[(nodes + 1) * length / 4, (nodes + 3) * length / 4]
        timeweights = np.tile(tw * length / 4, 2)
        wall = coupled_wall_maps(A[-1], E, length=length)['wall_time_profile_value_maps']
        covariance = 0.
        T = higgs_u2_real_representation()['real_generators']
        for u, weight, tg in zip(times, timeweights, smooth_ghost_temporal_values(times, length)):
            b, bp = 2 * min(u / length, 1 - u / length), (2 if u < length / 2 else -2) / length
            t = np.r_[b, bp, tg[0, :2], tg[1, :2]]
            W = np.zeros((400, 1200))
            W[:, :1120] = np.einsum('t,tij->ij', t, wall)
            hs = paired_scalar_orbit_maps(H, Hd, t, radial[-1])
            kin, four, two, gg, derivatives, dt, ds = scalar_point(weights, H, Hd, A[-1], E, W, hs)
            Kkin += weight * kin
            K4 += weight * four
            K2 += weight * two
            scalarG += weight * gg
            expected = []
            for base in (dt, *ds):
                U = np.einsum('cij,j->ci', T, base)
                block = np.zeros((80, 320))
                for i in range(2):
                    for j in range(2):
                        block[:, 160 * i + 80 * j:160 * i + 80 * (j + 1)] = -radial[-1, j, 0] * t[2 + 2 * i] * np.kron(U.T, np.eye(20))
                expected.append(block)
            covariance = max(covariance, maximum(derivatives[:, :, 800:1120] - expected))
        commonKin = Kkin.copy()
        commonKin[:1120, :1120] += MAXWELL_TO_CAP * K
        commonG = scalarG.copy()
        commonG[:1120, :1120] += MAXWELL_TO_CAP * G
        fixing = MAXWELL_TO_CAP * B.T @ F
        controls = point_controls(A[-1], At[-1], Ar[-1], E, Y, haar, radial[-1], density[-1], metric[-1],
            H, Hd, weights, length)
        for name, matrix in dict(one_form_Hessian_per_kappa=K, one_form_Gram_per_kappa=G,
                curvature_contact_per_kappa=contact, FP_Hessian_per_kappa=ghostK, ghost_Gram_per_kappa=ghostG,
                weak_Lorenz=F, weak_gradient_pairing=B, finite_Lorenz_slice_projector=Pi,
                scalar_kinetic_Hessian=Kkin, scalar_lambda_coefficient=K4,
                scalar_lambda_nu_squared_coefficient=K2, scalar_Gram=scalarG,
                common_kinetic_Hessian=commonKin, common_Gram=commonG, finite_Lorenz_fixing=fixing).items():
            save_sparse(arrays, side + '_' + name, matrix)
        arrays.update({side + '_' + k: v for k, v in dict(A=A, A_time=At, A_radial=Ar,
            positive_metric=metric, positive_two_form_densities=density, YM_pushforward_weight=common,
            H=H, H_time=Hd, intrinsic_weights=weights, raw=raw).items()})
        D = np.eye(1200)[:, 800:1120]
        records.append(dict(side=side, retained_cell_coordinate_length=length, test_dimension=1200, ghost_dimension=320,
            original_basis_A_reconstruction_absolute=Adefect,
            pushforward_metric_identity_relative=maximum(density[:, 3] - density[:, 0] * density[:, 1] / density[:, 2]) / maximum(density[:, 3]),
            FP_equals_D_Gram_D_relative=norm(G[800:, 800:] - ghostK) / norm(ghostK),
            finite_slice_idempotence_absolute=maximum(Pi @ Pi - Pi),
            finite_slice_D_absolute=maximum(Pi @ D),
            weak_Lorenz_slice_relative=norm(F @ Pi) / norm(F),
            common_Hessian_symmetry_relative=norm(commonKin - commonKin.T) / norm(commonKin),
            curvature_contact_norm=norm(contact), curvature_contact_nonzero=bool(norm(contact) > 0),
            gauge_scalar_cross_kinetic_norm=norm(Kkin[:1120, 1120:]),
            dependent_ghost_scalar_Gram_cross_norm=norm(scalarG[800:1120, 1120:]),
            paired_scalar_covariance_absolute=covariance,
            offshell_common_Hessian_on_ghost_image_norm=norm(commonKin @ D),
            potential_coefficient_norms=dict(lambda_coefficient=norm(K4), lambda_nu_squared_coefficient=norm(K2)),
            H_norm=norm(H), H_time_norm=norm(Hd), A_time_norm=norm(At), A_radial_norm=norm(Ar),
            literal_controls=controls))
        print(json.dumps(dict(completed=side, curvature_contact_norm=norm(contact),
            scalar_gauge_cross=norm(Kkin[:1120, 1120:]), FP_Gram_relative=records[-1]['FP_equals_D_Gram_D_relative'])), flush=True)
    for name, module in list(sys.modules.items()):
        path = getattr(module, '__file__', None)
        if name.startswith('bhsm.') and path and Path(path).is_relative_to(ROOT):
            pin(Path(path).relative_to(ROOT).as_posix())
    pin(Path(__file__).resolve().relative_to(ROOT).as_posix())
    for path in ('src/bhsm/interface/muon_regular_reset_brst_domain.py',
                 'src/bhsm/interface/master_action/reduction.py',
                 'src/bhsm/interface/bhsm_standard_model_gauge_vertices.py'):
        pin(path)
    result = dict(classification='ACTUAL_REAL_EW4_HIGGS_FP_FROZEN_COEFFICIENT_CELL_FORMS', records=records,
        background='same saved original core4 plus separate actual wall as the full384 D5 source-first packet',
        gauge_group_scope='EW4 only: unit-Tr16 SU2xU1; color8 complement NOT assembled or removed',
        color_complement_owner='bhsm_standard_model_gauge_vertices.multiplet_generators/SU3',
        angular_scope='all20 real scalar harmonics n1+n3, nonlinear literal products kept on exact degree12 Haar grid',
        first_complex_map='320 ghosts -> exact DG one-form image and dependent -eta H scalar image',
        FP_map='Gghost^-1 B D; B=<Deta,a>_1 in the same positive YM pushforward pairing',
        finite_slice='Pi=I-D KFP^-1 B; declared finite Lorenz representative, NOT physical quotient',
        potential='K=Kkin + lambda_H*Klambda + (lambda_H*nu_squared_action)*Klambda_nu2',
        potential_matching_values_selected=False, no_Rxi_scalar_mass_gauge_fixing_added=True,
        offshell_Euler_contact_retained=True, stationarity_assumed=False,
        ghost_antighost_statistics_not_counted_as_bosonic_multiplicity=True,
        physical_reset_incidence=None,
        reset_available_owner='muon_regular_reset_brst_domain: supplied actual U,F,total density and conormal jets required',
        master_constraint_owner='master_action.reduction.variational_intertwiner/domain_and_hessian',
        microscopic_Pstrat_identity=False, common_SM12_or_M8_graded_operator_completed=False,
        global_BRST_nilpotence_or_quotient_completed=False, physical_native_force=None,
        physical_outgoing_response=None, physical_E_B_full_derivative_at_2e_minus10=False,
        physical_stationary_background_solved=False, physical_spin_normalization=None,
        physical_muon_moment=None, coupled_corrections=0,
        new_field_profile_history_or_source_campaigns=0,
        frozen_coordinate_basis_evaluation_at_five_nodes=True,
        all_recorded_real_operands_had_exactly_zero_imaginary_part=True,
        input_and_source_sha256=dict(sorted(pins.items())))
    out.mkdir(parents=True)
    _compressed_npz(out / 'forms.npz', arrays)
    result['numerical_sha256'] = sha256((out / 'forms.npz').read_bytes()).hexdigest()
    (out / 'result.json').write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    execute(args.output)
