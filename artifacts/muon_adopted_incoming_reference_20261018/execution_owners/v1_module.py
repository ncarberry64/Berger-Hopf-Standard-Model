"""Original incoming-reference Gauss elimination under the adopted selector.

This is a constrained comparison-block application on inherited nonzero
fields, not a complete stationary reference or a collider Cauchy embedding.
Unresolved native/reference loads remain explicit affine operands.
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial.legendre import leggauss

from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_retarded_hypercharge import regular_radial_basis, WALL
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_nonlinear_chronological_n0_action import analytic_constant_maxwell_batch
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation


M = np.sqrt(8)*np.column_stack((np.eye(3), np.zeros(3)))


def stationary_gauss_realization(raw, *, radial_points=48):
    """Assemble exact n0 parent Gauss rows on a stationary comparison iterate.

    q, lapse/shift, normal position, ALL independent gauge values and H are
    inherited from the incoming raw268. Ordinary coordinate rates vanish
    only for this proposed stationary comparison iterate. Covariant electric
    fields, mechanical curvature and Higgs charge remain in the action.
    The actual incoming moving state is not declared stationary.
    """
    if not np.isrealobj(raw):
        raise ValueError('real incoming material-chart fields required')
    r = np.asarray(raw, float)
    if r.shape != (268,) or not np.isfinite(r).all():
        raise ValueError('actual finite incoming raw268 required')
    if type(radial_points) is not int or radial_points < 8:
        raise ValueError('at least eight original-domain radial points required')
    x, w = leggauss(radial_points)
    rho, weights = WALL*(x+1)/2, WALL*w/2
    q, v, m, s = r[:37], np.zeros(37), r[74:98], r[98]
    geometry = geometric_connection_coefficient_jets(12, q, v, m, rho,
        source_value=s, source_rate=0., clock='coordinate_time')
    names = ('electric', 'radial', 'angular', 'electric_radial', 'shift')
    densities = np.array([[row[k].value for k in names] for row in geometry['rows']])
    lam = np.array([row['connection_lambda'].value for row in geometry['rows']])
    lam_rho = np.array([row['lambda_rho'].value for row in geometry['rows']])
    basis, derivative = regular_radial_basis(rho, 3)
    coefficients = r[100:180].reshape(4, 5, 4).copy()
    gauge = np.einsum('rp,pfc->rfc', basis, coefficients)
    gauge_rho = np.einsum('rp,pfc->rfc', derivative, coefficients)
    gauge[:, 2:] += (lam-1)[:, None, None]*M
    gauge_rho[:, 2:] += lam_rho[:, None, None]*M
    gauge_tau = np.zeros_like(gauge)  # stationary iterate; covariant terms retained
    identity = np.eye(4)
    pv = np.einsum('rp,ci->rcpi', basis, identity).reshape(radial_points, 4, 16)
    pr = np.einsum('rp,ci->rcpi', derivative, identity).reshape(radial_points, 4, 16)
    lift = np.zeros((radial_points, 60, 16))
    lift[:, :4] = pv
    lift[:, 40:44] = pr

    # Intrinsic scalar couples only to the wall trace. Its temporal Gauss
    # Hessian is independent of lambda_H and nu; neither is assigned zero.
    metric = intrinsic_m4_weight_jet(12, q, v, m, source_value=s, source_rate=0.)
    scalar = r[260:264]
    generators = higgs_u2_real_representation()['real_generators']
    source_map = np.einsum('cij,j->ic', generators, scalar)
    volume = 2*np.pi**2
    scalar_temporal_matrix = 2*metric['wT'].value/volume*(source_map.T@source_map)
    initial = coefficients[:, 0].reshape(16)

    def evaluate(temporal_coefficients):
        c = np.asarray(temporal_coefficients, float)
        if c.shape != (16,) or not np.isfinite(c).all():
            raise ValueError('all original16 temporal profile coefficients required')
        delta = c-initial
        a, ar = gauge.copy(), gauge_rho.copy()
        a[:, 0] += np.einsum('rci,i->rc', pv, delta)
        ar[:, 0] += np.einsum('rci,i->rc', pr, delta)
        local = analytic_constant_maxwell_batch(a, gauge_tau, ar, densities)
        gradient = MAXWELL_TO_CAP*np.einsum('rai,ra,r->i', lift, local['gradient'], weights)
        hessian = MAXWELL_TO_CAP*np.einsum('rai,rab,rbj,r->ij', lift, local['hessian'], lift, weights)
        gradient[12:] += scalar_temporal_matrix@c[12:]
        hessian[12:, 12:] += scalar_temporal_matrix
        return dict(gradient=np.real_if_close(gradient).real,
                    hessian=np.real_if_close(hessian).real, gauge=a, gauge_rho=ar,
                    local_gradient=local['gradient'])

    return dict(initial=initial, evaluate=evaluate, rho=rho, radial_quadrature=weights,
                basis=basis, derivative=derivative, geometry=geometry,
                densities=densities, raw=r.copy(), scalar_temporal_matrix=scalar_temporal_matrix)


def eliminate_interior_gauss(raw, *, radial_points=48):
    """Numerically eliminate12 interior rows for EVERY unresolved load ell.

    x_i(ell)=x_particular-K_ii^-1 ell_i. The four inherited wall values are
    fixed inputs; their reaction is returned, not set to zero. This affine
    family is an actual block solve, not a selected reference state.
    """
    realization = stationary_gauss_realization(raw, radial_points=radial_points)
    initial, evaluate = realization['initial'], realization['evaluate']
    before = evaluate(initial)
    k = before['hessian']
    interior = k[:12, :12]
    source_response = -np.linalg.solve(interior, np.eye(12))
    correction = source_response@before['gradient'][:12]
    particular = initial.copy()
    particular[:12] += correction
    after = evaluate(particular)
    wall_response = k[12:, :12]@source_response
    # Independent negative/finite perturbation test of the exact affine
    # elimination. This probes basis columns, not chosen physical occupations.
    affine_defect = 0.
    for j in range(12):
        amplitude = max(1., np.linalg.norm(before['gradient'][:12]))/16
        ell = np.eye(12)[j]*amplitude
        test = particular.copy()
        test[:12] += source_response@ell
        check = evaluate(test)['gradient'][:12]+ell
        affine_defect = max(affine_defect, float(np.max(abs(check))))
    # Independent derivative-form zero-trace test beyond the three interior
    # temporal profiles. It is not declared zero by the Galerkin solve.
    x = realization['rho']/WALL
    phi, phir = 16*x*x*(1-x)**2, 32*x*(1-x)*(1-2*x)/WALL
    def complement(application):
        g = application['local_gradient']
        return MAXWELL_TO_CAP*np.einsum('r,rc->c', realization['radial_quadrature'],
            phi[:, None]*g[:, :4]+phir[:, None]*g[:, 40:44]).real
    return dict(realization=realization, before=before, after=after,
                particular=particular, correction=correction,
                unresolved_load_response=source_response, wall_load_response=wall_response,
                wall_Schur=k[12:, 12:]+k[12:, :12]@source_response@k[:12, 12:],
                affine_identity_residual=affine_defect,
                complement_before=complement(before), complement_after=complement(after))


def stationary_parent_field_realization(raw, *, radial_points=48):
    """All80 original static gauge-value rows on the same inherited seed.

    The scalar's gauge variation is exact and independent of its potential
    matching parameters. Geometry/Higgs variations and quantum loads remain
    independent required rows. No classical/reference background subtraction
    changes the independent-field derivative.
    """
    base = stationary_gauss_realization(raw, radial_points=radial_points)
    r = base['raw']
    initial = r[100:180].copy()
    n = len(base['rho'])
    p = np.einsum('rp,ai->rapi', base['basis'], np.eye(20)).reshape(n, 20, 80)
    pr = np.einsum('rp,ai->rapi', base['derivative'], np.eye(20)).reshape(n, 20, 80)
    lift = np.zeros((n, 60, 80))
    lift[:, :20], lift[:, 40:] = p, pr
    # Reuse the exactly inherited non-temporal base from the16-row assembly.
    original = base['evaluate'](base['initial'])
    metric = intrinsic_m4_weight_jet(12, r[:37], np.zeros(37), r[74:98],
                                    source_value=r[98], source_rate=0.)
    generators = higgs_u2_real_representation()['real_generators']
    u = np.einsum('cij,j->ic', generators, r[260:264])
    field_weights = np.r_[metric['wT'].value, 0., -np.repeat(metric['wS'].value, 3)]
    scalar_k = 2/(2*np.pi**2)*np.kron(np.diag(field_weights), u.T@u)
    wall_mechanical = np.zeros((5, 4))
    wall_mechanical[2:] = M*(metric['mechanical_connection_lambda'].value-1)

    def evaluate(coefficients):
        c = np.asarray(coefficients, float)
        if c.shape != (80,) or not np.isfinite(c).all():
            raise ValueError('all80 original static gauge coefficients required')
        delta = c-initial
        a = original['gauge']+(p@delta).reshape(n, 5, 4)
        ar = original['gauge_rho']+(pr@delta).reshape(n, 5, 4)
        local = analytic_constant_maxwell_batch(a, np.zeros_like(a), ar, base['densities'])
        weights = MAXWELL_TO_CAP*base['radial_quadrature']
        gradient = np.einsum('rai,ra,r->i', lift, local['gradient'], weights, optimize=True)
        hessian = np.einsum('rai,raj,r->ij', lift, local['hessian']@lift, weights, optimize=True)
        wall = c[60:80]+wall_mechanical.reshape(20)
        gradient[60:] += scalar_k@wall
        hessian[60:, 60:] += scalar_k
        value = np.dot(weights, local['value'])+.5*wall@scalar_k@wall
        return dict(value=float(value.real), gradient=gradient.real,
                    hessian=hessian.real, gauge=a, gauge_rho=ar,
                    local_gradient=local['gradient'])

    active = np.array([20*profile+4*field+channel for profile in range(3)
                       for field in (0, 2, 3, 4) for channel in range(4)])
    return dict(base=base, initial=initial, evaluate=evaluate, active=active,
                frozen=np.array(sorted(set(range(80))-set(active))))


def solve_classical_reference_block(raw, *, radial_points=48, max_iterations=12):
    """Damped nonlinear solve of the48 determined classical interior rows.

    All20 inherited wall values and all16 A_rho values stay fixed. Their
    equations are exported, never removed from physical admission. The
    unknown native/reference projected load is retained by its full48-column
    implicit response; no reference occupation or sea is selected here.
    """
    realization = stationary_parent_field_realization(raw, radial_points=radial_points)
    x = realization['initial'].copy()
    evaluate, active = realization['evaluate'], realization['active']
    first = evaluate(x)
    diagonal = np.abs(np.diag(first['hessian'])[active])
    scale = 1/np.sqrt(np.maximum(diagonal, np.max(diagonal)*1e-14))
    history = []
    status = 'ITERATION_LIMIT'
    for iteration in range(max_iterations+1):
        current = evaluate(x)
        g = current['gradient'][active]
        norm = float(np.linalg.norm(scale*g))
        history.append(dict(iteration=iteration, original_row_max=float(np.max(abs(g))),
                            fixed_scaled_norm=norm))
        if np.max(abs(g)) < 2e-11:
            status = 'CLASSICAL_INTERIOR_BLOCK_CONVERGED'
            break
        if iteration == max_iterations:
            break
        k = current['hessian'][np.ix_(active, active)]
        scaled = scale[:, None]*k*scale[None]
        step = scale*np.linalg.solve(scaled, -scale*g)
        accepted = False
        for half in range(18):
            fraction = 2.**(-half)
            candidate = x.copy()
            candidate[active] += fraction*step
            trial = evaluate(candidate)
            merit = float(np.linalg.norm(scale*trial['gradient'][active]))
            if np.isfinite(merit) and merit < norm:
                history[-1].update(step_fraction=fraction, accepted_scaled_norm=merit)
                x, accepted = candidate, True
                break
        if not accepted:
            status = 'LINE_SEARCH_STALL'
            break
    final = evaluate(x)
    k = final['hessian'][np.ix_(active, active)]
    response = -np.linalg.solve(k, np.eye(len(active)))
    return dict(realization=realization, initial=first, final=final,
                coefficients=x, active=active, status=status, history=history,
                unresolved_load_response=response,
                frozen_row_load_response=final['hessian'][np.ix_(realization['frozen'], active)]@response)


def reference_endpoint_data(application):
    """Consume the solved fields in original face and temporal momenta.

    Literal face conormals are kept separate from integrated wall-lift
    reactions. Neither is set to zero or identified with a child/beam.
    """
    realization = application['realization']
    base, c = realization['base'], application['coefficients']
    r = base['raw']
    geometry = geometric_connection_coefficient_jets(12, r[:37], np.zeros(37),
        r[74:98], np.array([WALL]), source_value=r[98], source_rate=0.)
    row = geometry['rows'][0]
    b, br = regular_radial_basis(np.array([WALL]), 3)
    a = np.einsum('rp,pfc->rfc', b, c.reshape(4, 5, 4))
    ar = np.einsum('rp,pfc->rfc', br, c.reshape(4, 5, 4))
    a[:, 2:] += M*(row['connection_lambda'].value-1)
    ar[:, 2:] += M*row['lambda_rho'].value
    densities = np.array([[row[k].value for k in ('electric','radial','angular','electric_radial','shift')]])
    local = analytic_constant_maxwell_batch(a, np.zeros_like(a), ar, densities)
    face = MAXWELL_TO_CAP*local['gradient'][0, 40:60].real
    final = application['final']
    bulk = analytic_constant_maxwell_batch(final['gauge'], np.zeros_like(final['gauge']),
                                          final['gauge_rho'], base['densities'])
    momenta = MAXWELL_TO_CAP*np.einsum('rp,rfc,r->pfc', base['basis'],
        bulk['gradient'][:, 20:40].reshape(-1, 5, 4), base['radial_quadrature']).real
    metric = intrinsic_m4_weight_jet(12, r[:37], np.zeros(37), r[74:98],
                                    source_value=r[98], source_rate=0.)
    generators = higgs_u2_real_representation()['real_generators']
    covariant_h = np.einsum('c,cij,j->i', a[0,0], generators, r[260:264])
    scalar_momentum = 2*metric['wT'].value/(2*np.pi**2)*covariant_h
    return dict(parent_outward_radial_gauge_conormal=face,
                temporal_gauge_momentum80=momenta.reshape(80),
                scalar_real_temporal_momentum4=scalar_momentum,
                wall_lift_reaction20=final['gradient'][60:].copy(),
                wall_total_connection=a[0], R4=metric['R4'].value,
                proper_lapse=metric['induced_lapse'].value)


def assigned_reference_constraint_polynomial(application, *, cap_points=32):
    """Evaluate the remaining original24 geometry/multiplier rows.

    Return coefficients of nu_action^2 and gamma rather than assign their
    unknown values. This evaluates a residual, not a full-field correction.
    """
    from .muon_birth_coupled_constraint_retraction import pointwise_assigned_action
    from .muon_parent_gauge_geometry_correction import retained_scalar_matching_coefficients, ORBIT_VOLUME_SQUARED
    from .muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet
    realization = application['realization']
    base, c = realization['base'], application['coefficients']
    r = base['raw']
    values = np.einsum('rp,pfc->rfc', base['basis'], c.reshape(4,5,4))
    radial = np.einsum('rp,pfc->rfc', base['derivative'], c.reshape(4,5,4))
    fields = dict(gauge=values[:,None], gauge_tau=np.zeros_like(values[:,None]),
                  gauge_rho=radial[:,None], gauge_angular=np.zeros((len(values),1,3,5,4)))
    matching = retained_scalar_matching_coefficients()
    action = pointwise_assigned_action(r[:37], np.zeros(37), r[74:98],
        rho=base['rho'], radial_quadrature=base['radial_quadrature'], fields=fields,
        H_real=r[260:264], H_rate=np.zeros(4), wall_gauge=c.reshape(4,5,4)[-1],
        lambda_H=matching['lambda_H'], nu_squared_action=None, surface_gamma=None,
        normal=r[98], normal_rate=0., cap_points=cap_points)
    metric = intrinsic_m4_weight_jet(12, r[:37], np.zeros(37), r[74:98],
                                    source_value=r[98], source_rate=0.)
    value_map = np.zeros((1,4,8)); value_map[0,:,:4] = np.eye(4)
    derivative_map = np.zeros((1,4,4,8)); derivative_map[0,0,:,4:] = np.eye(4)
    scalar = material_intrinsic_higgs_gauge_action_jet(metric,
        scalar_coefficients=np.r_[r[260:264],np.zeros(4)], scalar_value_map=value_map,
        scalar_derivative_map=derivative_map, gauge_coefficients=c[60:],
        gauge_trace_map=np.eye(20).reshape(1,5,4,20), angular_quadrature=np.ones(1),
        lambda_H=matching['lambda_H'], nu_squared_action=0.)
    # Zero is used only to extract the returned polynomial coefficients,
    # not as a physical Higgs-center or energy-unit assignment.
    p = scalar['nu_squared_polynomial_coefficients']
    coefficients = np.array([action['multiplier_constraints'],
        p[1].gradient[74:98]/ORBIT_VOLUME_SQUARED,
        p[2].gradient[74:98]/ORBIT_VOLUME_SQUARED])
    higgs = np.array([term.gradient[100:104]/ORBIT_VOLUME_SQUARED for term in p])
    return dict(multiplier_nu_polynomial3x24=coefficients,
                multiplier_area_per_gamma24=action['surface_gradient_per_gamma'][74:98],
                scalar_nu_polynomial3x4=higgs, matching=matching,
                polynomial_equation='C0+nu_action_squared*C1+nu_action_squared^2*C2+gamma*C_area+surviving_native_reference_rows=0',
                physical_nu_or_gamma_assigned=False)
