"""Restricted affine derivative of the evaluated operator-current return.

Only the already existing magnetic coordinate d[160]=1 is used. The supplied
base U is reused; the new tangent has84x30 entries. Classical M/B/K, F, the test
responses, geometry, coefficient maps, initial isometry and occupation operand
are held fixed in THIS explicitly declared affine control. Their physical total
derivatives, source contacts and density/reference derivatives are not zeroed.

The finite controls independently propagate H0+epsilon*V_d from the initial
isometry. Their84-mode finite-field cutoff is a numerical control, not a full
nonlinear field/collider solve or original physical derivative admission.

No calculation is executed at import. A caller must save each callback event
before narration; callbacks may supply previously saved finite-control results
through ``finite_cache`` to resume without repeating those applications.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping

import numpy as np
from scipy.integrate import solve_ivp

from bhsm.interface.muon_causal_operator_wall_current import (
    forced_scalar_canonical, gauss_table, gauge_return_at,
    independent_original_scalar_DAE, magnitude, norms,
)


def existing_magnetic_direction():
    direction = np.zeros(166)
    direction[160] = 1.
    return direction


def _ue(value):
    array = np.asarray(value, complex)
    if array.shape == (84, 84):
        array = array[:, :30]
    if array.shape != (84, 30) or not np.isfinite(array).all():
        raise ValueError('explicit finite84x30 evolved initial isometry required')
    return array


def _coefficient_hamiltonian(path, vertices, interpolate, s, direction=None):
    H = interpolate(path.s, path.history['H'], float(s))
    if H.shape != (84, 84):
        raise ValueError('the declared reached84 Hamiltonian is required')
    if direction is None:
        return H
    V = np.einsum('b,bij->ij', path.coefficients(float(s))@direction, vertices,
                  optimize=True)
    return H, V


def tangent_initial_isometry(path, U, vertices, interpolate, *,
                             rtol=2e-12, atol=2e-17):
    """D_d(UE)'=-iT[H D_d(UE)+V_d UE], with held initial isometry."""
    direction = existing_magnetic_direction()
    def rhs(s, flat):
        H, V = _coefficient_hamiltonian(path, vertices, interpolate, s, direction)
        value = flat.reshape(84, 30)
        return (-1j*path.T*(H@value+V@_ue(U(float(s))))).ravel()
    solution = solve_ivp(rhs, (0., 1.), np.zeros(84*30, complex), method='DOP853',
        rtol=rtol, atol=atol, max_step=.125, dense_output=True)
    if not solution.success:
        raise ArithmeticError(solution.message)
    def tangent(s):
        return solution.sol(float(s)).reshape(84, 30)
    return tangent, dict(method='DOP853', nfev=solution.nfev, rtol=rtol,
        atol=atol, max_step=.125, integrated_shape=[84, 30],
        initial_tangent='held initial isometry; derivative zero, no physical vacuum selected')


def finite_affine_initial_isometry(path, vertices, interpolate, epsilon, *,
                                   rtol=2e-12, atol=2e-15):
    """Independent finite-field propagation, with no tangent/base-U input."""
    direction = existing_magnetic_direction()
    def rhs(s, flat):
        H, V = _coefficient_hamiltonian(path, vertices, interpolate, s, direction)
        return (-1j*path.T*(H+epsilon*V)@flat.reshape(84, 30)).ravel()
    solution = solve_ivp(rhs, (0., 1.), np.eye(84, dtype=complex)[:, :30].ravel(),
        method='DOP853', rtol=rtol, atol=atol, max_step=.125, dense_output=True)
    if not solution.success:
        raise ArithmeticError(solution.message)
    def evolved(s):
        return solution.sol(float(s)).reshape(84, 30)
    return evolved, dict(epsilon=float(epsilon), method='DOP853', nfev=solution.nfev,
        rtol=rtol, atol=atol, max_step=.125,
        field_family='H_epsilon=H0+epsilon*V_d; no nonlinear field re-solve',
        finite_field_domain='declared reached84 compression; higher-order paths retain its cutoff')


