"""Exact tensor contraction of the changing-cell Lorenz pairing.

This audit changes arithmetic, not fields, test coordinates or physics.  It
consumes preserved actual point values; MP arithmetic does not increase the
precision of those binary64 coefficients or certify the analytic history.
"""
from __future__ import annotations

import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np
import mpmath as mp
from scipy import sparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'audits'))
from bhsm.interface.muon_parent_maxwell_corrected_retarded import _ad
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm_real_changing_cell_ew_radial_refinement_20261016 import compare

REFINEMENT_SOURCE_SHA = '5421fc2b1d856a67846cb78e0827581f1f74e7d5de25d30cfabb23f9eca82aa4'
TIME6_SHA = '9a132366d729c85ea1d83815a5482fbf6352b117507e9f447abb4c3b7534739d'


def number(x):
    """Lift the exact stored finite binary64 number, not a decimal guess."""
    return mp.mpf(float(x))


def array(a):
    a = np.asarray(a)
    return np.array([number(x) for x in a.flat], dtype=object).reshape(a.shape)


def zeros(shape):
    a = np.empty(shape, dtype=object)
    a.fill(mp.mpf(0))
    return a


def identity(n):
    a = zeros((n, n))
    for i in range(n):
        a[i, i] = mp.mpf(1)
    return a


def load_matrix(z, name):
    return sparse.csr_matrix((z[name + '_data'], z[name + '_indices'],
                              z[name + '_indptr']),
                             shape=tuple(z[name + '_shape'])).toarray()


def save_matrix(z, name, a):
    s = sparse.csr_matrix(a)
    z[name + '_data'] = s.data
    z[name + '_indices'] = s.indices
    z[name + '_indptr'] = s.indptr
    z[name + '_shape'] = np.array(s.shape)


def tensors():
    # Four ghost profiles; columns are ten ordinary profile/component blocks
    # and four complete covariant-gradient blocks.  Last eighty scalar
    # columns remain zero in this existing one-form Lorenz representative.
    return dict(S=zeros((4, 14, 4, 4)), L=zeros((4, 14, 3, 4, 4)),
                R=zeros((4, 14, 3, 4, 4)), Q=zeros((4, 14)),
                ghost_G4=zeros((4, 4)))


def point_tensors(A, metric, temporal, radial, tent):
    """Complete B=(D eta)^T g a before large angular contractions.

    A[1] is the radial connection VALUE.  Neither A_time nor the radial
    derivative of A enters this one-form Gram.  Actual transposes are kept.
    """
    A, metric, temporal, radial = map(array, (A, metric, temporal, radial))
    I = identity(4)
    mu, gt, gr, gs, beta, radius = metric
    # Preserve the literal source normalization.  The value-only _ad is
    # linear in A; compute its source matrices at held finite input values.
    ad = [array(_ad(np.array([float(x) for x in a]))) for a in A]
    H = ad[0] - beta * ad[1]
    Hr = H.T @ H
    Ar = ad[1]
    Arr = Ar.T @ Ar
    angular_internal = sum((a.T @ a for a in ad[2:]), zeros((4, 4)))
    profiles = []
    for p in range(2):
        for j in range(2):
            tp, tpr = temporal[p, :2]
            u, ur = radial[j, :2]
            profiles.append((tpr * u - beta * tp * ur, tp * u, tp * ur))
    out = tensors()
    b = number(tent)
    for g, (ag, bg, cg) in enumerate(profiles):
        for i in range(2):
            v = radial[i, 0]
            c = b * v
            normal = ag * I + bg * H.T
            radial_dual = cg * I + bg * Ar.T
            out['S'][g, i * 5] = c * gt * normal
            out['S'][g, i * 5 + 1] = c * (-beta * gt * normal + gr * radial_dual)
            for a in range(3):
                col = i * 5 + 2 + a
                out['S'][g, col] = c * gs * bg * ad[2 + a].T
                out['R'][g, col, a] = c * gs * bg * I
        for h, (ah, bh, ch) in enumerate(profiles):
            col = 10 + h
            out['S'][g, col] = (
                gt * (ag * ah * I + ag * bh * H + bg * ah * H.T + bg * bh * Hr)
                + gr * (cg * ch * I + cg * bh * Ar + bg * ch * Ar.T + bg * bh * Arr)
                + gs * bg * bh * angular_internal)
            for a in range(3):
                out['L'][g, col, a] = gs * bg * bh * ad[2 + a].T
                out['R'][g, col, a] = gs * bg * bh * ad[2 + a]
            out['Q'][g, col] = gs * bg * bh
            out['ghost_G4'][g, h] = mu * bg * bh
    return out


