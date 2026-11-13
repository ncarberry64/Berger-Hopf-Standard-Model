"""Temporal Galerkin enrichment of the same retained partial coupled action.

The new functions b(t)P_k(2t/L+1) enrich geometry, multipliers, normal,
all five independent gauge fields and the four real Higgs components on
one vector.  They preserve both endpoint values and rates.  In particular
they cannot repair a nonzero constraint density at a fixed affine past
face; that defect is evaluated and exported, not called an E0 datum.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import legval,legder

from .muon_parent_gauge_geometry_correction import (
    ROOT,FIELD_ORDER,ORBIT_VOLUME_SQUARED,MAXWELL_TO_CAP,SOURCE_RECEIPTS,
    compact_temporal_basis,correction_representation,_geometry_map,
    retained_state,moving_cap_action_jet,intrinsic_m4_weight_jet,
    geometric_connection_coefficient_jets,background_subtracted_maxwell_action_jet,
    full_maxwell_weak_geometric_jets,full_maxwell_gauge_hessian_matrix,
    regular_radial_basis,WALL,_deterministic_npz,
)
from .muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet


def compact_legendre_time_jet(time,length,order):
    """Analytic value/rate of bP_k; representation order is not physics."""
    if type(order) is not int or order<1:
        raise ValueError('a positive finite temporal representation order is required')
    t=np.asarray(time,float);b,bt=compact_temporal_basis(t,length);x=2*t/length+1
    v=np.empty(t.shape+(order,));d=np.empty_like(v)
    for k in range(order):
        c=np.zeros(k+1);c[-1]=1.;p=legval(x,c)
        v[...,k]=b*p
        d[...,k]=bt*p+b*legval(x,legder(c))*2/length
    return v,d


def temporal_representation(*,temporal_order=2,**base_parameters):
    base=correction_representation(**base_parameters)
    basis,rate=compact_legendre_time_jet(base['time'],base['length'],temporal_order)
    gc=base['gauge_count'];sc=4*temporal_order+4*int(base['include_scalar_mean'])
    return dict(base=base,temporal_order=temporal_order,time_basis=basis,time_rate=rate,
        geometry_count=62*temporal_order,gauge_count=gc*temporal_order,
        scalar_count=sc,scalar_start=(62+gc)*temporal_order,
        count=(66+gc)*temporal_order+4*int(base['include_scalar_mean']))


def include_recorded_coefficients(coefficients,representation):
    """Exact inclusion of the original single compact time trial."""
    base=representation['base'];c=np.asarray(coefficients,float)
    if c.shape!=(base['count'],):
        raise ValueError('recorded finite coefficients disagree with the base representation')
    result=np.zeros(representation['count']);result[:62]=c[:62]
    g=representation['geometry_count'];gc=base['gauge_count']
    result[g:g+gc]=c[62:62+gc]
    s=representation['scalar_start'];result[s:s+4]=c[base['scalar_start']:base['scalar_start']+4]
    if base['include_scalar_mean']:result[-4:]=c[-4:]
    return result


def temporal_iterate_at_time(time,coefficients,representation,reference,*,rho=None):
    """All derivatives and field applications come from the same vector."""
    c=np.asarray(coefficients,float);r=representation;base=r['base'];nt=r['temporal_order']
    if c.shape!=(r['count'],) or not np.isfinite(c).all():
        raise ValueError('one finite common coefficient vector is required')
    b,bt=compact_legendre_time_jet(np.array([time]),base['length'],nt);b=b[0];bt=bt[0]
    geom=c[:r['geometry_count']].reshape(nt,62);q,v,m=reference
    qq=q+time*v+b@geom[:,:37];vv=v+bt@geom[:,:37]
    mm=m+b@geom[:,37:61];s=float(b@geom[:,61]);sr=float(bt@geom[:,61])
    p=np.hstack([_geometry_map(x,y) for x,y in zip(b,bt)])
    grid=base['rho'] if rho is None else np.asarray(rho,float)
    h,hr=regular_radial_basis(grid,base['radial_order'])
    gb=np.zeros((len(grid),base['gauge_count'],1,5,4));gr=np.zeros_like(gb)
    for j,label in enumerate(base['gauge_labels']):
        f=FIELD_ORDER.index(label['field']);i=label['internal'];rad=label['radial']
        gb[:,j,0,f,i]=h[:,rad];gr[:,j,0,f,i]=hr[:,rad]
    gc=c[r['geometry_count']:r['scalar_start']].reshape(nt,base['gauge_count'])
    fields=dict(gauge=np.einsum('rjpic,j->rpic',gb,b@gc),
        gauge_tau=np.einsum('rjpic,j->rpic',gb,bt@gc),
        gauge_rho=np.einsum('rjpic,j->rpic',gr,b@gc),
        gauge_angular=np.zeros((len(grid),1,3,5,4)))
    tests=dict(tests=np.concatenate([x*gb for x in b],axis=1),
        tests_tau=np.concatenate([x*gb for x in bt],axis=1),
        tests_rho=np.concatenate([x*gr for x in b],axis=1),
        tests_angular=np.zeros((len(grid),r['gauge_count'],1,3,5,4)))
    sc=c[r['scalar_start']:];V=np.zeros((1,4,r['scalar_count']));D=np.zeros((1,4,4,r['scalar_count']))
    for k,(x,y) in enumerate(zip(b,bt)):
        V[0,:,4*k:4*k+4]=x*np.eye(4);D[0,0,:,4*k:4*k+4]=y*np.eye(4)
    if base['include_scalar_mean']:V[0,:,-4:]=np.eye(4)
    return dict(q=qq,qdot=vv,m=mm,normal=s,normal_rate=sr,fields=fields,tests=tests,
        geometry_map=p,scalar_value_map=V,scalar_derivative_map=D,
        H_real=V[0]@sc,H_coordinate_time_derivative=D[0,0]@sc,
        scope='same-vector local temporal trial; not a physical C1 history or E0 trace')


def temporal_coupled_application(coefficients,representation,reference,*,nu_squared_action=None,surface_gamma=None):
    """Differentiate the retained partial action on the enriched vector."""
    r=representation;base=r['base'];n=r['count'];ng=r['geometry_count'];gs=slice(ng,r['scalar_start'])
    sc=r['scalar_count'];ss=r['scalar_start'];c=np.asarray(coefficients,float)
    sectors={name:dict(value=0.,residual=np.zeros(n),hessian=np.zeros((n,n))) for name in
        ('cap','independent_Maxwell','intrinsic_H_kinetic_quartic','intrinsic_H_potential_per_nu2',
         'surface_per_gamma','H_zero_potential_per_lambda_nu4')}
    moments=[]
    for time,wt in zip(base['time'],base['time_quadrature']):
        data=temporal_iterate_at_time(time,c,r,reference)
        q,v,m,s,sr=(data[k] for k in ('q','qdot','m','normal','normal_rate'))
        P=data['geometry_map'];fields=data['fields'];tests=data['tests']
        cap=moving_cap_action_jet(12,q,v,m,points=base['cap_points'],source_value=s,source_rate=sr)
        geometry=geometric_connection_coefficient_jets(12,q,v,m,base['rho'],source_value=s,source_rate=sr)
        delta=background_subtracted_maxwell_action_jet(geometry,base['radial_quadrature'],np.ones(1),**fields)
        weak=full_maxwell_weak_geometric_jets(geometry,base['radial_quadrature'],np.ones(1),**fields,**tests)
        hh=full_maxwell_gauge_hessian_matrix(geometry,base['radial_quadrature'],np.ones(1),**fields,**tests)
        for name,jet in (('cap',cap['total']),('surface_per_gamma',cap['surface_per_gamma'])):
            target=sectors[name];target['value']+=wt*jet.value
            target['residual'][:ng]+=wt*(P.T@jet.gradient)
            target['hessian'][:ng,:ng]+=wt*(P.T@jet.hessian@P)
        target=sectors['independent_Maxwell'];scale=wt*MAXWELL_TO_CAP
        target['value']+=scale*delta['value'];target['residual'][:ng]+=scale*(P.T@delta['gradient'])
        target['residual'][gs]+=scale*weak['weak']['values']
        target['hessian'][:ng,:ng]+=scale*(P.T@delta['hessian']@P)
        mixed=scale*(weak['weak']['geometric_jacobian']@P)
        target['hessian'][gs,:ng]+=mixed;target['hessian'][:ng,gs]+=mixed.T
        target['hessian'][gs,gs]+=scale*hh['matrix']
        metric=intrinsic_m4_weight_jet(12,q,v,m,source_value=s,source_rate=sr)
        b,_=compact_legendre_time_jet(np.array([time]),base['length'],r['temporal_order'])
        wall_h,_=regular_radial_basis(np.array([WALL]),base['radial_order'])
        trace=np.zeros((1,5,4,r['gauge_count']))
        for k in range(r['temporal_order']):
            for j,label in enumerate(base['gauge_labels']):
                trace[0,FIELD_ORDER.index(label['field']),label['internal'],k*base['gauge_count']+j]=b[0,k]*wall_h[0,label['radial']]
        lam=base['scalar_matching']['lambda_H']
        scalar=material_intrinsic_higgs_gauge_action_jet(metric,scalar_coefficients=c[ss:],
            scalar_value_map=data['scalar_value_map'],scalar_derivative_map=data['scalar_derivative_map'],
            gauge_coefficients=c[gs],gauge_trace_map=trace,angular_quadrature=np.ones(1),lambda_H=lam,nu_squared_action=0.)
        lift=np.zeros((100+sc+r['gauge_count'],n));lift[:100,:ng]=P
        lift[100:100+sc,ss:]=np.eye(sc);lift[100+sc:,gs]=np.eye(r['gauge_count'])
        for name,jet,factor in zip(('intrinsic_H_kinetic_quartic','intrinsic_H_potential_per_nu2','H_zero_potential_per_lambda_nu4'),
                scalar['nu_squared_polynomial_coefficients'],(1.,1.,1/lam)):
            target=sectors[name];scale=wt*factor/ORBIT_VOLUME_SQUARED
            target['value']+=scale*jet.value;target['residual']+=scale*(lift.T@jet.gradient)
            target['hessian']+=scale*(lift.T@jet.hessian@lift)
        scalar_jets=scalar['nu_squared_polynomial_coefficients']
        scalar_assigned=scalar_jets[0]
        if nu_squared_action is not None:
            scalar_assigned=scalar_assigned+nu_squared_action*scalar_jets[1]+nu_squared_action**2*scalar_jets[2]
        cap_density=cap['total'].gradient[74:98]
        maxwell_density=MAXWELL_TO_CAP*delta['gradient'][74:98]
        higgs_density=scalar_assigned.gradient[74:98]/ORBIT_VOLUME_SQUARED
        surface_density=cap['surface_per_gamma'].gradient[74:98]
        total_density=cap_density+maxwell_density+higgs_density
        if surface_gamma is not None:total_density=total_density+surface_gamma*surface_density
        moments.append(dict(time=float(time),multiplier_constraint_density=total_density,
            cap_multiplier_constraint_density=cap_density,
            independent_Maxwell_multiplier_constraint_density=maxwell_density,
            Higgs_assigned_multiplier_constraint_density=higgs_density,
            surface_multiplier_constraint_density_per_gamma=surface_density,
            temporal_gauge_momentum_tests=MAXWELL_TO_CAP*weak['temporal_momentum_test']['values'],
            radial_gauge_momentum_tests=MAXWELL_TO_CAP*weak['radial_momentum_test']['values']))
    terms=[('cap',1.),('independent_Maxwell',1.),('intrinsic_H_kinetic_quartic',1.)]
    if nu_squared_action is not None:
        if not np.isfinite(nu_squared_action) or nu_squared_action<0:
            raise ValueError('finite nonnegative shared nu squared parameter required')
        terms.extend((('intrinsic_H_potential_per_nu2',nu_squared_action),
            ('H_zero_potential_per_lambda_nu4',lam*nu_squared_action**2)))
    if surface_gamma is not None:
        if not np.isfinite(surface_gamma):raise ValueError('finite surface coefficient parameter required')
        terms.append(('surface_per_gamma',surface_gamma))
    value=sum(f*sectors[name]['value'] for name,f in terms)
    residual=sum((f*sectors[name]['residual'] for name,f in terms),np.zeros(n))
    hessian=sum((f*sectors[name]['hessian'] for name,f in terms),np.zeros((n,n)))
    density=np.array([x['multiplier_constraint_density'] for x in moments])
    l2=float(np.sqrt(np.einsum('t,ti,ti->',base['time_quadrature'],density,density)/base['length']))
    return dict(value=float(value),residual=residual,hessian=hessian,sectors=sectors,moments=moments,
        constraint_density_max=float(np.max(abs(density))),constraint_density_rms=l2,
        constraint_density=density,action_parameters=dict(nu_squared_action=nu_squared_action,surface_gamma=surface_gamma))


def temporal_newton_iterations(coefficients,representation,reference,*,max_iterations=8,rank_tolerance=1e-11,
                              relative_tolerance=1e-9,absolute_tolerance=1e-12,action_parameters=None):
    """Residual Newton with indefinite congruence solve and actual damping."""
    parameters={} if action_parameters is None else action_parameters
    current=np.asarray(coefficients,float).copy();initial=temporal_coupled_application(current,representation,reference,**parameters)
    fixed_scale=1/np.sqrt(np.maximum(np.max(abs(initial['hessian']),axis=1),1e-30))
    initial_norm=float(np.linalg.norm(fixed_scale*initial['residual']));target=max(absolute_tolerance,relative_tolerance*initial_norm)
    value=initial;history=[];steps=[];status='MAXIMUM_ITERATIONS'
    for iteration in range(max_iterations):
        norm=float(np.linalg.norm(fixed_scale*value['residual']))
        if norm<=target:status='FINITE_RESIDUAL_TOLERANCE';break
        h=(value['hessian']+value['hessian'].T)/2
        scale=1/np.sqrt(np.maximum(np.max(abs(h),axis=1),1e-30))
        eigen,u=np.linalg.eigh(scale[:,None]*h*scale[None,:]);active=abs(eigen)>rank_tolerance*max(abs(eigen))
        delta=-scale*(u[:,active]@((u[:,active].T@(scale*value['residual']))/eigen[active]))
        linear=h@delta+value['residual'];trials=[];accepted=False
        for half in range(15):
            damping=2.**(-half)
            try:
                candidate=temporal_coupled_application(current+damping*delta,representation,reference,**parameters)
                newnorm=float(np.linalg.norm(fixed_scale*candidate['residual']))
                good=np.isfinite(newnorm) and newnorm<norm
            except (ValueError,FloatingPointError,OverflowError):
                candidate=None;newnorm=None;good=False
            trials.append(dict(step=damping,scaled_residual=newnorm,admissible=bool(good)))
            if good:accepted=True;break
        history.append(dict(iteration=iteration,rank=int(sum(active)),nullity=int(sum(~active)),
            initial_scaled_residual=norm,linearized_residual_norm=float(np.linalg.norm(linear)),
            constraint_density_max=value['constraint_density_max'],constraint_density_rms=value['constraint_density_rms'],
            accepted=accepted,damping_history=trials))
        steps.append(dict(correction=delta,hessian=h,initial_residual=value['residual'],linearized_residual=linear))
        if not accepted:status='DAMPING_STALL';break
        current+=damping*delta;value=candidate
    final_norm=float(np.linalg.norm(fixed_scale*value['residual']))
    if final_norm<=target:status='FINITE_RESIDUAL_TOLERANCE'
    return dict(coefficients=current,initial=initial,final=value,history=history,steps=steps,status=status,
        fixed_scale=fixed_scale,initial_scaled_residual=initial_norm,final_scaled_residual=final_norm,target=target)


def materialize_temporal_application(initial_application,output,*,temporal_order=2,time_points=10,max_iterations=8,
                                    initial_coefficients_key='updated_coefficients',repository=ROOT):
    root=Path(repository);source=Path(initial_application);out=Path(output)
    if not source.is_absolute():source=root/source
    if out.exists():raise FileExistsError('preserve earlier applications; choose a new output directory')
    metadata=json.loads((source/'result.json').read_text(encoding='utf8'))
    if sha256((source/'application.npz').read_bytes()).hexdigest()!=metadata['numerical_sha256']:
        raise ValueError('initial coefficient bytes disagree with their action receipt')
    base_args=dict(length=metadata['numerical_local_interval_length'],time_points=time_points,
        radial_points=metadata['radial_quadrature_order'],cap_points=metadata['cap_quadrature_order'],
        radial_order=metadata['gauge_unknowns']//20-int(metadata['include_wall_lift']),
        include_wall_lift=metadata['include_wall_lift'],include_scalar_mean=metadata['include_scalar_mean'],repository=root)
    rep=temporal_representation(temporal_order=temporal_order,**base_args)
    if initial_coefficients_key not in ('initial_coefficients','updated_coefficients'):
        raise ValueError('an explicitly recorded initial or updated common coefficient vector is required')
    with np.load(source/'application.npz',allow_pickle=False) as data:initial=include_recorded_coefficients(data[initial_coefficients_key],rep)
    refs=list(SOURCE_RECEIPTS)+['src/bhsm/interface/muon_parent_temporal_enrichment.py',
        'src/bhsm/interface/muon_material_higgs_gauge_action.py']
    hashes={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}
    source_hashes={name:sha256((source/name).read_bytes()).hexdigest() for name in ('result.json','application.npz')}
    reference=retained_state(root)
    result=temporal_newton_iterations(initial,rep,reference,max_iterations=max_iterations,action_parameters=metadata['action_parameters'])
    endpoint_density=[]
    for time in (-rep['base']['length'],0.):
        d=temporal_iterate_at_time(time,result['coefficients'],rep,reference)
        cap=moving_cap_action_jet(12,d['q'],d['qdot'],d['m'],points=rep['base']['cap_points'],source_value=d['normal'],source_rate=d['normal_rate'])
        endpoint_density.append(cap['total'].gradient[74:98])
    if hashes!={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}:
        raise RuntimeError('an action owner changed during the application')
    arrays=dict(initial_coefficients=initial,updated_coefficients=result['coefficients'],
        initial_residual=result['initial']['residual'],initial_hessian=result['initial']['hessian'],
        updated_residual=result['final']['residual'],updated_hessian=result['final']['hessian'],
        time=rep['base']['time'],time_basis=rep['time_basis'],time_basis_derivative=rep['time_rate'],
        initial_constraint_density=result['initial']['constraint_density'],updated_constraint_density=result['final']['constraint_density'],
        temporal_face_cap_constraint_density=np.array(endpoint_density),fixed_congruence_scale=result['fixed_scale'])
    for key in ('cap_multiplier_constraint_density','independent_Maxwell_multiplier_constraint_density',
                'Higgs_assigned_multiplier_constraint_density','surface_multiplier_constraint_density_per_gamma'):
        arrays['updated_'+key]=np.array([moment[key] for moment in result['final']['moments']])
    if result['steps']:
        arrays.update(iteration_corrections=np.array([x['correction'] for x in result['steps']]),
            iteration_initial_residuals=np.array([x['initial_residual'] for x in result['steps']]),
            iteration_hessians=np.array([x['hessian'] for x in result['steps']]),
            iteration_linearized_residuals=np.array([x['linearized_residual'] for x in result['steps']]))
    out.mkdir(parents=True);_deterministic_npz(out/'application.npz',arrays)
    receipt=dict(scope='EVALUATED_SAME_ACTION_TEMPORAL_ENRICHMENT_PARAMETER_TRIAL',
        temporal_order=temporal_order,temporal_quadrature_order=time_points,count=rep['count'],
        geometry_unknowns=rep['geometry_count'],gauge_unknowns=rep['gauge_count'],scalar_unknowns=rep['scalar_count'],
        include_wall_lift=rep['base']['include_wall_lift'],include_scalar_mean=rep['base']['include_scalar_mean'],
        radial_order=rep['base']['radial_order'],radial_quadrature_order=rep['base']['radial_points'],
        cap_quadrature_order=rep['base']['cap_points'],gauge_labels=rep['base']['gauge_labels'],
        iteration_status=result['status'],iteration_history=result['history'],
        initial_scaled_residual=result['initial_scaled_residual'],final_scaled_residual=result['final_scaled_residual'],finite_residual_target=result['target'],
        initial_constraint_density_max=result['initial']['constraint_density_max'],updated_constraint_density_max=result['final']['constraint_density_max'],
        initial_constraint_density_rms=result['initial']['constraint_density_rms'],updated_constraint_density_rms=result['final']['constraint_density_rms'],
        temporal_face_CAP_constraint_density_max=[float(np.max(abs(x))) for x in endpoint_density],
        endpoint_obstruction='bP_k and its rate vanish at both temporal faces, so the affine past-face constraint defect is unchanged by this compact enrichment',
        numerical_local_interval_length=rep['base']['length'],physical_branch_duration=False,
        action_parameters=metadata['action_parameters'],source_action_receipt_sha256=source_hashes['result.json'],
        source_coefficients_sha256=source_hashes['application.npz'],input_hashes=hashes,
        initial_coefficients_key=initial_coefficients_key,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        stationary_E1_claim=False,physical_E0_trace_selected=False,finite_residual_is_pointwise_action_solution=False,
        constraint_density_scope='TOTAL assigned cap+independentMaxwell+H0/nu polynomial; assignedgamma added; per-gamma load separately exported',
        gauge_trace_chart='MATERIAL_REFERENCE_ONE_FORM',extra_gauge_advection_removed=True,
        physical_Pauli_contraction=False,physical_unit_assigned=False,Gauss_rows_eliminated=False,
        gamma_is_physical_independent_parameter=False,nu_squared_values_are_parameter_trials=True,
        error_scope='finite numerical Galerkin residual/density diagnostics; no continuum certificate or interacting/native completion')
    (out/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return receipt


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--initial-application',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--temporal-order',type=int,default=2)
    p.add_argument('--time-points',type=int,default=10);p.add_argument('--max-iterations',type=int,default=8)
    p.add_argument('--use-recorded-initial',action='store_true')
    a=p.parse_args();print(json.dumps(materialize_temporal_application(a.initial_application,a.output,
        temporal_order=a.temporal_order,time_points=a.time_points,max_iterations=a.max_iterations,
        initial_coefficients_key='initial_coefficients' if a.use_recorded_initial else 'updated_coefficients'),sort_keys=True))
