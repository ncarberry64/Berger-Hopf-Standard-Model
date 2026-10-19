"""One coupled off-shell application of the exact SM-reference subtraction.

The retained zeta action and resolved native heat are replacements, not
independent species. This module consumes the known subtraction and its
field-dependent Hessian. Unknown heat/state/exterior loads and their
derivatives remain separate operands. No interacting inverse is inferred.
"""
from __future__ import annotations

import numpy as np

from .muon_adopted_incoming_reference import static_field_maps, M
from .muon_moving_geometric_action import moving_cap_action_jet
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import (
    background_subtracted_maxwell_action_jet, full_maxwell_weak_geometric_jets,
)
from .muon_nonlinear_chronological_n0_action import analytic_constant_maxwell_batch
from .muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_parent_gauge_geometry_correction import (
    retained_scalar_matching_coefficients, ORBIT_VOLUME_SQUARED,
)
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_parent_retarded_hypercharge import WALL
from .aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient


# q37,m24,s1; original80+extraAt4; H4; log(common GeV unit).
GEOMETRY_IDS = np.r_[np.arange(37), np.arange(74,99)]
GEOMETRY = slice(0,62)
GAUGE = slice(62,146)
HIGGS = slice(146,150)
LOG_UNIT = 150
MULTIPLIER_ROWS = np.arange(37,61)
EULER_ROWS = np.arange(150)  # dS/de is NOT the physical calibration equation.


def coupled_seed(saved):
    """Restore actual saved fields; do not solve/refine the52 directions."""
    r = saved['incoming_seed_raw268']
    matching = retained_scalar_matching_coefficients()
    h0,h1,_ = saved['scalar_nu_polynomial3x4']
    u = -np.dot(h1,h0)/np.dot(h1,h1)
    e = .5*np.log(matching['nu_squared_GeV_squared']/u)
    return np.r_[r[GEOMETRY_IDS],saved['solved_explicit_coefficients84'],r[260:264],e]


def scalar_joint_lift():
    """Map original geometry100,H4,gauge84,e to common static151 chart."""
    p = np.zeros((189,151))
    p[GEOMETRY_IDS,np.arange(62)] = 1.
    p[100:104,146:150] = np.eye(4)
    p[104:188,62:146] = np.eye(84)
    p[188,150] = 1.
    return p


def _geometry_fields(x):
    z = np.asarray(x,float)
    if z.shape != (151,) or not np.isfinite(z).all():
        raise ValueError('finite explicit coupled151 iterate required')
    raw = np.zeros(100)
    raw[GEOMETRY_IDS] = z[:62]
    return raw


def reference_subtraction(raw):
    """Exact +(59/30) N_b/R4 two-jet, with ambient original lapse.

    This removes the old attached zero-source determinant, not inherited
    occupations. Full SM heat and correlations are still required. The
    induced lapse is not interchangeable with ambient N_b in this term.
    """
    w = intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],
                              source_value=raw[98],source_rate=raw[99])
    return standard_model_casimir_coefficient()*w['fields']['N']/w['R4']