def assemble(tensor, E):
    """Assemble all 320x1200 entries in MP, then round once to binary64."""
    E = array(E)
    Qangular = sum((a.T @ a for a in E), zeros((20, 20)))
    I20 = identity(20)
    B = zeros((320, 1200))
    for g in range(4):
        for h in range(14):
            for a in range(4):
                for b in range(4):
                    block = tensor['S'][g, h, a, b] * I20
                    for k in range(3):
                        block = (block + tensor['L'][g, h, k, a, b] * E[k]
                                 + tensor['R'][g, h, k, a, b] * E[k].T)
                    if a == b:
                        block = block + tensor['Q'][g, h] * Qangular
                    B[g * 80 + a * 20:g * 80 + (a + 1) * 20,
                      h * 80 + b * 20:h * 80 + (b + 1) * 20] = block
    return B


def ghost_column(index, A, E, temporal, radial):
    """Independent literal 5x80 covariant image of one ghost coefficient."""
    g, k = divmod(index, 80)
    p, j = divmod(g, 2)
    internal, harmonic = divmod(k, 20)
    tp, tpr = array(temporal[p, :2])
    u, ur = array(radial[j, :2])
    out = zeros((5, 80))
    for mu in range(5):
        ad = array(_ad(A[mu]))
        for a in range(4):
            out[mu, a * 20 + harmonic] += tp * u * ad[a, internal]
    out[0, k] += tpr * u
    out[1, k] += tp * ur
    for a in range(3):
        for hh in range(20):
            out[2 + a, internal * 20 + hh] += tp * u * number(E[a, hh, harmonic])
    return out


def literal_entry(i, j, A, E, metric, temporal, radial, tent):
    """Independent literal full 5x80 image dot product, no tensor moments."""
    left = ghost_column(i, A, E, temporal, radial)
    if j < 800:
        profile, within = divmod(j, 400)
        component, k = divmod(within, 80)
        right = zeros((5, 80))
        right[component, k] = number(tent) * number(radial[profile, 0])
    elif j < 1120:
        right = ghost_column(j - 800, A, E, temporal, radial)
    else:
        return mp.mpf(0)
    mu, gt, gr, gs, beta, radius = array(metric)
    normal_left = left[0] - beta * left[1]
    normal_right = right[0] - beta * right[1]
    return (gt * mp.fsum(x * y for x, y in zip(normal_left, normal_right))
            + gr * mp.fsum(x * y for x, y in zip(left[1], right[1]))
            + gs * mp.fsum(left[a, k] * right[a, k] for a in range(2, 5) for k in range(80)))


def tensor_entry(tensor, E, i, j):
    g, k = divmod(i, 80)
    a, hh = divmod(k, 20)
    h, k = divmod(j, 80)
    b, kk = divmod(k, 20)
    if h >= 14:
        return mp.mpf(0)
    result = tensor['S'][g, h, a, b] if hh == kk else mp.mpf(0)
    result += mp.fsum(tensor['L'][g, h, n, a, b] * number(E[n, hh, kk])
                      + tensor['R'][g, h, n, a, b] * number(E[n, kk, hh]) for n in range(3))
    if a == b:
        result += tensor['Q'][g, h] * mp.fsum(number(E[n, q, hh]) * number(E[n, q, kk])
                                              for n in range(3) for q in range(20))
    return result


def inverse4(g):
    return mp.matrix(g.tolist()) ** -1


def apply_inverse(g, B):
    """Exact G4 tensor I80 inverse acting on every retained coordinate."""
    F = zeros(B.shape)
    for a in range(4):
        for b in range(4):
            F[a * 80:(a + 1) * 80] += g[a, b] * B[b * 80:(b + 1) * 80]
    return F


def as_float(a):
    return np.array([float(x) for x in a.flat], dtype=float).reshape(a.shape)


def fixed_entry(B, F, i, j):
    return number(MAXWELL_TO_CAP) * mp.fsum(B[k, i] * F[k, j] for k in range(320))


def full_fixing(B, F):
    """Full MP contraction; exact zero sparsity only, no symmetry projection."""
    result = zeros((1200, 1200))
    factor = number(MAXWELL_TO_CAP)
    for k in range(320):
        left = [(i, factor * value) for i, value in enumerate(B[k]) if value != 0]
        right = [(j, value) for j, value in enumerate(F[k]) if value != 0]
        for i, value in left:
            for j, other in right:
                result[i, j] += value * other
    return result


