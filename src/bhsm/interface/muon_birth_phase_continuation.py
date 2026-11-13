"""Full-action phase continuation carrying canonical momenta between steps.

The x/p pair, not a re-Legendre-transformed midpoint velocity, is passed
to the next implicit step.  Velocities and all multiplier/Gauss variables
are solved at every stage.  This is a finite assigned-action application;
it does not select the physical event, wall return or formation interval.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import numpy as np

from .muon_birth_coupled_primal_midpoint import nonlinear_midpoint_rows, endpoint_raw_from_assigned_application
from .muon_parent_gauge_geometry_correction import ROOT, SOURCE_RECEIPTS, correction_representation
from .muon_parent_mean_causal_action import mean_coordinate_lift
from .muon_pointwise_full_field_action import pointwise_full_field_action, pointwise_wall_gauge_conormal


def _compressed_npz(path,arrays):
    """Fixed member order/timestamps; compression changes no array values."""
    with ZipFile(path,'w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for name in sorted(arrays):
            stream=BytesIO();np.lib.format.write_array(stream,np.asarray(arrays[name]),allow_pickle=False)
            member=ZipInfo(name+'.npy',date_time=(1980,1,1,0,0,0));member.compress_type=ZIP_DEFLATED
            member.external_attr=0o600<<16;archive.writestr(member,stream.getvalue(),compresslevel=9)


def solve_phase_midpoint(x0, p0, eta_guess, step, action_evaluator, *, tolerance=2e-12,
                         max_iterations=10, rank_tolerance=1e-12, checkpoint=None,
                         initial_unknowns=None, row_scale=None, iteration_offset=0):
    """Solve the same action rows with the actual incoming canonical pair."""
    x0=np.asarray(x0,float);p0=np.asarray(p0,float);eta=np.asarray(eta_guess,float);n=len(x0)
    if p0.shape!=x0.shape or len(eta)<=2*n or not np.array_equal(eta[:n],x0):
        raise ValueError('same x/p phase and x/v/y stage guess required')
    a=action_evaluator(eta)
    z=np.r_[x0+step*eta[n:2*n],p0+step*a['gradient'][:n],eta[n:]] if initial_unknowns is None else np.array(initial_unknowns,float,copy=True)
    app=nonlinear_midpoint_rows(z,x0,p0,step,action_evaluator)
    scale=1/np.maximum(np.max(abs(app['jacobian']),axis=1),1.) if row_scale is None else np.asarray(row_scale,float)
    history=[];records=[];status='MAXIMUM_ITERATIONS'
    if checkpoint is not None:checkpoint(iteration_offset,z,app,scale,history,'INITIAL_OR_RESUMED')
    for k in range(max_iterations):
        r,J=app['residual'],app['jacobian'];norm=float(np.linalg.norm(scale*r))
        if norm<tolerance:status='REPRESENTED_PHASE_TOLERANCE';break
        col=1/np.maximum(np.max(abs(scale[:,None]*J),axis=0),np.finfo(float).tiny)
        U,s,V=np.linalg.svd(scale[:,None]*J*col[None,:],full_matrices=True)
        keep=s>rank_tolerance*max(s)
        dz=-col*(V[keep].T@((U[:,keep].T@(scale*r))/s[keep]))
        trials=[];accepted=False
        for j in range(18):
            damping=2.**(-j);trial=z+damping*dz
            try:
                candidate=nonlinear_midpoint_rows(trial,x0,p0,step,action_evaluator)
                newnorm=float(np.linalg.norm(scale*candidate['residual']));good=np.isfinite(newnorm) and newnorm<norm
            except (ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError):
                newnorm=None;good=False
            trials.append(dict(damping=damping,scaled_residual=newnorm,accepted=bool(good)))
            if good:accepted=True;break
        history.append(dict(iteration=iteration_offset+k,scaled_residual=norm,rank=int(sum(keep)),
            omitted_left_projection_norm=float(np.linalg.norm(U[:,~keep].T@(scale*r))),
            linearized_scaled_residual=float(np.linalg.norm(scale*(J@dz+r))),damping_history=trials))
        records.append(dict(jacobian=J,linearization_unknowns=z.copy(),correction=dz,
            singular_values=s,right_vectors=V,left_vectors=U,column_scale=col,
            left_source_projections=U.T@(scale*r),retained_singular_values=keep))
        if not accepted:status='DAMPING_STALL';break
        z=trial;app=candidate
        if checkpoint is not None:checkpoint(iteration_offset+k+1,z,app,scale,history,'ACCEPTED_STEP')
    if np.linalg.norm(scale*app['residual'])<tolerance:status='REPRESENTED_PHASE_TOLERANCE'
    return dict(unknowns=z,application=app,row_scale=scale,history=history,records=records,status=status,
        scaled_residual=float(np.linalg.norm(scale*app['residual'])),incoming_x=x0,incoming_p=p0)


def discrete_action_cotangents(application, step):
    """Endpoint derivatives of h*L((x0+x1)/2,(x1-x0)/h,y).

    These are endpoint derivatives of the represented discrete action.
    They are not new zero-Neumann conditions or an assumed event drive.
    """
    a=application['action'];n=len(application['x_new']);g=a['gradient']
    return dict(initial_face=step*g[:n]/2-g[n:2*n],
                final_face=step*g[:n]/2+g[n:2*n],
                algebraic=step*g[2*n:])


def phase_continuation(x0,p0,eta_guess,span,steps,action_evaluator,*,checkpoint=None,
                       start_stage=0,resumed_unknowns=None,resumed_row_scale=None,
                       resumed_iteration=0,**solver_options):
    """Keep actual canonical output when chaining equal oriented steps."""
    if type(steps) is not int or steps<1 or not np.isfinite(span) or span==0:
        raise ValueError('positive step count and nonzero oriented finite span required')
    x=np.array(x0,float,copy=True);p=np.array(p0,float,copy=True);eta=np.array(eta_guess,float,copy=True)
    if type(start_stage) is not int or not 0<=start_stage<steps:raise ValueError('valid resumed stage required')
    applications=[];h=span/steps
    for k in range(start_stage,steps):
        cb=None if checkpoint is None else lambda i,z,a,s,hist,status:checkpoint(k,i,z,a,s,hist,status,x.copy(),p.copy(),eta.copy())
        resume=dict(initial_unknowns=resumed_unknowns,row_scale=resumed_row_scale,iteration_offset=resumed_iteration) if k==start_stage else {}
        result=solve_phase_midpoint(x,p,eta,h,action_evaluator,checkpoint=cb,**resume,**solver_options)
        result['stage']=k
        applications.append(result)
        if result['status']!='REPRESENTED_PHASE_TOLERANCE':break
        a=result['application'];x=a['x_new'].copy();p=a['p_new'].copy()
        eta=np.r_[x,a['v_mid'],a['y_mid']]
    return dict(applications=applications,x_final=x,p_final=p,stage_guess=eta,step=h,
        completed_steps=start_stage+sum(a['status']=='REPRESENTED_PHASE_TOLERANCE' for a in applications),
        actual_canonical_momentum_carried=True)


def materialize_phase_continuation(initial_application,output,*,side,span,steps,
                                  radial_points=48,cap_points=48,max_iterations=10,repository=ROOT,resume_checkpoint=None):
    root=Path(repository);source=Path(initial_application);source=source if source.is_absolute() else root/source
    out=Path(output)
    if out.exists():raise FileExistsError('preserve evidence; choose new output directory')
    if (side=='incoming' and span>=0) or (side=='outgoing' and span<=0):
        raise ValueError('incoming past / outgoing future orientation required')
    raw,receipt,rhash=endpoint_raw_from_assigned_application(source,side)
    rep=correction_representation(radial_points=radial_points,radial_order=2,cap_points=cap_points,
        include_wall_lift=True,include_scalar_mean=True)
    P=mean_coordinate_lift(rep['gauge_labels'])['lift'];eta0=P.T@raw
    params=receipt['action_parameters'];evaluate=lambda eta:pointwise_full_field_action(P@eta,rep,**params)
    refs=list(SOURCE_RECEIPTS)+['src/bhsm/interface/muon_pointwise_full_field_action.py',
        'src/bhsm/interface/muon_parent_mean_causal_action.py','src/bhsm/interface/muon_material_higgs_gauge_action.py',
        'src/bhsm/interface/muon_birth_coupled_primal_midpoint.py','src/bhsm/interface/muon_birth_phase_continuation.py']
    hashes={f:sha256((root/f).read_bytes()).hexdigest() for f in refs}
    a0=evaluate(eta0);p0=a0['gradient'][90:180]
    x_start=eta0[:90];p_start=p0;guess_start=eta0;start_stage=0;resume_sha=None;resume_options={}
    if resume_checkpoint is not None:
        cp=Path(resume_checkpoint);cp=cp if cp.is_absolute() else root/cp;b=(cp/'result.json').read_bytes();cr=json.loads(b)
        if cr['input_hashes']!=hashes or cr['consumed_receipt_sha256']!=rhash or (cr['side'],cr['span'],cr['steps'])!=(side,span,steps):
            raise ValueError('resume must preserve source, endpoint, representation and span')
        if (cr['radial_points'],cr['cap_points'],cr['action_parameters'])!=(radial_points,cap_points,params):
            raise ValueError('resume must preserve quadrature and action parameters')
        if sha256((cp/'application.npz').read_bytes()).hexdigest()!=cr['numerical_sha256']:raise ValueError('checkpoint hash mismatch')
        with np.load(cp/'application.npz',allow_pickle=False) as saved:
            x_start=saved['incoming_x'];p_start=saved['incoming_p'];guess_start=saved['stage_guess']
            resume_options=dict(resumed_unknowns=saved['unknowns'],resumed_row_scale=saved['row_scale'],resumed_iteration=cr['iteration'])
        start_stage=cr['stage'];resume_sha=sha256(b).hexdigest()
    out.mkdir(parents=True)
    def checkpoint(stage,iteration,z,a,scale,history,status,x,p,eta):
        folder=out/'checkpoints'/f'stage_{stage:04d}'/f'accepted_{iteration:04d}';folder.mkdir(parents=True)
        _compressed_npz(folder/'application.npz',dict(incoming_x=x,incoming_p=p,stage_guess=eta,
            unknowns=z,residual=a['residual'],jacobian=a['jacobian'],row_scale=scale,
            midpoint_raw=P@a['midpoint_coefficients']))
        md=dict(scope='FULL_ASSIGNED_ACTION_PHASE_STEP_CHECKPOINT',stage=stage,iteration=iteration,status=status,
            side=side,span=span,step=span/steps,steps=steps,scaled_residual=float(np.linalg.norm(scale*a['residual'])),
            radial_points=radial_points,cap_points=cap_points,action_parameters=params,
            iteration_history=history,input_hashes=hashes,consumed_receipt_sha256=rhash,
            numerical_sha256=sha256((folder/'application.npz').read_bytes()).hexdigest(),
            resume_argv=['C:/Python314/python.exe','-m','bhsm.interface.muon_birth_phase_continuation',
                '--initial-application',str(source),'--output','CHOOSE_NEW_OUTPUT_DIRECTORY','--side',side,
                '--span',str(span),'--steps',str(steps),'--radial-points',str(radial_points),'--cap-points',str(cap_points),
                '--max-iterations',str(max_iterations),'--resume-checkpoint',str(folder)],
            resume_environment=dict(PYTHONPATH='src'))
        (folder/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    result=phase_continuation(x_start,p_start,guess_start,span,steps,evaluate,max_iterations=max_iterations,
        checkpoint=checkpoint,start_stage=start_stage,**resume_options)
    if hashes!={f:sha256((root/f).read_bytes()).hexdigest() for f in refs}:raise RuntimeError('owner changed during phase continuation')
    stages=result['applications'];apps=[s['application'] for s in stages]
    contacts=[discrete_action_cotangents(a,result['step']) for a in apps]
    conormals=[pointwise_wall_gauge_conormal(P@a['midpoint_coefficients'],rep)['radial_action_covector'] for a in apps]
    arrays=dict(initial_raw=raw,initial_master=eta0,initial_p=p0,x_final=result['x_final'],p_final=result['p_final'],
        stage_indices=np.array([s['stage'] for s in stages]),
        stage_unknowns=np.array([s['unknowns'] for s in stages]),stage_midpoint_raw=np.array([P@a['midpoint_coefficients'] for a in apps]),
        stage_residual=np.array([a['residual'] for a in apps]),stage_row_scale=np.array([s['row_scale'] for s in stages]),
        stage_jacobian=np.array([a['jacobian'] for a in apps]),
        stage_initial_face=np.array([c['initial_face'] for c in contacts]),stage_final_face=np.array([c['final_face'] for c in contacts]),
        material_wall_conormals=np.array(conormals))
    for k,s in enumerate(stages):
        if s['records']:
            for name in s['records'][0]:
                arrays[f'stage_{s["stage"]:04d}_iteration_{name}']=np.array([r[name] for r in s['records']])
    _compressed_npz(out/'application.npz',arrays)
    md=dict(scope='EVALUATED_FULL_ASSIGNED_ACTION_PHASE_CONTINUATION',side=side,span=span,steps=steps,
        completed_steps=result['completed_steps'],resumed_stage=start_stage,resumed_checkpoint_sha256=resume_sha,
        actual_canonical_momentum_carried=True,
        stages=[dict(status=s['status'],scaled_residual=s['scaled_residual'],history=s['history']) for s in stages],
        finite_euler_norms=[float(np.linalg.norm(a['finite_dynamic_euler'])) for a in apps],
        constraint_norms=[float(np.linalg.norm(a['algebraic_constraint'])) for a in apps],
        canonical_initial_contact_defects=[float(np.linalg.norm(c['initial_face']+s['incoming_p'])) for c,s in zip(contacts,stages)],
        canonical_final_contact_defects=[float(np.linalg.norm(c['final_face']-a['p_new'])) for c,a in zip(contacts,apps)],
        wall_conormal_norms=[float(np.linalg.norm(c)) for c in conormals],
        action_parameters=params,radial_points=radial_points,cap_points=cap_points,input_hashes=hashes,
        consumed_receipt_sha256=rhash,consumed_coefficients_sha256=receipt['numerical_sha256'],
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        numerical_rank_not_physical_gauge_count=True,regularizing_shift=0.,all_multiplier_and_Gauss_rows_retained=True,
        physical_unit_equation='GF=cF[common charged-current action]/E_kappa^2 remains shared equation',
        unassigned_area_equation='gamma=alpha_FSC*ell_current^(-m); omitted assigned value is not gamma0',
        temporal_scope='incoming23 past / outgoing24 future from common E1; finite numerical span, not full E0/child history',
        wall_scope='represented free wall trial equations; actual conormals retained, complementary interface not selected',
        physical_birth_formation_closed=False,physical_native_heat_closed=False,physical_Pauli_value=False,
        error_scope='binary64 finite action and analytic Newton Jacobian; no continuum, producer-rounding or physical-event certificate')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--initial-application',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--side',choices=('incoming','outgoing'),required=True)
    p.add_argument('--span',type=float,required=True);p.add_argument('--steps',type=int,required=True)
    p.add_argument('--radial-points',type=int,default=48);p.add_argument('--cap-points',type=int,default=48)
    p.add_argument('--max-iterations',type=int,default=10);p.add_argument('--resume-checkpoint',type=Path);a=p.parse_args()
    print(json.dumps(materialize_phase_continuation(a.initial_application,a.output,side=a.side,span=a.span,steps=a.steps,
        radial_points=a.radial_points,cap_points=a.cap_points,max_iterations=a.max_iterations,resume_checkpoint=a.resume_checkpoint),sort_keys=True))
