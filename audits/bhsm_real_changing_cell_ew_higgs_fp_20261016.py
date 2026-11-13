"""Changing REAL incoming/child EW4/Higgs/FP coefficient-cell assembly.

Every Gauss time uses the owned saved-phase sampler and original full D5
coefficient constructor. Fixed reference-coordinate trial maps are never
renormalized under time/radial refinement. This is a constituent action
form application, not microscopic P_strat, a stationary mean or exterior.
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
sys.path.insert(0, str(ROOT / 'audits'))
sys.path.insert(0, str(ROOT / 'scripts'))
import bhsm_real_ew_higgs_fp_common_forms_20261016 as frozen
from bhsm_real_full_d5_combined_eta_open_form_20261016 import radial_representation, sample_coefficients
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_parent_positive_brst_ghost import (
    ghost_radial_values, smooth_ghost_temporal_values, covariant_ghost_gradient_images)
from bhsm.interface.muon_parent_positive_coupled_field import coupled_wall_maps, VOLUME
from bhsm.interface.muon_parent_positive_coupled_temporal import one_form_point_row, paired_scalar_orbit_maps
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
from bhsm.interface.muon_parent_maxwell_corrected_retarded import _ad
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation

FROZEN_PRODUCER_SHA = '4da9bf48b9e759c296d35c6d5813cf36309e245e19b7a2062f8fa2416a75c4f9'
PHASES = dict(incoming='artifacts/muon_finite_normal_phase_20261011/incoming_run_1',
              outgoing='artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
MATRIX_NAMES = ('one_form_Hessian_per_kappa', 'one_form_Gram_per_kappa', 'curvature_contact_per_kappa',
    'FP_Hessian_per_kappa', 'ghost_Gram_per_kappa', 'weak_Lorenz', 'weak_gradient_pairing',
    'finite_Lorenz_slice_projector', 'scalar_kinetic_Hessian', 'scalar_lambda_coefficient',
    'scalar_lambda_nu_squared_coefficient', 'scalar_Gram', 'common_kinetic_Hessian',
    'common_Gram', 'finite_Lorenz_fixing')


def real_coefficients(c):
    return {k: frozen.real(v, k) for k, v in c.items() if isinstance(v, np.ndarray)}


def source_fields(c, raw, rep):
    """Literal radial trace map plus already-composed inherited profile."""
    value = np.einsum('rjfac,j->rac', rep['gauge_basis'], raw[100:180])
    radial = np.einsum('rjfac,j->rac', rep['gauge_radial_basis'], raw[100:180])
    value[:, 2:] += M * (c['mechanical_profile'][:, 0, None, None] - 1)
    radial[:, 2:] += M * c['mechanical_profile'][:, 2, None, None]
    defect = frozen.maximum(value - c['gauge_connection_material'])
    if defect > 1e-13:
        raise ValueError('Same fixed original source chart required')
    return c['gauge_connection_material'], c['gauge_connection_material_first'][0], radial, defect


def direction_vectors(length):
    row = np.arange(1, 1201)
    mixed = (np.cos(row * .173) + np.sin(row * .119)) / np.sqrt(1200)
    mixed[800:] *= length
    scalar = np.zeros(1200)
    scalar[1120:] = np.cos(np.arange(1, 81) * .193) / np.sqrt(80)
    return np.array([mixed, scalar])


def scalar_ghost_coefficients(z, radial, tg):
    ghost = z[800:1120].reshape(2, 2, 4, 20)
    derivative = lambda t, r: np.einsum('p,r,prch->ch', t, r, ghost)
    return tuple(derivative(tg[:, t], radial[:, r]) for t, r in ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2)))


def literal_trial_coefficients(z, radial, temporal, tg, A, At, Ar, E):
    """Direct value/first maps of one fixed full common coefficient vector.

    This does not call the assembled point Hessian or its curvature map.
    Products in the ensuing action are evaluated on the full Haar grid.
    """
    b, bp = temporal
    ordinary = z[:800].reshape(2, 5, 4, 20)
    a = b * np.einsum('r,rfch->fch', radial[:, 0], ordinary)
    at = bp * np.einsum('r,rfch->fch', radial[:, 0], ordinary)
    ar = b * np.einsum('r,rfch->fch', radial[:, 1], ordinary)
    eta, et, er, ett, etr, err = scalar_ghost_coefficients(z, radial, tg)
    a += np.einsum('fcg,gh->fch', np.array([_ad(x) for x in A]), eta)
    a[0] += et
    a[1] += er
    a[2:] += np.einsum('aij,cj->aci', E, eta)
    at += np.einsum('fcg,gh->fch', np.array([_ad(x) for x in At]), eta)
    at += np.einsum('fcg,gh->fch', np.array([_ad(x) for x in A]), et)
    at[0] += ett
    at[1] += etr
    at[2:] += np.einsum('aij,cj->aci', E, et)
    ar += np.einsum('fcg,gh->fch', np.array([_ad(x) for x in Ar]), eta)
    ar += np.einsum('fcg,gh->fch', np.array([_ad(x) for x in A]), er)
    ar[0] += etr
    ar[1] += err
    ar[2:] += np.einsum('aij,cj->aci', E, er)
    ea = np.einsum('aij,fcj->afci', E, a)
    return a, at, ar, ea, eta, et


def literal_YM_values(A, At, Ar, E, Y, haar, density, radial, tf, tg, directions, steps):
    values = np.empty((len(directions), len(steps)))
    base = np.broadcast_to(A, (len(Y), 5, 4))
    baset, baser = [np.broadcast_to(a, base.shape) for a in (At, Ar)]
    for k, z in enumerate(directions):
        a, at, ar, ea, _, _ = literal_trial_coefficients(z, radial, tf, tg, A, At, Ar, E)
        a, at, ar = [np.einsum('ph,fch->pfc', Y, a) for a in (a, at, ar)]
        ea = np.einsum('ph,afch->apfc', Y, ea)
        for j, step in enumerate(steps):
            F = frozen.literal_curvatures(base + step * a, baset + step * at, baser + step * ar, step * ea)
            values[k, j] = .5 * frozen.curved_pair(F, F, density, haar)
    return values


def literal_scalar_values(A, H, Hd, E, Y, haar, weights, radial, tf, tg, directions, steps):
    values = np.empty((len(directions), len(steps), 3))
    T = higgs_u2_real_representation()['real_generators']
    b, bp = tf
    for k, z in enumerate(directions):
        # Only value and eta/time are needed at the intrinsic seam; no
        # H extension or duplicate bulk Yukawa term is introduced.
        a, _, _, _, eta, et = literal_trial_coefficients(z, radial, tf, tg, A, np.zeros_like(A), np.zeros_like(A), E)
        U = np.einsum('cij,j->ci', T, H)
        Ut = np.einsum('cij,j->ci', T, Hd)
        h = b * z[1120:].reshape(4, 20) - U.T @ eta
        ht = bp * z[1120:].reshape(4, 20) - U.T @ et - Ut.T @ eta
        a = np.einsum('ph,fch->pfc', Y, a)
        hv, htv = Y @ h.T, Y @ ht.T
        eh = np.array([Y @ (h @ e.T).T for e in E])
        for j, step in enumerate(steps):
            hh = H + step * hv
            oo = np.einsum('pfc,cij->pfij', A[None] + step * a, T)
            dt = Hd + step * htv + np.einsum('pij,pj->pi', oo[:, 0], hh)
            ds = np.array([step * eh[i] + np.einsum('pij,pj->pi', oo[:, 2 + i], hh) for i in range(3)])
            h2 = np.sum(hh ** 2, axis=1)
            values[k, j] = np.array([
                weights[0] * np.einsum('p,pi,pi', haar, dt, dt)
                    + weights[1] * np.einsum('p,api,api', haar, ds, ds),
                weights[2] * (haar @ (h2 ** 2)), -2 * weights[2] * (haar @ h2)]) / VOLUME
    return values


def assemble(phase, side, angular, *, radial_order, time_order):
    length = abs(float(phase['receipt']['span']) / int(phase['receipt']['steps']))
    if phase['receipt']['steps'] != 1:
        raise ValueError('This actual application owns the preserved one-cell histories')
    origin = -length if side == 'incoming' else 0.
    x, w = np.polynomial.legendre.leggauss(radial_order)
    rho, rw = (x + 1) * WALL / 2, w * WALL / 2
    allrho = np.r_[rho, WALL]
    rep = radial_representation(phase['representation'], allrho)
    radial = ghost_radial_values(allrho)
    E, Y, haar = (angular[k] for k in ('E', 'Y', 'haar'))
    tx, tw = np.polynomial.legendre.leggauss(time_order)
    times = np.r_[(tx + 1) * length / 4, (tx + 3) * length / 4]
    timeweights = np.tile(tw * length / 4, 2)
    temporal = smooth_ghost_temporal_values(times, length)
    K, G, contact = [np.zeros((1120, 1120)) for _ in range(3)]
    ghostG = np.zeros((320, 320))
    ghostK = np.zeros((320, 320))
    Kkin, K4, K2, scalarG = [np.zeros((1200, 1200)) for _ in range(4)]
    sources, snapshots = {}, []
    directions = direction_vectors(length)
    fd_steps = (.08, .04, .02)
    literal_steps = np.unique([0.] + [sign * mult * h for h in fd_steps for sign in (-1, 1) for mult in (1, 2)])
    literal = np.zeros((2, len(literal_steps), 4))
    covariance, Adefect = 0., 0.
    scalarT = higgs_u2_real_representation()['real_generators']
    for index, (u, weight, tg) in enumerate(zip(times, timeweights, temporal)):
        coordinate_time = float(u + origin)
        c, sample = sample_coefficients(phase, coordinate_time, rep)
        c = real_coefficients(c)
        raw = frozen.real(sample['raw_fields'], 'actual changing raw')
        rawtime = frozen.real(sample['raw_coordinate_time_derivative'], 'actual changing raw time')
        A, At, Ar, defect = source_fields(c, raw, rep)
        Adefect = max(Adefect, defect)
        metric, density, push = frozen.positive_geometry(c, raw)
        b = 2 * min(u / length, 1 - u / length)
        bp = (2 if u < length / 2 else -2) / length
        tf = np.r_[b, bp, tg[0, :2], tg[1, :2]]
        for j in range(radial_order):
            row = one_form_point_row(A[j], At[j], Ar[j], E, radial[j], metric[j], density[j], tf)
            scale = weight * rw[j]
            K += scale * row['Hessian']
            G += scale * row['Gram']
            contact += scale * row['curvature_contact']
            ghostG += scale * row['ghost_Gram']
            # An independent complete DG application constructs the FP
            # form, rather than defining it as a copied Gram subblock.
            gradient = covariant_ghost_gradient_images(A[j], At[j], Ar[j], E, tg, radial[j])['value']
            mu, gt, gr, gs, beta, radius = metric[j]
            normal = gradient[0] - beta * gradient[1]
            ghostK += scale * (gt * normal.T @ normal + gr * gradient[1].T @ gradient[1]
                + gs * sum(a.T @ a for a in gradient[2:]))
            literal[:, :, 0] += scale * MAXWELL_TO_CAP * literal_YM_values(
                A[j], At[j], Ar[j], E, Y, haar, density[j], radial[j], (b, bp), tg, directions, literal_steps)
        H, Hd = c['intrinsic_H_realified'], c['intrinsic_H_realified_first'][0]
        R, ell = c['radius'][-1], c['surface_proper_clock_rate'][-1]
        weights = np.array([R ** 3 / ell, ell * R, ell * R ** 3])
        W = np.zeros((400, 1200))
        W[:, :1120] = np.einsum('t,tij->ij', tf,
            coupled_wall_maps(A[-1], E, length=length)['wall_time_profile_value_maps'])
        hs = paired_scalar_orbit_maps(H, Hd, tf, radial[-1])
        kin, four, two, gg, derivatives, dt, ds = frozen.scalar_point(weights, H, Hd, A[-1], E, W, hs)
        Kkin += weight * kin
        K4 += weight * four
        K2 += weight * two
        scalarG += weight * gg
        expected = []
        for base in (dt, *ds):
            U = np.einsum('cij,j->ci', scalarT, base)
            block = np.zeros((80, 320))
            for p in range(2):
                for r in range(2):
                    block[:, 160 * p + 80 * r:160 * p + 80 * (r + 1)] = -radial[-1, r, 0] * tf[2 + 2 * p] * np.kron(U.T, np.eye(20))
            expected.append(block)
        covariance = max(covariance, frozen.maximum(derivatives[:, :, 800:1120] - expected))
        literal[:, :, 1:] += weight * literal_scalar_values(A[-1], H, Hd, E, Y, haar,
            weights, radial[-1], (b, bp), tg, directions, literal_steps)
        for name, value in dict(raw=raw, rawtime=rawtime, A=A, A_time=At, A_radial=Ar,
                positive_metric=metric, positive_two_form_densities=density, pushforward_weight=push,
                H=H, H_time=Hd, intrinsic_weights=weights).items():
            sources.setdefault(name, []).append(value)
        snapshots.append([coordinate_time, float(sample['stage_time']), ell, R, frozen.norm(rawtime),
            frozen.norm(A), frozen.norm(At), frozen.norm(Ar), frozen.norm(H), frozen.norm(Hd),
            frozen.norm(c['mechanical_profile'][:, 0]), frozen.norm(c['mechanical_profile_first'][0, :, 0])])
        print(json.dumps(dict(side=side, radial_order=radial_order, time_node=index + 1,
            time_nodes=len(times), coordinate_time=coordinate_time)), flush=True)
    B = np.zeros((320, 1200))
    B[:, :1120] = G[800:, :]
    F = cho_solve(cho_factor(ghostG, lower=True), B)
    remove = cho_solve(cho_factor(ghostK, lower=True), B)
    Pi = np.eye(1200)
    Pi[800:1120] -= remove
    common = Kkin.copy()
    common[:1120, :1120] += MAXWELL_TO_CAP * K
    commonGram = scalarG.copy()
    commonGram[:1120, :1120] += MAXWELL_TO_CAP * G
    matrices = dict(zip(MATRIX_NAMES, (K, G, contact, ghostK, ghostG, F, B, Pi,
        Kkin, K4, K2, scalarG, common, commonGram, MAXWELL_TO_CAP * B.T @ F)))
    targets = np.array([[z[:1120] @ (MAXWELL_TO_CAP * K) @ z[:1120], z @ Kkin @ z,
                         z @ K4 @ z, z @ K2 @ z] for z in directions])
    target_index = {float(s): i for i, s in enumerate(literal_steps)}
    sweeps = []
    for k, name in enumerate(('mixed_length_scaled', 'independent_scalar_unscaled')):
        zero = literal[k, target_index[0.]]
        steps = []
        for h in fd_steps:
            at = lambda s: literal[k, target_index[float(s)]]
            sec = (16 * (at(h) + at(-h) - 2 * zero) - (at(2 * h) + at(-2 * h) - 2 * zero)) / (12 * h ** 2)
            steps.append(dict(step=h, literal=sec.tolist(), target=targets[k].tolist(),
                absolute_error=abs(sec - targets[k]).tolist(),
                relative_to_nonzero=[float(abs(a - b) / abs(b)) if b else None for a, b in zip(sec, targets[k])]))
        sweeps.append(dict(direction=name, component_order=['YM', 'intrinsic_kinetic', 'lambda_coefficient', 'lambda_nu_squared_coefficient'], steps=steps))
    snapshots = np.array(snapshots)
    summary = dict(side=side, radial_order=radial_order, time_order_per_tent_half=time_order,
        future_coordinate_time_origin=origin, retained_cell_length=length,
        proper_induced_lapse_minimum=float(snapshots[:, 2].min()), proper_induced_lapse_maximum=float(snapshots[:, 2].max()),
        no_background_or_reference_germ_replaced=True, original_fixed_basis_A_reconstruction_absolute=Adefect,
        change_over_sampled_times={name: frozen.norm(np.asarray(value)[-1] - np.asarray(value)[0])
            for name, value in sources.items() if name in ('raw', 'A', 'A_time', 'H', 'H_time', 'positive_metric', 'intrinsic_weights')},
        curvature_contact_norm=frozen.norm(contact), gauge_scalar_kinetic_cross_norm=frozen.norm(Kkin[:1120, 1120:]),
        offshell_common_kinetic_Hessian_on_D_norm=frozen.norm(common[:, 800:1120]),
        dependent_scalar_covariance_absolute=covariance,
        FP_equals_D_Gram_D_relative=frozen.norm(ghostK - G[800:, 800:]) / frozen.norm(ghostK),
        finite_slice_idempotence_absolute=frozen.maximum(Pi @ Pi - Pi),
        finite_slice_D_absolute=frozen.maximum(Pi[:, 800:1120]),
        weak_Lorenz_slice_relative=frozen.norm(F @ Pi) / frozen.norm(F),
        common_Hessian_symmetry_relative=frozen.norm(common - common.T) / frozen.norm(common),
        literal_full_changing_action_second_sweeps=sweeps,
        native_force_or_exterior_load=None, physical_derivative_gate=False)
    arrays = dict(radial_points=allrho, radial_coordinate_weights=rw, temporal_u=times,
        temporal_coordinate_time=times + origin, temporal_coordinate_weights=timeweights,
        ghost_temporal_value_rate_second=temporal, ghost_radial_value_rate_second=radial,
        fixed_background_gauge_value_map=rep['gauge_basis'], fixed_background_gauge_radial_map=rep['gauge_radial_basis'],
        snapshots=snapshots, literal_steps=literal_steps, literal_action_values=literal,
        literal_directions=directions, literal_Hessian_targets=targets)
    arrays.update({name: np.asarray(value) for name, value in sources.items()})
    return matrices, arrays, summary


def execute(output, radial_orders, time_order):
    out = Path(output)
    if out.exists():
        raise FileExistsError('Preserve previous actual applications')
    if radial_orders[0] != 4 or min(radial_orders) < 4 or len(set(radial_orders)) != len(radial_orders) or time_order < 2:
        raise ValueError('Original Gauss4 baseline and explicit distinct refinement orders required')
    frozen_path = ROOT / 'audits/bhsm_real_ew_higgs_fp_common_forms_20261016.py'
    if sha256(frozen_path.read_bytes()).hexdigest() != FROZEN_PRODUCER_SHA:
        raise ValueError('Preserve the verified frozen common form producer')
    s = scalar_s3_discretization(3)
    ids = np.array([i for i, row in enumerate(s['real_basis_labels']) if row[0] in (1, 3)])
    angular = dict(E=s['real_angular_derivative_matrices'][:, ids][:, :, ids],
        Y=s['real_basis_values'][:, ids], haar=s['haar_weights'])
    arrays = dict(EW4_real_angular_derivatives=angular['E'])
    records, comparison, pins = [], [], {}
    for side, folder in PHASES.items():
        phase = load_profile_preserving_phase(folder, repository=ROOT)
        pins.update(phase['input_hashes'])
        previous = None
        for radial_order in radial_orders:
            matrices, source, summary = assemble(phase, side, angular, radial_order=radial_order, time_order=time_order)
            prefix = f'{side}_radial{radial_order}_'
            for name, value in matrices.items():
                frozen.save_sparse(arrays, prefix + name, value)
            arrays.update({prefix + name: value for name, value in source.items()})
            records.append(summary)
            if previous is not None:
                old_order, old = previous
                comparison.append(dict(side=side, radial_orders=[old_order, radial_order],
                    coefficient_chart_identical=True, temporal_rule_identical=True,
                    matrices={name: dict(relative_Frobenius=frozen.norm(matrices[name] - old[name]) / max(frozen.norm(matrices[name]), np.finfo(float).tiny),
                        absolute_maximum=frozen.maximum(matrices[name] - old[name])) for name in MATRIX_NAMES}))
            previous = radial_order, matrices
    for name, module in list(sys.modules.items()):
        path = getattr(module, '__file__', None)
        if ((name.startswith('bhsm.') or name in ('bhsm_real_ew_higgs_fp_common_forms_20261016',
                'bhsm_real_full_d5_combined_eta_open_form_20261016')) and path and Path(path).is_relative_to(ROOT)):
            pins[Path(path).relative_to(ROOT).as_posix()] = sha256(Path(path).read_bytes()).hexdigest()
    pins[Path(__file__).resolve().relative_to(ROOT).as_posix()] = sha256(Path(__file__).read_bytes()).hexdigest()
    for p, h in pins.items():
        if sha256((ROOT / p).read_bytes()).hexdigest() != h:
            raise RuntimeError('Consumed source/input changed: ' + p)
    result = dict(classification='ACTUAL_CHANGING_REAL_ONE_CELL_EW4_HIGGS_FP_FORMS', records=records,
        radial_comparisons=comparison, radial_orders=radial_orders, time_order_per_tent_half=time_order,
        angular_scope='all20 real n1+n3 harmonics; full nonlinear products on degree12 Haar rule',
        gauge_scope='EW4 only; color8 complement not silently removed or assigned a multiplicity',
        actual_coefficient_constructor='original d5_trial_stage_coefficients through sample_coefficients',
        clock='incoming t=u-L, child t=u, dt/du=+1; distinct actual induced proper lapse at every node',
        state_sampler='same saved one-cell x-affine/vy-held phase and inherited affine parent/reference source clock',
        test_chart='fixed original reference-rho basis and fixed temporal coefficient chart; no node-dependent renormalization',
        intrinsic_H_stratum='actual moving wall only, once; no bulkD5 Higgs mass or duplicate D4 kinetic term',
        scalar_potential='unassigned lambda_H and lambda_H*nu_action^2 coefficient matrices',
        finite_FP_and_Lorenz_complex_only=True, physical_reset_incidence=None,
        offshell_Euler_contacts_remain_required=True,
        background_stationary=False, native_quantum_force=None, physical_exterior_load=None,
        microscopic_Pstrat_or_global_BRST_quotient_completed=False,
        radial_or_temporal_physical_convergence_claimed=False,
        full_physical_outgoing_E_B_derivative_at_2e_minus10=False,
        physical_spin_normalization=None, physical_muon_magnetic_moment=None,
        coupled_corrections=0, new_physical_histories_or_field_solves=0,
        original_saved_history_constitutive_coefficients_evaluated_at_Gauss_times=True,
        comparison_data_imported=False, frozen_producer_preserved_sha256=FROZEN_PRODUCER_SHA,
        input_and_source_sha256=dict(sorted(pins.items())))
    out.mkdir(parents=True)
    _compressed_npz(out / 'changing_forms.npz', arrays)
    result['numerical_sha256'] = sha256((out / 'changing_forms.npz').read_bytes()).hexdigest()
    (out / 'result.json').write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--radial-orders', nargs='+', type=int, default=[4, 8])
    parser.add_argument('--time-order', type=int, default=4)
    a = parser.parse_args()
    execute(a.output, a.radial_orders, a.time_order)
