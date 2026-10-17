"""Same-action temporal gauge/Higgs traces, cotangents and constraints.

The computational common bundle/frame is the already-proved homogeneous
graph.  Its spatial trace is inherited, not a new physical identity map.
Geometry q is fixed to the current same-event initializer.  Both v/m,
all At/Ar/Ai values, dynamic gauge rates and Higgs values/rates vary in one
vector.  The two radial wall conormals are outputs, never temporal jump
conditions.  Formation, common scale and the complete geometric reset
lift remain separate reached equations.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_birth_coupled_primal_midpoint import endpoint_raw_from_assigned_application
from .muon_birth_phase_continuation import _compressed_npz
from .muon_birth_two_arm_assigned_action import same_action_attachment_momentum
from .muon_parent_gauge_geometry_correction import ROOT,SOURCE_RECEIPTS,STATE_SOURCE,correction_representation
from .muon_parent_mean_causal_action import VOLUME
from .muon_parent_maxwell_full_weak import FIELD_ORDER
from .muon_pointwise_full_field_action import pointwise_full_field_action,pointwise_wall_gauge_conormal
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_birth_trace_enriched_action import trace_enriched_representation,pointwise_trace_enriched_action,trace_enriched_wall_conormal


def endpoint_layout(representation):
    labels=representation['gauge_labels']
    dynamic=np.array([i for i,l in enumerate(labels) if l['field']!=FIELD_ORDER[0]])
    At=np.array([i for i,l in enumerate(labels) if l['field']==FIELD_ORDER[0]])
    N=len(labels);hs=100+2*N;nr=hs+8
    if N%20 or len(dynamic)!=4*len(At):raise ValueError('full five-component common radial representation required')
    free=np.r_[np.arange(37,98),np.arange(100,100+N),100+N+dynamic,np.arange(hs,hs+8)]
    return dict(dynamic=dynamic,At=At,free=free,all_free=np.r_[free,nr+free],raw_count=nr,gauge_count=N,H_start=hs,
        velocities=np.r_[np.arange(37,74),99,np.arange(100+N,hs),np.arange(hs+4,hs+8)])


def paired_field_endpoint_rows(raw_pair,action_evaluator,representation,state_weights):
    """Actual rows and exact Jacobian on the admissible fixed-q chart."""
    raw=np.asarray(raw_pair,float)
    weights=np.asarray(state_weights,float);layout=endpoint_layout(representation)
    nr,N,hs=(layout[k] for k in ('raw_count','gauge_count','H_start'))
    if raw.shape!=(2,nr) or not np.isfinite(raw).all():raise ValueError('same enlarged parent/child raw vectors required')
    if 'affine_profile_reference_states' in representation:
        if not np.array_equal(raw[:,:37],representation['affine_profile_reference_states'][:,:37]) or np.any(raw[:,98:100]):
            raise ValueError('this exact source-image match owns fixed q traces and zero normal/rate; new trace jets require enrichment')
    if weights.shape!=(98,) or np.any(weights<=0):raise ValueError('retained positive state98 normalization required')
    apps=[action_evaluator(x) for x in raw];r=[];J=[];energies=[]
    for side,(x,a) in enumerate(zip(raw,apps)):
        G,H=a['raw_gradient'],a['raw_hessian'];off=nr*side
        constraint=np.r_[np.arange(74,98),100+layout['At']]
        scale=np.r_[1/weights[74:],np.ones(len(layout['At']))]
        block=np.zeros((len(constraint),2*nr));block[:,off:off+nr]=scale[:,None]*H[constraint]
        r.extend(scale*G[constraint]);J.extend(block)
        v=np.zeros(nr);v[layout['velocities']]=x[layout['velocities']]
        energy=float(v@G-a['value']);energies.append(energy)
        dE=H@v-G;dE[layout['velocities']]+=G[layout['velocities']]
        row=np.zeros(2*nr);row[off:off+nr]=dE;r.append(energy);J.append(row)
    # temporal orientation: parent final +Pi, child initial -Pi.
    affine=np.zeros(len(layout['dynamic']))
    if 'affine_difference_coefficients' in representation:
        for j,i in enumerate(layout['dynamic']):
            label=representation['gauge_labels'][i];field=FIELD_ORDER.index(label['field'])
            if field>=2 and label['internal']==field-2:
                affine[j]=np.sqrt(8)*representation['affine_difference_coefficients'][label['radial']]
    for fields,momenta,offset in ((100+layout['dynamic'],100+N+layout['dynamic'],affine),
                           (np.arange(hs,hs+4),np.arange(hs+4,hs+8),np.zeros(4))):
        trace=raw[1,fields]-raw[0,fields]-offset;block=np.zeros((len(fields),2*nr))
        block[:,fields]=-np.eye(len(fields));block[:,nr+fields]=np.eye(len(fields))
        r.extend(trace);J.extend(block)
        jump=apps[0]['raw_gradient'][momenta]-apps[1]['raw_gradient'][momenta]
        block=np.c_[apps[0]['raw_hessian'][momenta],-apps[1]['raw_hessian'][momenta]]
        r.extend(jump);J.extend(block)
    return dict(residual=np.asarray(r),jacobian=np.asarray(J),arms=apps,energies=np.asarray(energies),layout=layout,
        affine_mechanical_trace_source=affine,
        temporal_pairing='real coefficient dual from the same action; scalar 2Re already in realification',
        physical_fullfield_junction_closed=False)


def shared_parameter_sources(raw_pair,applications,representation,state_weights,nu_squared_action):
    """Exact reached per-gamma and d/d(nu^2) loads, without assigning gamma."""
    rows_gamma=[];rows_nu=[]
    layout=endpoint_layout(representation)
    nr,hs=layout['raw_count'],layout['H_start'];na=len(layout['At']);nd=len(layout['dynamic'])
    for x,a in zip(raw_pair,applications):
        v=np.zeros(nr);v[layout['velocities']]=x[layout['velocities']]
        sg=np.zeros(nr);sg[:100]=a['surface_gradient_per_gamma']
        rows_gamma.extend(sg[74:98]/state_weights[74:]);rows_gamma.extend(np.zeros(na))
        rows_gamma.append(float(v@sg-a['surface_value_per_gamma']))
        weights=intrinsic_m4_weight_jet(12,x[:37],x[37:74],x[74:98],source_value=x[98],source_rate=x[99])
        w=weights['wV'];lam=representation['scalar_matching']['lambda_H'];gap=x[hs:hs+4]@x[hs:hs+4]-nu_squared_action
        derivative_value=2*lam*w.value*gap/VOLUME**2;sn=np.zeros(nr)
        sn[:100]=2*lam*w.gradient*gap/VOLUME**2;sn[hs:hs+4]=4*lam*w.value*x[hs:hs+4]/VOLUME**2
        rows_nu.extend(sn[74:98]/state_weights[74:]);rows_nu.extend(np.zeros(na));rows_nu.append(float(v@sn-derivative_value))
    rows_gamma.extend(np.zeros(2*nd+8));rows_nu.extend(np.zeros(2*nd+8))
    return dict(gamma=np.asarray(rows_gamma),nu_squared_action=np.asarray(rows_nu),
        log_energy_unit=-2*nu_squared_action*np.asarray(rows_nu),
        log_energy_role='chain-rule load at fixed matched nu_GeV^2; GF=cF/E_kappa^2 still needed, not logE stationarity')


def solve_paired_field_endpoint(initial,action_evaluator,representation,state_weights,*,max_iterations=10,
                                tolerance=2e-10,checkpoint=None,row_scale=None,iteration_offset=0):
    raw=np.array(initial,float,copy=True);layout=endpoint_layout(representation);free=layout['all_free']
    current=paired_field_endpoint_rows(raw,action_evaluator,representation,state_weights)
    w=np.tile(np.r_[state_weights[37:],np.ones(layout['gauge_count']+len(layout['dynamic'])+8)],2)
    scale=1/np.maximum(np.max(abs(current['jacobian'][:,free]/w[None,:]),axis=1),1.) if row_scale is None else np.asarray(row_scale,float)
    history=[];records=[];status='MAXIMUM_ITERATIONS'
    if checkpoint is not None:checkpoint(iteration_offset,raw,current,scale,history,'INITIAL_OR_RESUMED')
    for it in range(max_iterations):
        r=current['residual'];J=current['jacobian'][:,free];norm=float(np.linalg.norm(scale*r))
        if norm<tolerance:status='REPRESENTED_TEMPORAL_FIELD_TOLERANCE';break
        U,s,V=np.linalg.svd(scale[:,None]*J/w[None,:],full_matrices=True);keep=s>1e-12*max(s)
        correction=-(V[:len(s)][keep].T@((U[:,keep].T@(scale*r))/s[keep]))/w
        trials=[];accepted=False
        for k in range(18):
            damping=2.**(-k);trial=raw.copy();trial.reshape(-1)[free]+=damping*correction
            try:
                candidate=paired_field_endpoint_rows(trial,action_evaluator,representation,state_weights)
                newnorm=float(np.linalg.norm(scale*candidate['residual']));good=np.isfinite(newnorm) and newnorm<norm
            except (ValueError,FloatingPointError,np.linalg.LinAlgError,OverflowError):newnorm=None;good=False
            trials.append(dict(damping=damping,scaled_residual=newnorm,accepted=bool(good)))
            if good:accepted=True;break
        history.append(dict(iteration=iteration_offset+it,scaled_residual=norm,rank=int(sum(keep)),damping_history=trials,
            weighted_step_norm=float(np.linalg.norm(w*correction)),
            omitted_left_projection_norm=float(np.linalg.norm(U[:,~keep].T@(scale*r))),
            linearized_scaled_residual=float(np.linalg.norm(scale*(J@correction+r)))))
        records.append(dict(jacobian=J,linearization_raw=raw.copy(),correction=correction,singular_values=s,
            left_vectors=U,right_vectors=V,left_source_projections=U.T@(scale*r),retained_singular_values=keep))
        if not accepted:status='DAMPING_STALL';break
        raw=trial;current=candidate
        if checkpoint is not None:checkpoint(iteration_offset+it+1,raw,current,scale,history,'ACCEPTED_STEP')
    if np.linalg.norm(scale*current['residual'])<tolerance:status='REPRESENTED_TEMPORAL_FIELD_TOLERANCE'
    return dict(raw=raw,application=current,history=history,records=records,row_scale=scale,
        coefficient_weights=w,free_indices=free,status=status,scaled_residual=float(np.linalg.norm(scale*current['residual'])))


def materialize_paired_field_endpoint(initial_application,output,*,repository=ROOT,max_iterations=10,radial_points=48,cap_points=48,resume_checkpoint=None):
    root=Path(repository);source=Path(initial_application);source=source if source.is_absolute() else root/source;out=Path(output)
    if out.exists():raise FileExistsError('preserve earlier applications')
    rows=[endpoint_raw_from_assigned_application(source,side) for side in ('incoming','outgoing')]
    original=np.array([r[0] for r in rows]);receipt=rows[0][1];rhash=rows[0][2]
    if np.any(original[:,100:220]):raise ValueError('this initializer must preserve its actual zero independent gauge seed')
    rep=trace_enriched_representation(original,radial_points=radial_points,cap_points=cap_points)
    layout=endpoint_layout(rep);initial=np.zeros((2,layout['raw_count']));initial[:,:100]=original[:,:100];initial[:,-8:]=original[:,-8:]
    with np.load(root/STATE_SOURCE,allow_pickle=False) as a:weights=a['state_weights']
    params=receipt['action_parameters'];evaluate=lambda x:pointwise_trace_enriched_action(x,rep,**params)
    refs=list(SOURCE_RECEIPTS)+['src/bhsm/interface/muon_pointwise_full_field_action.py','src/bhsm/interface/muon_parent_mean_causal_action.py',
        'src/bhsm/interface/muon_material_higgs_gauge_action.py','src/bhsm/interface/muon_birth_coupled_primal_midpoint.py',
        'src/bhsm/interface/muon_birth_phase_continuation.py','src/bhsm/interface/muon_birth_two_arm_assigned_action.py',
        'src/bhsm/interface/muon_birth_paired_field_endpoint.py','src/bhsm/interface/muon_birth_trace_enriched_action.py']
    hashes={p:sha256((root/p).read_bytes()).hexdigest() for p in refs};out.mkdir(parents=True)
    resume_options={};resume_sha=None
    if resume_checkpoint is not None:
        cp=Path(resume_checkpoint);cp=cp if cp.is_absolute() else root/cp;b=(cp/'result.json').read_bytes();cr=json.loads(b)
        if cr['input_hashes']!=hashes or cr['consumed_receipt_sha256']!=rhash or (cr['radial_points'],cr['cap_points'],cr['action_parameters'])!=(radial_points,cap_points,params):
            raise ValueError('resume must preserve pinned input/action/domain')
        if sha256((cp/'application.npz').read_bytes()).hexdigest()!=cr['numerical_sha256']:raise ValueError('checkpoint hash mismatch')
        with np.load(cp/'application.npz',allow_pickle=False) as saved:
            solve_initial=saved['raw_pair'];resume_options=dict(row_scale=saved['row_scale'],iteration_offset=cr['accepted_iteration'])
        resume_sha=sha256(b).hexdigest()
    else:solve_initial=initial
    def checkpoint(k,raw,app,scale,history,status):
        folder=out/'checkpoints'/f'accepted_{k:04d}';folder.mkdir(parents=True)
        _compressed_npz(folder/'application.npz',dict(raw_pair=raw,residual=app['residual'],jacobian=app['jacobian'],row_scale=scale))
        md=dict(scope='REPRESENTED_TEMPORAL_FIELD_ENDPOINT_CHECKPOINT',accepted_iteration=k,status=status,
            scaled_residual=float(np.linalg.norm(scale*app['residual'])),history=history,input_hashes=hashes,
            consumed_receipt_sha256=rhash,action_parameters=params,radial_points=radial_points,cap_points=cap_points,
            numerical_sha256=sha256((folder/'application.npz').read_bytes()).hexdigest(),
            resume_argv=['C:/Python314/python.exe','-m','bhsm.interface.muon_birth_paired_field_endpoint',
                '--initial-application',str(source),'--output','CHOOSE_NEW_OUTPUT_DIRECTORY','--max-iterations',str(max_iterations),
                '--radial-points',str(radial_points),'--cap-points',str(cap_points),'--resume-checkpoint',str(folder)],
            resume_environment=dict(PYTHONPATH='src'))
        (folder/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    result=solve_paired_field_endpoint(solve_initial,evaluate,rep,weights,max_iterations=max_iterations,checkpoint=checkpoint,**resume_options)
    if hashes!={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}:raise RuntimeError('owner changed during endpoint correction')
    app=result['application'];raw=result['raw'];faces=[trace_enriched_wall_conormal(x,rep) for x in raw]
    parameters=shared_parameter_sources(raw,app['arms'],rep,weights,params['nu_squared_action'])
    old_lifts=[same_action_attachment_momentum(x[:37],dict(gradient=a['raw_gradient'][:100],hessian=a['raw_hessian'][:100,:100])) for x,a in zip(raw,app['arms'])]
    arrays=dict(initial_raw_pair=initial,updated_raw_pair=raw,updated_residual=app['residual'],updated_jacobian=app['jacobian'],
        updated_gradients=np.array([a['raw_gradient'] for a in app['arms']]),updated_hessians=np.array([a['raw_hessian'] for a in app['arms']]),
        row_scale=result['row_scale'],coefficient_weights=result['coefficient_weights'],free_indices=result['free_indices'],state_weights=weights,
        lateral_wall_conormals=np.array([f['radial_action_covector'] for f in faces]),
        gamma_residual_source=parameters['gamma'],nu_squared_residual_source=parameters['nu_squared_action'],
        log_energy_residual_source=parameters['log_energy_unit'],old_fixed_field_attachment_momenta=np.array([l['momentum'] for l in old_lifts]))
    arrays.update(affine_profile_reference_states=rep['affine_profile_reference_states'],
        affine_interior_projection=rep['affine_interior_projection'],affine_difference_coefficients=rep['affine_difference_coefficients'],
        radial_value_map=rep['radial_value_map'],radial_derivative_map=rep['radial_derivative_map'],
        gauge_basis=rep['gauge_basis'],gauge_radial_basis=rep['gauge_radial_basis'],
        wall_trace_map=rep['wall_trace_map'],wall_radial_derivative_map=rep['wall_radial_derivative_map'],
        affine_mechanical_trace_source=app['affine_mechanical_trace_source'],rho=rep['rho'],radial_quadrature=rep['radial_quadrature'])
    if result['records']:
        for key in result['records'][0]:arrays['iteration_'+key]=np.array([r[key] for r in result['records']])
    _compressed_npz(out/'application.npz',arrays)
    r=app['residual'];na=len(layout['At']);nd=len(layout['dynamic']);arm=25+na;trace0=2*arm;scalar0=trace0+2*nd
    md=dict(scope='EVALUATED_REPRESENTED_TEMPORAL_GAUGE_HIGGS_ENDPOINT_CORRECTION',status=result['status'],
        scaled_residual=result['scaled_residual'],unscaled_residual_norm=float(np.linalg.norm(r)),history=result['history'],
        row_count=len(r),raw_arm_count=layout['raw_count'],gauge_count=layout['gauge_count'],gauge_labels=rep['gauge_labels'],
        parent_multiplier_norm=float(np.linalg.norm(r[:24])),parent_Gauss_norm=float(np.linalg.norm(r[24:24+na])),
        child_multiplier_norm=float(np.linalg.norm(r[arm:arm+24])),child_Gauss_norm=float(np.linalg.norm(r[arm+24:arm+24+na])),
        total_energies=app['energies'].tolist(),gauge_trace_norm=float(np.linalg.norm(r[trace0:trace0+nd])),
        gauge_temporal_dual_jump_norm=float(np.linalg.norm(r[trace0+nd:scalar0])),scalar_trace_norm=float(np.linalg.norm(r[scalar0:scalar0+4])),
        scalar_temporal_dual_jump_norm=float(np.linalg.norm(r[scalar0+4:scalar0+8])),
        affine_profile_enrichment=dict(former_radial_space_L2_complement=rep['former_radial_space_L2_complement'],
            boundary_anchored_complement_norm=rep['affine_complement_norm'],wall_coefficient=rep['affine_wall_coefficient'],
            value_reconstruction_max=rep['affine_trace_reconstruction_max'],radial_derivative_reconstruction_max=rep['affine_trace_derivative_reconstruction_max'],
            fixed_velocity_multiplier_jet_max=rep['affine_velocity_multiplier_jet_max']),
        old_fixed_field_geometric_attachment_jump_norm=float(np.linalg.norm(old_lifts[1]['momentum']-old_lifts[0]['momentum'])),
        old_attachment_role='same-action fixed-field geometry37 lift diagnostic; fullfield constrained lift not substituted',
        lateral_wall_conormal_norms=[float(np.linalg.norm(f['radial_action_covector'])) for f in faces],
        field_graph='jointly transformed homogeneous common bundle/coordinate slice; actual affine mechanical profile difference retained exactly in enriched radial space',
        geometry_trace_policy='both original q37 fixed; wall metric graph inherited, distinct bulk profiles retained; no varied q/normal trace derivative omitted',
        At_policy=f'both independent At{na} Gauss rows retained; no invented At-dot kinetic or At temporal Dirichlet condition',
        temporal_cotangent_policy='parent-final plus Pi, child-initial minus Pi, real coefficient dual; no second scalar density',
        lateral_policy='radial conormals separate; not equated across temporal birth or setzero',
        shared_parameter_sources=dict(gamma_norm=float(np.linalg.norm(parameters['gamma'])),nu_squared_norm=float(np.linalg.norm(parameters['nu_squared_action'])),
            log_energy_norm=float(np.linalg.norm(parameters['log_energy_unit']))),
        unassigned_area_equation='gamma=alpha_FSC*ell_current^(-m); no alpha_EM substitution or gamma0 claim',
        common_scale_equation='GF=cF[common charged-current action]/E_kappa^2; logE load is not a stationarity equation',
        action_parameters=params,radial_points=radial_points,cap_points=cap_points,input_hashes=hashes,consumed_receipt_sha256=rhash,
        resumed_checkpoint_sha256=resume_sha,
        consumed_coefficients_sha256=receipt['numerical_sha256'],numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        physical_fullfield_junction_closed=False,physical_formation_closed=False,physical_native_heat_closed=False,physical_Pauli_value=False,
        error_scope='binary64 finite nonlinear action and exact analytic residual Jacobian; numerical minimum-residual corrections, not a physical branch selector')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--initial-application',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--max-iterations',type=int,default=10);p.add_argument('--radial-points',type=int,default=48);p.add_argument('--cap-points',type=int,default=48)
    p.add_argument('--resume-checkpoint',type=Path)
    a=p.parse_args();print(json.dumps(materialize_paired_field_endpoint(a.initial_application,a.output,max_iterations=a.max_iterations,
        radial_points=a.radial_points,cap_points=a.cap_points,resume_checkpoint=a.resume_checkpoint),sort_keys=True))
