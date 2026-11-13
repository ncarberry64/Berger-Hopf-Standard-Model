"""Same-event two-arm assigned action rows and numerical initialization.

Incoming23 ends at t=0; outgoing24 begins there. The local arm lengths are
numerical representations, never an E0 history or a physical duration.
This application uses the actual assigned action on both regular arms.
Its attachment momenta use that action's constraint-admissible Hessian lift.
The retained ordered velocity eigenline is exported only as a diagnostic;
it is not the total normal formation operator or a selected muon mode.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import legval,legder

from .muon_birth_coupled_constraint_retraction import pointwise_assigned_action
from .muon_parent_gauge_geometry_correction import (
    ROOT,STATE_SOURCE,SOURCE_RECEIPTS,correction_representation,_deterministic_npz,
)
from .aether_full_reset_action_jacobian import (
    _attachment_jacobian_at_order,_attachment_coordinates_at_order,
    _trace_jacobian_at_order,_symmetric_power,
)


def two_arm_time_jet(time,length,order,side):
    """bP_k with its coordinate-time derivative on the correctly oriented arm."""
    if side not in ('incoming','outgoing') or length<=0 or type(order) is not int or order<1:
        raise ValueError('positive length/order and incoming/outgoing arm required')
    t=np.asarray(time,float);u=(t+length)/length if side=='incoming' else t/length
    if np.any(u<0) or np.any(u>1):raise ValueError('time outside the declared oriented arm')
    b=16*u*u*(1-u)**2;bt=32*u*(1-u)*(1-2*u)/length;x=2*u-1
    values=[];rates=[]
    for k in range(order):
        c=np.zeros(k+1);c[-1]=1.;p=legval(x,c)
        values.append(b*p);rates.append(bt*p+2*b*legval(x,legder(c))/length)
    return np.stack(values,axis=-1),np.stack(rates,axis=-1)


def same_action_attachment_momentum(q,action):
    """Solve the owned lift stationarity equations without an A^-1 assumption.

    G=[B;L_mv], G ell=[I2;0].  A ell+G^T mu=0 is algebraically the
    retained A^-1 compliance formula whenever those two inverses exist.
    The saddle solve handles an individually singular A only when the
    complete constrained saddle remains nonsingular. No shift is added.
    """
    h=action['hessian'];A=h[37:74,37:74];C=h[74:98,37:74]
    B=_attachment_jacobian_at_order(12,q);G=np.vstack((B,C))
    target=np.zeros((26,2));target[:2]=np.eye(2)
    K=np.block([[A,G.T],[G,np.zeros((26,26))]])
    rhs=np.vstack((np.zeros((37,2)),target))
    row=np.max(abs(K),axis=1)
    if np.any(row==0):raise np.linalg.LinAlgError('unbound lift saddle direction')
    scale=1/np.sqrt(row);balanced=scale[:,None]*K*scale[None,:]
    solution=scale[:,None]*np.linalg.solve(balanced,scale[:,None]*rhs)
    lift=solution[:37];reaction=solution[37:]
    return dict(momentum=lift.T@action['gradient'][37:74],lift=lift,reaction=reaction,
        saddle=K,saddle_residual=K@solution-rhs,
        boundary_lift_residual=B@lift-np.eye(2),constraint_annihilation=C@lift,
        balanced_condition_number=float(np.linalg.cond(balanced)),
        velocity_form_eigenvalues=np.linalg.eigvalsh((A+A.T)/2),
        stationarity_not_positive_minimization=True,regularizing_shift=0.)


def assigned_arm_endpoint(state,action_arguments,branch_reference):
    """Actual endpoint C, fixed-field canonical energy and attachment dual."""
    x=np.asarray(state,float)
    if x.shape!=(98,):raise ValueError('one q37/v37/m24 endpoint required')
    # The current initializer has zero independent gauge temporal rate.
    # A general rate needs its literal Maxwell canonical dual, not an
    # omitted term silently treated as zero.
    if np.any(action_arguments['fields']['gauge_tau']):
        raise ValueError('this finite endpoint initializer requires its recorded zero independent gauge rate')
    app=pointwise_assigned_action(x[:37],x[37:74],x[74:],**action_arguments)
    Hrate=np.asarray(action_arguments['H_rate'])
    energy=float(x[37:74]@app['gradient'][37:74]
        +action_arguments.get('normal_rate',0)*app['gradient'][99]
        +Hrate@app['scalar_real_canonical_dual']-app['value'])
    p=same_action_attachment_momentum(x[:37],app)
    values,vectors=np.linalg.eigh((app['hessian'][37:98,37:98]+app['hessian'][37:98,37:98].T)/2)
    index=int(np.argmax(abs(vectors.T@branch_reference)))
    return dict(action=app,energy=energy,canonical=p,
        ordered_velocity_diagnostic=dict(index=index,value=float(values[index]),
            overlap=float(abs(vectors[:,index]@branch_reference)),formation_criterion=False))


def two_arm_assigned_rows(states,arguments,state_weights,branch_reference,normalization_coordinates):
    """C/E/trace/canonical rows from both action applications at common E1.

    The finite common scalar trace is an explicit numerical restriction.
    No general U_H/Ad_w transport image or momentum-return remainder is
    discarded: this application does not assert those full-field rows are
    solved. The total birth/formation system must append their producer.
    """
    states=np.asarray(states,float)
    if states.shape!=(2,98) or len(arguments)!=2:raise ValueError('incoming and outgoing endpoints required')
    apps=[assigned_arm_endpoint(s,a,branch_reference) for s,a in zip(states,arguments)]
    weights=np.asarray(state_weights,float);B0=_attachment_jacobian_at_order(12,normalization_coordinates)
    T=_trace_jacobian_at_order(12);D=np.vstack((T,B0[1]))
    W=_symmetric_power(D@np.diag(1/weights[:37]**2)@D.T,-.5)
    P=_symmetric_power(B0@B0.T,.5)
    raw=np.r_[T@(states[1,:37]-states[0,:37]),
        _attachment_coordinates_at_order(12,states[1,:37])[1]-_attachment_coordinates_at_order(12,states[0,:37])[1]]
    canonical=P@(apps[1]['canonical']['momentum']-apps[0]['canonical']['momentum'])
    r=np.r_[apps[0]['action']['multiplier_constraints']/weights[74:],apps[0]['energy'],
        W@raw,apps[1]['action']['multiplier_constraints']/weights[74:],apps[1]['energy'],canonical]
    return dict(residual=r,arms=apps,raw_trace_attachment=raw,normalized_trace_attachment=W@raw,
        normalized_canonical_child_minus_parent=canonical,ordered_velocity_diagnostic=[a['ordered_velocity_diagnostic'] for a in apps],
        residual_scope='56 assigned C/E/trace/canonical rows; total normal formation and exact full-field transport not substituted',
        physical_birth_solution=False)


def _fixed_q_jacobian(states,arguments,weights,reference,normalization,base,*,difference_step=2e-5):
    """Analytic C/E rows, finite-difference same-action canonical lift rows."""
    J=np.zeros((56,122));steps=np.zeros(122)
    for side in range(2):
        s=states[side];a=base['arms'][side]['action'];offset=61*side;row=0 if side==0 else 29
        J[row:row+24,offset:offset+61]=a['hessian'][74:98,37:98]/weights[74:,None]
        # Here fixed Hrate and normalrate are zero in the actual binder.
        if np.any(arguments[side]['H_rate']) or arguments[side].get('normal_rate',0)!=0:
            raise ValueError('analytic initializer energy Jacobian presently binds zero recorded H/normal rates')
        E=s[37:74]@a['hessian'][37:74,37:98]-a['gradient'][37:98]
        E[:37]+=a['gradient'][37:74]
        J[row+24,offset:offset+61]=E
        P=_symmetric_power(_attachment_jacobian_at_order(12,normalization)@_attachment_jacobian_at_order(12,normalization).T,.5)
        for k in range(61):
            eps=difference_step/max(weights[37+k],1e-100);steps[offset+k]=eps
            plus=s.copy();minus=s.copy();plus[37+k]+=eps;minus[37+k]-=eps
            pp=assigned_arm_endpoint(plus,arguments[side],reference)['canonical']['momentum']
            pm=assigned_arm_endpoint(minus,arguments[side],reference)['canonical']['momentum']
            J[54:56,offset+k]=(1 if side else -1)*(P@((pp-pm)/(2*eps)))
    return J,steps


def initialize_two_arm_rows(states,arguments,weights,reference,normalization,*,max_iterations=6,tolerance=2e-8):
    """Minimum weighted actual residual correction; not a physical selector."""
    states=np.array(states,float,copy=True);initial=two_arm_assigned_rows(states,arguments,weights,reference,normalization)
    current=initial;history=[];records=[];w=np.tile(weights[37:],2)
    scale=1/np.maximum(np.max(abs(_fixed_q_jacobian(states,arguments,weights,reference,normalization,current)[0]/w),axis=1),1.)
    status='MAXIMUM_ITERATIONS'
    for it in range(max_iterations):
        r=current['residual'];norm=float(np.linalg.norm(scale*r))
        if norm<tolerance:status='ASSIGNED_TWO_ARM_TOLERANCE';break
        J,eps=_fixed_q_jacobian(states,arguments,weights,reference,normalization,current)
        JW=scale[:,None]*J/w[None,:];U,s,V=np.linalg.svd(JW,full_matrices=False);keep=s>1e-11*max(s)
        step=-(V[keep].T@((U[:,keep].T@(scale*r))/s[keep]))/w
        accepted=False;trials=[]
        for k in range(15):
            damping=2.**(-k);candidate_states=states.copy()
            candidate_states[:,37:]+=damping*step.reshape(2,61)
            try:
                candidate=two_arm_assigned_rows(candidate_states,arguments,weights,reference,normalization)
                newnorm=float(np.linalg.norm(scale*candidate['residual']));good=np.isfinite(newnorm) and newnorm<norm
            except (ValueError,FloatingPointError,np.linalg.LinAlgError,OverflowError):newnorm=None;good=False
            trials.append(dict(damping=damping,scaled_residual=newnorm,accepted=bool(good)))
            if good:accepted=True;break
        history.append(dict(iteration=it,scaled_residual=norm,rank=int(sum(keep)),damping_history=trials,
            weighted_step_norm=float(np.linalg.norm(w*step)),linearized_scaled_residual=float(np.linalg.norm(scale*(J@step+r)))))
        records.append(dict(jacobian=J,difference_steps=eps,residual=r,step=step,singular_values=s))
        if not accepted:status='DAMPING_STALL';break
        states=candidate_states;current=candidate
    if np.linalg.norm(scale*current['residual'])<tolerance:status='ASSIGNED_TWO_ARM_TOLERANCE'
    return dict(initial=initial,final=current,states=states,history=history,records=records,row_scale=scale,status=status,
        final_scaled_residual=float(np.linalg.norm(scale*current['residual'])),tolerance=tolerance)


def materialize_two_arm_initializer(initial_application,output,*,repository=ROOT,max_iterations=6):
    root=Path(repository);source=Path(initial_application);out=Path(output)
    if not source.is_absolute():source=root/source
    if out.exists():raise FileExistsError('preserve earlier evidence; choose a new output directory')
    raw=(source/'result.json').read_bytes();receipt=json.loads(raw)
    if sha256((source/'application.npz').read_bytes()).hexdigest()!=receipt['numerical_sha256']:raise ValueError('endpoint input hash mismatch')
    with np.load(root/STATE_SOURCE,allow_pickle=False) as f:
        retained=f['state'];weights=f['state_weights'];reference=f['branch_reference']
    with np.load(source/'application.npz',allow_pickle=False) as f:
        child=np.r_[f['updated_q'],f['updated_qdot'],f['updated_m']];H=f['H_real'];Hrate=f['H_rate'];wall=f['wall_gauge']
    if np.any(Hrate) or np.any(wall):raise ValueError('current binder consumes the recorded zero temporal field trace rates/independent wall gauge')
    rep=correction_representation(radial_points=48,radial_order=2,cap_points=48)
    fields=dict(gauge=np.zeros((48,1,5,4)),gauge_tau=np.zeros((48,1,5,4)),gauge_rho=np.zeros((48,1,5,4)),gauge_angular=np.zeros((48,1,3,5,4)))
    arg=dict(rho=rep['rho'],radial_quadrature=rep['radial_quadrature'],fields=fields,H_real=H,H_rate=Hrate,
        wall_gauge=wall,lambda_H=rep['scalar_matching']['lambda_H'],cap_points=48,**receipt['action_parameters'])
    states=np.array([retained[98:],child]);arguments=[arg.copy(),arg.copy()]
    from .muon_birth_reset_evaluation import NORMALIZATION_SOURCE
    with np.load(root/NORMALIZATION_SOURCE,allow_pickle=False) as f:normalization=f['normalization_coordinates']
    refs=list(SOURCE_RECEIPTS)+['src/bhsm/interface/muon_birth_coupled_constraint_retraction.py',
        'src/bhsm/interface/muon_material_higgs_gauge_action.py','src/bhsm/interface/muon_birth_two_arm_assigned_action.py',
        'src/bhsm/interface/aether_canonical_momentum_action_jacobian.py','src/bhsm/interface/aether_full_reset_action_jacobian.py',NORMALIZATION_SOURCE]
    hashes={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}
    result=initialize_two_arm_rows(states,arguments,weights,reference,normalization,max_iterations=max_iterations)
    if hashes!={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}:raise RuntimeError('an owner changed during two-arm application')
    arrays=dict(initial_states=states,updated_states=result['states'],initial_residual=result['initial']['residual'],
        updated_residual=result['final']['residual'],state_weights=weights,branch_reference=reference,normalization_coordinates=normalization,
        H_real=H,H_rate=Hrate,row_scale=result['row_scale'],
        updated_action_gradients=np.array([x['action']['gradient'] for x in result['final']['arms']]),
        updated_action_hessians=np.array([x['action']['hessian'] for x in result['final']['arms']]),
        updated_momentum_lifts=np.array([x['canonical']['lift'] for x in result['final']['arms']]),
        updated_lift_saddle_residuals=np.array([x['canonical']['saddle_residual'] for x in result['final']['arms']]),
        updated_lift_constraint_annihilations=np.array([x['canonical']['constraint_annihilation'] for x in result['final']['arms']]))
    if result['records']:
        for key in ('jacobian','difference_steps','residual','step','singular_values'):
            arrays['iteration_'+key]=np.array([r[key] for r in result['records']])
    out.mkdir(parents=True);_deterministic_npz(out/'application.npz',arrays)
    md=dict(scope='EVALUATED_REDUCED_TWO_ARM_ASSIGNED_ACTION_NEWTON_INITIALIZER',status=result['status'],iteration_history=result['history'],
        final_scaled_residual=result['final_scaled_residual'],tolerance=result['tolerance'],
        initial_residual_norm=float(np.linalg.norm(arrays['initial_residual'])),updated_residual_norm=float(np.linalg.norm(arrays['updated_residual'])),
        residual_groups=dict(incoming_C=list(range(24)),incoming_E=[24],trace_attachment=list(range(25,29)),outgoing_C=list(range(29,53)),outgoing_E=[53],canonical_jump=[54,55]),
        ordered_velocity_diagnostic=result['final']['ordered_velocity_diagnostic'],ordered_velocity_is_formation_criterion=False,
        formation_owner='covariant_bubble_interface_mechanics.build_payload.nucleation: total constrained normal H_form with gamma and event drive',
        temporal_arm_policy='incoming23[-L,0], outgoing24[0,L]; E1 both t0; no physical arm duration selected',
        scalar_trace_role='recorded finite common constant trace only; general U_H image/return producer is not replaced by identity or erased',
        scalar_gauge_full_transport_closed=False,total_formation_rows_closed=False,physical_birth_solution=False,
        area_role='owned alpha_FSC*ell_current^(-m) shared unknown; per-gamma application remains explicit, not fittedzero',
        action_parameters=receipt['action_parameters'],canonical_lift='same assigned A/C/B constrained saddle; no arbitrary regularizer',
        canonical_lift_conditions=[x['canonical']['balanced_condition_number'] for x in result['final']['arms']],
        energy_scope='assigned classical cap+Maxwell+H body action at recorded zero independent field rates; native effective load not included',
        physical_Pauli_contraction=False,physical_unit_assigned=False,input_hashes=hashes,
        consumed_receipt_sha256=sha256(raw).hexdigest(),consumed_coefficients_sha256=receipt['numerical_sha256'],
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        error_scope='binary64 actual nonlinear residual; C/E Jacobians analytic, canonical-lift Jacobian centered finite differences; no continuum or physical-event certificate')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--initial-application',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--max-iterations',type=int,default=6);a=p.parse_args()
    print(json.dumps(materialize_two_arm_initializer(a.initial_application,a.output,max_iterations=a.max_iterations),sort_keys=True))