def assemble_known_coupled(x, *, rho, radial_weights, cap_points=32,
                           saved=None, seed=None):
    """Original static action two-jet, plus the evaluated replacement term.

    Unknown Gamma_heat, reference20 contractions, bulk native, endpoints
    and exterior rows are not represented by zeros in this returned known
    subtotal. Their value/Jacobian operands remain required in the caller.
    Surface gamma is returned as an unevaluated coefficient two-jet.
    """
    x = np.asarray(x,float)
    raw = _geometry_fields(x)
    q,v,m,s,sd = raw[:37],raw[37:74],raw[74:98],raw[98],raw[99]
    c,h,e = x[GAUGE],x[HIGGS],float(x[LOG_UNIT])
    n = len(rho)
    p,pr = static_field_maps(rho,enrich_temporal=True)
    a,ar = (p@c).reshape(n,1,5,4),(pr@c).reshape(n,1,5,4)
    fields = dict(gauge=a,gauge_tau=np.zeros_like(a),gauge_rho=ar,
                  gauge_angular=np.zeros((n,1,3,5,4)))
    cap = moving_cap_action_jet(12,q,v,m,points=cap_points,source_value=s,source_rate=sd)
    geometry = geometric_connection_coefficient_jets(12,q,v,m,rho,
        source_value=s,source_rate=sd,clock='coordinate_time')
    mw = background_subtracted_maxwell_action_jet(geometry,radial_weights,np.ones(1),**fields)
    tests = p.transpose(0,2,1).reshape(n,84,1,5,4)
    tests_r = pr.transpose(0,2,1).reshape(n,84,1,5,4)
    weak = full_maxwell_weak_geometric_jets(geometry,radial_weights,np.ones(1),**fields,
        tests=tests,tests_tau=np.zeros_like(tests),tests_rho=tests_r,
        tests_angular=np.zeros((n,84,1,3,5,4)))['weak']
    names = ('electric','radial','angular','electric_radial','shift')
    densities = np.array([[r[k].value for k in names] for r in geometry['rows']])
    total,total_r = a[:,0].copy(),ar[:,0].copy()
    total[:,2:] += np.array([r['connection_lambda'].value-1 for r in geometry['rows']])[:,None,None]*M
    total_r[:,2:] += np.array([r['lambda_rho'].value for r in geometry['rows']])[:,None,None]*M
    local = analytic_constant_maxwell_batch(total,np.zeros_like(total),total_r,densities)
    lift = np.zeros((n,60,84));lift[:,:20]=p;lift[:,40:]=pr
    kaa = MAXWELL_TO_CAP*np.einsum('rai,raj,r->ij',lift,local['hessian']@lift,radial_weights,optimize=True).real
    w = intrinsic_m4_weight_jet(12,q,v,m,source_value=s,source_rate=sd)
    wall_map,_ = static_field_maps(np.array([WALL]),enrich_temporal=True)
    matching = retained_scalar_matching_coefficients()
    scalar = material_intrinsic_higgs_gauge_action_jet(w,
        scalar_coefficients=h,scalar_value_map=np.eye(4)[None],
        scalar_derivative_map=np.zeros((1,4,4,4)),gauge_coefficients=c,
        gauge_trace_map=wall_map.reshape(1,5,4,84),angular_quadrature=np.ones(1),
        lambda_H=matching['lambda_H'],nu_squared_GeV_squared=matching['nu_squared_GeV_squared'],
        log_energy_unit_GeV=e)['action']/ORBIT_VOLUME_SQUARED
    sp = scalar_joint_lift()
    gradient,hessian = sp.T@scalar.gradient,sp.T@scalar.hessian@sp
    gi = GEOMETRY_IDS
    gradient[:62] += cap['total'].gradient[gi]+MAXWELL_TO_CAP*mw['gradient'][gi]
    hessian[:62,:62] += cap['total'].hessian[np.ix_(gi,gi)]+MAXWELL_TO_CAP*mw['hessian'][np.ix_(gi,gi)]
    gradient[GAUGE] += MAXWELL_TO_CAP*weak['values']
    hessian[GAUGE,GAUGE] += kaa
    cross = MAXWELL_TO_CAP*weak['geometric_jacobian'][:,gi]
    hessian[GAUGE,GEOMETRY] += cross
    hessian[GEOMETRY,GAUGE] += cross.T
    cache_defect = None
    reused = saved is not None and seed is not None and np.array_equal(x,seed)
    if reused:
        oldg,oldk = saved['final_weak_field_rows84'],saved['final_weak_field_Hessian84']
        cache_defect = dict(gradient_max=float(np.max(abs(gradient[GAUGE]-oldg))),
            hessian_max=float(np.max(abs(hessian[GAUGE,GAUGE]-oldk))))
        if max(cache_defect.values()) > 5e-11:
            raise ValueError('saved classical block input identity failed')
        gradient[GAUGE],hessian[GAUGE,GAUGE] = oldg,oldk
    original_gradient,original_hessian = gradient.copy(),hessian.copy()
    ct = -cap['retained_local_Casimir']
    independent = reference_subtraction(raw)
    check = max(abs(ct.value-independent.value),np.max(abs(ct.gradient-independent.gradient)),
                np.max(abs(ct.hessian-independent.hessian)))
    if check > 2e-11:
        raise ArithmeticError('exact original Casimir subtraction mismatch')
    delta_g,delta_k = np.zeros(151),np.zeros((151,151))
    delta_g[:62],delta_k[:62,:62] = ct.gradient[gi],ct.hessian[np.ix_(gi,gi)]
    gradient += delta_g;hessian += delta_k
    original_geometry_full = (cap['total'].gradient+MAXWELL_TO_CAP*mw['gradient']
                              +scalar.gradient[:100])
    known_geometry_full = original_geometry_full+ct.gradient
    area_g,area_k = np.zeros(151),np.zeros((151,151))
    area_g[:62] = cap['surface_per_gamma'].gradient[gi]
    area_k[:62,:62] = cap['surface_per_gamma'].hessian[np.ix_(gi,gi)]
    required_cf = matching['G_F_GeV_minus2']*np.exp(2*e)
    unit_known_gradient = np.zeros(151);unit_known_gradient[150]=2*required_cf
    return dict(original_gradient=original_gradient,original_hessian=original_hessian,
        known_gradient=gradient,known_hessian=hessian,
        subtraction_gradient=delta_g,subtraction_hessian=delta_k,
        subtraction_value=float(ct.value),subtraction_original_twojet_defect=float(check),
        original_action_value=float(cap['total'].value+MAXWELL_TO_CAP*mw['value']+scalar.value),
        known_action_value=float(cap['total'].value+MAXWELL_TO_CAP*mw['value']+scalar.value+ct.value),
        area_gradient_per_gamma=area_g,area_hessian_per_gamma=area_k,
        classical_scalar_log_unit_cotangent=float(gradient[150]),
        required_cF=float(required_cf),unit_known_gradient=unit_known_gradient,
        R4=float(w['R4'].value),induced_lapse=float(w['induced_lapse'].value),
        ambient_lapse=float(w['fields']['N'].value),unit_initializer_GeV=float(np.exp(e)),
        raw_geometry100=raw,cache_reused=reused,cache_defect=cache_defect,
        original_geometry_full_covector100=original_geometry_full,
        known_geometry_full_covector100=known_geometry_full,
        total_connection=total,total_connection_radial=total_r,densities=densities,value_map=p,
        scalar_unit_polynomial_evaluated=float(matching['nu_squared_GeV_squared']*np.exp(-2*e)))


