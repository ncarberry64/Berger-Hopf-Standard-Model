"""Restricted packet/current and temporal Gauss continuation applications.

The complete constant-angular full18 Cauchy component is an invariant
coefficient subdomain of a supplied homogeneous comparison.  Its arbitrary
sign-projected spin seeds are numerical continuation data, not the adopted
localized Gaussian beams.  No inherited occupation, normal mode, transverse
field or native/reference load is assigned by this module.

The temporal solve applies Delta(g_classical)+t*j_pair_wall=0.  This is a
frozen-remainder difference initializer.  The absolute classical residual and
the unknown seed remainder survive separately; convergence is not physical
admission and does not change the 2e-10 physical guard.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import expm

from .muon_incoming_comparison_time_lift import sector_projector_source


HAAR_VOLUME = 2*np.pi**2
PHYSICAL_GUARD = 2e-10


def _finite(value, shape, name, *, real=False):
    raw = np.asarray(value)
    if raw.shape != shape or (real and not np.isrealobj(raw)):
        raise ValueError(f'explicit {name} with shape {shape} required')
    result = np.asarray(raw, float if real else complex)
    if not np.isfinite(result).all():
        raise ValueError(f'finite {name} required')
    return result


def electron_family_lift(family=2):
    """All weak and charged-singlet spin entries in one retained family."""
    if type(family) is not int or family not in (0, 1, 2):
        raise ValueError('one retained family index is required')
    return np.eye(18)[:, [2*family, 2*family+1, 6+2*family,
                         7+2*family, 12+2*family, 13+2*family]]


def _orthonormal_projected_columns(projector, seeds, rank_guard, *, sign_basis=None):
    # Apply the projector in its orthonormal spectral factorization.  A tiny
    # Yukawa overlap can be well conditioned within a sign sector; forming
    # P@seed first would amplify cancellation outside that sector when the
    # columns are normalized.
    projected = (projector@seeds if sign_basis is None else
                 sign_basis@(sign_basis.conj().T@seeds))
    gram = projected.conj().T@projected
    values, vectors = np.linalg.eigh(gram)
    if values[-1] <= 0 or values[0] <= rank_guard*values[-1]:
        raise ValueError('the declared spin seeds lose rank in this sign sector')
    columns = projected@(vectors@np.diag(values**-.5)@vectors.conj().T)
    return columns, values


def sign_projected_constant_sections(h18, H, *, family=2, gap_guard=1e-12,
                                     rank_guard=1e-12):
    """Project balanced Higgs-charged chiral spin seeds into full sign sectors.

    Each fixed spin seed is (left Higgs-charged + right charged)/sqrt(2).
    Both chiralities participate before spectral projection, avoiding an
    artificially tiny Yukawa overlap from a purely left trial.  Spectral
    projection is performed on the full family6, including its neutral
    component; the charged4 fiber is never imposed as a reducing subspace.
    Symmetric Gram normalization chooses no eigenline within a degenerate
    sign sector.  This is an explicit trial prescription, not physical spin
    selection, a wave operator, or a reconstructed stationary past.
    """
    h = _finite(h18, (18, 18), 'same-background Hamiltonian')
    higgs = _finite(H, (2,), 'same-background Higgs')
    if min(gap_guard, rank_guard) <= 0 or not np.isfinite([gap_guard, rank_guard]).all():
        raise ValueError('positive finite gap and seed-rank guards required')
    if np.max(abs(h-h.conj().T)) > 1e-12*max(1., np.max(abs(h))):
        raise ValueError('a Hermitian original Hamiltonian is required')
    norm = float(np.vdot(higgs, higgs).real)
    if norm <= 0:
        raise ValueError('nonzero Higgs is required for the stated spin seeds')
    C = electron_family_lift(family)
    leakage = (np.eye(18)-C@C.T)@h@C
    if np.max(abs(leakage)) > 1e-12*max(1., np.max(abs(h))):
        raise ValueError('the supplied full family does not reduce this Hamiltonian')
    he = C.T@h@C
    energies, basis = np.linalg.eigh(he)
    if np.min(abs(energies)) <= gap_guard:
        raise ValueError('gap-closing modes require their original boundary rule')
    sectors = sector_projector_source(he, np.zeros((1, 6, 6), complex))
    seeds = np.zeros((6, 2), complex)
    seeds[:2] = higgs[0]/np.sqrt(2*norm)*np.eye(2)
    seeds[2:4] = higgs[1]/np.sqrt(2*norm)*np.eye(2)
    seeds[4:6] = np.eye(2)/np.sqrt(2)
    up, up_gram = _orthonormal_projected_columns(sectors['positive'], seeds, rank_guard,
                                              sign_basis=basis[:, energies > 0])
    down, down_gram = _orthonormal_projected_columns(sectors['negative'], seeds, rank_guard,
                                                  sign_basis=basis[:, energies < 0])
    U, V = C@up/np.sqrt(HAAR_VOLUME), C@down/np.sqrt(HAAR_VOLUME)
    F = np.c_[U, V]
    time_first = -1j*h@F
    return dict(particle_modes=U[None], antiparticle_modes=V[None],
        coefficient_columns=np.sqrt(HAAR_VOLUME)*F,
        particle_proper_time_first=time_first[None, :, :2],
        antiparticle_proper_time_first=time_first[None, :, 2:],
        full18_Hamiltonian=h, electron_Hamiltonian=he,
        electron_family_lift=C, balanced_charged_spin_seeds6=seeds,
        positive_projector6=sectors['positive'], negative_projector6=sectors['negative'],
        eigenvalues6=sectors['eigenvalues'],
        projected_seed_Gram_eigenvalues=np.array([up_gram, down_gram]),
        complete_Haar_Cauchy_Gram=HAAR_VOLUME*F.conj().T@F,
        original_family_reduction_rows=leakage,
        original_positive_boundary_rows=(np.eye(6)-sectors['positive'])@up,
        original_negative_boundary_rows=(np.eye(6)-sectors['negative'])@down,
        original_Dirac_first_rows=1j*time_first-h@F,
        quadrature=np.array([HAAR_VOLUME]),
        computational_domain='full18 tensor normalized constant scalar on unit S3',
        adopted_beam_moments_achieved=False, physical_admission=False,
        physical_guard=PHYSICAL_GUARD)


def evolve_constant_sections(sections, proper_times):
    """Evaluate exp(-i h tau) on the same static represented Cauchy domain."""
    times = np.asarray(proper_times, float)
    if times.ndim != 1 or not len(times) or not np.isfinite(times).all():
        raise ValueError('finite nonempty proper-time samples required')
    h = _finite(sections['full18_Hamiltonian'], (18, 18), 'Hamiltonian')
    F = np.concatenate((sections['particle_modes'], sections['antiparticle_modes']), axis=2)[0]
    values = np.array([expm(-1j*t*h)@F for t in times])
    first = -1j*np.einsum('ab,tbi->tai', h, values)
    return dict(proper_times=times, particle_modes=values[:, :, :2],
        antiparticle_modes=values[:, :, 2:], proper_time_first=first,
        original_Dirac_rows=1j*first-np.einsum('ab,tbi->tai', h, values),
        complete_Haar_Cauchy_Gram=HAAR_VOLUME*np.einsum('tai,taj->tij',values.conj(),values))


def evaluate_constant_packet(sections, *, pair_density, annihilators,
                             normalization_owner, canonical_spatial_density=1.):
    """Consume the original exact Fock source, retaining its full4 channels.

    The returned integrated source uses the complete constant-domain Haar
    quadrature.  It is not a coordinate dipole or a parent volume source.
    Its parent wall cotangent still needs the declared common trace map.
    """
    from audits.bhsm_collider_incoming_field_current import (
        original_material_Gauss_source, validate_action_packet_Cauchy_Gram,
    )
    density = float(canonical_spatial_density)
    if not np.isfinite(density) or density <= 0:
        raise ValueError('positive explicit canonical spatial density required')
    U, V = sections['particle_modes'], sections['antiparticle_modes']
    gram = validate_action_packet_Cauchy_Gram(particle_modes=U,
        antiparticle_modes=V, quadrature=np.array([HAAR_VOLUME]))
    source = original_material_Gauss_source(particle_modes=U, antiparticle_modes=V,
        canonical_spatial_density=np.array([density]), pair_density=pair_density,
        annihilators=annihilators, normalization_owner=normalization_owner)
    return dict(**source, **gram,
        integrated_material_At_source4=HAAR_VOLUME*source['lepton_material_At_action_source_density'][0],
        physical_admission=False)


def temporal_indices(coefficient_count):
    """Original radial-major A_t coefficients, including declared enrichment."""
    if coefficient_count not in (80, 84):
        raise ValueError('original80 or explicitly enriched84 field chart required')
    indices = np.array([20*p+c for p in range(4) for c in range(4)])
    return np.r_[indices, np.arange(80, 84)] if coefficient_count == 84 else indices


def solve_temporal_difference(realization, seed84, packet_load_callback, *,
        continuation_steps=8, max_iterations=16, absolute_tolerance=2e-11,
        rank_tolerance=1e-12, difference_step=2e-6, continuation_strengths=None):
    """Solve all represented temporal difference rows, exporting every row.

    callback(c) returns the original four integrated material A_t loads in
    the SAME wall cotangent.  Each step recomputes that packet dependence.
    Its centered finite difference is a provisional numerical Jacobian,
    never a physical derivative certificate.  Every original classical
    field row is evaluated before and after.  Other fields are frozen
    continuation data; their equations and unknown remainder are retained.
    A deficient Jacobian stops with its left-cokernel projection, rather
    than choosing a pseudoinverse correction.
    """
    c0 = np.asarray(seed84)
    if c0.ndim != 1:
        raise ValueError('one explicit original field coefficient vector required')
    indices = temporal_indices(len(c0))
    c0 = _finite(c0, (len(c0),), 'seed field coefficients', real=True).copy()
    if (type(continuation_steps) is not int or continuation_steps < 1 or
            type(max_iterations) is not int or max_iterations < 1 or
            min(absolute_tolerance, rank_tolerance, difference_step) <= 0 or
            not np.isfinite([absolute_tolerance, rank_tolerance, difference_step]).all()):
        raise ValueError('positive continuation counts and numerical controls required')
    if continuation_strengths is None:
        strengths = np.arange(1, continuation_steps+1)/continuation_steps
    else:
        strengths = np.asarray(continuation_strengths, float)
        if (strengths.ndim != 1 or not len(strengths) or
                not np.isfinite(strengths).all() or np.any(strengths <= 0) or
                np.any(strengths > 1) or np.any(np.diff(strengths) <= 0) or
                strengths[-1] != 1.):
            raise ValueError('continuation strengths must increase in (0,1] and end at 1')
    evaluate = realization['evaluate']
    before = evaluate(c0)
    g0 = _finite(before['gradient'], c0.shape, 'original seed gradient', real=True)
    insertion = np.zeros((len(c0), 4)); insertion[60:64] = np.eye(4)
    def packet(c):
        return _finite(packet_load_callback(c), (4,), 'same-wall packet load', real=True)
    def residual(c, strength):
        application = evaluate(c)
        load = packet(c)
        all_rows = application['gradient']-g0+strength*insertion@load
        return all_rows[indices], application, load, all_rows
    c = c0.copy(); history = []; status = 'CONTINUATION_CONVERGED'
    failed_strength = None; singular_values = np.empty(0); cokernel = np.empty(0)
    achieved_strength = 0.; derivative_failures = []
    last_converged_coefficients = c0.copy()
    for strength in strengths:
        strength = float(strength)
        converged = False
        for iteration in range(max_iterations+1):
            r, application, load, all_rows = residual(c, strength)
            row_max = float(np.max(abs(r)))
            entry = dict(strength=strength, iteration=iteration, original_difference_row_max=row_max)
            history.append(entry)
            if row_max <= absolute_tolerance:
                converged = True
                achieved_strength = strength
                last_converged_coefficients = c.copy()
                break
            if iteration == max_iterations:
                status = 'ITERATION_LIMIT'; break
            load_J = np.zeros((4, len(indices)))
            derivative_ready = True
            for j, column in enumerate(indices):
                initial_step = difference_step*max(1., abs(c[column]))
                samples = []
                for shrink in range(21):
                    step = initial_step*2.**-shrink
                    plus, minus = c.copy(), c.copy()
                    plus[column] += step; minus[column] -= step
                    try:
                        load_J[:, j] = (packet(plus)-packet(minus))/(2*step)
                    except (ValueError, ArithmeticError, FloatingPointError) as error:
                        samples.append(dict(step=step, error=str(error)))
                        continue
                    break
                else:
                    derivative_ready = False
                if samples:
                    derivative_failures.append(dict(strength=strength, iteration=iteration,
                        coefficient_index=int(column), reached_coefficient=float(c[column]),
                        attempts=samples, admissible_neighborhood_found=derivative_ready))
                if not derivative_ready:
                    status = 'PACKET_DERIVATIVE_UNRESOLVED'
                    entry['unresolved_derivative_coefficient'] = int(column)
                    break
            if not derivative_ready:
                break
            jacobian = application['hessian'][np.ix_(indices, indices)]
            jacobian = jacobian+strength*insertion[indices]@load_J
            scale = 1/np.sqrt(np.maximum(np.linalg.norm(jacobian, axis=1), 1e-30))
            scaled = scale[:, None]*jacobian*scale[None]
            left, singular_values, _ = np.linalg.svd(scaled, full_matrices=True)
            rank = int(np.sum(singular_values > rank_tolerance*max(1., singular_values[0])))
            entry['Jacobian_rank'] = rank
            if rank != len(indices):
                cokernel = left[:, rank:].T@(scale*r)
                entry['left_cokernel_residual_max'] = float(np.max(abs(cokernel)))
                status = 'JACOBIAN_RANK_DEFICIENT'; break
            step = scale*np.linalg.solve(scaled, -scale*r)
            merit = float(np.linalg.norm(scale*r)); accepted = False
            for half in range(20):
                fraction = 2.**-half; trial = c.copy()
                trial[indices] += fraction*step
                try:
                    trial_r = residual(trial, strength)[0]
                    trial_merit = float(np.linalg.norm(scale*trial_r))
                except (ValueError, ArithmeticError, FloatingPointError):
                    continue
                if np.isfinite(trial_merit) and trial_merit < merit:
                    c = trial; accepted = True
                    entry['accepted_step_fraction'] = fraction
                    break
            if not accepted:
                status = 'LINE_SEARCH_STALL'; break
        if not converged:
            failed_strength = strength
            break
    final = evaluate(c); load = packet(c)
    full_load = insertion@load
    full_difference = final['gradient']-g0+full_load
    attempted_strength = 1. if failed_strength is None else failed_strength
    attempted_difference = final['gradient']-g0+attempted_strength*full_load
    return dict(coefficients=c, seed_coefficients=c0, temporal_indices=indices,
        status=status, failed_continuation_strength=failed_strength, history=history,
        achieved_continuation_strength=achieved_strength,
        continuation_strengths=strengths.copy(),
        last_converged_coefficients=last_converged_coefficients,
        last_attempted_continuation_strength=attempted_strength,
        seed_classical=before, final_classical=final,
        integrated_packet_wall_source4=load, packet_field_load=full_load,
        full_original_classical_rows=final['gradient'].copy(),
        full_known_absolute_rows=final['gradient']+full_load,
        full_original_difference_rows=full_difference,
        temporal_original_difference_rows=full_difference[indices],
        full_last_attempted_difference_rows=attempted_difference,
        temporal_last_attempted_difference_rows=attempted_difference[indices],
        seed_original_classical_rows=g0.copy(),
        Jacobian_singular_values=singular_values,
        left_cokernel_projected_residual=cokernel,
        packet_derivative_failures=derivative_failures,
        unresolved_remainder_equation='absolute R = g_classical(c)+j_pair_wall(c)+R_other(c); difference requires R_other(c)-R_other(c0)=0 only as a restricted initializer; seed absolute R remains unclosed',
        numerical_Jacobian='original classical Hessian plus centered difference of recomputed exact packet wall load',
        physical_admission=False, physical_guard=PHYSICAL_GUARD)
