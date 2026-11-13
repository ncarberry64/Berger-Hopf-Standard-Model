"""Full-field constrained attachment added to the evaluated birth rows.

Every represented dynamic field enters the actual velocity-form saddle.
The inherited two geometric coordinates and all multiplier/Gauss rows
are retained.  Centered directional Hessian applications with step
halving supply the canonical cotangent derivative, not an old p2 lift.
Original q traces remain fixed; the affine trace source is consequently
fixed on this numerical chart.  No physical formation or unit is chosen.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT,STATE_SOURCE
from .muon_birth_reset_evaluation import NORMALIZATION_SOURCE
from .aether_full_reset_action_jacobian import _attachment_jacobian_at_order,_symmetric_power
from .muon_birth_trace_enriched_phase import load_enriched_endpoint
from .muon_birth_trace_enriched_action import generic_coordinate_lift,pointwise_trace_enriched_action,trace_enriched_wall_conormal
from .muon_birth_paired_field_endpoint import paired_field_endpoint_rows,endpoint_layout,shared_parameter_sources
from .muon_birth_full_field_attachment import constrained_attachment_lift,inherited_full_field_boundary,attachment_momentum_cotangent
from .muon_birth_phase_continuation import _compressed_npz


def paired_attachment_rows(raw_pair,evaluator,representation,state_weights,normalization_coordinates):
    base=paired_field_endpoint_rows(raw_pair,evaluator,representation,state_weights)
    coord=generic_coordinate_lift(representation['gauge_labels']);P=coord['lift'];nx=coord['x_count'];ny=coord['y_count']
    attachments=[]
    for raw,action in zip(raw_pair,base['arms']):
        B,_=inherited_full_field_boundary(raw[:37],nx,len(P[0]))
        attachments.append(constrained_attachment_lift(dict(gradient=P.T@action['raw_gradient'],hessian=P.T@action['raw_hessian']@P),
            B,dynamic_count=nx,algebraic_count=ny))
    B0=_attachment_jacobian_at_order(12,normalization_coordinates);normalization=_symmetric_power(B0@B0.T,.5)
    jump=normalization@(attachments[1]['momentum']-attachments[0]['momentum'])
    return dict(residual=np.r_[base['residual'],jump],base=base,attachments=attachments,
        normalization=normalization,coordinates=coord,attachment_jump=jump)


def paired_attachment_jacobian(raw_pair,evaluator,representation,state_weights,current,*,difference_step=2e-5):
    P=current['coordinates']['lift'];nx=current['coordinates']['x_count'];ny=current['coordinates']['y_count'];nr=len(P)
    raw_weights=np.r_[state_weights,np.ones(nr-98)];master_weights=abs(P.T)@raw_weights
    J=np.zeros((len(current['residual']),2*nr));J[:-2]=current['base']['jacobian'];details=[]
    for side,(raw,action) in enumerate(zip(raw_pair,current['base']['arms'])):
        eta=P.T@raw;B,db=inherited_full_field_boundary(raw[:37],nx,len(eta))
        a=dict(gradient=P.T@action['raw_gradient'],hessian=P.T@action['raw_hessian']@P)
        eval_master=lambda value:dict(gradient=(v:=evaluator(P@value))['gradient'],hessian=v['hessian'])
        coarse=attachment_momentum_cotangent(eta,eval_master,B,db,dynamic_count=nx,algebraic_count=ny,
            coordinate_weights=master_weights,difference_step=difference_step,base_action=a)
        fine=attachment_momentum_cotangent(eta,eval_master,B,db,dynamic_count=nx,algebraic_count=ny,
            coordinate_weights=master_weights,difference_step=difference_step/2,base_action=a)
        sign=-1 if side==0 else 1;J[-2:,nr*side:nr*(side+1)]=sign*current['normalization']@fine['cotangent']@P.T
        difference=(fine['cotangent']-coarse['cotangent'])@P.T
        free=current['base']['layout']['free']
        details.append(dict(coarse_cotangent=coarse['cotangent'],fine_cotangent=fine['cotangent'],
            third_action_contraction=fine['third_action_contraction'],boundary_contact=fine['boundary_contact'],
            free_weighted_step_halving_norm=float(np.linalg.norm(difference[:,free]/raw_weights[free])),
            free_weighted_step_halving_relative=float(np.linalg.norm(difference[:,free]/raw_weights[free])/max(1.,np.linalg.norm((fine['cotangent']@P.T)[:,free]/raw_weights[free]))),
            difference_step=difference_step,fine_difference_step=difference_step/2))
    return J,details


def solve_paired_attachment(initial,evaluator,representation,state_weights,normalization_coordinates,*,
        max_iterations=10,tolerance=2e-10,difference_step=2e-5,checkpoint=None,row_scale=None,iteration_offset=0):
    raw=np.array(initial,float,copy=True);layout=endpoint_layout(representation);free=layout['all_free']
    weights=np.tile(np.r_[state_weights[37:],np.ones(layout['gauge_count']+len(layout['dynamic'])+8)],2)
    evaluate=lambda value:paired_attachment_rows(value,evaluator,representation,state_weights,normalization_coordinates)
    current=evaluate(raw);history=[];records=[];status='MAXIMUM_ITERATIONS';scale=row_scale
    for k in range(max_iterations+1):
        J,details=paired_attachment_jacobian(raw,evaluator,representation,state_weights,current,difference_step=difference_step)
        if scale is None:scale=1/np.maximum(np.max(abs(J[:,free]/weights),axis=1),1.)
        norm=float(np.linalg.norm(scale*current['residual']))
        if checkpoint is not None:checkpoint(iteration_offset+k,raw,current,J,details,scale,history,'ACCEPTED_OR_INITIAL')
        if norm<tolerance:status='REPRESENTED_FULL_FIELD_ATTACHMENT_TOLERANCE';break
        if k==max_iterations:break
        U,s,V=np.linalg.svd(scale[:,None]*J[:,free]/weights,full_matrices=True);keep=s>1e-12*max(s)
        correction=-(V[:len(s)][keep].T@((U[:,keep].T@(scale*current['residual']))/s[keep]))/weights
        trials=[];accepted=False
        for i in range(18):
            damping=2.**(-i);trial=raw.copy();trial.reshape(-1)[free]+=damping*correction
            try:
                candidate=evaluate(trial);newnorm=float(np.linalg.norm(scale*candidate['residual']));good=np.isfinite(newnorm) and newnorm<norm
            except (ValueError,FloatingPointError,np.linalg.LinAlgError,OverflowError):newnorm=None;good=False
            trials.append(dict(damping=damping,scaled_residual=newnorm,accepted=bool(good)))
            if good:accepted=True;break
        history.append(dict(iteration=iteration_offset+k,scaled_residual=norm,rank=int(sum(keep)),damping_history=trials,
            weighted_step_norm=float(np.linalg.norm(weights*correction)),
            left_omitted_source_norm=float(np.linalg.norm(U[:,~keep].T@(scale*current['residual']))),
            linearized_scaled_residual=float(np.linalg.norm(scale*(J[:,free]@correction+current['residual']))),
            cotangent_step_halving=[dict(norm=d['free_weighted_step_halving_norm'],relative=d['free_weighted_step_halving_relative']) for d in details]))
        records.append(dict(jacobian=J[:,free],linearization_raw=raw.copy(),correction=correction,singular_values=s,
            left_vectors=U,right_vectors=V,left_source_projections=U.T@(scale*current['residual']),retained_singular_values=keep))
        if not accepted:status='DAMPING_STALL';break
        raw=trial;current=candidate
    return dict(raw=raw,application=current,jacobian=J,cotangent_details=details,row_scale=scale,history=history,records=records,
        free_indices=free,coefficient_weights=weights,status=status,scaled_residual=float(np.linalg.norm(scale*current['residual'])))


def materialize_paired_attachment(initial_application,output,*,repository=ROOT,max_iterations=10,difference_step=2e-5,resume_checkpoint=None):
    root=Path(repository);out=Path(output)
    if out.exists():raise FileExistsError('preserve prior evidence')
    loaded=load_enriched_endpoint(initial_application,side='incoming',repository=root);source=loaded['source'];rep=loaded['representation']
    with np.load(source/'application.npz',allow_pickle=False) as a:initial=a['updated_raw_pair']
    with np.load(root/STATE_SOURCE,allow_pickle=False) as a:weights=a['state_weights']
    with np.load(root/NORMALIZATION_SOURCE,allow_pickle=False) as a:normalization=a['normalization_coordinates']
    params=loaded['receipt']['action_parameters'];evaluate=lambda value:pointwise_trace_enriched_action(value,rep,**params)
    hashes=dict(loaded['receipt']['input_hashes'])
    for p in [NORMALIZATION_SOURCE,'src/bhsm/interface/muon_birth_full_field_attachment.py','src/bhsm/interface/muon_birth_paired_attachment_endpoint.py',
        'src/bhsm/interface/muon_birth_trace_enriched_phase.py','src/bhsm/interface/aether_canonical_momentum_action_jacobian.py']:
        hashes[p]=sha256((root/p).read_bytes()).hexdigest()
    resume_options={};resume_sha=None
    if resume_checkpoint is not None:
        cp=Path(resume_checkpoint);cp=cp if cp.is_absolute() else root/cp;rb=(cp/'result.json').read_bytes();cr=json.loads(rb)
        if cr['input_hashes']!=hashes or cr['consumed_receipt_sha256']!=loaded['receipt_sha256'] or cr['difference_step']!=difference_step:
            raise ValueError('resume must preserve action, numerical frame, paired endpoint and directional step')
        if sha256((cp/'application.npz').read_bytes()).hexdigest()!=cr['numerical_sha256']:raise ValueError('checkpoint changed')
        with np.load(cp/'application.npz',allow_pickle=False) as a:initial=a['raw_pair'];resume_options=dict(row_scale=a['row_scale'],iteration_offset=cr['accepted_iteration'])
        resume_sha=sha256(rb).hexdigest()
    out.mkdir(parents=True)
    def checkpoint(k,raw,app,J,details,scale,history,status):
        folder=out/'checkpoints'/f'accepted_{k:04d}';folder.mkdir(parents=True)
        _compressed_npz(folder/'application.npz',dict(raw_pair=raw,residual=app['residual'],jacobian=J,row_scale=scale,
            full_field_attachment_momenta=np.array([a['momentum'] for a in app['attachments']]),
            cotangent_coarse=np.array([d['coarse_cotangent'] for d in details]),cotangent_fine=np.array([d['fine_cotangent'] for d in details])))
        md=dict(scope='FULL_FIELD_ATTACHMENT_ENDPOINT_CHECKPOINT',accepted_iteration=k,status=status,history=history,
            scaled_residual=float(np.linalg.norm(scale*app['residual'])),difference_step=difference_step,input_hashes=hashes,
            consumed_receipt_sha256=loaded['receipt_sha256'],numerical_sha256=sha256((folder/'application.npz').read_bytes()).hexdigest(),
            resume_argv=['C:/Python314/python.exe','-m','bhsm.interface.muon_birth_paired_attachment_endpoint',
                '--initial-application',str(source),'--output','CHOOSE_NEW_OUTPUT_DIRECTORY','--max-iterations',str(max_iterations),
                '--difference-step',str(difference_step),'--resume-checkpoint',str(folder)],resume_environment=dict(PYTHONPATH='src'))
        (folder/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    result=solve_paired_attachment(initial,evaluate,rep,weights,normalization,max_iterations=max_iterations,
        difference_step=difference_step,checkpoint=checkpoint,**resume_options)
    if hashes!={p:sha256((root/p).read_bytes()).hexdigest() for p in hashes}:raise RuntimeError('action owner changed')
    raw=result['raw'];app=result['application'];fields=app['base'];attachments=app['attachments']
    faces=[trace_enriched_wall_conormal(x,rep) for x in raw]
    parameters=shared_parameter_sources(raw,fields['arms'],rep,weights,params['nu_squared_action'])
    arrays=dict(initial_raw_pair=initial,updated_raw_pair=raw,updated_residual=app['residual'],updated_jacobian=result['jacobian'],
        updated_gradients=np.array([a['raw_gradient'] for a in fields['arms']]),updated_hessians=np.array([a['raw_hessian'] for a in fields['arms']]),
        full_field_attachment_momenta=np.array([a['momentum'] for a in attachments]),
        full_field_attachment_lifts=np.array([a['lift'] for a in attachments]),full_field_saddles=np.array([a['saddle'] for a in attachments]),
        full_field_saddle_solutions=np.array([a['saddle_solution'] for a in attachments]),full_field_saddle_adjoints=np.array([a['adjoint'] for a in attachments]),
        full_field_saddle_residuals=np.array([a['saddle_residual'] for a in attachments]),full_field_constraint_annihilation=np.array([a['constraint_annihilation'] for a in attachments]),
        cotangent_coarse=np.array([d['coarse_cotangent'] for d in result['cotangent_details']]),cotangent_fine=np.array([d['fine_cotangent'] for d in result['cotangent_details']]),
        normalization_coordinates=normalization,attachment_normalization=app['normalization'],free_indices=result['free_indices'],
        coefficient_weights=result['coefficient_weights'],row_scale=result['row_scale'],state_weights=weights,
        lateral_wall_conormals=np.array([f['radial_action_covector'] for f in faces]),
        gamma_field_residual_source=parameters['gamma'],nu_squared_field_residual_source=parameters['nu_squared_action'])
    for key in ('affine_profile_reference_states','affine_interior_projection','affine_difference_coefficients','radial_value_map','radial_derivative_map',
        'gauge_basis','gauge_radial_basis','wall_trace_map','wall_radial_derivative_map','rho','radial_quadrature'):arrays[key]=rep[key]
    for key in result['records'][0] if result['records'] else []:arrays['iteration_'+key]=np.array([r[key] for r in result['records']])
    _compressed_npz(out/'application.npz',arrays)
    md=dict(scope='EVALUATED_FULL_FIELD_CONSTRAINED_ATTACHMENT_ENDPOINT_CORRECTION',status=result['status'],
        scaled_residual=result['scaled_residual'],unscaled_residual_norm=float(np.linalg.norm(app['residual'])),history=result['history'],
        attachment_jump_norm=float(np.linalg.norm(app['attachment_jump'])),field_rows_norm=float(np.linalg.norm(fields['residual'])),
        full_field_attachment_momenta=[a['momentum'].tolist() for a in attachments],
        balanced_saddle_condition_numbers=[a['balanced_condition_number'] for a in attachments],
        saddle_residual_norms=[float(np.linalg.norm(a['saddle_residual'])) for a in attachments],
        saddle_adjoint_residual_norms=[float(np.linalg.norm(a['adjoint_residual'])) for a in attachments],
        constraint_annihilation_norms=[float(np.linalg.norm(a['constraint_annihilation'])) for a in attachments],
        lift_norms=[float(np.linalg.norm(a['lift'])) for a in attachments],
        final_cotangent_step_halving=[dict(norm=d['free_weighted_step_halving_norm'],relative=d['free_weighted_step_halving_relative']) for d in result['cotangent_details']],
        difference_step=difference_step,fine_difference_step=difference_step/2,raw_arm_count=len(raw[0]),row_count=len(app['residual']),
        gauge_count=rep['gauge_count'],gauge_labels=rep['gauge_labels'],affine_profile_enrichment=loaded['receipt']['affine_profile_enrichment'],
        lateral_wall_conormal_norms=[float(np.linalg.norm(f['radial_action_covector'])) for f in faces],
        geometry_trace_policy='original q37 pair fixed; existing wall trace graph retained; affine source held fixed on this chart',
        attachment_policy='inherited B2, full Lvv106 and L_yv40 including24 multiplier and16 Gauss rows; saddle stationarity, no inverse-A/positivity assumption',
        normal_policy='moving normal belongs the full velocity form but no physical formation section/eigenline selected',
        shared_parameters='nu_action parameter trial; gamma=alpha_FSC*ell_current^(-m), GF=cF/E_kappa^2 remain equations, no zero or physical unit assigned',
        action_parameters=params,radial_points=len(rep['rho']),cap_points=rep['cap_points'],input_hashes=hashes,
        consumed_receipt_sha256=loaded['receipt_sha256'],consumed_coefficients_sha256=loaded['receipt']['numerical_sha256'],resumed_checkpoint_sha256=resume_sha,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        physical_fullfield_junction_closed=False,physical_formation_closed=False,physical_native_heat_closed=False,physical_Pauli_value=False,
        error_scope='binary64 finite nonlinear action, exact saddle solves and centered directional Hessian differences with halving diagnostics; no continuum or producer-rounding certificate')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--initial-application',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--max-iterations',type=int,default=10);p.add_argument('--difference-step',type=float,default=2e-5);p.add_argument('--resume-checkpoint',type=Path)
    a=p.parse_args();print(json.dumps(materialize_paired_attachment(a.initial_application,a.output,max_iterations=a.max_iterations,
        difference_step=a.difference_step,resume_checkpoint=a.resume_checkpoint),sort_keys=True))