def _current_terms(path, state, vertices, interpolate, c, b, *, tangent=None):
    """Stage4 currents or their state derivative; all80 vertices remain active."""
    direct = np.zeros((166, 30, 30), complex)
    scalar_pullback = np.zeros_like(direct)
    forcing = []
    for s, weight in zip(c, b):
        ue = _ue(state(float(s)))
        if tangent is None:
            operator = np.einsum('ai,bac,cj->bij', ue.conj(), vertices, ue, optimize=True)
        else:
            due = _ue(tangent(float(s)))
            operator = (np.einsum('ai,bac,cj->bij', due.conj(), vertices, ue, optimize=True)
                +np.einsum('ai,bac,cj->bij', ue.conj(), vertices, due, optimize=True))
        coefficient = path.coefficients(float(s))
        direct -= path.T**2*weight*np.tensordot(coefficient[:64].T, operator[:64], axes=1)
        scalar_pullback -= path.T**2*weight*np.tensordot(coefficient[64:].T, operator[64:], axes=1)
        lapse = float(interpolate(path.s, path.N, float(s)))
        forcing.append(-path.T**2*lapse*np.tensordot(path.J[:16, :16].T,
                                                    operator[64:], axes=1))
    return direct, scalar_pullback, np.asarray(forcing)


def _causal_return(path, direct, scalar_pullback, forcing, c, b, a, *, original_check=False):
    """New RHS through the unchanged scalar system, with both endpoint types."""
    canonical = forced_scalar_canonical(path, forcing, a, b)
    returned = np.zeros((134, 900), complex)
    for index in range(4):
        G, Gd = path.wall_input_at_sample(index+1)
        ell, momentum = gauge_return_at(path, f'q{index:03d}', canonical['stages'][index])
        returned += b[index]*(G.T@ell+Gd.T@momentum)
    final = canonical['final']
    Hc, Pc = path.hs['final'][:16], path.hs['final'][16:]
    endpoint = Pc.T@final[:16]-Hc.T@final[16:]
    Gf, _ = path.wall_input_at_sample(5)
    _, final_gauge_momentum = gauge_return_at(path, 'hi', final)
    # The forced initial correction is held zero; its initial temporal term vanishes.
    gauge_endpoint = Gf.T@final_gauge_momentum
    wall = direct[32:].reshape(134, 900)+returned
    arrays = dict(Higgs_current_stage_hat=forcing,
        direct_matter_pullback166_hat=direct,
        scalar_matter_pullback166_hat=scalar_pullback,
        scalar_forced_stages=canonical['stages'].reshape(4, 32, 30, 30),
        scalar_forced_final=final.reshape(32, 30, 30),
        scalar_causal_wall_return134_hat=returned.reshape(134, 30, 30),
        actual_direct_plus_causal_wall134_hat=wall.reshape(134, 30, 30),
        scalar_symplectic_endpoint166_hat=endpoint.reshape(166, 30, 30),
        wall_gauge_temporal_endpoint_hat=gauge_endpoint.reshape(134, 30, 30),
        wall_gauge_Euler_return_hat=(returned-gauge_endpoint).reshape(134, 30, 30))
    metrics = dict(canonical_stage_residual=norms(canonical['canonical_equation_residual']),
        same_rule_scalar_Green_identity=norms(returned-scalar_pullback[32:].reshape(134, 900)-endpoint[32:]),
        omitted_scalar_endpoint_negative_control=norms(wall-(direct+scalar_pullback)[32:].reshape(134, 900)))
    if original_check:
        original = independent_original_scalar_DAE(path, forcing, a, b)
        metrics.update(independent_original_DAE_residual=norms(original['equation_residual']),
            independent_original_DAE_stage_difference=norms(original['stages']-canonical['stages']),
            independent_original_DAE_final_difference=norms(original['final']-final))
        arrays['original_DAE_stages'] = original['stages'].reshape(4, 32, 30, 30)
    return arrays, metrics


COMPARE_KEYS = ('Higgs_current_stage_hat', 'scalar_forced_final',
                'actual_direct_plus_causal_wall134_hat', 'scalar_symplectic_endpoint166_hat')


