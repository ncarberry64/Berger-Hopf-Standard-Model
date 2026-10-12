"""Same-x/same-Pi complex constitutive correction with named gauge frames."""
from __future__ import annotations
import numpy as np
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_trace_enriched_charged_current_response import enriched_central_profiles
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation


def canonical_central_frame(raw,representation):
    """Literal two central temporal generators, including scalar velocity.

    These coefficient identities are action-owned. They are not chosen
    from small numerical eigenvectors. A named temporal At frame retains
    reactions and every original Legendre/Gauss/multiplier equation.
    """
    rep=representation;c=generic_coordinate_lift(rep['gauge_labels']);n,m=c['x_count'],c['y_count']
    profiles=enriched_central_profiles(rep);theta=profiles['theta_coefficients'];derivative=profiles['radial_derivative_coefficients']
    At=np.array([j for j,i in enumerate(c['At_indices'])if rep['gauge_labels'][i]['internal']==3])
    Ar=np.array([j for j,i in enumerate(c['dynamic_gauge_indices'])if rep['gauge_labels'][i]['field']=='A_rho'and rep['gauge_labels'][i]['internal']==3])
    if len(At)!=4 or len(Ar)!=4:raise ValueError('all original central radial gauge profiles required')
    Z=np.zeros((n+m,2),complex);Z[38+Ar]=derivative;Z[n+24+At]=theta
    wall=rep['wall_trace_map'][0,3,c['At_indices'][At]]@theta
    T=higgs_u2_real_representation()['real_generators'][3];H=np.asarray(raw,complex)[260:264]
    Z[n-4:n]=-np.outer(T@H,wall)
    C=np.zeros((2,n+m),complex);C[:,n+24+At]=theta.T
    return dict(literal_generators=Z,named_frame_covectors=C,
        generator_scope='delta Ar_dot=theta_r, delta At=theta, delta Hdot=-G_HY H theta_wall',
        exact_source_or_spectral_rows_deleted=False)


def complex_constitutive_compatibility(eta,p0,evaluate,frame,*,max_iterations=3,
                                      tolerance=2e-10,checkpoint=None):
    """Solve Lv=the actual supplied Pi, Ly=0 at the same retained x.

    All original equations are exported even if the named frame reaction
    is nonzero. No source is projected away and no mode is fitted. Failure
    to solve gives the actual residual and source compatibility, rather
    than silently changing initial momentum to Lv of a held velocity.
    """
    eta=np.asarray(eta,complex).copy();p0=np.asarray(p0,complex);n=len(p0)
    C=np.asarray(frame['named_frame_covectors'],complex);Z=np.asarray(frame['literal_generators'],complex)
    if len(eta)<=2*n or C.shape!=(2,len(eta)-n)or Z.shape!=(len(eta)-n,2):
        raise ValueError('same full x/v/y, actual Pi and named two-action frames required')
    fixed=eta[:n].copy();reference=eta[n:].copy();rho=np.zeros(2,complex);history=[];status='ITERATION_LIMIT'
    def app(e,rho):
        a=evaluate(e);g=np.asarray(a['gradient'],complex);D=np.asarray(a['hessian'],complex)[n:,n:]
        r=np.r_[g[n:2*n]-p0,g[2*n:]]
        framed=np.r_[r+C.T@rho,C@(e[n:]-reference)]
        K=np.block([[D,C.T],[C,np.zeros((2,2),complex)]])
        return a,r,framed,K
    for iteration in range(max_iterations+1):
        a,r,f,K=app(eta,rho);scale=1/np.maximum(np.max(abs(K),axis=1),1.)
        merit=float(np.linalg.norm(scale*f));record=dict(iteration=iteration,scaled_residual=merit,
            original_residual_max=float(np.max(abs(r))),original_Gauss_multiplier_max=float(np.max(abs(r[n:]))),
            action_generator_image_max=float(np.max(abs(K[:-2,:-2]@Z))),
            literal_gauge_source_compatibility_max=float(np.max(abs(Z.T@r))),
            named_frame_reaction_max=float(np.max(abs(rho))))
        history.append(record)
        if checkpoint is not None:checkpoint(iteration,eta,rho,a,r,f,K,history)
        if merit<=tolerance:status='FRAMED_CONSTITUTIVE_TOLERANCE';break
        if iteration==max_iterations:break
        col=1/np.maximum(np.max(abs(scale[:,None]*K),axis=0),np.finfo(float).tiny)
        balanced=scale[:,None]*K*col[None]
        dz=col*np.linalg.solve(balanced,-scale*f)
        record.update(balanced_condition_number=float(np.linalg.cond(balanced)),
            original_linearized_residual_max=float(np.max(abs(K@dz+f))))
        accepted=False;trials=[]
        for j in range(12):
            damping=2.**(-j);trial=eta.copy();trial[n:]+=damping*dz[:-2];rhot=rho+damping*dz[-2:]
            try:
                _,rr,ff,_=app(trial,rhot);new=float(np.linalg.norm(scale*ff));good=np.isfinite(new)and new<merit
            except (ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError):new=None;good=False
            trials.append(dict(damping=damping,scaled_residual=new,accepted=bool(good)))
            if good:accepted=True;break
        record['trials']=trials
        if not accepted:status='LINE_SEARCH_STALL';break
        eta,rho=trial,rhot
    a,r,f,K=app(eta,rho)
    return dict(status=status,coefficients=eta,canonical_momentum_target=p0,action=a,
        original_constitutive_rows=r,framed_rows=f,framed_Jacobian=K,frame_reactions=rho,
        literal_generator_image=K[:-2,:-2]@Z,literal_gauge_source_compatibility=Z.T@r,
        fixed_position_defect=eta[:n]-fixed,history=history,
        initial_momentum_recomputed_from_corrected_velocity=False,
        numerical_eigenvectors_or_pseudoinverse_used=False,
        physical_gauge_quotient_or_first_hit_selected=False)