def coupled_subtraction_step(seed, before, saved, *, evaluate, max_scaled_step=.02,
                             rank_relative_tolerance=1e-10):
    """Consume actual subtraction in a coupled off-shell load homotopy.

    Executed equation: g_original(z)-g_original(seed)+d ct(z)=0 on150
    original rows, with e allowed as an underdetermined column. No Euler-e
    equation, chosen cF or unknown native load closes it. The first known
    Schur uses the saved classical52 factor only at its identical inputs.
    Complete physical load/Jacobian still contain ell and D ell.
    """
    a = 62+saved['active_interior_rows52'].astype(int)
    b = np.array(sorted(set(range(151))-set(a)))
    rows = b[b!=LOG_UNIT]
    k = before['known_hessian']
    inv = -saved['reference_native_load_partial_response52']
    if np.max(abs(k[np.ix_(a,a)]@inv-np.eye(52))) > 5e-11:
        raise ValueError('saved52 classical inverse no longer matches known block')
    schur = k[np.ix_(rows,b)]-k[np.ix_(rows,a)]@inv@k[np.ix_(a,b)]
    load = before['subtraction_gradient'][rows]
    # Explicit numerical coordinate/row metrics; no physical gauge quotient
    # is inferred from a numerical rank or a minimum-norm nullspace choice.
    variable_scale = np.maximum(1.,abs(seed[b]))
    row_scale = 1/np.maximum(1.,np.linalg.norm(schur*variable_scale[None],axis=1))
    scaled = row_scale[:,None]*schur*variable_scale[None]
    u,s,vt = np.linalg.svd(scaled,full_matrices=True)
    rank = int(np.sum(s>rank_relative_tolerance*s[0]))
    y = -vt[:rank].T@((u[:,:rank].T@(row_scale*load))/s[:rank])
    delta = np.zeros(151);delta[b]=variable_scale*y
    delta[a] = -inv@(k[np.ix_(a,b)]@delta[b])
    chart_scale = np.maximum(1.,abs(seed))
    fraction = min(1.,max_scaled_step/max(np.max(abs(delta/chart_scale)),1e-300))
    records=[]; accepted=False;after=before;candidate=seed.copy()
    old = before['original_gradient'][EULER_ROWS]
    row_metric = np.maximum(1.,abs(old))
    for half in range(12):
        damping=fraction*2.**(-half)
        try:
            proposed=seed+damping*delta
            trial=evaluate(proposed)
            # Full subtraction is present in every trial; damping changes
            # the iterate, not the source or the physical load definition.
            homotopy=(trial['original_gradient'][EULER_ROWS]-old
                      +trial['subtraction_gradient'][EULER_ROWS])
            zero_step=before['subtraction_gradient'][EULER_ROWS]
            norm=float(np.linalg.norm(homotopy/row_metric))
            good=np.isfinite(norm) and norm < np.linalg.norm(zero_step/row_metric)
            records.append(dict(damping=damping,homotopy_norm=norm,
                frozen_field_norm=float(np.linalg.norm(zero_step/row_metric)),accepted=bool(good)))
        except (ValueError,ArithmeticError,FloatingPointError,OverflowError) as error:
            records.append(dict(damping=damping,accepted=False,error=type(error).__name__))
            good=False
        if good:
            candidate,after,accepted=proposed,trial,True
            break
    linear = k[np.ix_(EULER_ROWS,np.arange(151))]@delta+before['subtraction_gradient'][EULER_ROWS]
    return dict(candidate=candidate,after=after,accepted=accepted,full_linear_step=delta,
        actual_step=candidate-seed,active52=a,reduced_rows98=rows,reduced_columns99=b,
        Schur98x99=schur,reduced_load98=load,variable_scale99=variable_scale,row_scale98=row_scale,
        singular_values98=s,numerical_rank=rank,rank_relative_tolerance=rank_relative_tolerance,
        numerical_right_nullspace=vt[rank:].T,numerical_left_nullspace=u[:,rank:],
        scaled_left_null_load=u[:,rank:].T@(row_scale*load),
        linearized_unscaled_original_rows150=linear,trial_history=records,
        physical_correction_admitted=False)


