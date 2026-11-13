"""Nonlinear full-action midpoint continuation of the two E1 arm germs.

Every iterate executes the literal cap, independent Maxwell and material
Higgs action on its same raw228 vector. Gauss and multiplier equations
remain algebraic. An implicit step avoids an instantaneous Legendre
inverse and does not assume zero accelerations or multiplier rates.
The finite arm length and radial wall representation are numerical;
their action cotangents are retained without declaring a physical wall
ensemble, an E0 history, formation solution or native Pauli value.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import (
    ROOT, SOURCE_RECEIPTS, correction_representation, _deterministic_npz,
)
from .muon_pointwise_full_field_action import pointwise_full_field_action, pointwise_wall_gauge_conormal
from .muon_parent_mean_causal_action import mean_coordinate_lift


def nonlinear_midpoint_rows(unknowns, x0, p0, step, action_evaluator):
    """Action-generated x/p/Legendre/Gauss equations and exact Jacobian."""
    x0=np.asarray(x0,float);p0=np.asarray(p0,float);n=len(x0);z=np.asarray(unknowns,float)
    m=len(z)-3*n
    if n<1 or p0.shape!=(n,) or m<1 or not np.isfinite(step) or step==0:
        raise ValueError('paired phase and nonzero oriented coordinate-time step required')
    x,p,v,y=z[:n],z[n:2*n],z[2*n:3*n],z[3*n:]
    eta=np.r_[(x0+x)/2,v,y];a=action_evaluator(eta);G=a['gradient'];H=a['hessian']
    if G.shape!=(2*n+m,) or H.shape!=(2*n+m,2*n+m):
        raise ValueError('same complete x/v/y action gradient and Hessian required')
    r=np.r_[x-x0-step*v,p-p0-step*G[:n],G[n:2*n]-(p0+p)/2,G[2*n:]]
    J=np.zeros((3*n+m,3*n+m));J[:n,:n]=np.eye(n);J[:n,2*n:3*n]=-step*np.eye(n)
    J[n:2*n,:n]=-step/2*H[:n,:n];J[n:2*n,n:2*n]=np.eye(n)
    J[n:2*n,2*n:]= -step*H[:n,n:]
    J[2*n:3*n,:n]=H[n:2*n,:n]/2;J[2*n:3*n,n:2*n]=-np.eye(n)/2
    J[2*n:3*n,2*n:]=H[n:2*n,n:]
    J[3*n:,:n]=H[2*n:,:n]/2;J[3*n:,2*n:]=H[2*n:,n:]
    return dict(residual=r,jacobian=J,midpoint_coefficients=eta,action=a,
        finite_dynamic_euler=(p-p0)/step-G[:n],finite_legendre=r[2*n:3*n],algebraic_constraint=r[3*n:],
        x_new=x,p_new=p,v_mid=v,y_mid=y,instantaneous_Legendre_inverse_used=False)


def solve_nonlinear_midpoint(eta0, step, action_evaluator, *, max_iterations=10,
        tolerance=2e-9, checkpoint=None, initial_unknowns=None, row_scale=None,
        iteration_offset=0,rank_tolerance=1e-12):
    """Damped same-action Newton, retaining all rows and null projections."""
    eta0=np.asarray(eta0,float);base=action_evaluator(eta0);n=base['Lxx'].shape[0]
    x0=eta0[:n];v0=eta0[n:2*n];p0=base['gradient'][n:2*n];y0=eta0[2*n:]
    z=np.r_[x0+step*v0,p0+step*base['gradient'][:n],v0,y0] if initial_unknowns is None else np.array(initial_unknowns,float,copy=True)
    current=nonlinear_midpoint_rows(z,x0,p0,step,action_evaluator)
    scale=1/np.maximum(np.max(abs(current['jacobian']),axis=1),1.) if row_scale is None else np.asarray(row_scale,float)
    history=[];status='MAXIMUM_ITERATIONS';records=[]
    if checkpoint is not None:checkpoint(iteration_offset,z,current,scale,history,'INITIAL_OR_RESUMED',z)
    for index in range(max_iterations):
        r=current['residual'];J=current['jacobian'];norm=float(np.linalg.norm(scale*r))
        if norm<tolerance:status='REPRESENTED_MIDPOINT_TOLERANCE';break
        RJ=scale[:,None]*J;col=1/np.maximum(np.max(abs(RJ),axis=0),np.finfo(float).tiny)
        balanced=RJ*col[None,:];U,s,V=np.linalg.svd(balanced,full_matrices=True)
        keep=s>rank_tolerance*max(s);correction=-col*(V[keep].T@((U[:,keep].T@(scale*r))/s[keep]))
        trials=[];accepted=False
        for k in range(18):
            damping=2.**(-k);candidate_z=z+damping*correction
            try:
                candidate=nonlinear_midpoint_rows(candidate_z,x0,p0,step,action_evaluator)
                newnorm=float(np.linalg.norm(scale*candidate['residual']));good=np.isfinite(newnorm) and newnorm<norm
            except (ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError):newnorm=None;good=False
            trials.append(dict(damping=damping,scaled_residual=newnorm,accepted=bool(good)))
            if good:accepted=True;break
        history.append(dict(iteration=iteration_offset+index,scaled_residual=norm,rank=int(sum(keep)),
            rank_tolerance=rank_tolerance,damping_history=trials,
            linearized_scaled_residual=float(np.linalg.norm(scale*(J@correction+r))),
            omitted_left_projection_norm=float(np.linalg.norm(U[:,~keep].T@(scale*r)))))
        records.append(dict(jacobian=J,linearization_unknowns=z.copy(),correction=correction,
            singular_values=s,left_vectors=U,right_vectors=V,column_scale=col,
            retained_singular_values=keep,left_source_projections=U.T@(scale*r)))
        if not accepted:status='DAMPING_STALL';break
        old=z.copy();z=candidate_z;current=candidate
        if checkpoint is not None:checkpoint(iteration_offset+index+1,z,current,scale,history,'ACCEPTED_STEP',old)
    if np.linalg.norm(scale*current['residual'])<tolerance:status='REPRESENTED_MIDPOINT_TOLERANCE'
    return dict(initial_action=base,initial_master_coefficients=eta0,initial_canonical=p0,
        unknowns=z,application=current,history=history,records=records,row_scale=scale,status=status,
        final_scaled_residual=float(np.linalg.norm(scale*current['residual'])),
        rank_is_numerical_step_not_physical_gauge_count=True,regularizing_shift=0.)


def endpoint_raw_from_assigned_application(source,side):
    """Bind actual corrected same-event states, without a field trace packet."""
    source=Path(source);raw=(source/'result.json').read_bytes();receipt=json.loads(raw)
    if sha256((source/'application.npz').read_bytes()).hexdigest()!=receipt['numerical_sha256']:
        raise ValueError('two-arm endpoint archive hash mismatch')
    if side not in ('incoming','outgoing'):raise ValueError('incoming/outgoing arm required')
    with np.load(source/'application.npz',allow_pickle=False) as f:
        if 'updated_states' in f:
            states=f['updated_states'];H=f['H_real'];Ht=f['H_rate']
            x=states[0 if side=='incoming' else 1]
        else:
            c=f['updated_coefficients'];k=0 if side=='incoming' else 1
            x=c[98*k:98*k+98];H=c[196+4*k:200+4*k];Ht=c[204+4*k:208+4*k]
    r=np.zeros(228);r[:98]=x;r[220:224]=H;r[224:228]=Ht
    # Independent fields are the recorded zero-gauge initializer, not a
    # proof of zero gauge Euler or a physical vacuum.
    return r,receipt,sha256(raw).hexdigest()


def materialize_midpoint(initial_application,output,*,side,step,repository=ROOT,
        max_iterations=10,radial_points=48,cap_points=48,resume_checkpoint=None):
    root=Path(repository);source=Path(initial_application);source=source if source.is_absolute() else root/source
    out=Path(output)
    if out.exists():raise FileExistsError('preserve earlier evidence; choose a new output directory')
    if (side=='incoming' and step>=0) or (side=='outgoing' and step<=0):raise ValueError('past incoming and future child step orientations required')
    raw,receipt,receipt_sha=endpoint_raw_from_assigned_application(source,side)
    rep=correction_representation(radial_points=radial_points,radial_order=2,cap_points=cap_points,
        include_wall_lift=True,include_scalar_mean=True)
    P=mean_coordinate_lift(rep['gauge_labels'])['lift'];eta0=P.T@raw
    if np.any(P@eta0!=raw):raise ValueError('raw fields must be in the exact x/v/y representation')
    params=receipt['action_parameters']
    def evaluate(eta):return pointwise_full_field_action(P@eta,rep,**params)
    refs=list(SOURCE_RECEIPTS)+['src/bhsm/interface/muon_pointwise_full_field_action.py',
        'src/bhsm/interface/muon_parent_mean_causal_action.py','src/bhsm/interface/muon_material_higgs_gauge_action.py',
        'src/bhsm/interface/muon_birth_coupled_primal_midpoint.py']
    hashes={p:sha256((root/p).read_bytes()).hexdigest() for p in refs};z=None;scale=None;offset=0;resume_sha=None
    if resume_checkpoint is not None:
        cp=Path(resume_checkpoint);cp=cp if cp.is_absolute() else root/cp;b=(cp/'result.json').read_bytes();cr=json.loads(b)
        if cr['input_hashes']!=hashes or cr['consumed_receipt_sha256']!=receipt_sha or cr['side']!=side or cr['step']!=step:
            raise ValueError('resume must preserve the exact action, endpoint and oriented step')
        if sha256((cp/'application.npz').read_bytes()).hexdigest()!=cr['numerical_sha256']:raise ValueError('checkpoint hash mismatch')
        with np.load(cp/'application.npz',allow_pickle=False) as f:z=f['unknowns'];scale=f['row_scale']
        offset=cr['accepted_iteration'];resume_sha=sha256(b).hexdigest()
    out.mkdir(parents=True)
    def checkpoint(index,unknowns,application,scale,history,status,linearization_point):
        folder=out/'checkpoints'/('accepted_'+str(index).zfill(4));folder.mkdir(parents=True)
        _deterministic_npz(folder/'application.npz',dict(unknowns=unknowns,residual=application['residual'],
            jacobian=application['jacobian'],jacobian_unknowns=unknowns,row_scale=scale,
            previous_linearization_unknowns=linearization_point,initial_master_coefficients=eta0,
            midpoint_raw_coefficients=P@application['midpoint_coefficients'],raw_hessian=application['action']['raw_hessian']))
        md=dict(scope='FULL_ASSIGNED_ACTION_REPRESENTED_MIDPOINT_CONTINUATION',status=status,accepted_iteration=index,
            side=side,step=step,radial_points=radial_points,cap_points=cap_points,action_parameters=params,
            input_hashes=hashes,consumed_receipt_sha256=receipt_sha,iteration_history=history,
            scaled_residual=float(np.linalg.norm(scale*application['residual'])),
            numerical_sha256=sha256((folder/'application.npz').read_bytes()).hexdigest(),
            resume_argv=['C:/Python314/python.exe','-m','bhsm.interface.muon_birth_coupled_primal_midpoint',
                '--initial-application',str(source),'--output','CHOOSE_NEW_OUTPUT_DIRECTORY',
                '--side',side,'--step',str(step),'--radial-points',str(radial_points),'--cap-points',str(cap_points),
                '--resume-checkpoint',str(folder),'--max-iterations',str(max_iterations)],
            resume_environment=dict(PYTHONPATH='src'),physical_two_arm_solution=False)
        (folder/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    result=solve_nonlinear_midpoint(eta0,step,evaluate,max_iterations=max_iterations,checkpoint=checkpoint,
        initial_unknowns=z,row_scale=scale,iteration_offset=offset)
    if hashes!={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}:raise RuntimeError('an owner changed during the continuation')
    app=result['application'];face=pointwise_wall_gauge_conormal(P@app['midpoint_coefficients'],rep)
    arrays=dict(initial_raw_coefficients=raw,initial_master_coefficients=eta0,initial_canonical=result['initial_canonical'],
        updated_unknowns=result['unknowns'],updated_residual=app['residual'],updated_jacobian=app['jacobian'],
        updated_midpoint_raw=P@app['midpoint_coefficients'],updated_action_gradient=app['action']['raw_gradient'],
        updated_action_hessian=app['action']['raw_hessian'],row_scale=result['row_scale'],
        temporal_parent_initial_canonical=result['initial_canonical'],temporal_other_face_canonical=app['p_new'],
        material_wall_conormal=face['radial_action_covector'],material_wall_conormal_geometry_derivative=face['geometry_derivative'])
    if result['records']:
        for key in result['records'][0]:arrays['iteration_'+key]=np.array([r[key] for r in result['records']])
    _deterministic_npz(out/'application.npz',arrays)
    md=dict(scope='EVALUATED_FULL_ASSIGNED_ACTION_NONLINEAR_MIDPOINT_COMPONENT',side=side,step=step,
        status=result['status'],iteration_history=result['history'],final_scaled_residual=result['final_scaled_residual'],
        finite_dynamic_euler_norm=float(np.linalg.norm(app['finite_dynamic_euler'])),
        finite_legendre_norm=float(np.linalg.norm(app['finite_legendre'])),
        algebraic_constraint_norm=float(np.linalg.norm(app['algebraic_constraint'])),
        multiplier_constraint_norm=float(np.linalg.norm(app['algebraic_constraint'][:24])),
        At_Gauss_constraint_norm=float(np.linalg.norm(app['algebraic_constraint'][24:])),
        scalar_dynamic_euler_norm=float(np.linalg.norm(app['finite_dynamic_euler'][86:90])),
        gauge_dynamic_euler_norm=float(np.linalg.norm(app['finite_dynamic_euler'][38:86])),
        normal_dynamic_euler=float(app['finite_dynamic_euler'][37]),
        wall_conormal_norm=float(np.linalg.norm(face['radial_action_covector'])),
        gauge_fields_and_Gauss_kept=True,scalar_and_mixed_action_kept=True,instantaneous_Legendre_inverse_used=False,
        regularizing_shift=0.,rank_is_numerical_step_not_physical_gauge_count=True,
        temporal_policy='birth t0; incoming negative step, outgoing positive step; finite continuation initializer, not E0 or full child history',
        wall_policy='all independent wall-lift trial coefficients retained in this finite action; actual face conormal exported; physical complementary return not selected',
        temporal_face_policy='canonical endpoint covectors retained; no artificial zero-Neumann temporal condition',
        scalar_body_source='local classical Grassmann bodyJ0; quantum/effective/native load not deleted or completed',
        physical_unit_equation='GF=cF[common charged-current action]/E_kappa^2 remains reached shared calibration equation',
        area_role='owned alpha_FSC*ell_current^(-m), not alpha_EM/fittedgamma0; parameter remains unassigned',
        action_parameters=params,radial_points=radial_points,cap_points=cap_points,
        input_hashes=hashes,consumed_receipt_sha256=receipt_sha,consumed_coefficients_sha256=receipt['numerical_sha256'],
        resumed_checkpoint_sha256=resume_sha,numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        physical_birth_formation_closed=False,physical_native_heat_closed=False,physical_Pauli_value=False,
        error_scope='binary64 exact analytic finite-action Jacobian; nonlinear residual and numerical singular-vector projections retained; temporal/radial discretization and physical-event errors not enclosed')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--initial-application',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--side',choices=('incoming','outgoing'),required=True);p.add_argument('--step',type=float,required=True)
    p.add_argument('--max-iterations',type=int,default=10);p.add_argument('--radial-points',type=int,default=48);p.add_argument('--cap-points',type=int,default=48)
    p.add_argument('--resume-checkpoint',type=Path);a=p.parse_args()
    print(json.dumps(materialize_midpoint(a.initial_application,a.output,side=a.side,step=a.step,
        max_iterations=a.max_iterations,radial_points=a.radial_points,cap_points=a.cap_points,resume_checkpoint=a.resume_checkpoint),sort_keys=True))
