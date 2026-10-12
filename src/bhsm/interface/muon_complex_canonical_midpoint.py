"""Literal complex canonical midpoint equations with named action frames.

The action and its explicit coordinate-time callback are analytic.  No
Hilbert adjoint, real projection, or numerical spectral quotient enters
this continuation.  A stage may be used as canonical data only after all
original x/p/Legendre/Gauss equations satisfy the declared tolerance.
"""
from __future__ import annotations
import numpy as np


def complex_canonical_midpoint_rows(unknowns, x0, p0, step, evaluate):
    """Execute all original action equations at one complex midpoint."""
    x0=np.asarray(x0,complex);p0=np.asarray(p0,complex);z=np.asarray(unknowns,complex)
    n=len(x0);m=len(z)-3*n;h=complex(step)
    if n<1 or m<1 or p0.shape!=x0.shape or h==0 or not np.isfinite(h):
        raise ValueError('complete complex canonical pair and nonzero oriented step required')
    x,p,v,y=z[:n],z[n:2*n],z[2*n:3*n],z[3*n:]
    eta=np.r_[(x0+x)/2,v,y];a=evaluate(eta)
    G=np.asarray(a['gradient'],complex);H=np.asarray(a['hessian'],complex)
    if G.shape!=(2*n+m,) or H.shape!=(2*n+m,)*2 or not np.isfinite(G).all() or not np.isfinite(H).all():
        raise ValueError('same finite full analytic action gradient/Hessian required')
    r=np.r_[x-x0-h*v,p-p0-h*G[:n],G[n:2*n]-(p0+p)/2,G[2*n:]]
    J=np.zeros((len(z),len(z)),complex)
    J[:n,:n]=np.eye(n);J[:n,2*n:3*n]=-h*np.eye(n)
    J[n:2*n,:n]=-h*H[:n,:n]/2;J[n:2*n,n:2*n]=np.eye(n)
    J[n:2*n,2*n:]=-h*H[:n,n:]
    J[2*n:3*n,:n]=H[n:2*n,:n]/2;J[2*n:3*n,n:2*n]=-np.eye(n)/2
    J[2*n:3*n,2*n:]=H[n:2*n,n:]
    J[3*n:,:n]=H[2*n:,:n]/2;J[3*n:,2*n:]=H[2*n:,n:]
    return dict(residual=r,jacobian=J,midpoint_coefficients=eta,action=a,
                x_new=x,p_new=p,v_mid=v,y_mid=y,
                initial_action_cotangent=h*G[:n]/2-G[n:2*n],
                final_action_cotangent=h*G[:n]/2+G[n:2*n],
                algebraic_action_cotangent=h*G[2*n:])


def solve_complex_canonical_midpoint(x0,p0,eta_guess,step,evaluate,frame,*,
        tolerance=2e-10,max_iterations=12,checkpoint=None,initial_unknowns=None,
        frame_reference=None,start_reaction=None):
    """Direct bordered Newton retaining every original complex action row.

    ``frame`` acts on the original v/y coordinates, as in the retained
    constitutive application.  Reactions are exported in those exact
    Legendre/Gauss rows.  They are not silently discarded as gauge loads.
    """
    x0=np.asarray(x0,complex);p0=np.asarray(p0,complex);eta=np.asarray(eta_guess,complex)
    n=len(x0);C=np.asarray(frame['named_frame_covectors'],complex);nf=len(C)
    if p0.shape!=x0.shape or len(eta)<=2*n or not np.array_equal(eta[:n],x0) or C.shape!=(nf,len(eta)-n):
        raise ValueError('same full x/p/v/y initial chart and named action frame required')
    a0=evaluate(eta);h=complex(step)
    z=np.r_[x0+h*eta[n:2*n],p0+h*a0['gradient'][:n],eta[n:]] if initial_unknowns is None else np.asarray(initial_unknowns,complex).copy()
    frame_reference=eta[n:].copy()if frame_reference is None else np.asarray(frame_reference,complex).copy()
    rho=np.zeros(nf,complex)if start_reaction is None else np.asarray(start_reaction,complex).copy()
    if frame_reference.shape!=eta[n:].shape or rho.shape!=(nf,):
        raise ValueError('complete original named-frame reference/reaction required')
    F=np.zeros((nf,len(z)),complex);F[:,2*n:]=C
    # The corresponding dual enters only the original constitutive rows.
    E=np.zeros((len(z),nf),complex);E[2*n:]=C.T
    history=[];status='ITERATION_LIMIT'
    def app(z,rho):
        a=complex_canonical_midpoint_rows(z,x0,p0,h,evaluate)
        f=np.r_[a['residual']+E@rho,F@z-C@frame_reference]
        K=np.block([[a['jacobian'],E],[F,np.zeros((nf,nf),complex)]])
        return a,f,K
    a,f,K=app(z,rho)
    row_scale=1/np.maximum(np.max(abs(K),axis=1),1.)
    for iteration in range(max_iterations+1):
        merit=float(np.linalg.norm(row_scale*f));r=a['residual']
        record=dict(iteration=iteration,scaled_framed_residual=merit,
                    original_rows_max=float(np.max(abs(r))),
                    original_Gauss_multiplier_max=float(np.max(abs(r[3*n:]))),
                    named_frame_reaction_max=float(np.max(abs(rho))) if nf else 0.)
        history.append(record)
        if checkpoint is not None:checkpoint(iteration,z,rho,a,f,K,row_scale,history)
        if merit<=tolerance and np.max(abs(r))<=tolerance:
            status='ALL_ORIGINAL_COMPLEX_CANONICAL_ROWS_TOLERANCE';break
        if iteration==max_iterations:break
        col=1/np.maximum(np.max(abs(row_scale[:,None]*K),axis=0),np.finfo(float).tiny)
        B=row_scale[:,None]*K*col[None,:]
        dz=col*np.linalg.solve(B,-row_scale*f)
        record['balanced_condition_number']=float(np.linalg.cond(B))
        record['linearized_original_bordered_residual_max']=float(np.max(abs(K@dz+f)))
        accepted=False;trials=[]
        for j in range(18):
            damping=2.**(-j);zt=z+damping*dz[:-nf] if nf else z+damping*dz
            rt=rho+damping*dz[-nf:] if nf else rho
            try:
                at,ft,Kt=app(zt,rt);new=float(np.linalg.norm(row_scale*ft));good=np.isfinite(new) and new<merit
            except (ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError):new=None;good=False
            trials.append(dict(damping=damping,scaled_framed_residual=new,accepted=bool(good)))
            if good:accepted=True;break
        record['trials']=trials
        if not accepted:status='LINE_SEARCH_STALL';break
        z,rho,a,f,K=zt,rt,at,ft,Kt
    return dict(status=status,unknowns=z,frame_reactions=rho,application=a,
                framed_rows=f,framed_Jacobian=K,row_scale=row_scale,history=history,
                incoming_x=x0,incoming_p=p0,step=h,original_frame_reference=frame_reference,
                actual_canonical_momentum_carried=True,
                original_rows_deleted=0,numerical_spectral_quotient_used=False,
                physical_stop_or_exterior_selected=False)