def coupled_known_subtotal_trial(seed, before, saved, *, evaluate,
                                 max_scaled_step=.02,rank_relative_tolerance=1e-10):
    """One provisional Newton trial of the actual known150 original rows.

    This initializer reduces R_known, not a residual shifted by a fitted
    force. Full R=R_known+gamma*R_area+ell and its physical-unit row remain
    unevaluated. Trial acceptance is only numerical known-subtotal merit.
    """
    a = 62+saved['active_interior_rows52'].astype(int)
    b = np.array(sorted(set(range(151))-set(a)))
    rows = b[b!=LOG_UNIT]
    k,g = before['known_hessian'],before['known_gradient']
    inv = -saved['reference_native_load_partial_response52']
    if np.max(abs(k[np.ix_(a,a)]@inv-np.eye(52))) > 5e-11:
        raise ValueError('saved52 inverse does not match unchanged classical block')
    schur = k[np.ix_(rows,b)]-k[np.ix_(rows,a)]@inv@k[np.ix_(a,b)]
    load = g[rows]-k[np.ix_(rows,a)]@inv@g[a]
    variable_scale = np.maximum(1.,abs(seed[b]))
    row_scale = 1/np.maximum(1.,np.linalg.norm(schur*variable_scale[None],axis=1))
    scaled = row_scale[:,None]*schur*variable_scale[None]
    u,s,vt = np.linalg.svd(scaled,full_matrices=True)
    rank = int(np.sum(s>rank_relative_tolerance*s[0]))
    y = -vt[:rank].T@((u[:,:rank].T@(row_scale*load))/s[:rank])
    delta = np.zeros(151);delta[b] = variable_scale*y
    delta[a] = -inv@(g[a]+k[np.ix_(a,b)]@delta[b])
    fraction = min(1.,max_scaled_step/max(np.max(abs(delta/np.maximum(1.,abs(seed)))),1e-300))
    merit_scale = 1/np.maximum(1.,abs(g[EULER_ROWS]))
    merit = float(np.linalg.norm(merit_scale*g[EULER_ROWS]))
    records=[];accepted=False;after=before;candidate=seed.copy()
    for half in range(12):
        damping=fraction*2.**(-half)
        try:
            proposed=seed+damping*delta
            trial=evaluate(proposed)
            norm=float(np.linalg.norm(merit_scale*trial['known_gradient'][EULER_ROWS]))
            good=np.isfinite(norm) and norm<merit
            records.append(dict(damping=damping,known_merit_before=merit,
                known_merit_after=norm,accepted=bool(good)))
        except (ValueError,ArithmeticError,FloatingPointError,OverflowError) as error:
            records.append(dict(damping=damping,accepted=False,error=type(error).__name__))
            good=False
        if good:
            candidate,after,accepted=proposed,trial,True
            break
    linear = k[np.ix_(EULER_ROWS,np.arange(151))]@delta+g[EULER_ROWS]
    return dict(candidate=candidate,after=after,accepted=accepted,full_linear_step=delta,
        actual_step=candidate-seed,active52=a,reduced_rows98=rows,reduced_columns99=b,
        Schur98x99=schur,reduced_load98=load,variable_scale99=variable_scale,row_scale98=row_scale,
        merit_scale150=merit_scale,singular_values98=s,numerical_rank=rank,
        rank_relative_tolerance=rank_relative_tolerance,
        numerical_right_nullspace=vt[rank:].T,numerical_left_nullspace=u[:,rank:],
        scaled_left_null_load=u[:,rank:].T@(row_scale*load),
        linearized_unscaled_original_rows150=linear,trial_history=records,
        physical_correction_admitted=False)
