"""Actual assigned-sector E1 multiplier constraints and Newton initializer.

The minimum weighted correction is a numerical retraction onto the
represented 24 constraints.  It does not select a physical branch, solve
the event/reset/formation equations or make the symbolic area coefficient
zero.  The full same-action first and second derivatives are consumed;
the prescribed finite field trace is held in its computational chart.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import numpy as np

from .muon_parent_temporal_enrichment import temporal_representation,temporal_iterate_at_time
from .muon_parent_gauge_geometry_correction import (
    ROOT,STATE_SOURCE,SOURCE_RECEIPTS,retained_state,moving_cap_action_jet,
    intrinsic_m4_weight_jet,geometric_connection_coefficient_jets,
    background_subtracted_maxwell_action_jet,ORBIT_VOLUME_SQUARED,MAXWELL_TO_CAP,
    _deterministic_npz,WALL,
)
from .muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet


def pointwise_assigned_action(q,qdot,m,*,rho,radial_quadrature,fields,H_real,H_rate,
                             wall_gauge,lambda_H,nu_squared_action=None,surface_gamma=None,
                             normal=0.,normal_rate=0.,cap_points=48):
    """The literal local cap+independentMaxwell+materialH action two-jet."""
    cap=moving_cap_action_jet(12,q,qdot,m,points=cap_points,source_value=normal,source_rate=normal_rate)
    geometry=geometric_connection_coefficient_jets(12,q,qdot,m,rho,source_value=normal,source_rate=normal_rate)
    maxwell=background_subtracted_maxwell_action_jet(geometry,radial_quadrature,np.ones(1),**fields)
    weights=intrinsic_m4_weight_jet(12,q,qdot,m,source_value=normal,source_rate=normal_rate)
    scalar_map=np.zeros((1,4,8));scalar_map[0,:,:4]=np.eye(4)
    derivative_map=np.zeros((1,4,4,8));derivative_map[0,0,:,4:]=np.eye(4)
    gauge_map=np.eye(20).reshape(5,4,20)[None]
    scalar=material_intrinsic_higgs_gauge_action_jet(weights,
        scalar_coefficients=np.r_[H_real,H_rate],scalar_value_map=scalar_map,scalar_derivative_map=derivative_map,
        gauge_coefficients=np.asarray(wall_gauge,float).reshape(20),gauge_trace_map=gauge_map,
        angular_quadrature=np.ones(1),lambda_H=lambda_H,nu_squared_action=0.)
    h=scalar['nu_squared_polynomial_coefficients'][0]
    if nu_squared_action is not None:
        if not np.isfinite(nu_squared_action) or nu_squared_action<0:
            raise ValueError('an explicit nonnegative action-unit nu squared is required')
        h=h+nu_squared_action*scalar['nu_squared_polynomial_coefficients'][1]+nu_squared_action**2*scalar['nu_squared_polynomial_coefficients'][2]
    sectors=dict(cap=dict(value=cap['total'].value,gradient=cap['total'].gradient,hessian=cap['total'].hessian),
        independent_Maxwell=dict(value=MAXWELL_TO_CAP*maxwell['value'],gradient=MAXWELL_TO_CAP*maxwell['gradient'],hessian=MAXWELL_TO_CAP*maxwell['hessian']),
        Higgs_assigned=dict(value=h.value/ORBIT_VOLUME_SQUARED,gradient=h.gradient[:100]/ORBIT_VOLUME_SQUARED,hessian=h.hessian[:100,:100]/ORBIT_VOLUME_SQUARED))
    if surface_gamma is not None:
        if not np.isfinite(surface_gamma):raise ValueError('finite explicitly assigned area coefficient required')
        a=cap['surface_per_gamma'];sectors['surface_assigned']=dict(value=surface_gamma*a.value,
            gradient=surface_gamma*a.gradient,hessian=surface_gamma*a.hessian)
    value=sum(x['value'] for x in sectors.values());gradient=sum((x['gradient'] for x in sectors.values()),np.zeros(100))
    hessian=sum((x['hessian'] for x in sectors.values()),np.zeros((100,100)))
    return dict(value=float(value),gradient=gradient,hessian=hessian,
        multiplier_constraints=gradient[74:98],constraint_jacobian=hessian[74:98],sectors=sectors,
        surface_gradient_per_gamma=cap['surface_per_gamma'].gradient,
        surface_hessian_per_gamma=cap['surface_per_gamma'].hessian,
        cap_energy=float(qdot@cap['total'].gradient[37:74]+normal_rate*cap['total'].gradient[99]-cap['total'].value),
        scalar_real_canonical_dual=2*weights['wT'].value*scalar['DH_real'][0,0]/(2*np.pi**2),
        physical_Pauli_contraction=False,stationary_E1_claim=False)


def retract_multiplier_constraints(q,qdot,m,weights,*,action_arguments,max_iterations=10,
                                  absolute_tolerance=2e-9,relative_tolerance=1e-10,rank_tolerance=1e-12):
    """Iterate actual constraints with a weighted underdetermined Newton step."""
    q=np.asarray(q,float);x=np.r_[qdot,m].astype(float);w=np.asarray(weights,float)
    if x.shape!=(61,) or w.shape!=(61,) or not np.isfinite(w).all() or np.any(w<=0):
        raise ValueError('positive inherited action weights for37 velocity+24 multiplier coordinates required')
    evaluate=lambda z:pointwise_assigned_action(q,z[:37],z[37:],**action_arguments)
    initial=evaluate(x);current=initial;history=[];steps=[]
    first=float(np.linalg.norm(initial['multiplier_constraints']));target=max(absolute_tolerance,relative_tolerance*first)
    status='MAXIMUM_ITERATIONS'
    for index in range(max_iterations):
        residual=current['multiplier_constraints'];norm=float(np.linalg.norm(residual))
        if norm<=target:status='ASSIGNED_MULTIPLIER_CONSTRAINT_TOLERANCE';break
        j=current['constraint_jacobian'][:,37:98];jw=j/w[None,:]
        u,s,vt=np.linalg.svd(jw,full_matrices=False);active=s>rank_tolerance*max(s)
        step=-(vt[active].T@((u[:,active].T@residual)/s[active]))/w
        linear=j@step+residual;trials=[];accepted=False
        for half in range(18):
            damping=2.**(-half)
            try:
                candidate=evaluate(x+damping*step);newnorm=float(np.linalg.norm(candidate['multiplier_constraints']))
                good=np.isfinite(newnorm) and newnorm<norm
            except (ValueError,FloatingPointError,OverflowError):candidate=None;newnorm=None;good=False
            trials.append(dict(step=damping,constraint_norm=newnorm,admissible=bool(good)))
            if good:accepted=True;break
        history.append(dict(iteration=index,rank=int(sum(active)),constraint_norm=norm,
            weighted_step_norm=float(np.linalg.norm(w*step)),linearized_residual_norm=float(np.linalg.norm(linear)),
            accepted=accepted,damping_history=trials))
        steps.append(dict(step=step,jacobian=j,residual=residual,linearized_residual=linear,singular_values=s))
        if not accepted:status='DAMPING_STALL';break
        x+=damping*step;current=candidate
    if np.linalg.norm(current['multiplier_constraints'])<=target:status='ASSIGNED_MULTIPLIER_CONSTRAINT_TOLERANCE'
    return dict(q=q,qdot=x[:37],m=x[37:],initial=initial,final=current,history=history,steps=steps,
        target=target,status=status,weighted_total_update_norm=float(np.linalg.norm(w*(x-np.r_[qdot,m]))))


def materialize_constraint_retraction(initial_application,output,*,repository=ROOT):
    root=Path(repository);source=Path(initial_application);out=Path(output)
    if not source.is_absolute():source=root/source
    if out.exists():raise FileExistsError('preserve earlier evidence; choose a new output directory')
    raw=(source/'result.json').read_bytes();receipt=json.loads(raw)
    if receipt['temporal_order']!=1:raise ValueError('this endpoint binder presently consumes the frozen single-time-mode representation')
    if sha256((source/'application.npz').read_bytes()).hexdigest()!=receipt['numerical_sha256']:
        raise ValueError('source coefficient bytes do not match receipt')
    rep=temporal_representation(temporal_order=1,length=receipt['numerical_local_interval_length'],
        time_points=receipt['temporal_quadrature_order'],radial_points=receipt['radial_quadrature_order'],
        radial_order=receipt['radial_order'],cap_points=receipt['cap_quadrature_order'],
        include_wall_lift=receipt['include_wall_lift'],include_scalar_mean=receipt['include_scalar_mean'])
    with np.load(source/'application.npz',allow_pickle=False) as f:c=f['updated_coefficients']
    reference=retained_state(root);data=temporal_iterate_at_time(0.,c,rep,reference)
    wall=temporal_iterate_at_time(0.,c,rep,reference,rho=np.array([WALL]))
    with np.load(root/STATE_SOURCE,allow_pickle=False) as f:weights=f['state_weights'][37:98]
    refs=list(SOURCE_RECEIPTS)+['src/bhsm/interface/muon_parent_temporal_enrichment.py',
        'src/bhsm/interface/muon_material_higgs_gauge_action.py','src/bhsm/interface/muon_birth_coupled_constraint_retraction.py']
    hashes={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}
    arguments=dict(rho=rep['base']['rho'],radial_quadrature=rep['base']['radial_quadrature'],fields=data['fields'],
        H_real=data['H_real'],H_rate=data['H_coordinate_time_derivative'],wall_gauge=wall['fields']['gauge'][0,0],
        lambda_H=rep['base']['scalar_matching']['lambda_H'],normal=data['normal'],normal_rate=data['normal_rate'],
        cap_points=rep['base']['cap_points'],**receipt['action_parameters'])
    result=retract_multiplier_constraints(data['q'],data['qdot'],data['m'],weights,action_arguments=arguments)
    if hashes!={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}:
        raise RuntimeError('an action owner changed during the endpoint application')
    arrays=dict(initial_q=data['q'],initial_qdot=data['qdot'],initial_m=data['m'],
        updated_q=result['q'],updated_qdot=result['qdot'],updated_m=result['m'],state_action_weights=weights,
        H_real=data['H_real'],H_rate=data['H_coordinate_time_derivative'],wall_gauge=wall['fields']['gauge'][0,0],
        initial_constraints=result['initial']['multiplier_constraints'],updated_constraints=result['final']['multiplier_constraints'],
        initial_action_gradient=result['initial']['gradient'],updated_action_gradient=result['final']['gradient'],
        initial_action_hessian=result['initial']['hessian'],updated_action_hessian=result['final']['hessian'],
        updated_surface_gradient_per_gamma=result['final']['surface_gradient_per_gamma'])
    if result['steps']:
        arrays.update(iteration_steps=np.array([x['step'] for x in result['steps']]),iteration_jacobians=np.array([x['jacobian'] for x in result['steps']]),
            iteration_residuals=np.array([x['residual'] for x in result['steps']]),iteration_linearized_residuals=np.array([x['linearized_residual'] for x in result['steps']]))
    out.mkdir(parents=True);_deterministic_npz(out/'application.npz',arrays)
    metadata=dict(scope='EVALUATED_ASSIGNED_SECTOR_E1_CONSTRAINT_NEWTON_INITIALIZER',status=result['status'],
        iteration_history=result['history'],target=result['target'],initial_constraint_norm=float(np.linalg.norm(arrays['initial_constraints'])),
        updated_constraint_norm=float(np.linalg.norm(arrays['updated_constraints'])),updated_constraint_max=float(np.max(abs(arrays['updated_constraints']))),
        weighted_total_update_norm=result['weighted_total_update_norm'],action_parameters=receipt['action_parameters'],
        scalar_field_role='same recorded finite coefficient trace; numerical parametertrial, not selected physical H',
        constraint_scope='24 total assigned multiplier rows; energy/reset/event/canonicalbirth rows not yet included',
        area_role='owned gamma=alpha_FSC*ell_current^(-m) remains shared unknown; per-gamma density exported, not assignedzero/fitted',
        correction_role='weighted underdetermined Newton initializer, not physical branch selection',
        frozen_q_trace=True,velocity_multiplier_traces_changed=True,canonical_reset_preserved=False,
        baseline_Maxwell_added_again=False,gauge_trace_chart='MATERIAL_REFERENCE_ONE_FORM',
        oldgeometric_center_is_full_stationary_state=False,full_event_stationarity=False,
        physical_unit_assigned=False,physical_Pauli_contraction=False,
        consumed_receipt_sha256=sha256(raw).hexdigest(),consumed_coefficients_sha256=receipt['numerical_sha256'],input_hashes=hashes,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        error_scope='floating-point actual Newton constraint residual; no rigorous/continuum certificate or completed interacting event solve')
    (out/'result.json').write_text(json.dumps(metadata,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return metadata


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--initial-application',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize_constraint_retraction(a.initial_application,a.output),sort_keys=True))
