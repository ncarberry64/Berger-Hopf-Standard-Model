"""Warm balanced Newton on the original complex constitutive equations.

The original named frame reference and its reaction are explicit inputs.
This additive solver preserves the older producer bytes and all of its
stored applications.  Scaling changes the linear solve, never its source.
"""
from __future__ import annotations
import numpy as np


def warm_complex_constitutive_compatibility(eta,p0,evaluate,frame,*,
        frame_reference=None,start_reaction=None,max_iterations=12,
        tolerance=2e-10,checkpoint=None):
    eta=np.asarray(eta,complex).copy();p0=np.asarray(p0,complex);n=len(p0)
    C=np.asarray(frame['named_frame_covectors'],complex);Z=np.asarray(frame['literal_generators'],complex)
    reference=eta[n:].copy()if frame_reference is None else np.asarray(frame_reference,complex).copy()
    rho=np.zeros(len(C),complex)if start_reaction is None else np.asarray(start_reaction,complex).copy()
    if len(eta)<=2*n or C.shape!=(2,len(eta)-n)or Z.shape!=(len(eta)-n,2)or reference.shape!=eta[n:].shape or rho.shape!=(2,):
        raise ValueError('same complete x/Pi/v/y and explicit original named-frame reference required')
    fixed=eta[:n].copy();history=[];status='ITERATION_LIMIT'
    def app(e,r):
        a=evaluate(e);g=np.asarray(a['gradient'],complex);D=np.asarray(a['hessian'],complex)[n:,n:]
        original=np.r_[g[n:2*n]-p0,g[2*n:]]
        f=np.r_[original+C.T@r,C@(e[n:]-reference)]
        K=np.block([[D,C.T],[C,np.zeros((2,2),complex)]])
        if not np.isfinite(f).all()or not np.isfinite(K).all():raise ValueError('finite retained analytic chart required')
        return a,original,f,K
    a,r,f,K=app(eta,rho)
    # This merit scaling is fixed at the reached warm start, so line-search
    # descent and convergence are assessed in one declared norm.
    row_scale=1/np.maximum(np.max(abs(K),axis=1),1.)
    for iteration in range(max_iterations+1):
        merit=float(np.linalg.norm(row_scale*f));record=dict(iteration=iteration,
            scaled_framed_residual=merit,original_residual_max=float(np.max(abs(r))),
            original_momentum_rows_max=float(np.max(abs(r[:n]))),
            original_Gauss_multiplier_max=float(np.max(abs(r[n:]))),
            named_frame_residual_max=float(np.max(abs(f[-2:]))),
            named_frame_reaction_max=float(np.max(abs(rho))),
            literal_gauge_source_compatibility_max=float(np.max(abs(Z.T@r))),
            action_generator_image_max=float(np.max(abs(K[:-2,:-2]@Z))))
        history.append(record)
        if checkpoint is not None:checkpoint(iteration,eta,rho,a,r,f,K,row_scale,history)
        if np.max(abs(r))<=tolerance and np.max(abs(f))<=tolerance:
            status='ALL_ORIGINAL_COMPLEX_CONSTITUTIVE_ROWS_TOLERANCE';break
        if iteration==max_iterations:break
        col=1/np.maximum(np.max(abs(row_scale[:,None]*K),axis=0),np.finfo(float).tiny)
        balanced=row_scale[:,None]*K*col[None,:]
        correction=col*np.linalg.solve(balanced,-row_scale*f)
        record.update(balanced_condition_number=float(np.linalg.cond(balanced)),
            correction_norm=float(np.linalg.norm(correction)),
            linearized_original_bordered_residual_max=float(np.max(abs(K@correction+f))))
        accepted=False;trials=[]
        for j in range(20):
            damping=2.**(-j);trial=eta.copy();trial[n:]+=damping*correction[:-2];rt=rho+damping*correction[-2:]
            try:
                at,rr,ff,Kt=app(trial,rt);new=float(np.linalg.norm(row_scale*ff));good=np.isfinite(new)and new<merit
            except (ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError):new=None;good=False
            trials.append(dict(damping=damping,scaled_framed_residual=new,accepted=bool(good)))
            if good:accepted=True;break
        record['trials']=trials
        if not accepted:status='LINE_SEARCH_STALL';break
        eta,rho,a,r,f,K=trial,rt,at,rr,ff,Kt
    return dict(status=status,coefficients=eta,canonical_momentum_target=p0,action=a,
        original_constitutive_rows=r,framed_rows=f,framed_Jacobian=K,row_scale=row_scale,
        frame_reactions=rho,original_frame_reference=reference,history=history,
        fixed_position_defect=eta[:n]-fixed,literal_generator_image=K[:-2,:-2]@Z,
        literal_gauge_source_compatibility=Z.T@r,
        original_target_or_named_reference_changed=False,
        numerical_eigenvectors_or_pseudoinverse_used=False,
        physical_gauge_quotient_or_first_hit_selected=False)