def execute(refinement, application, output, orders, dps):
    refinement, application, out = map(Path, (refinement, application, output))
    if out.exists():
        raise FileExistsError('Preserve previous precision readouts')
    if sha256((ROOT / 'audits/bhsm_real_changing_cell_ew_radial_refinement_20261016.py').read_bytes()).hexdigest() != REFINEMENT_SOURCE_SHA:
        raise ValueError('Frozen refinement source changed')
    original_bytes = (application / 'changing_forms.npz').read_bytes()
    if sha256(original_bytes).hexdigest() != TIME6_SHA:
        raise ValueError('Original corrected TIME6 archive required')
    ref_report = json.loads((refinement / 'result.json').read_text())
    pins = dict(ref_report['input_and_source_sha256'])
    with np.load(application / 'changing_forms.npz', allow_pickle=False) as z:
        E = z['EW4_real_angular_derivatives'].copy()
        original = {side: {n: load_matrix(z, side + '_radial32_' + n) for n in
                    ('weak_gradient_pairing', 'weak_Lorenz', 'finite_Lorenz_fixing')}
                    for side in ('incoming', 'outgoing')}
    out.mkdir(parents=True)
    records = []
    inputs = {}
    for side in ('incoming', 'outgoing'):
        previous = None
        for order in orders:
            source = refinement / f'{side}_radial{order}' / 'forms.npz'
            inputs[f'{side}_radial{order}/forms.npz'] = sha256(source.read_bytes()).hexdigest()
            with np.load(source, allow_pickle=False) as z:
                values = {n: z[n].copy() for n in ('A', 'positive_metric', 'temporal_u',
                          'temporal_coordinate_weights', 'radial_coordinate_weights',
                          'ghost_radial_value_rate_second', 'ghost_temporal_value_rate_second')}
                baseline = {n: load_matrix(z, n) for n in ('weak_gradient_pairing', 'weak_Lorenz',
                            'finite_Lorenz_fixing', 'ghost_Gram_per_kappa')}
            control_indices = [(284, 924), (44, 924), (0, 0), (84, 200)]
            with mp.workdps(dps):
                total = tensors()
                controls = [mp.mpf(0) for _ in control_indices]
                point_errors = []
                times = values['temporal_u']
                # Pair actual mirror nodes before summing.  Both coefficients
                # and weights are retained independently; no equality or
                # constant background is imposed on a mirror pair.
                pairs = [(i, len(times) - 1 - i) for i in range(len(times) // 2)]
                for r in range(order):
                    rw = number(values['radial_coordinate_weights'][r])
                    radial = values['ghost_radial_value_rate_second'][r]
                    for left, right in pairs:
                        group = []
                        for ti in (left, right):
                            temporal = values['ghost_temporal_value_rate_second'][ti]
                            tent = 2 * min(times[ti] / 1e-5, 1 - times[ti] / 1e-5)
                            A, metric = values['A'][ti, r], values['positive_metric'][ti, r]
                            point = point_tensors(A, metric, temporal, radial, tent)
                            weight = rw * number(values['temporal_coordinate_weights'][ti])
                            group.append((weight, point))
                            for ci, (i, j) in enumerate(control_indices):
                                literal = literal_entry(i, j, A, E, metric, temporal, radial, tent)
                                controls[ci] += weight * literal
                                if r in (0, order // 2, order - 1) and ti in (0, len(times) // 2, len(times) - 1):
                                    expanded = tensor_entry(point, E, i, j)
                                    point_errors.append(dict(radial_index=r, time_index=ti, row=i, column=j,
                                        literal=mp.nstr(literal, 65), tensor=mp.nstr(expanded, 65),
                                        absolute=mp.nstr(abs(literal - expanded), 8)))
                        for name in total:
                            total[name] += group[0][0] * group[0][1][name] + group[1][0] * group[1][1][name]
                    if r % 8 == 0 or r == order - 1:
                        print(json.dumps(dict(side=side, radial_order=order, radial_index=r + 1,
                                              radial_count=order, dps=dps)), flush=True)
                Bmp = assemble(total, E)
                Gi = inverse4(total['ghost_G4'])
                Fmp = apply_inverse(Gi, Bmp)
                B, F = as_float(Bmp), as_float(Fmp)
                G4 = as_float(total['ghost_G4'])
                binary_fixing = MAXWELL_TO_CAP * B.T @ F
                fixing_mp = full_fixing(Bmp, Fmp)
                fixing = as_float(fixing_mp)
                comparisons = dict(B_against_fast=compare(baseline['weak_gradient_pairing'], B),
                                   F_against_fast=compare(baseline['weak_Lorenz'], F),
                                   fixing_against_fast=compare(baseline['finite_Lorenz_fixing'], fixing),
                                   final_binary_fixing_against_MP=compare(fixing, binary_fixing),
                                   ghost_G_against_fast=compare(baseline['ghost_Gram_per_kappa'], np.kron(G4, np.eye(80))))
                if order == 32:
                    comparisons.update(B_against_original=compare(original[side]['weak_gradient_pairing'], B),
                        F_against_original=compare(original[side]['weak_Lorenz'], F),
                        fixing_against_original=compare(original[side]['finite_Lorenz_fixing'], fixing))
                if previous is not None:
                    comparisons.update(B_adjacent_rule=compare(previous['B'], B),
                        F_adjacent_rule=compare(previous['F'], F),
                        fixing_adjacent_rule=compare(previous['fixing'], fixing))
                selected = []
                for (i, j), literal in zip(control_indices, controls):
                    selected.append(dict(row=i, column=j, literal_MP_integral=mp.nstr(literal, 65),
                        tensor_MP_integral=mp.nstr(Bmp[i, j], 65),
                        absolute=mp.nstr(abs(literal - Bmp[i, j]), 8)))
                fi, fj = (412, 892) if side == 'incoming' else (924, 444)
                fixed_mp = fixed_entry(Bmp, Fmp, fi, fj)
                scalar_fixing = dict(row=fi, column=fj, MP_value=mp.nstr(fixed_mp, 65),
                    stored_rounded_value=float(fixing[fi, fj]),
                    stored_conversion_error=float(abs(number(fixing[fi, fj]) - fixed_mp)),
                    independent_MP_sum_error=mp.nstr(abs(fixing_mp[fi, fj] - fixed_mp), 8),
                    binary_counterpart_value=float(binary_fixing[fi, fj]),
                    binary_final_contraction_error=float(abs(number(binary_fixing[fi, fj]) - fixed_mp)))
                record = dict(side=side, radial_order=order, arithmetic_dps=dps,
                    input_values_remain_frozen_binary64=True, actual_mirror_node_coefficients_held_independently=True,
                    comparisons=comparisons, integrated_literal_MP_controls=selected,
                    point_literal_MP_controls=point_errors, selected_fixing_final_contraction=scalar_fixing,
                    angular_adjoint_defect=float(np.max(abs(E + E.transpose(0, 2, 1)))),
                    angular_adjoint_defect_projected_to_zero=False,
                    maximum_literal_MP_integrated_absolute=mp.nstr(max(abs(c - Bmp[i, j]) for (i, j), c in zip(control_indices, controls)), 8),
                    no_analytic_history_or_physical_derivative_certificate=True)
            folder = out / f'{side}_radial{order}'
            folder.mkdir()
            arrays = dict(ghost_Gram4=G4)
            for name, matrix in (('B', B), ('F', F), ('fixing', fixing)):
                save_matrix(arrays, name, matrix)
            _compressed_npz(folder / 'forms.npz', arrays)
            record['numerical_sha256'] = sha256((folder / 'forms.npz').read_bytes()).hexdigest()
            (folder / 'result.json').write_text(json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf8', newline='\n')
            records.append(record)
            previous = dict(B=B, F=F, fixing=fixing)
    for name, module in list(sys.modules.items()):
        path = getattr(module, '__file__', None)
        if path and (name.startswith('bhsm.') or name.startswith('bhsm_real_')) and Path(path).is_relative_to(ROOT):
            pins[Path(path).relative_to(ROOT).as_posix()] = sha256(Path(path).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()] = sha256(Path(__file__).read_bytes()).hexdigest()
    for name, digest in pins.items():
        if sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('Owner changed: ' + name)
    result = dict(classification='MP_TENSOR_LORENZ_CONTRACTION_OVER_FROZEN_ACTUAL_REAL_SAMPLES',
        records=records, source_and_owner_sha256=dict(sorted(pins.items())),
        actual_input_archive_sha256=inputs, original_TIME6_archive_sha256=TIME6_SHA,
        final_fixing_matrix_contraction_arithmetic='MP; independent selected scalar fsum and retained binary64 counterpart',
        fields_or_basis_resampled=False, constant_background_moments_substituted=False,
        source_coefficient_input_uncertainty_bounded=False, physical_derivative_pass=False,
        coupled_corrections=0, physical_muon_moment=None)
    (out / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf8', newline='\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refinement', required=True)
    parser.add_argument('--application', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--orders', nargs='+', type=int, default=[32, 64, 128])
    parser.add_argument('--dps', type=int, default=80)
    args = parser.parse_args()
    if args.dps < 65 or any(q not in (32, 64, 128) for q in args.orders):
        raise ValueError('Declared original rules and meaningful MP precision required')
    execute(args.refinement, args.application, args.output, args.orders, args.dps)