def affine_current_derivative(path, U, vertices, interpolate, *,
        steps=(.5, .25, .125), checkpoint: Callable | None=None,
        finite_cache: Mapping | None=None, analytic_cache: Mapping | None=None):
    """Return one source-restricted derivative and independent finite controls.

    ``checkpoint(event, arrays, metadata)`` must persist arrays/hashes/equations
    before returning. Reused ``finite_cache`` entries are keyed by ``float.hex``
    epsilon, and contain {arrays, metadata}; the CALLER must validate their
    exact input/code identities and hashes before supplying them here.

    No V_cd contact is added because V_c is held fixed in the declared affine
    control. This is never an assumption that the physical V_cd vanishes. The
    scalar F/test/geometry derivative and occupation/reference motion remain
    additional required terms of the physical total derivative.
    """
    c, b, a = gauss_table()
    if magnitude(c-path.c) > 2e-14:
        raise ValueError('chronological rule identity changed')
    steps = tuple(float(step) for step in steps)
    if len(steps) < 3 or any(not np.isfinite(step) or step <= 0 for step in steps):
        raise ValueError('at least three explicit positive finite difference steps required')
    if any(right >= left for left, right in zip(steps, steps[1:])):
        raise ValueError('independent difference steps must shrink')
    if analytic_cache is not None:
        analytic=analytic_cache['arrays'];analytic_metrics=analytic_cache['metadata']
    else:
        tangent, tangent_solver = tangent_initial_isometry(path, U, vertices, interpolate)
        direct, pullback, forcing = _current_terms(path, U, vertices, interpolate, c, b, tangent=tangent)
        analytic, analytic_metrics = _causal_return(path, direct, pullback, forcing, c, b, a,
                                                   original_check=True)
        analytic['tangent_UE_stages'] = np.asarray([tangent(float(s)) for s in c])
        analytic['tangent_UE_final'] = tangent(1.)
        analytic_metrics['source_direction'] = {'coordinate166':160, 'coordinate574':568, 'coefficient':1.}
        analytic_metrics['tangent_solver'] = tangent_solver
        analytic_metrics['current_derivative_Hermiticity'] = norms(
            forcing-forcing.conj().swapaxes(-1, -2))
        analytic_metrics['wall_derivative_Hermiticity'] = norms(
            analytic['actual_direct_plus_causal_wall134_hat']-
            analytic['actual_direct_plus_causal_wall134_hat'].conj().swapaxes(-1, -2))
        if checkpoint is not None:
            checkpoint('analytic_affine_current_derivative', analytic, analytic_metrics)
    cache = {} if finite_cache is None else dict(finite_cache)
    finite_records = []
    for step in steps:
        terms = []
        for multiplier in (2., 1., -1., -2.):
            epsilon = float(multiplier*step)
            identity = epsilon.hex()
            if identity not in cache:
                finite, solver = finite_affine_initial_isometry(path, vertices, interpolate, epsilon)
                dg, sh, jh = _current_terms(path, finite, vertices, interpolate, c, b)
                values, consistency = _causal_return(path, dg, sh, jh, c, b, a)
                sample = np.asarray([finite(float(s)) for s in c])
                metadata = dict(solver=solver, consistency=consistency,
                    sample_current_isometry_error=norms(sample.conj().swapaxes(-1, -2)@sample-np.eye(30)))
                compact = {key: values[key] for key in COMPARE_KEYS}
                cache[identity] = dict(arrays=compact, metadata=metadata)
                if checkpoint is not None:
                    checkpoint('finite_affine_'+identity, compact, metadata)
            terms.append(cache[identity]['arrays'])
        differences = {}
        record = dict(step=step, difference_rule='fourth-order central (-f(2h)+8f(h)-8f(-h)+f(-2h))/(12h)',
                      errors={}, physical_derivative_admission=False)
        for key in COMPARE_KEYS:
            fd = (-terms[0][key]+8*terms[1][key]-8*terms[2][key]+terms[3][key])/(12*step)
            error = fd-analytic[key]
            reference = magnitude(analytic[key])
            record['errors'][key] = dict(**norms(error),
                derivative_maximum_entry_absolute=reference,
                relative_to_derivative_maximum=(magnitude(error)/reference if reference else None),
                finite_difference_roundoff_scale=np.finfo(float).eps*
                    sum(abs(weight)*magnitude(term[key]) for weight, term in zip((1, 8, 8, 1), terms))/(12*step))
            differences[key+'_fourth_order'] = fd
        if checkpoint is not None:
            checkpoint('finite_difference_step_'+step.hex(), differences, record)
        finite_records.append(record)
    report = dict(classification='FIXED_GEOMETRY_FIXED_CLASSICAL_MAP_AFFINE_OPERATOR_CURRENT_DERIVATIVE',
        analytic=analytic_metrics, independent_finite_field=finite_records,
        source_direction={'coordinate166':160, 'coordinate574':568, 'coefficient':1.},
        field_family='H0+epsilon*V_d; V_c held fixed by affine control definition only',
        classical_scope='saved M/B/K,F,test/endpoint maps fixed; new derivative forcing RHS only',
        quantum_scope='initial30, reached84; no density/reference contraction',
        physical_flags=dict(physical_total_derivative_admitted=False, physical_wall_closed=False,
            physical_collider_solved=False, coupled_physical_corrections=0,
            state_or_reference_selected=False, physical_a_mu=None, physical_g_mu=None),
        error_scope='same four-node classical/current rule; independent affine finite-field differences; no physical time/radial/domain error enclosure',
        NEXT_OPERAND='Complete actual source-chart contacts, classical operator/test/domain motion, geometry/interface/native/exterior terms and physical state/reference correspondence before physical admission.')
    return analytic, report, cache
