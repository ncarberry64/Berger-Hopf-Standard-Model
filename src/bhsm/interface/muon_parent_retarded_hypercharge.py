"""Retarded parent Maxwell DtN applications in the retained central sector.

The hypercharge projection of the saved coexact eight photon lifts commutes
with the mechanical SU(2) connection.  The actual radial/time/shift terms
therefore close in that sector.  This implements the parent fixed-trace
functional, not a chosen reflecting interface condition.  The wall trace
is the input; its reaction is the output to a later paired interface solve.

The receipt-pinned E1+ snapshot below is frozen explicitly.  It is an
evaluated predecessor action component, not a stationary E1 solution or
the completed native photon kernel.  Source pulses and finite basis orders
are numerical Green-application probes, not selected particle modes,
lifetimes, physical soft transfers, or values of the heat cutoff.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import simpson, solve_ivp
from scipy.linalg import cho_factor, cho_solve
from scipy.special import eval_jacobi, gammaln

from .ae3_c2_photon_symbol_audit import stable_weight_and_log_derivative
from .muon_birth_candidate_geometry_action import (
    ROOT, RESET_RECEIPT, STATE_SOURCE, evaluate_retained_candidate_geometry,
)
from .muon_matched_mechanical_source import angular_blocks
from .muon_moving_geometric_action import retained_state
from .muon_parent_maxwell_velocity import current_parent_fields


SOURCE = 'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz'
WALL = np.pi/2
ALPHA = (np.sqrt(45.)-3)/2


def central_source_reduction(repository=ROOT):
    """Verify the actual hypercharge source closure before scalar reduction."""
    path = Path(repository)/SOURCE
    with np.load(path, allow_pickle=False) as data:
        original = np.array(data['original_n1'])
    central = np.zeros_like(original)
    central[:, :, 3] = original[:, :, 3]
    S = central.reshape(8, -1).T
    C, T, contact, J, ad = angular_blocks(1)
    C, T, contact = (np.kron(A, np.eye(2)) for A in (C, T, contact))
    G0 = np.einsum('imn,cd->icmdn', 2j*J, np.eye(4))
    G1 = np.einsum('icd,mn->icmdn', ad, np.eye(2))
    G = np.kron((G0-G1).reshape(24, 8), np.eye(2))
    checks = dict(
        background_commutator_norm=float(np.linalg.norm(T@S)),
        curvature_contact_norm=float(np.linalg.norm(contact@S)),
        coexact_Gauss_norm=float(np.linalg.norm(G.conj().T@S)),
        curl_squared_9_residual=float(np.linalg.norm(C.conj().T@C@S-9*S)),
        source_Gram_10_over_3_residual=float(np.linalg.norm(S.conj().T@S-(10/3)*np.eye(8))))
    if max(checks.values()) > 2e-11:
        raise ValueError('saved central source no longer closes the retained coexact sector')
    return dict(source_Gram=S.conj().T@S, checks=checks,
                source_path=SOURCE, source_sha256=sha256(path.read_bytes()).hexdigest(),
                physical_total_photon_projection=False,
                saved_central_source_norm_squared=10/3,
                evaluated_coordinate='unit angular lift times H_Y; saved central source is sqrt(10/3) times this lift',
                internal_generator='H_Y=-iY/sqrt(10/3); Tr16(H_Y^dagger H_Y)=1')


def frozen_e1_coefficients(rho, repository=ROOT):
    """Evaluate the actual E1+ metric and all predecessor Maxwell densities.

    beta is the original one-form coefficient, not beta=T_b b.  Accordingly
    there is no invented H/2 chart contact in this coordinate.  The common
    kappa1/connection-trace attachment factor is factored from every term.
    """
    repository = Path(repository)
    candidate = evaluate_retained_candidate_geometry(repository)
    q, velocity, multipliers = retained_state(repository)
    state = np.concatenate((q, velocity, multipliers))[None]
    rho = np.asarray(rho, float)
    if rho.ndim != 1 or not np.isfinite(rho).all() or np.any(rho <= 0) or np.any(rho > WALL):
        raise ValueError('radial points must lie in 0<rho<=pi/2')
    fields = current_parent_fields(state, [np.log(candidate['geometry']['R4'])], rho)
    weight = np.array([stable_weight_and_log_derivative(float(x))[0] for x in rho])
    K, C, r, nu, shift = (fields[key][0] for key in (
        'connection_component_coefficient_per_kappa1', 'C_rho',
        'base_radius', 'proper_lapse', 'proper_shift_rho'))
    common = 2*np.pi**2*K*weight
    e, radial, angular = common*C*r/nu, common*nu*r/C, common*nu*C/r
    return dict(rho=rho, electric=e, radial=radial, angular=angular,
                shift=shift, weight=weight, geometry=fields,
                state_source=candidate['source'],
                overall_normalization='kappa1 divided by the SAME connection embedding index; not assigned',
                field_coordinate='original beta one-form coefficient',
                geometry_scope='FROZEN_ACTUAL_E1_PLUS_COEFFICIENT_COMPONENT',
                stationary_base_claim=False)


def regular_radial_basis(rho, order):
    """Friedrichs finite-energy interior tests plus an independent wall lift.

    Lambda~8 rho^3/(3pi), r_orbit~C_rho(0)rho, K_comp and lapse finite.
    Hence radial density~rho^4, angular density~rho^2, d/r~rho^-2.
    The coexact indicial equation is alpha(alpha+3)=9.  The negative root
    has divergent action energy; the positive root is retained.  Interior
    columns vanish at the wall; prescribing that trace is part of DtN.
    Jacobi polynomials are normalized for the pole kinetic weight
    x^(4+2alpha)(1-x)^2.  They span exactly the same polynomial spaces
    as Legendre columns; this changes numerical coordinates, not the form.
    """
    if type(order) is not int or order < 1:
        raise ValueError('positive radial Galerkin order required')
    rho = np.asarray(rho, float)
    if np.any(rho <= 0) or np.any(rho > WALL):
        raise ValueError('basis evaluated on regular cap points')
    x = rho/WALL
    regular = x**ALPHA
    derivative = ALPHA*x**(ALPHA-1)/WALL
    B, D = [], []
    for j in range(order):
        a, b = 2., 4+2*ALPHA
        lognorm = (gammaln(j+a+1)+gammaln(j+b+1)-gammaln(j+1)
                   -gammaln(j+a+b+1)-np.log(2*j+a+b+1))
        normalization = np.exp(-lognorm/2)
        value = normalization*eval_jacobi(j, a, b, 2*x-1)
        first = (normalization*(j+a+b+1)/WALL
                 *eval_jacobi(j-1, a+1, b+1, 2*x-1)) if j else np.zeros_like(x)
        B.append(regular*(1-x)*value)
        D.append((derivative*(1-x)-regular/WALL)*value+regular*(1-x)*first)
    B.append(regular); D.append(derivative)
    return np.column_stack(B), np.column_stack(D)


def maxwell_galerkin_form(order, coefficient_evaluator, *, quadrature_order=256):
    """Assemble M,N,K from the complete reduced Lorentz Maxwell action.

    L=(dotq M dotq)/2-dotq N q-(q K q)/2.  Thus p=M dotq-N q and
    M qdd+(N^T-N) qdot+Kq=j.  The last coordinate is a prescribed wall
    trace, with its reaction retained; no Robin coefficient is inserted.
    """
    if type(quadrature_order) is not int or quadrature_order <= order+1:
        raise ValueError('quadrature must resolve the represented radial form')
    nodes, weights = leggauss(quadrature_order)
    rho, weights = WALL*(nodes+1)/2, WALL*weights/2
    data = coefficient_evaluator(rho)
    B, D = regular_radial_basis(rho, order)
    e, r, d, shift = (np.asarray(data[k], float) for k in ('electric', 'radial', 'angular', 'shift'))
    if any(A.shape != rho.shape or not np.isfinite(A).all() for A in (e, r, d, shift)):
        raise ValueError('same finite radial density grid required')
    if np.any(e <= 0) or np.any(r <= 0) or np.any(d <= 0):
        raise ValueError('positive lapse and normal-frame Maxwell form required')
    M = B.T@((weights*e)[:, None]*B)
    N = B.T@((weights*e*shift)[:, None]*D)
    Kshift = D.T@((weights*e*shift**2)[:, None]*D)
    Kspatial = D.T@((weights*r)[:, None]*D)+B.T@((9*weights*d)[:, None]*B)
    M = (M+M.T)/2
    Kshift, Kspatial = (Kshift+Kshift.T)/2, (Kspatial+Kspatial.T)/2
    K = Kspatial-Kshift
    np.linalg.cholesky(M); np.linalg.cholesky(Kspatial)
    return dict(M=M, N=N, K=K, Kspatial=Kspatial, Kshift=Kshift,
                gyro=N.T-N, radial_order=order,
                quadrature_order=quadrature_order, coefficients=data,
                coordinate_stiffness_min_eigenvalue=float(np.linalg.eigvalsh(K)[0]),
                mass_condition_number=float(np.linalg.cond(M[:order, :order])),
                shift_light_ratio_max=float(np.max(abs(shift)*np.sqrt(e/r))),
                pole_domain='finite action Friedrichs closure; alpha(alpha+3)=9',
                wall_domain='input Dirichlet trace; its parent reaction is returned')


def compact_trace_pulse(times, duration):
    """C3 compact unit trace probe and its first/second derivatives."""
    t = np.asarray(times, float)
    if not np.isfinite(duration) or duration <= 0:
        raise ValueError('positive explicitly numerical source duration required')
    inside = (t > 0) & (t < duration)
    z = np.pi*t/duration; s, c = np.sin(z), np.cos(z); a = np.pi/duration
    value = np.where(inside, s**4, 0.)
    first = np.where(inside, 4*a*s**3*c, 0.)
    second = np.where(inside, 4*a*a*(3*s*s*c*c-s**4), 0.)
    return value, first, second


def retarded_parent_dtn_application(form, *, source_duration, final_time,
                                    time_steps, rtol=2e-10, atol=2e-12):
    """Execute fixed-trace parent response, conormal, work and adjoint checks.

    Only the perturbation has zero past Cauchy data.  The background metric
    and mechanical connection are the supplied coefficient evaluator's.
    The compact pulse is a CONTROL_ONLY Green input; no initial base gauge
    field, scalar field, physical external current, or soft limit is set.
    """
    if type(time_steps) is not int or time_steps < 8 or final_time <= source_duration:
        raise ValueError('resolve an interval extending beyond compact source support')
    M, C, K = (form[key] for key in ('M', 'gyro', 'K'))
    n = form['radial_order']; factor = cho_factor(M[:n, :n])
    solve = lambda x: cho_solve(factor, x)
    A = np.block([[np.zeros((n, n)), np.eye(n)],
                  [-solve(K[:n, :n]), -solve(C[:n, :n])]])
    forcing = -solve(np.column_stack((K[:n, n], C[:n, n], M[:n, n])))

    def force(t):
        g, dg, ddg = compact_trace_pulse(t, source_duration)
        return forcing@np.array([g, dg, ddg])

    def rhs(t, y):
        return A@y+np.concatenate((np.zeros(n), force(t)))

    # Independent dense quadrature, split exactly where the compact source
    # stops.  This avoids integrating its piecewise second derivative
    # across a Simpson panel.  time_steps still controls the ODE max step.
    intervals = [max(8, 2*int(np.ceil(2*time_steps*t/final_time)))
                 for t in (source_duration, final_time-source_duration)]
    split = intervals[0]
    grid = np.concatenate((np.linspace(0, source_duration, split+1),
                           np.linspace(source_duration, final_time, intervals[1]+1)[1:]))

    def integrate(values):
        return float(simpson(values[:split+1], x=grid[:split+1])
                     +simpson(values[split:], x=grid[split:]))
    result = solve_ivp(rhs, (0, final_time), np.zeros(2*n), method='DOP853',
                       rtol=rtol, atol=atol, max_step=final_time/time_steps,
                       dense_output=True)
    if not result.success:
        raise ArithmeticError(f'retarded Maxwell integration failed: {result.message}')
    y = result.sol(grid).T
    g, dg, ddg = compact_trace_pulse(grid, source_duration)
    q, velocity = np.column_stack((y[:, :n], g)), np.column_stack((y[:, n:], dg))
    forces = np.column_stack((g, dg, ddg))@forcing.T
    acceleration = np.column_stack(((y@A.T)[:, n:]+forces, ddg))
    residual = acceleration@M.T+velocity@C.T+q@K.T
    reaction = residual[:, -1]
    energy = .5*np.einsum('ti,ij,tj->t', velocity, M, velocity)+.5*np.einsum('ti,ij,tj->t', q, K, q)
    # This positive normal-frame quadratic is distinct from the conserved
    # coordinate-time energy above, which can be indefinite for a large shift.
    normal_energy = (.5*np.einsum('ti,ij,tj->t', velocity, M, velocity)
                     -np.einsum('ti,ij,tj->t', velocity, form['N'], q)
                     +.5*np.einsum('ti,ij,tj->t', q, form['Kspatial']+form['Kshift'], q))
    work = integrate(reaction*dg)
    momentum = velocity@M.T-q@form['N'].T
    lagrangian = (.5*np.einsum('ti,ij,tj->t', velocity, M, velocity)
                  -np.einsum('ti,ij,tj->t', velocity, form['N'], q)
                  -.5*np.einsum('ti,ij,tj->t', q, K, q))
    action = integrate(lagrangian)
    trace_contraction = integrate(g*reaction)
    endpoint = float(q[-1]@momentum[-1]-q[0]@momentum[0])
    Bwall, Dwall = regular_radial_basis(np.array([WALL]), n)
    wall_data = form['coefficients']
    # The direct conormal is an independent derivative test of the radial
    # approximation, not the assembled reaction row recycled as a check.
    wall_r = wall_data['wall_radial']
    wall_e, wall_shift = wall_data.get('wall_electric', 0.), wall_data.get('wall_shift', 0.)
    if wall_e < 0 or wall_r <= 0 or wall_r-wall_e*wall_shift**2 <= 0:
        raise ValueError('prescribed wall trace requires a timelike wall worldtube')
    radial_derivative = np.einsum('i,ti->t', Dwall[0], q)
    # Opposite the outward action flux.  The retained wall has sin(2rho)=0
    # and hence shift=0 analytically, but the complete expression is kept.
    direct_conormal = wall_e*wall_shift*dg+(wall_r-wall_e*wall_shift**2)*radial_derivative
    direct_conormal_pairing = integrate(g*direct_conormal)
    reaction_norm = float(np.sqrt(integrate(reaction**2)))
    # Adjoint readout at a fixed interior point, using the represented form.
    eval_basis = regular_radial_basis(np.array([.75*WALL]), n)[0][0, :n]
    readout = np.concatenate((eval_basis, np.zeros(n)))
    adjoint = solve_ivp(lambda t, z: -A.T@z, (final_time, 0), readout,
                        method='DOP853', rtol=rtol, atol=atol,
                        max_step=final_time/time_steps, dense_output=True)
    if not adjoint.success:
        raise ArithmeticError('retarded response adjoint failed')
    z = adjoint.sol(grid).T
    adjoint_force = np.einsum('ti,ti->t', z[:, n:], forces)
    adjoint_contraction = integrate(adjoint_force)
    output = float(readout@y[-1])
    return dict(times=grid, trace=g, reaction=reaction, direct_conormal=direct_conormal,
                state=q, velocity=velocity, energy=energy, normal_energy=normal_energy,
                boundary_trace_contraction=trace_contraction,
                direct_conormal_trace_pairing=direct_conormal_pairing,
                weak_conormal_pairing_difference=float(abs(trace_contraction-direct_conormal_pairing)),
                reaction_L2_norm=reaction_norm,
                action=action, temporal_endpoint_contact=endpoint,
                final_energy=float(energy[-1]), source_work=work,
                energy_work_defect=float(abs(energy[-1]-energy[0]-work)),
                energy_work_relative_defect=float(abs(energy[-1]-energy[0]-work)
                    /(1+abs(energy[-1])+abs(energy[0])+abs(work))),
                on_shell_action_boundary_defect=float(abs(2*action+trace_contraction-endpoint)),
                interior_algebraic_residual_max=float(np.max(abs(residual[:, :-1]))),
                conormal_reaction_L2_difference=float(np.sqrt(integrate((reaction-direct_conormal)**2))),
                adjoint_readout=output, adjoint_source_contraction=adjoint_contraction,
                adjoint_defect=float(abs(output-adjoint_contraction)),
                source_duration=source_duration, final_time=final_time, time_steps=time_steps,
                quadrature_grid_points=len(grid), quadrature_source_breakpoint_split=True,
                source_scope='CONTROL_ONLY compact wall-trace Green application',
                retarded_initial_perturbation='delta A=delta Pi=0 before source support',
                background_initial_state_assigned=False,
                coordinate_energy_may_be_indefinite=True,
                normal_frame_energy_min=float(np.min(normal_energy)),
                numerical_integrator=dict(method='DOP853', rtol=rtol, atol=atol,
                                          evaluations=result.nfev),
                native_heat_evaluated=False, physical_Pauli_contraction=False)


def evaluate_frozen_e1_hypercharge(repository=ROOT, *, radial_orders=(48, 64, 80),
                                   time_steps=(256, 512, 1024)):
    """Apply actual retained coefficients with independent radial/time refinement."""
    repository = Path(repository); source = central_source_reduction(repository)
    snapshot = evaluate_retained_candidate_geometry(repository)
    duration = float(snapshot['geometry']['R4'])/3
    final = 3*duration

    def coefficients(rho):
        data = frozen_e1_coefficients(rho, repository)
        wall = frozen_e1_coefficients(np.array([WALL]), repository)
        data.update(wall_radial=float(wall['radial'][0]),
                    wall_electric=float(wall['electric'][0]),
                    wall_shift=float(wall['shift'][0]))
        return data

    if len(radial_orders) < 2 or len(time_steps) < 2:
        raise ValueError('independent radial and time refinement require two orders each')
    if tuple(sorted(set(radial_orders))) != tuple(radial_orders) or tuple(sorted(set(time_steps))) != tuple(time_steps):
        raise ValueError('strictly increasing radial orders and time steps required')
    runs = []
    refinement = [(order, time_steps[-1], 'RADIAL_AT_FIXED_FINE_TIME') for order in radial_orders]
    refinement += [(radial_orders[-1], steps, 'TIME_AT_FIXED_FINE_RADIAL') for steps in time_steps[:-1]]
    for order, steps, axis in refinement:
        form = maxwell_galerkin_form(order, coefficients, quadrature_order=max(256, 12*order))
        application = retarded_parent_dtn_application(form, source_duration=duration,
            final_time=final, time_steps=steps)
        application['refinement_axis'] = axis
        application['saved_central_source_trace_matrix'] = (
            application['boundary_trace_contraction']*source['source_Gram'])
        application['saved_central_source_diagonal_pairing'] = (
            application['boundary_trace_contraction']*(10/3))
        runs.append(dict(form=form, response=application))
    return dict(source=source, snapshot=snapshot, runs=runs,
                scope='EVALUATED_FROZEN_ACTUAL_E1_PLUS_PREDECESSOR_HYPERCHARGE_DTN_COMPONENT',
                overall_common_normalization_assigned=False,
                completed_native_kernel=False, stationary_E1_base=False)


def _deterministic_npz(path, arrays):
    """Write ordinary NPZ members with fixed archive metadata for replay."""
    with ZipFile(path, 'w', compression=ZIP_STORED) as archive:
        for name, value in sorted(arrays.items()):
            stream = BytesIO()
            np.lib.format.write_array(stream, np.asarray(value), allow_pickle=False)
            member = ZipInfo(name+'.npy', date_time=(1980, 1, 1, 0, 0, 0))
            member.compress_type = ZIP_STORED
            member.external_attr = 0o600 << 16
            archive.writestr(member, stream.getvalue())


def materialize(output, repository=ROOT):
    """Save this new application without modifying retained predecessor evidence."""
    output = Path(output)
    if output.exists():
        raise FileExistsError('use a new output directory and preserve prior evidence')
    output.mkdir(parents=True)
    result = evaluate_frozen_e1_hypercharge(repository)
    summary = []
    for index, item in enumerate(result['runs']):
        form, response = item['form'], item['response']
        _deterministic_npz(output/f'run_{index}.npz', dict(M=form['M'], N=form['N'], K=form['K'],
                 Kspatial=form['Kspatial'], Kshift=form['Kshift'],
                 **{k:v for k,v in response.items() if isinstance(v, np.ndarray)}))
        summary.append(dict(radial_order=form['radial_order'], quadrature_order=form['quadrature_order'],
            **{k:form[k] for k in ('coordinate_stiffness_min_eigenvalue','mass_condition_number','shift_light_ratio_max')},
            **{k:v for k,v in response.items() if not isinstance(v, np.ndarray)}))
    references = [STATE_SOURCE, RESET_RECEIPT, SOURCE,
        'src/bhsm/interface/muon_parent_retarded_hypercharge.py',
        'src/bhsm/interface/muon_parent_maxwell_velocity.py',
        'src/bhsm/interface/muon_matched_mechanical_source.py',
        'src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py']
    receipt = dict(scope=result['scope'], normalization=result['runs'][0]['form']['coefficients']['overall_normalization'],
        input_hashes={p:sha256((Path(repository)/p).read_bytes()).hexdigest() for p in references},
        source_checks=result['source']['checks'], runs=summary,
        source_coordinate=result['source']['evaluated_coordinate'],
        saved_central_source_norm_squared=result['source']['saved_central_source_norm_squared'],
        finite_energy_pole=dict(weight='Lambda~8 rho^3/(3pi)', radial_density_power=4,
            angular_density_power=2, indicial_equation='alpha(alpha+3)=9', alpha=float(ALPHA)),
        geometry_time_policy='Actual E1+ snapshot frozen; old step1222 history is not substituted for E1 chronology',
        wall_worldtube=dict(shift_analytic='sin(2rho)=0 at rho=pi/2',
                            proper_lapse=1., trace_type='TIMELIKE_FIXED_TRACE_DTN_INPUT'),
        source_scope='CONTROL_ONLY prescribed compact wall trace; actual angular source representation',
        coupled_interface_wall_condition_assigned=False,
        approximation_claim='Finite Galerkin source pairing; refinement differences are not certified tail bounds',
        strong_conormal_convergence_claim=False,
        stationary_E1_base=False, complete_native_kernel=False,
        physical_Pauli_contraction=False, common_normalization_assigned=False)
    text = json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False)+'\n'
    (output/'result.json').write_text(text, encoding='utf8', newline='\n')
    return receipt


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    receipt = materialize(args.output)
    print(json.dumps(dict(scope=receipt['scope'], source_checks=receipt['source_checks'],
        runs=[{k:r[k] for k in ('radial_order', 'time_steps', 'boundary_trace_contraction',
            'energy_work_defect', 'adjoint_defect', 'conormal_reaction_L2_difference')} for r in receipt['runs']]), sort_keys=True))
