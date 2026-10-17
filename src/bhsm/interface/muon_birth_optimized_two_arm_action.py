"""Checkpointed same-action endpoint/scalar birth initializer.

This is a restricted numerical initializer, with zero independent gauge
one-forms. Incoming23 and outgoing24 meet at t=0. Geometry, Higgs values,
rates, canonical densities and an initial U2 identification share one
vector. The latter is an unknown, never a prescribed physical identity.
The spatial metric/connection graph is enforced by a round-S3 isometry
and its constant fundamental bundle lift in this homogeneous component.
Full gauge Euler and formation equations are not discarded as solved.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.linalg import expm, expm_frechet

from .muon_birth_zero_gauge_geometry_action import zero_gauge_geometry_action
from .muon_birth_two_arm_assigned_action import same_action_attachment_momentum
from .muon_parent_gauge_geometry_correction import (
    ROOT, STATE_SOURCE, SOURCE_RECEIPTS, correction_representation, _deterministic_npz,
)
from .muon_birth_reset_evaluation import NORMALIZATION_SOURCE
from .aether_full_reset_action_jacobian import (
    _attachment_jacobian_at_order, _attachment_coordinates_at_order,
    _trace_jacobian_at_order, _symmetric_power,
)
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_intrinsic_scalar_birth_rows import scalar_birth_action_rows
from .muon_intrinsic_worldvolume_scalar_transport import su2_to_unit_quaternion
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet

# [parent98,child98,parentH4,childH4,parentHrate4,childHrate4,
#  parentp4,childp4,U2log4,log(numerical formation interval)].
SIZE = 225
FREE = np.r_[np.arange(37,98),np.arange(135,196),np.arange(196,SIZE)]


def _complex(a): return np.asarray(a)[:2]+1j*np.asarray(a)[2:]


def _map(start):
    m=np.zeros((4,SIZE));m[:,start:start+4]=np.eye(4);return m


def _argument(base, c, side):
    return dict(base,H_real=c[196+4*side:200+4*side],H_rate=c[204+4*side:208+4*side])


def _endpoint(state, argument):
    a=zero_gauge_geometry_action(state[:37],state[37:74],state[74:],**argument)
    rate=np.asarray(argument['H_rate'])
    energy=float(state[37:74]@a['gradient'][37:74]+rate@a['scalar_real_canonical_dual']-a['value'])
    return dict(action=a,energy=energy,canonical=same_action_attachment_momentum(state[:37],a))


def canonical_lift_variation(action, canonical, gradient_variation, hessian_variation):
    """Fixed-q derivative of K y=R and p=ell^T L_v, before inversion.

    Delta B=0 at this fixed geometric trace. The action third directional
    application supplies delta A and delta C. Differencing its coefficients
    does not difference two inverse lifts across a nearly singular locus.
    This formula is exact for the supplied coefficient variations.
    """
    dh=np.asarray(hessian_variation);dg=np.asarray(gradient_variation)
    dG=np.vstack((np.zeros((2,37)),dh[74:98,37:74]))
    dK=np.block([[dh[37:74,37:74],dG.T],[dG,np.zeros((26,26))]])
    K=canonical['saddle'];y=np.vstack((canonical['lift'],canonical['reaction']))
    scale=1/np.sqrt(np.max(abs(K),axis=1));balanced=scale[:,None]*K*scale[None,:]
    dy=scale[:,None]*np.linalg.solve(balanced,scale[:,None]*(-dK@y))
    return dict(momentum_variation=dy[:37].T@action['gradient'][37:74]+canonical['lift'].T@dg[37:74],
        lift_variation=dy[:37],differentiated_saddle_residual=K@dy+dK@y,
        inverse_lifts_differenced=False)


def homogeneous_identification(logarithm, variation=None):
    """Unknown U2 and an associated isometry, with exact graph orientation.

    If F_B(g)=Sg, its right-frame pushforward obeys E_i F_B=Ad_S(j_i)F_B.
    With U=central*S and equal mechanical lambda, F_B*A_child=U A_parent U^-1.
    This enforces this spatial graph parametrically. It selects no S/phase.
    The spatial Haar Jacobian is one because F_B is an isometry.
    """
    z=np.asarray(logarithm,float);gens=higgs_u2_real_representation()['complex_generators']
    if z.shape!=(4,):raise ValueError('four U2 identification unknowns required')
    L=np.einsum('i,ijk->jk',z,gens);Ls=np.einsum('i,ijk->jk',z[:3],gens[:3])
    U=expm(L);S=expm(Ls);j=np.sqrt(8)*gens[:3]
    rotated=np.einsum('ab,ibc,cd->iad',S,j,S.conj().T)
    O=np.einsum('iab,jab->ij',rotated.conj(),j).real/2
    Q=su2_to_unit_quaternion(S[None])
    out=dict(U=U,S=S,frame_rotation=O,child_point=Q,
        spatial_haar_jacobian=1.,initial_identification_selected=False)
    if variation is not None:
        dz=np.asarray(variation,float)
        dU=expm_frechet(L,np.einsum('i,ijk->jk',dz,gens),compute_expm=False)
        dS=expm_frechet(Ls,np.einsum('i,ijk->jk',dz[:3],gens[:3]),compute_expm=False)
        # Derivative of the linear inverse quaternion chart.
        dQ=np.column_stack((dS[None,0,0].real,-dS[None,0,1].imag,
            -dS[None,0,1].real,-dS[None,0,0].imag))
        out.update(U_variation=dU,child_point_variation=dQ)
    return out


def scalar_boundary_rows(c, direction=None):
    """Exact closed homogeneous IVP solution, consumed by the birth owner.

    In this zero-independent-gauge representation At_ref=0, b=0 and
    div_Haar b=0. Thus Q=Q0, J=1, U=U0, without selecting any U0.
    The interval remains an explicit unknown with a zero column in these
    rows. It needs the formation/clock equations, not an arbitrary fit.
    No ordinary scalar spatial derivative or transport image is projected
    away. The one-point quadrature is exact only for this homogeneous graph.
    """
    c=np.asarray(c,float);v=direction;ident=homogeneous_identification(c[220:224],None if v is None else v[220:224])
    length=float(np.exp(c[224]));times=np.array([-length,0.]);Q=ident['child_point']
    flow=dict(coefficients=c,coefficient_variation=v,times=times,
        material_points=np.repeat(Q[None],2,axis=0),
        bundle_transport=np.repeat(ident['U'][None,None],2,axis=0),haar_jacobian=np.ones((2,1)))
    if v is not None:
        flow.update(material_points_variation=np.repeat(ident['child_point_variation'][None],2,axis=0),
            bundle_transport_variation=np.repeat(ident['U_variation'][None,None],2,axis=0),haar_jacobian_variation=np.zeros((2,1)))
    def basis(side,points,coefficients,variation):
        B=np.zeros((len(points),2,4),complex);B[:,0,0]=1;B[:,1,1]=1;B[:,0,2]=1j;B[:,1,3]=1j
        r=dict(basis=B)
        if variation is not None:r.update(basis_variation=np.zeros_like(B),basis_spatial_derivatives=np.zeros((len(points),3,2,4),complex))
        return r
    def density(side,points,coefficients,variation):
        offset=0 if side=='parent' else 98;x=coefficients[offset:offset+98]
        R=intrinsic_m4_weight_jet(12,x[:37],x[37:74],x[74:])['R4'];r=dict(density=np.full(len(points),R.value**3))
        if variation is not None:r.update(density_variation=np.full(len(points),3*R.value**2*(R.gradient[:98]@variation[offset:offset+98])),density_spatial_derivatives=np.zeros((len(points),3)))
        return r
    r=scalar_birth_action_rows(transport=flow,parent_birth_points=np.array([[1.,0.,0.,0.]]),
        birth_parent_time=0.,birth_child_time=0.,quadrature=np.ones(1),basis_evaluator=basis,density_evaluator=density,
        parent_coefficient_map=_map(196),child_coefficient_map=_map(200),
        parent_momentum_coefficient_map=_map(212),child_momentum_coefficient_map=_map(216),
        parent_birth_points_variation=np.zeros((1,4)) if v is not None else None)
    r['identification']=ident;r['formation_interval_selected']=False
    return r


def optimized_coupled_rows(c, base_arguments, weights, normalization):
    """72 actual assigned endpoint/scalar birth and Legendre rows."""
    c=np.asarray(c,float)
    if c.shape!=(SIZE,) or not np.isfinite(c).all():raise ValueError('finite same-vector225 coefficients required')
    states=c[:196].reshape(2,98);args=[_argument(base_arguments,c,i) for i in range(2)]
    arms=[_endpoint(states[i],args[i]) for i in range(2)]
    B0=_attachment_jacobian_at_order(12,normalization);T=_trace_jacobian_at_order(12)
    D=np.vstack((T,B0[1]));W=_symmetric_power(D@np.diag(1/weights[:37]**2)@D.T,-.5);P=_symmetric_power(B0@B0.T,.5)
    trace=np.r_[T@(states[1,:37]-states[0,:37]),_attachment_coordinates_at_order(12,states[1,:37])[1]-_attachment_coordinates_at_order(12,states[0,:37])[1]]
    r=np.r_[arms[0]['action']['multiplier_constraints']/weights[74:],arms[0]['energy'],W@trace,
        arms[1]['action']['multiplier_constraints']/weights[74:],arms[1]['energy'],
        P@(arms[1]['canonical']['momentum']-arms[0]['canonical']['momentum'])]
    boundary=scalar_boundary_rows(c)
    legendre=np.r_[2*c[212:216]-arms[0]['action']['scalar_real_canonical_dual'],
        2*c[216:220]-arms[1]['action']['scalar_real_canonical_dual']]
    graph=[];gens=higgs_u2_real_representation()['complex_generators'];U=boundary['identification']['U'];O=boundary['identification']['frame_rotation']
    lam=[]
    for s in states:lam.append(intrinsic_m4_weight_jet(12,s[:37],s[37:74],s[74:])['mechanical_connection_lambda'].value)
    Ap=(lam[0]-1)*np.sqrt(8)*gens[:3];Ac=(lam[1]-1)*np.sqrt(8)*gens[:3]
    for i in range(3):graph.append(np.einsum('j,jab->ab',O[i],Ac)-U@Ap[i]@U.conj().T)
    return dict(residual=np.r_[r,boundary['residual'],legendre],arms=arms,scalar_birth=boundary,
        scalar_legendre=legendre,spatial_connection_graph_residual=np.array(graph),
        projector_normalization=P,physical_birth_solution=False,
        unrepresented_scalar_image=boundary['transport_application']['image_projection_residual'])


def optimized_coupled_jacobian(c, base_arguments, weights, normalization, base, *, difference_step=2e-5):
    """Same-action analytic C/E/scalar rows and implicit canonical lift.

    H enters the fixed-zero-gauge geometry only through |H|^2 and |Hdot|^2.
    Their chain rule reduces the canonical differencing to at most two
    scalar radial columns per arm. Action Hessian directional coefficients
    are differenced, then the saddle is differentiated before inversion.
    The q traces are fixed: only FREE columns are consumed by the solve.
    No physical Higgs orientation is chosen.
    """
    J=np.zeros((72,SIZE));steps=np.zeros(SIZE)
    for side in range(2):
        o=98*side;Hidx=np.r_[np.arange(196+4*side,200+4*side),np.arange(204+4*side,208+4*side)]
        a=base['arms'][side]['action'];fullg=np.r_[a['gradient'],a['scalar_coefficient_gradient']]
        fullh=np.block([[a['hessian'],a['geometry_scalar_hessian']],
            [a['geometry_scalar_hessian'].T,a['scalar_coefficient_hessian']]])
        indices=np.r_[np.arange(o,o+98),[-1,-1],Hidx];active=indices>=0
        row=0 if side==0 else 29
        J[row:row+24,indices[active]]=fullh[74:98,active]/weights[74:,None]
        e=c[o+37:o+74]@fullh[37:74]+c[204+4*side:208+4*side]@fullh[104:108]-fullg
        e[37:74]+=fullg[37:74];e[104:108]+=fullg[104:108]
        J[row+24,indices[active]]=e[active]
        J[64+4*side:68+4*side,indices[active]]=-fullh[104:108,active]
        J[64+4*side:68+4*side,212+4*side:216+4*side]+=2*np.eye(4)
        arg=_argument(base_arguments,c,side);s=c[o:o+98];sign=1 if side else -1;P=base['projector_normalization']
        for k in range(61):
            idx=o+37+k;eps=difference_step/max(weights[37+k],1e-100);steps[idx]=eps
            plus=s.copy();minus=s.copy();plus[37+k]+=eps;minus[37+k]-=eps
            pp=zero_gauge_geometry_action(plus[:37],plus[37:74],plus[74:],**arg)
            pm=zero_gauge_geometry_action(minus[:37],minus[37:74],minus[74:],**arg)
            dp=canonical_lift_variation(a,base['arms'][side]['canonical'],
                (pp['gradient']-pm['gradient'])/(2*eps),(pp['hessian']-pm['hessian'])/(2*eps))
            J[54:56,idx]=sign*P@dp['momentum_variation']
        for start,key in ((196+4*side,'H_real'),(204+4*side,'H_rate')):
            field=c[start:start+4];R=float(field@field)
            if R==0:continue  # exact derivative of a squared norm at zero
            eps=min(difference_step*max(1.,R),R/4);ap=dict(arg);am=dict(arg)
            ap[key]=field*np.sqrt((R+eps)/R);am[key]=field*np.sqrt((R-eps)/R)
            pp=zero_gauge_geometry_action(s[:37],s[37:74],s[74:],**ap)
            pm=zero_gauge_geometry_action(s[:37],s[37:74],s[74:],**am)
            dp=canonical_lift_variation(a,base['arms'][side]['canonical'],
                (pp['gradient']-pm['gradient'])/(2*eps),(pp['hessian']-pm['hessian'])/(2*eps))
            J[54:56,start:start+4]=sign*np.outer(P@dp['momentum_variation'],2*field)
            steps[start:start+4]=eps
    for k in np.r_[np.arange(196,204),np.arange(212,225)]:
        v=np.zeros(SIZE);v[k]=1;J[56:64,k]=scalar_boundary_rows(c,v)['residual_variation']
    return J,steps


def solve_checkpointed(c,evaluate,jacobian,weights,*,max_iterations=8,tolerance=2e-8,
        row_scale=None,checkpoint=None,iteration_offset=0,free_indices=FREE):
    """Damped residual Newton; save the accepted vector before continuing."""
    c=np.array(c,float,copy=True);w=np.asarray(weights,float);free=np.asarray(free_indices,int)
    if w.shape!=free.shape or len(np.unique(free))!=len(free) or np.any(w<=0):raise ValueError('positive weights for unique free coefficient indices required')
    current=evaluate(c);J,eps=jacobian(c,current)
    if row_scale is None:row_scale=1/np.maximum(np.max(abs(J[:,free]/w[None,:]),axis=1),1.)
    scale=np.asarray(row_scale,float);history=[];status='MAXIMUM_ITERATIONS';lastJ=J
    if checkpoint is not None:checkpoint(iteration_offset,c,current,J,eps,scale,history,'INITIAL_OR_RESUMED',c)
    for it in range(max_iterations):
        r=current['residual'];norm=float(np.linalg.norm(scale*r))
        if norm<tolerance:status='ASSIGNED_SCALAR_BIRTH_TOLERANCE';break
        if it:J,eps=jacobian(c,current)
        JW=scale[:,None]*J[:,free]/w[None,:];U,s,V=np.linalg.svd(JW,full_matrices=False);keep=s>1e-11*max(s)
        step=-(V[keep].T@((U[:,keep].T@(scale*r))/s[keep]))/w;accepted=False;trials=[]
        for k in range(16):
            damping=2.**(-k);candidate_c=c.copy();candidate_c[free]+=damping*step
            try:
                candidate=evaluate(candidate_c);newnorm=float(np.linalg.norm(scale*candidate['residual']));good=np.isfinite(newnorm) and newnorm<norm
            except (ValueError,FloatingPointError,np.linalg.LinAlgError,OverflowError):newnorm=None;good=False
            trials.append(dict(damping=damping,scaled_residual=newnorm,accepted=bool(good)))
            if good:accepted=True;break
        history.append(dict(iteration=iteration_offset+it,scaled_residual=norm,rank=int(sum(keep)),
            weighted_step_norm=float(np.linalg.norm(w*step)),damping_history=trials,
            linearized_scaled_residual=float(np.linalg.norm(scale*(J[:,free]@step+r)))))
        lastJ=J
        if not accepted:status='DAMPING_STALL';break
        linearization_point=c.copy();c=candidate_c;current=candidate
        if checkpoint is not None:checkpoint(iteration_offset+it+1,c,current,J,eps,scale,history,'ACCEPTED_STEP',linearization_point)
    if np.linalg.norm(scale*current['residual'])<tolerance:status='ASSIGNED_SCALAR_BIRTH_TOLERANCE'
    return dict(coefficients=c,application=current,jacobian=lastJ,row_scale=scale,history=history,status=status,
        free_indices=free,final_scaled_residual=float(np.linalg.norm(scale*current['residual'])))


def materialize_optimized_initializer(initial_application,output,*,repository=ROOT,max_iterations=8,resume_checkpoint=None,cap_points=48):
    root=Path(repository);source=Path(initial_application);out=Path(output)
    if not source.is_absolute():source=root/source
    if out.exists():raise FileExistsError('preserve earlier evidence; choose a new output directory')
    raw=(source/'result.json').read_bytes();receipt=json.loads(raw)
    if sha256((source/'application.npz').read_bytes()).hexdigest()!=receipt['numerical_sha256']:raise ValueError('endpoint source hash mismatch')
    with np.load(root/STATE_SOURCE,allow_pickle=False) as f:retained=f['state'];weights=f['state_weights']
    with np.load(source/'application.npz',allow_pickle=False) as f:
        child=np.r_[f['updated_q'],f['updated_qdot'],f['updated_m']];H=f['H_real'];Hrate=f['H_rate'];wall=f['wall_gauge']
    if np.any(wall):raise ValueError('this initializer requires its exact zero independent wall trace')
    rep=correction_representation(radial_points=48,radial_order=2,cap_points=cap_points)
    fields={k:np.zeros((48,1,3,5,4) if k=='gauge_angular' else (48,1,5,4)) for k in ('gauge','gauge_tau','gauge_rho','gauge_angular')}
    args=dict(rho=rep['rho'],radial_quadrature=rep['radial_quadrature'],fields=fields,wall_gauge=wall,
        lambda_H=rep['scalar_matching']['lambda_H'],cap_points=cap_points,**receipt['action_parameters'])
    with np.load(root/NORMALIZATION_SOURCE,allow_pickle=False) as f:normalization=f['normalization_coordinates']
    c=np.r_[retained[98:],child,H,H,Hrate,Hrate,np.zeros(8),np.zeros(4),np.log(.001)]
    from .muon_birth_homogeneous_identification_quotient import homogeneous_identification_slice
    quotient=homogeneous_identification_slice(c);c=quotient['coefficients'];free=quotient['free_indices']
    w=np.r_[weights,weights,np.ones(29)][free];scale=None;offset=0
    refs=list(SOURCE_RECEIPTS)+[NORMALIZATION_SOURCE,
        'src/bhsm/interface/muon_birth_coupled_constraint_retraction.py','src/bhsm/interface/muon_birth_two_arm_assigned_action.py',
        'src/bhsm/interface/muon_birth_zero_gauge_geometry_action.py','src/bhsm/interface/muon_birth_optimized_two_arm_action.py',
        'src/bhsm/interface/muon_birth_homogeneous_identification_quotient.py',
        'src/bhsm/interface/muon_intrinsic_scalar_birth_rows.py','src/bhsm/interface/muon_intrinsic_worldvolume_scalar_transport.py',
        'src/bhsm/interface/muon_material_higgs_gauge_action.py']
    hashes={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}
    resume_hash=None
    if resume_checkpoint is not None:
        cp=Path(resume_checkpoint);cp=cp if cp.is_absolute() else root/cp
        b=(cp/'result.json').read_bytes();cr=json.loads(b);resume_hash=sha256(b).hexdigest()
        if cr['input_hashes']!=hashes or cr['consumed_receipt_sha256']!=sha256(raw).hexdigest() or cr['cap_points']!=cap_points:raise ValueError('resume must preserve exact source/input/representation bindings')
        if sha256((cp/'application.npz').read_bytes()).hexdigest()!=cr['numerical_sha256']:raise ValueError('checkpoint byte hash mismatch')
        with np.load(cp/'application.npz',allow_pickle=False) as f:
            c=f['coefficients'];scale=f['row_scale']
            if not np.array_equal(f['free_indices'],free):raise ValueError('resume must preserve the same proved computational gauge slice')
        offset=cr['accepted_iteration']
    evaluate=lambda z:optimized_coupled_rows(z,args,weights,normalization)
    jac=lambda z,b:optimized_coupled_jacobian(z,args,weights,normalization,b)
    out.mkdir(parents=True)
    def checkpoint(iteration,cc,app,J,eps,scale,history,status,linearization_point):
        folder=out/'checkpoints'/('accepted_'+str(iteration).zfill(4));folder.mkdir(parents=True)
        _deterministic_npz(folder/'application.npz',dict(coefficients=cc,residual=app['residual'],last_jacobian=J,
            difference_steps=eps,row_scale=scale,free_indices=free,coefficient_weights=w,last_jacobian_coefficients=linearization_point,
            state_weights=weights,normalization_coordinates=normalization,
            action_gradients=np.array([a['action']['gradient'] for a in app['arms']]),
            action_hessians=np.array([a['action']['hessian'] for a in app['arms']]),
            connection_graph_residual=app['spatial_connection_graph_residual']))
        md=dict(scope='REDUCED_ASSIGNED_ENDPOINT_SCALAR_BIRTH_INITIALIZER',accepted_iteration=iteration,status=status,
            input_hashes=hashes,consumed_receipt_sha256=sha256(raw).hexdigest(),cap_points=cap_points,
            action_parameters=receipt['action_parameters'],lambda_H=args['lambda_H'],iteration_history=history,
            scaled_residual=float(np.linalg.norm(scale*app['residual'])),numerical_sha256=sha256((folder/'application.npz').read_bytes()).hexdigest(),
            last_jacobian_role='evaluated at saved last_jacobian_coefficients; accepted coefficients and residual are saved separately',
            resume_argv=['C:/Python314/python.exe','-m','bhsm.interface.muon_birth_optimized_two_arm_action',
                '--initial-application',str(source),'--output','CHOOSE_NEW_OUTPUT_DIRECTORY','--resume-checkpoint',str(folder),
                '--cap-points',str(cap_points),'--max-iterations',str(max_iterations)],
            resume_environment=dict(PYTHONPATH='src'),physical_birth_solution=False)
        (folder/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    initial=evaluate(c);result=solve_checkpointed(c,evaluate,jac,w,max_iterations=max_iterations,row_scale=scale,checkpoint=checkpoint,iteration_offset=offset,free_indices=free)
    if hashes!={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}:raise RuntimeError('an owner changed during the application')
    app=result['application'];arrays=dict(initial_coefficients=c,updated_coefficients=result['coefficients'],initial_residual=initial['residual'],
        updated_residual=app['residual'],last_jacobian=result['jacobian'],row_scale=result['row_scale'],coefficient_weights=w,free_indices=free,
        state_weights=weights,normalization_coordinates=normalization,
        updated_action_gradients=np.array([a['action']['gradient'] for a in app['arms']]),
        updated_action_hessians=np.array([a['action']['hessian'] for a in app['arms']]),
        updated_connection_graph_residual=app['spatial_connection_graph_residual'],
        updated_scalar_transport=app['scalar_birth']['transport_application']['trace_transport'],
        updated_scalar_image_remainder=app['unrepresented_scalar_image'])
    _deterministic_npz(out/'application.npz',arrays)
    md=dict(scope='EVALUATED_REDUCED_TWO_ARM_SCALAR_BIRTH_NEWTON_INITIALIZER',status=result['status'],iteration_history=result['history'],
        final_scaled_residual=result['final_scaled_residual'],updated_residual_norm=float(np.linalg.norm(app['residual'])),
        scalar_trace_momentum_norm=float(np.linalg.norm(app['residual'][56:64])),scalar_legendre_norm=float(np.linalg.norm(app['residual'][64:])),
        connection_graph_max=float(np.max(abs(app['spatial_connection_graph_residual']))),
        scalar_image_remainder_max=float(np.max(abs(app['unrepresented_scalar_image']))),
        unassigned_formation_interval_column_norm=float(np.linalg.norm(result['jacobian'][:,-1])),
        initial_identification_coordinates=result['coefficients'][220:224].tolist(),
        identification_gauge_slice='joint child coordinate g_old=S g_new and bundle U0_dagger; H/Hdot/p/connection transformed together',
        physical_initial_identification_selected=False,closed_holonomy_or_large_gauge_data_erased=False,
        temporal_arm_policy='incoming23[-L,0], outgoing24[0,L]; same E1 t0; germ/interval numerical, not physical history',
        pairing='2Re once; p complex density, Legendre real dual=2p; no second metric density',
        graph_scope='homogeneous equal-radius spatial isometry plus constant U2 lift; no general angular/domain closure',
        independent_gauge_scope='a=a_t=a_r=a_angular=0 restriction; full gauge Euler/mixed rows not assertedzero',
        action_parameters=receipt['action_parameters'],cap_points=cap_points,input_hashes=hashes,
        consumed_receipt_sha256=sha256(raw).hexdigest(),consumed_coefficients_sha256=receipt['numerical_sha256'],resumed_checkpoint_sha256=resume_hash,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        normal_formation_rows_closed=False,physical_birth_solution=False,physical_unit_assigned=False,physical_Pauli_contraction=False,
        area_role='gamma=alpha_FSC*ell_current^(-m) remains shared unknown; no gamma0/fitting or duplicate area attachment',
        remaining_action_equations='full independent gauge and continuation Euler/cotangents; total formation/clock/common-scale matching',
        error_scope='binary64 actual nonlinear residual; analytic scalar/C/E rows; centered action-Hessian directional coefficients and implicit saddle differentiation; no continuum/physical certificate')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--initial-application',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--resume-checkpoint',type=Path);p.add_argument('--max-iterations',type=int,default=8);p.add_argument('--cap-points',type=int,default=48)
    a=p.parse_args();print(json.dumps(materialize_optimized_initializer(a.initial_application,a.output,max_iterations=a.max_iterations,
        resume_checkpoint=a.resume_checkpoint,cap_points=a.cap_points),sort_keys=True))
