"""Moving proper-normal, gluing and clock contacts of a reached local trial.

This differentiates its actual coefficient trace maps, without identifying
the local frozen trial with a selected physical event-domain section.
"""
from __future__ import annotations
import numpy as np
from .muon_holomorphic_normal_geometry import _geometry_variables,_fields,_sqrt
from .muon_holomorphic_two_arm_reset import holomorphic_moving_trace
from .muon_complex_paired_normal_action import _balanced_solver


def proper_normal_trace_motion(raw,one_lift,raw_rate):
    x=np.asarray(raw,complex);P=np.asarray(one_lift,complex);rate=np.asarray(raw_rate,complex)[:100]
    q,v,m,delta,dr,wall,Cstar=_geometry_variables(x[:100]);F=_fields(12,q,v,m,wall)
    U=F['C']*(dr+F['beta'])/F['N'];root=_sqrt(1-U*U);factor=F['C']/root;lapse=F['N']*root
    tr=holomorphic_moving_trace(x);normal=factor.value*wall.gradient@P[:100,:106]
    normal_first=((factor.gradient@rate)*wall.gradient+factor.value*(wall.hessian@rate))@P[:100,:106]
    attachment=tr['attachment_first']@P[:100,:106]
    attachment_first=np.einsum('aij,j,ik->ak',tr['attachment_second'],rate,P[:100,:106],optimize=True)
    return dict(trace=np.vstack((attachment,normal)),trace_coordinate_time_first=np.vstack((attachment_first,normal_first)),
        lapse=lapse.value,lapse_coordinate_time_first=lapse.gradient@rate,
        wall_velocity=U.value,wall_velocity_coordinate_time_first=U.gradient@rate,
        prescribed_raw_coordinate_rate=rate)


def moving_frequency_trial(application,Hessian_time_first,trace_time_first,lapse_time_first):
    """Differentiate the exact bordered local trial, including moving rows.

    The coefficient-H time derivative, rather than the Euler contact
    polynomial, belongs here. Both effects are exported separately by the
    consumer. This derivative is not re-elimination of a variable operator.
    """
    from .muon_complex_paired_normal_action import analytic_frequency_polynomial
    a=application;K=a['bordered_polynomial'];d=len(a['action_polynomial'][0]);n=len(Hessian_time_first)-d
    dp=analytic_frequency_polynomial(Hessian_time_first,n);dT=np.asarray(trace_time_first,complex)
    if dT.shape!=a['normal_and_constraint_rows'].shape:raise ValueError('all normal/gluing/frame trace jets required')
    dK=np.zeros_like(K);dK[:,:d,:d]=dp;dK[0,:d,d:]=dT.T;dK[0,d:,:d]=dT
    solve,_=_balanced_solver(K[0]);right=a['right_taylor'];left=a['left_taylor'];dr=np.empty_like(right);dl=np.empty_like(left)
    for k in range(3):
        r=-sum(dK[j]@right[:,k-j]for j in range(k+1))-sum(K[j]@dr[:,k-j]for j in range(1,k+1))
        l=-sum(dK[j].T@left[:,k-j]for j in range(k+1))-sum(K[j].T@dl[:,k-j]for j in range(1,k+1))
        dr[:,k]=solve(r);dl[:,k]=solve(l,True)
    residual=np.column_stack([sum(K[j]@dr[:,k-j]+dK[j]@right[:,k-j]for j in range(k+1))for k in range(3)])
    dual=np.column_stack([sum(K[j].T@dl[:,k-j]+dK[j].T@left[:,k-j]for j in range(k+1))for k in range(3)])
    response=-dr[d];l=a['lapse'];ld=complex(lapse_time_first)
    return dict(bordered_polynomial_time_first=dK,right_taylor_time_first=dr,left_taylor_time_first=dl,
        original_time_first_rows=residual,transpose_time_first_rows=dual,
        response_taylor_time_first=response,normal_and_constraint_time_first=dT,
        proper_restoring_time_first=-response[0]/l+a['response_taylor'][0]*ld/l**2,
        proper_frequency_inertia_time_first=ld*a['response_taylor'][2]+l*response[2],
        lapse_coordinate_time_first=ld,moving_trial_not_reeliminated_variable_operator=True)


def strong_jacobi_normal_response(polynomial,normal_and_constraint_rows,*,lapse):
    """Re-eliminate the full reached local strong Jacobi coefficients.

    The non-self-adjoint first-germ polynomial is not relabelled an action
    Hessian. Its normal reaction is a local forced response; the physical
    event/exterior domain has not been selected by these trial rows.
    """
    p=np.asarray(polynomial,complex);T=np.asarray(normal_and_constraint_rows,complex)
    if p.ndim!=3 or p.shape[0]!=3 or p.shape[1]!=p.shape[2] or T.ndim!=2 or T.shape[1]!=p.shape[1]:
        raise ValueError('full local strong polynomial and all trace rows required')
    d=len(p[0]);K=np.zeros((3,d+len(T),d+len(T)),complex);K[:,:d,:d]=p;K[0,:d,d:]=T.T;K[0,d:,:d]=T
    rhs=np.zeros(len(K[0]),complex);rhs[d]=1;solve,balance=_balanced_solver(K[0])
    r=np.empty((len(rhs),3),complex);l=np.empty_like(r)
    r[:,0]=solve(rhs);l[:,0]=solve(rhs,True)
    for k in(1,2):
        r[:,k]=solve(-sum(K[j]@r[:,k-j]for j in range(1,k+1)))
        l[:,k]=solve(-sum(K[j].T@l[:,k-j]for j in range(1,k+1)),True)
    rows=np.column_stack([sum(K[j]@r[:,k-j]for j in range(k+1))-(rhs if k==0 else 0)for k in range(3)])
    dual=np.column_stack([sum(K[j].T@l[:,k-j]for j in range(k+1))-(rhs if k==0 else 0)for k in range(3)])
    response=-r[d]
    return dict(strong_polynomial=p,bordered_strong_polynomial=K,original_rhs=rhs,
        right_taylor=r,left_taylor=l,right_original_rows=rows,left_original_rows=dual,
        local_normal_reaction_taylor=response,normal_and_constraint_rows=T,
        same_clock_readout_taylor=response*np.array([1/complex(lapse),1,complex(lapse)]),
        all_multiplier_rows_retained=True,balanced_condition=float(np.linalg.cond(balance)),
        local_forced_response_not_action_selected_formation_density=True,
        frequency_and_coframe_frozen_at_one_reached_germ=True)
