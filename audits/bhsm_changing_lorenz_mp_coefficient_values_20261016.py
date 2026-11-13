"""Higher-precision values on the same retained changing real coefficient cell.

No new history, reference normalization, coupling or boundary load is selected.
The source's finite anchored-response rule and approximate original root are
explicit operands, not mislabeled the exact physical action.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
from pathlib import Path
from hashlib import sha256
from functools import lru_cache
import argparse
import json
import sys
import numpy as np
import mpmath as mp
from scipy.special import gammaln, betaln

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'audits'))
import bhsm_changing_lorenz_tensor_precision_20261016 as tensor
from bhsm.interface.muon_holomorphic_normal_geometry import anchored_holomorphic_chart
from bhsm.interface.muon_parent_retarded_hypercharge import WALL, ALPHA
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_parent_maxwell_corrected_retarded import _ad
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

TENSOR_SOURCE_SHA = 'a0fafae124d00be5954e0284fb2ed5891f645b4955af211a53a2e7494b39238a'
TENSOR_PAIR_RECEIPT_SHA = '31b1821bdac526eb7e42c986dda1b5fce1de6863370b454ee453cd1706f882f9'
PHASES = dict(incoming='artifacts/muon_finite_normal_phase_20261011/incoming_run_1',
              outgoing='artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
BASE = 'artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1'


def m(x):
    return x if isinstance(x, mp.mpf) else mp.mpf(float(x))


def ma(a):
    a = np.asarray(a)
    return np.array([m(x) for x in a.flat], dtype=object).reshape(a.shape)


def maxabs(a):
    return max((abs(x) for x in np.asarray(a).flat), default=mp.mpf(0))


def mp_compare(old, new):
    """Every unrounded entry, using the original retained-unit denominator."""
    if old.shape != new.shape:
        raise ValueError('Same fixed coefficient coordinates required')
    maximum, maximum_scaled, index = mp.mpf(0), mp.mpf(0), 0
    for k, (a, b) in enumerate(zip(old.flat, new.flat)):
        delta = abs(b - a)
        if delta == 0:
            continue
        maximum = max(maximum, delta)
        scaled = delta / max(mp.mpf(1), abs(a), abs(b))
        if scaled > maximum_scaled:
            maximum_scaled, index = scaled, k
    ij = tuple(map(int, np.unravel_index(index, old.shape)))
    return dict(max_absolute=mp.nstr(maximum, 65), max_entry_scaled=mp.nstr(maximum_scaled, 65),
                index=list(ij), old_value=mp.nstr(old[ij], 65), new_value=mp.nstr(new[ij], 65),
                denominator='max(1,abs(old),abs(new)) on every unrounded MP entry')


def constants(pi=None):
    # The reference chart is held fixed: no re-normalization of solved
    # coefficient coordinates under a precision or quadrature change.
    alpha = float(ALPHA)
    beta = 4 + 2 * alpha
    normalizations = []
    for j in range(2):
        lognorm = (gammaln(j + 3) + gammaln(j + beta + 1) - gammaln(j + 1)
                   - gammaln(j + beta + 3) - np.log(2 * j + beta + 3))
        normalizations.append(m(np.exp(-lognorm / 2)))
    return dict(pi=m(np.pi) if pi is None else pi, WALL=m(WALL), alpha=m(ALPHA),
                radius0=m(RADIUS0), jacobi_beta=m(beta), normalization=normalizations,
                ghost_second_normalization=m(np.exp(-betaln(3, 5 + 2 * alpha) / 2)),
                sqrt2=m(np.sqrt(2)), M=ma(M))


@lru_cache(maxsize=None)
def rule(order, mode, dps):
    """Nodes/weights on [0,1]; explicit original-binary versus MP rule."""
    if mode == 'original-binary':
        x, w = np.polynomial.legendre.leggauss(order)
        # Retain the original owner operation order before lifting.
        return tuple(map(m, (x + 1) / 2)), tuple(map(m, w / 2))
    if mode != 'mp':
        raise ValueError('Declared rule mode required')
    with mp.workdps(dps):
        x, w = mp.gauss_quadrature(order, 'legendre')
        return tuple((x[i] + 1) / 2 for i in range(order)), tuple(w[i] / 2 for i in range(order))


def geometry(raw, rho, c):
    """Literal value formulas from the owned _fields/material geometry map."""
    q, v, mul = raw[:37], raw[37:74], raw[74:98]
    s, sd = raw[98:100]
    logstar = q[0] + mp.fsum(q[k] * (-1) ** k for k in range(1, 13)) + mp.fsum(q[13 + j] * (-1) ** j for j in range(12))
    Cstar = c['radius0'] * mp.exp(logstar)
    logstar_dot = v[0] + mp.fsum(v[k] * (-1) ** k for k in range(1, 13)) + mp.fsum(v[13 + j] * (-1) ** j for j in range(12))
    delta, delta_dot = s / Cstar, (sd - s * logstar_dot) / Cstar
    wall = c['pi'] / 4 + delta
    chi = rho * wall / c['WALL']
    ck = [mp.cos(4 * k * chi) for k in range(1, 13)]
    cj = [mp.cos(4 * j * chi) for j in range(12)]
    window = mp.sin(2 * chi) ** 2
    u = mp.fsum(q[1 + j] * ck[j] for j in range(12))
    w = window * mp.fsum(q[13 + j] * cj[j] for j in range(12))
    b = window * mp.fsum(q[25 + j] * cj[j] for j in range(12))
    radius = c['radius0'] * mp.exp(q[0])
    A = radius * mp.exp(u + b) * mp.cos(chi)
    B = radius * mp.exp(u - b) * mp.sin(chi)
    C = radius * mp.exp(u + w)
    N = mp.exp(mp.fsum(mul[j] * ck[j] for j in range(12)))
    beta = mp.sin(4 * chi) * mp.fsum(mul[12 + j] * cj[j] for j in range(12))
    LF = mp.sqrt(A * A + B * B)
    R = A * B / LF
    jac = 2 * wall / c['WALL']
    shift = (2 * beta + 2 * rho * delta_dot / c['WALL']) / jac
    return dict(A=A, B=B, C=C, N=N, LF=LF, R=R, chi=chi,
                delta=delta, delta_dot=delta_dot, wall=wall, Cstar=Cstar,
                jac=jac, shift=shift, lam=A * A / (LF * LF))


def response_chart(delta, c, order, mode, dps):
    """Refine the same two anchored equations; preserve original root data."""
    if abs(delta) >= mp.mpf(2) / 9:
        raise ValueError('Same local anchored material chart required')
    x, w = rule(order, mode, dps)
    pi = c['pi']
    wall = pi / 4 + delta
    whole = [(pi * t / 2, weight) for t, weight in zip(x, w)]
    cap = [(wall * t, weight) for t, weight in zip(x, w)]

    def integral(a, nodes, length):
        terms, first = [], [[], []]
        for z, weight in nodes:
            basis = [mp.sin(2 * z), mp.sin(6 * z)]
            f = z + a[0] * basis[0] + a[1] * basis[1]
            terms.append(weight * mp.sin(2 * f) ** 2 / 4)
            Wf = mp.sin(4 * f) / 2
            for j in range(2):
                first[j].append(weight * Wf * basis[j])
        return length * mp.fsum(terms), [length * mp.fsum(v) for v in first]

    def equations(a):
        Z, Zd = integral(a, whole, pi / 2)
        N, Nd = integral(a, cap, wall)
        basis = [mp.sin(2 * wall), mp.sin(6 * wall)]
        residual = mp.matrix([wall + a[0] * basis[0] + a[1] * basis[1] - pi / 4, N / Z - mp.mpf('.5')])
        J = mp.matrix([basis, [(Nd[j] * Z - N * Zd[j]) / (Z * Z) for j in range(2)]])
        return residual, J, Z

    a = mp.matrix([-21 * delta / 16, -5 * delta / 16])
    for iterations in range(16):
        residual, J, Z = equations(a)
        if max(map(abs, residual)) <= mp.power(10, -dps + 10):
            break
        a += mp.lu_solve(J, -residual)
    residual, J, chart_Z = equations(a)
    if max(map(abs, residual)) > mp.power(10, -dps + 8) or 1 - 2 * abs(a[0]) - 6 * abs(a[1]) <= 0:
        raise ArithmeticError('Same anchored regular branch did not refine')
    # This exact conditional is owned by _response, independently of the
    # chart's finite-rule Z.  Do not conflate its two normalization values.
    production_Z = pi / 16 if delta == 0 else chart_Z
    return dict(a=tuple(a), chart_Z=chart_Z, Z=production_Z, residual=tuple(residual),
                J=J, iterations=iterations + 1, delta_zero_Z_override=(delta == 0),
                order=order, mode=mode, nodes=x, weights=w)


def localization(g, chart):
    terms = []
    for x, w in zip(chart['nodes'], chart['weights']):
        z = g['chi'] * x
        f = z + chart['a'][0] * mp.sin(2 * z) + chart['a'][1] * mp.sin(6 * z)
        terms.append(w * mp.sin(2 * f) ** 2 / 4)
    probability = g['chi'] * mp.fsum(terms) / chart['Z']
    return probability, 4 * probability * (1 - probability)


def profile_raw(raw, t):
    raw = ma(raw)
    out = raw.copy()
    out[:37] += t * raw[37:74]
    out[98] += t * raw[99]
    return out


def radial_basis(rho, reference, c):
    """Same frozen chart coefficients, no new normalization or projection."""
    x = rho / c['WALL']
    alpha = c['alpha']
    regular = x ** alpha
    derivative = alpha * x ** (alpha - 1) / c['WALL']
    P1 = ((2 - c['jacobi_beta']) + (c['jacobi_beta'] + 4) * (2 * x - 1)) / 2
    B0 = regular * (1 - x) * c['normalization'][0]
    D0 = (derivative * (1 - x) - regular / c['WALL']) * c['normalization'][0]
    # Retain the actual ghost_radial_values second-derivative owner and its
    # separately evaluated binary normalization constant.  B uses only
    # value/first, but nonzero seconds are not mislabeled zero jets.
    D20 = c['ghost_second_normalization'] * (
        alpha * (alpha - 1) * x ** (alpha - 2) * (1 - x)
        - 2 * alpha * x ** (alpha - 1)) / c['WALL'] ** 2
    D2wall = alpha * (alpha - 1) * x ** (alpha - 2) / c['WALL'] ** 2
    B1 = regular * (1 - x) * c['normalization'][1] * P1
    lam = [geometry(ma(np.r_[raw, 0., 0.]), rho, c)['lam'] for raw in reference['states']]
    enrichment = (lam[0] - lam[1] - B0 * m(reference['projection'][0])
                  - B1 * m(reference['projection'][1]) - regular * m(reference['wall'])) / m(reference['norm'])
    return np.array([B0, B1, enrichment, regular], dtype=object), np.array([[B0, D0, D20],
                                        [regular, derivative, D2wall]], dtype=object)


def coefficient(raw, t, rho, side, parent_reference, reference, c, chart, basis_data=None):
    g = geometry(raw, rho, c)
    p, weight = localization(g, chart)
    common = 2 * c['pi'] ** 4 * g['LF'] ** 5 * weight
    Ceff = g['C'] * g['wall'] / c['WALL']
    mu = common * g['N'] * Ceff * g['R'] ** 3
    gt = common * Ceff * g['R'] ** 3 / g['N']
    gr = common * g['N'] * g['R'] ** 3 / Ceff
    gs = common * g['N'] * Ceff * g['R']
    metric = np.array([mu, gt, gr, gs, g['shift'], g['R']], dtype=object)
    basis, radial = radial_basis(rho, reference, c) if basis_data is None else basis_data
    gauge = raw[100:180].reshape(4, 5, 4)
    A = sum((basis[j] * gauge[j] for j in range(4)), tensor.zeros((5, 4)))
    lam = g['lam']
    if side == 'outgoing':
        parent, refs = parent_reference
        lam = (geometry(profile_raw(parent, t), rho, c)['lam']
               - geometry(profile_raw(refs[0], t), rho, c)['lam']
               + geometry(profile_raw(refs[1], t), rho, c)['lam'])
    A[2:] += c['M'] * (lam - 1)
    if min(metric[:4]) <= 0 or not 0 < p < 1:
        raise ArithmeticError('Actual positive coefficient branch required')
    return dict(A=A, metric=metric, radial=radial, basis=basis, probability=p,
                localization_weight=weight, common=common, lam=lam, geometry=g)


def ad_native(a, c):
    """The source epsilon contraction/division, without rounding A to float."""
    out = tensor.zeros((4, 4))
    out[:3, :3] = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]],
                           [-a[1], a[0], 0]], dtype=object) / c['sqrt2']
    return out


def native_point(A, metric, temporal, radial, tent, c):
    """Same reviewed tensor identity, preserving MP coefficient values."""
    I = tensor.identity(4)
    mu, gt, gr, gs, beta, radius = metric
    ad = [ad_native(a, c) for a in A]
    H, Ar = ad[0] - beta * ad[1], ad[1]
    HH, RR = H.T @ H, Ar.T @ Ar
    angular = sum((a.T @ a for a in ad[2:]), tensor.zeros((4, 4)))
    profiles = []
    for p in range(2):
        for j in range(2):
            tp, dtp = temporal[p, :2]
            u, ur = radial[j, :2]
            profiles.append((dtp * u - beta * tp * ur, tp * u, tp * ur))
    out = tensor.tensors()
    for g, (ag, bg, cg) in enumerate(profiles):
        for i in range(2):
            v = tent * radial[i, 0]
            normal, radial_dual = ag * I + bg * H.T, cg * I + bg * Ar.T
            out['S'][g, i * 5] = v * gt * normal
            out['S'][g, i * 5 + 1] = v * (-beta * gt * normal + gr * radial_dual)
            for a in range(3):
                col = i * 5 + 2 + a
                out['S'][g, col] = v * gs * bg * ad[2 + a].T
                out['R'][g, col, a] = v * gs * bg * I
        for h, (ah, bh, ch) in enumerate(profiles):
            col = 10 + h
            out['S'][g, col] = (
                gt * (ag * ah * I + ag * bh * H + bg * ah * H.T + bg * bh * HH)
                + gr * (cg * ch * I + cg * bh * Ar + bg * ch * Ar.T + bg * bh * RR)
                + gs * bg * bh * angular)
            for a in range(3):
                out['L'][g, col, a] = gs * bg * bh * ad[2 + a].T
                out['R'][g, col, a] = gs * bg * bh * ad[2 + a]
            out['Q'][g, col] = gs * bg * bh
            out['ghost_G4'][g, h] = mu * bg * bh
    return out


def temporal_values(u, length):
    x = u / length
    p = x * x * (1 - x) ** 2
    dp = 2 * x - 6 * x * x + 4 * x ** 3
    ddp = 2 - 12 * x + 12 * x * x
    q = (2 * x - 1) * p
    dq = 2 * p + (2 * x - 1) * dp
    ddq = 4 * dp + (2 * x - 1) * ddp
    return np.array([[p, dp / length, ddp / length ** 2],
                     [q, dq / length, ddq / length ** 2]], dtype=object)


def load_inputs(refinement, application):
    refinement, application = map(Path, (refinement, application))
    if sha256(Path(tensor.__file__).read_bytes()).hexdigest() != TENSOR_SOURCE_SHA:
        raise ValueError('Preserve reviewed tensor owner')
    if sha256((application / 'changing_forms.npz').read_bytes()).hexdigest() != tensor.TIME6_SHA:
        raise ValueError('Original corrected TIME6 angular/input archive required')
    report = json.loads((refinement / 'result.json').read_text())
    pins = dict(report['input_and_source_sha256'])
    with np.load(ROOT / BASE / 'application.npz', allow_pickle=False) as z:
        ref = dict(states=z['affine_profile_reference_states'].copy(),
                   projection=z['affine_interior_projection'].copy())
    receipt = json.loads((ROOT / BASE / 'result.json').read_text())['affine_profile_enrichment']
    ref.update(wall=receipt['wall_coefficient'], norm=receipt['boundary_anchored_complement_norm'])
    phases, frozen = {}, {}
    for side in ('incoming', 'outgoing'):
        path = ROOT / PHASES[side]
        receipt = json.loads((path / 'result.json').read_text())
        if receipt['steps'] != 1:
            raise ValueError('This readout binds the actual retained one-cell chart')
        with np.load(path / 'application.npz', allow_pickle=False) as z:
            key = 'stage_midpoint_raw' if side == 'incoming' else 'stage_independent_raw'
            phases[side] = dict(midpoint=z[key][0].copy(), span=receipt['span'])
            if side == 'outgoing':
                phases[side]['parent_reference'] = (z['initial_pair'][0].copy(), z['reference_pair'].copy())
        with np.load(refinement / f'{side}_radial32/forms.npz', allow_pickle=False) as z:
            rates = z['rawtime'].copy()
            if not all(np.array_equal(rates[0], a) for a in rates):
                raise ValueError('Same stored affine cell tangent required')
            phases[side]['rate'] = rates[0]
        for order in (32, 64, 128):
            path = refinement / f'{side}_radial{order}/forms.npz'
            expected = next(r['numerical_sha256'] for r in report['records'] if r['side'] == side and r['radial_order'] == order)
            if sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError('Preserved actual refinement arrays changed')
            with np.load(path, allow_pickle=False) as z:
                frozen[side, order] = {n: z[n].copy() for n in
                    ('radial_points', 'radial_coordinate_weights', 'temporal_u',
                     'temporal_coordinate_weights', 'raw', 'A', 'positive_metric', 'fixed_basis')}
    with np.load(application / 'changing_forms.npz', allow_pickle=False) as z:
        E = z['EW4_real_angular_derivatives'].copy()
    for name, digest in pins.items():
        if sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Owner changed: ' + name)
    return phases, ref, frozen, E, pins


def raw_at(phase, t):
    return ma(phase['midpoint']) + (t - m(phase['span']) / 2) * ma(phase['rate'])


def time_nodes(phase, frozen, mode, order, dps):
    length = abs(m(phase['span']))
    if mode == 'original-binary':
        if order == 6:
            return tuple(map(m, frozen['temporal_u'])), tuple(map(m, frozen['temporal_coordinate_weights']))
        x, w = np.polynomial.legendre.leggauss(order)
        L = float(length)
        return tuple(map(m, np.r_[(x + 1) * L / 4, (x + 3) * L / 4])), tuple(map(m, np.tile(w * L / 4, 2)))
    x, w = rule(order, 'mp', dps)
    return tuple(length * t / 2 for t in x) + tuple(length * (1 + t) / 2 for t in x), tuple(length * a / 2 for a in w) * 2


def radial_nodes(frozen, mode, order, dps, c):
    if mode == 'original-binary':
        return tuple(map(m, frozen['radial_points'][:-1])), tuple(map(m, frozen['radial_coordinate_weights']))
    x, w = rule(order, 'mp', dps)
    return tuple(c['WALL'] * a for a in x), tuple(c['WALL'] * a for a in w)


def native_ghost(index, A, E, temporal, radial, c):
    """Literal five-component full80 image; independent tensor control."""
    g, k = divmod(index, 80)
    p, j = divmod(g, 2)
    internal, harmonic = divmod(k, 20)
    tp, tpr = temporal[p, :2]
    u, ur = radial[j, :2]
    out = tensor.zeros((5, 80))
    for mu in range(5):
        ad = ad_native(A[mu], c)
        for a in range(4):
            out[mu, a * 20 + harmonic] += tp * u * ad[a, internal]
    out[0, k] += tpr * u
    out[1, k] += tp * ur
    for a in range(3):
        for hh in range(20):
            out[2 + a, internal * 20 + hh] += tp * u * m(E[a, hh, harmonic])
    return out


def native_literal(i, j, A, E, metric, temporal, radial, tent, c):
    left = native_ghost(i, A, E, temporal, radial, c)
    if j < 800:
        profile, within = divmod(j, 400)
        component, k = divmod(within, 80)
        right = tensor.zeros((5, 80))
        right[component, k] = tent * radial[profile, 0]
    elif j < 1120:
        right = native_ghost(j - 800, A, E, temporal, radial, c)
    else:
        return mp.mpf(0)
    mu, gt, gr, gs, beta, radius = metric
    nl, nr = left[0] - beta * left[1], right[0] - beta * right[1]
    return (gt * mp.fsum(x * y for x, y in zip(nl, nr))
            + gr * mp.fsum(x * y for x, y in zip(left[1], right[1]))
            + gs * mp.fsum(left[a, k] * right[a, k] for a in range(2, 5) for k in range(80)))


def key_controls(phases, reference, frozen, E, dps):
    """Separate source root tolerance, finite rule, rule generation and pi."""
    c = constants()
    records = []
    for side in ('incoming', 'outgoing'):
        phase = phases[side]
        old = frozen[side, 128]
        origin = min(m(phase['span']), mp.mpf(0))
        for ti in (0, len(old['temporal_u']) - 1):
            u = m(old['temporal_u'][ti])
            t = u + origin
            raw = raw_at(phase, t)
            g0 = geometry(raw, m(old['radial_points'][0]), c)
            delta = g0['delta']
            original_delta = float(delta)
            original = anchored_holomorphic_chart(original_delta, points=96)
            for name in ('coefficients', 'implicit_residual', 'implicit_jacobian'):
                if np.any(np.asarray(original[name]).imag != 0):
                    raise ValueError('No complex-root projection')
            old_a = ma(np.asarray(original['coefficients']).real)
            same_delta = response_chart(m(original_delta), c, 96, 'original-binary', dps)
            binary96 = response_chart(delta, c, 96, 'original-binary', dps)
            precise96 = response_chart(delta, c, 96, 'mp', dps)
            precise128 = response_chart(delta, c, 128, 'mp', dps)
            true_pi = constants(mp.pi)
            true_chart = response_chart(delta, true_pi, 96, 'mp', dps)
            values = []
            for ri in (0, len(old['radial_coordinate_weights']) // 2, len(old['radial_coordinate_weights']) - 1):
                rho = m(old['radial_points'][ri])
                args = (raw, t, rho, side, phase.get('parent_reference'), reference)
                val = [coefficient(*args, c, chart) for chart in (binary96, precise96, precise128)]
                pi_val = coefficient(*args, true_pi, true_chart)
                compare = tensor.compare
                values.append(dict(radial_index=ri, rho=mp.nstr(rho, 65),
                    MP_coefficient_against_frozen=dict(A=compare(old['A'][ti, ri], tensor.as_float(val[0]['A'])),
                        metric=compare(old['positive_metric'][ti, ri], tensor.as_float(val[0]['metric'])),
                        basis=compare(old['fixed_basis'][ri], tensor.as_float(val[0]['basis']))),
                    binary96_to_MP96_metric_max_relative=mp.nstr(maxabs((val[1]['metric'][:4] - val[0]['metric'][:4]) / val[1]['metric'][:4]), 15),
                    MP96_to_MP128_metric_max_relative=mp.nstr(maxabs((val[2]['metric'][:4] - val[1]['metric'][:4]) / val[2]['metric'][:4]), 15),
                    binary_pi_to_true_pi_metric_max_relative=mp.nstr(maxabs((pi_val['metric'][:4] - val[1]['metric'][:4]) / pi_val['metric'][:4]), 15),
                    probability_values=[mp.nstr(a['probability'], 65) for a in val],
                    source_coefficient_input_precision_not_certified=True))
            records.append(dict(side=side, time_index=ti, coordinate_time=mp.nstr(t, 65),
                delta=mp.nstr(delta, 65), original_delta_binary_hex=original_delta.hex(),
                raw_MP_reconstruction_against_frozen=tensor.compare(old['raw'][ti], tensor.as_float(raw)),
                original_root_coefficients=np.asarray(original['coefficients']).real.tolist(),
                original_implicit_residual=np.asarray(original['implicit_residual']).real.tolist(),
                original_implicit_jacobian=np.asarray(original['implicit_jacobian']).real.tolist(),
                original_root_stopping_tolerance=4e-15,
                MP_root_correction_at_same_binary_delta=[mp.nstr(a - b, 65) for a, b in zip(same_delta['a'], old_a)],
                precise96_coefficients=[mp.nstr(a, 65) for a in precise96['a']],
                precise96_residual=[mp.nstr(a, 10) for a in precise96['residual']],
                MP96_to_MP128_root_change=[mp.nstr(b - a, 15) for a, b in zip(precise96['a'], precise128['a'])],
                coefficient_controls=values))
    for mode in ('original-binary', 'mp'):
        sentinel = response_chart(mp.mpf(0), c, 96, mode, dps)
        records.append(dict(delta_zero_sentinel=True, mode=mode,
            root_coefficients=[mp.nstr(a, 65) for a in sentinel['a']],
            chart_Z=mp.nstr(sentinel['chart_Z'], 65),
            production_Z=mp.nstr(sentinel['Z'], 65),
            owned_exact_delta_zero_override=sentinel['delta_zero_Z_override']))
    return records


def execute(refinement, application, tensor_reference, output, orders, mode, anchor_order, time_order, dps):
    refinement, application, tensor_reference, out = map(Path, (refinement, application, tensor_reference, output))
    if out.exists():
        raise FileExistsError('Preserve every original and unfavorable readout')
    if sha256((tensor_reference / 'result.json').read_bytes()).hexdigest() != TENSOR_PAIR_RECEIPT_SHA:
        raise ValueError('Original MP80 tensor comparison receipt required')
    tensor_report = json.loads((tensor_reference / 'result.json').read_text())
    phases, reference, frozen, E, pins = load_inputs(refinement, application)
    out.mkdir(parents=True)
    inputs = dict(original_TIME6_archive=sha256((application / 'changing_forms.npz').read_bytes()).hexdigest())
    records = []
    with mp.workdps(dps):
        c = constants()
        controls = key_controls(phases, reference, frozen, E, dps)
        for side in ('incoming', 'outgoing'):
            phase = phases[side]
            old32 = frozen[side, 32]
            length = abs(m(phase['span']))
            origin = min(m(phase['span']), mp.mpf(0))
            times, tw = time_nodes(phase, old32, mode, time_order, dps)
            snapshots = []
            for u, w in zip(times, tw):
                t = u + origin
                raw = raw_at(phase, t)
                g = geometry(raw, c['WALL'] / 2, c)
                chart = response_chart(g['delta'], c, anchor_order, mode, dps)
                snapshots.append(dict(u=u, t=t, w=w, raw=raw, chart=chart,
                    temporal=temporal_values(u, length), tent=2 * min(u / length, 1 - u / length)))
            previous = None
            previous_mp = None
            for order in orders:
                old = frozen[side, order]
                rho, rw = radial_nodes(old, mode, order, dps, c)
                bases = [radial_basis(r, reference, c) for r in rho]
                total = tensor.tensors()
                control_indices = [(284, 924), (0, 0), (20, 183), (40, 823)]
                literal_integrals = [mp.mpf(0) for _ in control_indices]
                point_errors, values = [], {}
                pairs = [(i, len(times) - 1 - i) for i in range(len(times) // 2)]
                for ri, (r, wr, basis) in enumerate(zip(rho, rw, bases)):
                    for left, right in pairs:
                        group = []
                        for ti in (left, right):
                            s = snapshots[ti]
                            val = coefficient(s['raw'], s['t'], r, side, phase.get('parent_reference'),
                                reference, c, s['chart'], basis_data=basis)
                            point = native_point(val['A'], val['metric'], s['temporal'], val['radial'], s['tent'], c)
                            weight = wr * s['w']
                            group.append((weight, point))
                            for k, (i, j) in enumerate(control_indices):
                                literal = native_literal(i, j, val['A'], E, val['metric'], s['temporal'], val['radial'], s['tent'], c)
                                literal_integrals[k] += weight * literal
                                if ri in (0, order // 2, order - 1) and ti in (0, len(times) // 2, len(times) - 1):
                                    expanded = tensor.tensor_entry(point, E, i, j)
                                    point_errors.append(dict(radial_index=ri, time_index=ti, row=i, column=j,
                                        literal=mp.nstr(literal, 65), tensor=mp.nstr(expanded, 65),
                                        absolute=mp.nstr(abs(literal - expanded), 8)))
                            values[ti, ri] = val
                        for name in total:
                            total[name] += group[0][0] * group[0][1][name] + group[1][0] * group[1][1][name]
                    if ri % 8 == 0 or ri == order - 1:
                        print(json.dumps(dict(side=side, radial_order=order, radial_index=ri + 1,
                            radial_count=order, rule_mode=mode, anchor_order=anchor_order,
                            time_order=time_order, dps=dps)), flush=True)
                Bmp = tensor.assemble(total, E)
                Fmp = tensor.apply_inverse(tensor.inverse4(total['ghost_G4']), Bmp)
                fixing_mp = tensor.full_fixing(Bmp, Fmp)
                B, F, fixing, G4 = map(tensor.as_float, (Bmp, Fmp, fixing_mp, total['ghost_G4']))
                basepath = tensor_reference / f'{side}_radial{order}/forms.npz'
                inputs[f'frozen_MP_tensor/{side}_radial{order}/forms.npz'] = sha256(basepath.read_bytes()).hexdigest()
                expected = next(r['numerical_sha256'] for r in tensor_report['records'] if r['side'] == side and r['radial_order'] == order)
                if inputs[f'frozen_MP_tensor/{side}_radial{order}/forms.npz'] != expected:
                    raise ValueError('Frozen MP comparison arrays changed')
                with np.load(basepath, allow_pickle=False) as z:
                    comparisons = {name + '_against_frozen_input_MP': tensor.compare(tensor.load_matrix(z, name), value)
                                   for name, value in (('B', B), ('F', F), ('fixing', fixing))}
                if previous is not None:
                    comparisons.update({name + '_adjacent_rule': tensor.compare(previous[name], value)
                                        for name, value in (('B', B), ('F', F), ('fixing', fixing))})
                unrounded = ({name: mp_compare(previous_mp[name], value)
                              for name, value in (('B', Bmp), ('F', Fmp), ('fixing', fixing_mp))}
                             if previous_mp is not None else None)
                integrated = [dict(row=i, column=j, literal_MP_integral=mp.nstr(literal, 65),
                    tensor_MP_integral=mp.nstr(Bmp[i, j], 65), absolute=mp.nstr(abs(literal - Bmp[i, j]), 8))
                    for (i, j), literal in zip(control_indices, literal_integrals)]
                sample_arrays = dict(A=np.array([[tensor.as_float(values[ti, ri]['A']) for ri in range(order)] for ti in range(len(times))]),
                    positive_metric=np.array([[tensor.as_float(values[ti, ri]['metric']) for ri in range(order)] for ti in range(len(times))]),
                    probability=np.array([[float(values[ti, ri]['probability']) for ri in range(order)] for ti in range(len(times))]),
                    localization_weight=np.array([[float(values[ti, ri]['localization_weight']) for ri in range(order)] for ti in range(len(times))]))
                folder = out / f'{side}_radial{order}'
                folder.mkdir()
                arrays = dict(ghost_Gram4=G4, radial_points=np.array(list(map(float, rho))),
                    radial_coordinate_weights=np.array(list(map(float, rw))),
                    temporal_u=np.array(list(map(float, times))), temporal_coordinate_time=np.array([float(s['t']) for s in snapshots]),
                    temporal_coordinate_weights=np.array(list(map(float, tw))),
                    ghost_radial_value_rate_second=np.array([tensor.as_float(a[1]) for a in bases]),
                    ghost_temporal_value_rate_second=np.array([tensor.as_float(s['temporal']) for s in snapshots]),
                    raw=np.array([tensor.as_float(s['raw']) for s in snapshots]),
                    rawtime=phase['rate'], source_midpoint=phase['midpoint'], fixed_basis=np.array([tensor.as_float(a[0]) for a in bases]),
                    EW4_real_angular_derivatives=E, **sample_arrays)
                for name, value in (('B', B), ('F', F), ('fixing', fixing)):
                    tensor.save_matrix(arrays, name, value)
                _compressed_npz(folder / 'forms.npz', arrays)
                record = dict(side=side, radial_order=order, arithmetic_dps=dps, quadrature_rule_mode=mode,
                    anchored_response_order=anchor_order, temporal_order_per_half=time_order,
                    comparisons=comparisons, integrated_literal_MP_controls=integrated,
                    full_unrounded_MP_adjacent_rule_comparisons=unrounded,
                    finite_Lorenz_component_adjacent_rule_pass=(all(mp.mpf(a['max_entry_scaled']) <= mp.mpf('2e-10')
                        for a in unrounded.values()) if unrounded is not None else None),
                    point_literal_MP_controls=point_errors,
                    actual_midpoint_and_affine_rate_reconstructed_in_MP=True,
                    original_reference_projection_and_normalizations_held=True,
                    scalar_Lorenz_columns_zero_from_existing_representative=True,
                    numerical_sha256=sha256((folder / 'forms.npz').read_bytes()).hexdigest(),
                    no_physical_native_outgoing_derivative_or_state_claim=True,
                    maximum_literal_MP_integrated_absolute=mp.nstr(max(abs(a - Bmp[i, j]) for (i, j), a in zip(control_indices, literal_integrals)), 8))
                (folder / 'result.json').write_text(json.dumps(record, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf8', newline='\n')
                records.append(record)
                previous = dict(B=B, F=F, fixing=fixing)
                previous_mp = dict(B=Bmp, F=Fmp, fixing=fixing_mp)
        constants_record = {k: ([mp.nstr(x, 65) for x in v] if k == 'normalization' else mp.nstr(v, 65))
                            for k, v in c.items() if k != 'M'}
    for name, module in list(sys.modules.items()):
        p = getattr(module, '__file__', None)
        if p and (name.startswith('bhsm.') or name.startswith('bhsm_')) and Path(p).is_relative_to(ROOT):
            pins[Path(p).relative_to(ROOT).as_posix()] = sha256(Path(p).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()] = sha256(Path(__file__).read_bytes()).hexdigest()
    for name, digest in pins.items():
        if sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('Owner changed: ' + name)
    result = dict(classification='MP_SAME_AFFINE_REAL_CELL_COEFFICIENT_AND_LORENZ_VALUES',
        records=records, key_coefficient_and_root_controls=controls,
        held_binary_chart_constants=constants_record,
        source_and_owner_sha256=dict(sorted(pins.items())), input_archive_sha256=inputs,
        quadrature_rule_mode=mode, anchored_response_order=anchor_order,
        temporal_order_per_half=time_order, arithmetic_dps=dps,
        reference_coordinates_renormalized=False, new_history_or_field_solution_selected=False,
        physical_native_heat_operator=None, physical_exterior_load=None, physical_reset_incidence=None,
        matched_Higgs_or_surface_coefficients_assigned=False, physical_derivative_pass=False,
        coupled_corrections=0, physical_muon_moment=None)
    (out / 'result.json').write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf8', newline='\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refinement', required=True)
    parser.add_argument('--application', required=True)
    parser.add_argument('--tensor-reference', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--orders', type=int, nargs='+', default=[32, 64, 128])
    parser.add_argument('--rule-mode', choices=['original-binary', 'mp'], required=True)
    parser.add_argument('--anchor-order', type=int, default=96)
    parser.add_argument('--time-order', type=int, default=6)
    parser.add_argument('--dps', type=int, default=80)
    args = parser.parse_args()
    if args.dps < 65 or args.anchor_order < 96 or args.time_order < 6 or any(q not in (32, 64, 128) for q in args.orders):
        raise ValueError('Declared retained rules and meaningful precision required')
    execute(args.refinement, args.application, args.tensor_reference, args.output, args.orders,
            args.rule_mode, args.anchor_order, args.time_order, args.dps)
