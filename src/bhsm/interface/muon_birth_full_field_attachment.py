"""Same-action full-field constraint-admissible attachment cotangent.

The inherited two geometric attachment coordinates are unchanged.  The
velocity form and annihilated constraint derivatives include every
represented dynamic field and multiplier/Gauss row.  Saddle stationarity
is used without an inverse-A or positive-minimum assumption.  The
directional derivative uses one saddle adjoint, preserving its reactions.
"""
from __future__ import annotations
import numpy as np

from .aether_full_reset_action_jacobian import _attachment_jacobian_at_order
from .aether_canonical_momentum_action_jacobian import _attachment_action_derivatives


def constrained_attachment_lift(action,boundary,*,dynamic_count,algebraic_count):
    g=np.asarray(action['gradient'],float);h=np.asarray(action['hessian'],float)
    n=dynamic_count;m=algebraic_count;B=np.asarray(boundary,float)
    if g.shape!=(2*n+m,) or h.shape!=(len(g),len(g)) or B.shape!=(2,n):
        raise ValueError('one same-action x/v/y jet and inherited two-coordinate boundary required')
    A=h[n:2*n,n:2*n];C=h[2*n:,n:2*n];G=np.vstack((B,C))
    K=np.block([[A,G.T],[G,np.zeros((m+2,m+2))]])
    rhs=np.zeros((len(K),2));rhs[n:n+2]=np.eye(2)
    rows=np.max(abs(K),axis=1)
    if np.any(rows==0):raise np.linalg.LinAlgError('unbound full-field saddle direction')
    scale=1/np.sqrt(rows);balanced=scale[:,None]*K*scale[None,:]
    solve=lambda r:scale[:,None]*np.linalg.solve(balanced,scale[:,None]*np.asarray(r))
    solution=solve(rhs);dual_rhs=np.r_[g[n:2*n],np.zeros(m+2)][:,None];adjoint=solve(dual_rhs)[:,0]
    lift=solution[:n];reaction=solution[n:]
    return dict(momentum=lift.T@g[n:2*n],lift=lift,reaction=reaction,saddle=K,
        saddle_solution=solution,adjoint=adjoint,row_scale=scale,
        saddle_residual=K@solution-rhs,adjoint_residual=K@adjoint-dual_rhs[:,0],
        boundary_lift_residual=B@lift-np.eye(2),constraint_annihilation=C@lift,
        balanced_condition_number=float(np.linalg.cond(balanced)),
        boundary=B,constraint_velocity=C,velocity_gradient=g[n:2*n],dynamic_count=n,algebraic_count=m,
        stationarity_not_positive_minimization=True,regularizing_shift=0.)


def attachment_momentum_variation(base,delta_gradient,delta_hessian,*,delta_boundary=None):
    """Exact implicit saddle derivative for supplied same-action first jets."""
    n=base['dynamic_count'];m=base['algebraic_count'];dg=np.asarray(delta_gradient,float);dh=np.asarray(delta_hessian,float)
    if dg.shape!=(2*n+m,) or dh.shape!=(len(dg),len(dg)):raise ValueError('same x/v/y action variation required')
    db=np.zeros((2,n)) if delta_boundary is None else np.asarray(delta_boundary,float)
    if db.shape!=(2,n):raise ValueError('same inherited attachment derivative required')
    dc=dh[2*n:,n:2*n];dG=np.vstack((db,dc));dK=np.block([[dh[n:2*n,n:2*n],dG.T],[dG,np.zeros((m+2,m+2))]])
    rhs=-dK@base['saddle_solution'];sc=base['row_scale'];K=base['saddle']
    ds=sc[:,None]*np.linalg.solve(sc[:,None]*K*sc[None,:],sc[:,None]*rhs)
    direct=ds[:n].T@base['velocity_gradient']+base['lift'].T@dg[n:2*n]
    adjoint=base['lift'].T@dg[n:2*n]-base['adjoint']@dK@base['saddle_solution']
    return dict(momentum_variation=adjoint,direct_variation=direct,
        direct_adjoint_difference=direct-adjoint,saddle_solution_variation=ds,
        derivative_saddle_residual=K@ds+dK@base['saddle_solution'])


def inherited_full_field_boundary(q,dynamic_count,master_count):
    """Inherited B/DB, padded into the same full-field dynamic coordinates."""
    B=np.zeros((2,dynamic_count));B[:,:37]=_attachment_jacobian_at_order(12,q)
    db=np.zeros((master_count,2,dynamic_count))
    db[:,:,:37]=_attachment_action_derivatives(12,np.asarray(q),np.ones(master_count))
    return B,db


def attachment_momentum_cotangent(eta,action_evaluator,boundary,boundary_derivatives,*,
        dynamic_count,algebraic_count,difference_step=2e-5,coordinate_weights=None,base_action=None):
    """Adjoint derivative via four directional Hessian applications.

    D3S[a_v+a_y,ell_v+mu_y,.] minus D3S[a_y,mu_y,.]
    gives the complete dK contraction; the inherited B derivatives are
    added separately.  Hessian symmetry supplies every coefficient
    derivative from a direction along the common adjoint.  Centered
    differences have a caller-visible step and are not a rigorous bound.
    """
    eta=np.asarray(eta,float);n=dynamic_count;m=algebraic_count
    action=action_evaluator(eta) if base_action is None else base_action
    base=constrained_attachment_lift(action,boundary,dynamic_count=n,algebraic_count=m)
    weights=np.ones(len(eta)) if coordinate_weights is None else np.asarray(coordinate_weights,float)
    db=np.asarray(boundary_derivatives,float)
    if weights.shape!=eta.shape or np.any(weights<=0) or db.shape!=(len(eta),2,n) or difference_step<=0:
        raise ValueError('positive same-coordinate weights, DB and difference step required')
    a=base['adjoint'];ell=base['lift'];mu=base['reaction']
    av=np.zeros(len(eta));av[n:2*n]=a[:n];av[2*n:]=a[n+2:]
    ay=np.zeros(len(eta));ay[2*n:]=a[n+2:]
    b=np.zeros((len(eta),2));b[n:2*n]=ell;b[2*n:]=mu[2:]
    by=np.zeros_like(b);by[2*n:]=mu[2:]
    directions=[]
    def derivative(direction):
        magnitude=float(np.max(abs(weights*direction)))
        if magnitude==0:return np.zeros_like(action['hessian'])
        unit=direction/magnitude
        p=action_evaluator(eta+difference_step*unit)['hessian'];q=action_evaluator(eta-difference_step*unit)['hessian']
        directions.append(dict(direction=direction,unit_direction=unit,restored_magnitude=magnitude,step=difference_step))
        return magnitude*(p-q)/(2*difference_step)
    third=derivative(av)@b-derivative(ay)@by
    contact=np.empty((len(eta),2))
    for k in range(len(eta)):
        contact[k]=a[:n]@db[k].T@mu[:2]+a[n:n+2]@db[k]@ell
    cotangent=(action['hessian'][n:2*n].T@ell-third-contact).T
    return dict(momentum=base['momentum'],cotangent=cotangent,base=base,
        third_action_contraction=third.T,boundary_contact=contact.T,
        directional_hessian_applications=directions,difference_step=difference_step,
        derivative_error_scope='centered directional binary64 Hessian differences; no rigorous rounding or continuum bound')
