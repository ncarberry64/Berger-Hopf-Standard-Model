"""Standalone-parent and inherited-child canonical source reconstitution."""
from __future__ import annotations
import numpy as np
from .muon_complex_paired_normal_action import _balanced_solver


def original_arm_constitutive_response(H,delta_x,delta_Pi,source,frame,*,phase_frame_value=None):
    H=np.asarray(H,complex);dx=np.asarray(delta_x,complex);dp=np.asarray(delta_Pi,complex);g=np.asarray(source,complex);n=len(dx)
    F=np.asarray(frame,complex);phase=H[n:,n:];frame_value=np.zeros(len(F),complex)if phase_frame_value is None else np.asarray(phase_frame_value,complex)
    K=np.block([[phase,F.T],[F,np.zeros((len(F),len(F)),complex)]])
    rhs=np.r_[np.r_[dp,np.zeros(len(H)-2*n)]-H[n:,:n]@dx-g[n:],frame_value]
    solve,balance=_balanced_solver(K);z=solve(rhs);direction=np.r_[dx,z[:len(phase)]]
    original=H[n:]@direction+g[n:]-np.r_[dp,np.zeros(len(H)-2*n)]
    return dict(direction=direction,original_phase_rows=original,framed_rows=K@z-rhs,
        frame_reactions=z[len(phase):],original_saddle=K,original_rhs=rhs,solution=z,
        canonical_momentum_target=dp,source_gradient=g,delta_x=dx,
        Gauss_rows=original[n:],Legendre_rows=original[:n],
        balanced_condition=float(np.linalg.cond(balance)),canonical_target_not_fitted=True)


def per_arm_source_reconstitution(parent_H,joint_H,direction,source,parent_frame,child_frame,*,standalone_parent_source=None):
    """Use own-parent Pi, then actual child source from reconstituted parent.

    The child target is the original demanded total Pi variation. The
    change of inherited source after parent reconstitution is retained in
    the child equations; no substitution of joint Pi for own parent Pi.
    """
    Hp=np.asarray(parent_H,complex);H=np.asarray(joint_H,complex);d=np.asarray(direction,complex);g=np.asarray(source,complex);n=106
    if Hp.shape!=(252,252)or H.shape!=(504,504)or d.shape!=(504,)or g.shape!=(504,):raise ValueError('same complete two-arm original action/source required')
    if standalone_parent_source is None:
        if np.any(g[:252]!=0):raise ValueError('standalone-parent source must be supplied independently of joint source')
        own=np.zeros(252,complex)
    else:own=np.asarray(standalone_parent_source,complex)
    if own.shape!=(252,):raise ValueError('full original standalone-parent source required')
    dp=Hp[n:2*n]@d[:252]+own[n:2*n]
    parent=original_arm_constitutive_response(Hp,d[:n],dp,own,parent_frame,
        phase_frame_value=np.asarray(parent_frame)@d[n:252])
    target=H[252+n:252+2*n]@d+g[252+n:252+2*n]
    inherited=H[252:,:252]@parent['direction'];source_child=g[252:]+inherited
    child=original_arm_constitutive_response(H[252:,252:],d[252:252+n],target,source_child,child_frame,
        phase_frame_value=np.asarray(child_frame)@d[252+n:])
    result=np.r_[parent['direction'],child['direction']]
    return dict(parent=parent,child=child,reconstituted_joint_direction=result,
        parent_own_momentum_target=dp,parent_joint_momentum_same_trial=H[n:2*n]@d+g[n:2*n],
        child_original_total_momentum_target=target,child_inherited_source=inherited,
        child_inherited_source_change=H[252:,:252]@(parent['direction']-d[:252]),
        original_joint_Gauss_rows=(H@result+g)[np.r_[np.arange(212,252),np.arange(464,504)]],
        parent_own_target_preserved=True,source_feedback_count=1,standalone_parent_source=own)


def arm_variational_midpoint_map(H,step,delta_x0,delta_Pi0,source_midpoint,frame,*,phase_frame_value=None,normal_covector=None):
    """Literal original358 linearized canonical midpoint and transpose map.

    H/source are the explicitly supplied actual face germ. Free final
    values and canonical duals are solved; no persistent reset trace load.
    """
    H=np.asarray(H,complex);x0=np.asarray(delta_x0,complex);p0=np.asarray(delta_Pi0,complex);g=np.asarray(source_midpoint,complex)
    n=len(x0);m=len(H)-2*n;h=complex(step);F=np.asarray(frame,complex)
    if H.shape!=(2*n+m,)*2 or p0.shape!=x0.shape or h==0:raise ValueError('same original face coefficient/source and oriented step required')
    dim=3*n+m;A=np.zeros((dim,dim),complex);rhs=np.zeros(dim,complex)
    A[:n,:n]=np.eye(n);A[:n,2*n:3*n]=-h*np.eye(n);rhs[:n]=x0
    A[n:2*n,:n]=-h*H[:n,:n]/2;A[n:2*n,n:2*n]=np.eye(n);A[n:2*n,2*n:]=-h*H[:n,n:]
    rhs[n:2*n]=p0+h*(H[:n,:n]@x0/2+g[:n])
    A[2*n:3*n,:n]=H[n:2*n,:n]/2;A[2*n:3*n,n:2*n]=-np.eye(n)/2;A[2*n:3*n,2*n:]=H[n:2*n,n:]
    rhs[2*n:3*n]=p0/2-H[n:2*n,:n]@x0/2-g[n:2*n]
    A[3*n:,:n]=H[2*n:,:n]/2;A[3*n:,2*n:]=H[2*n:,n:];rhs[3*n:]=-H[2*n:,:n]@x0/2-g[2*n:]
    C=np.zeros((len(F),dim),complex);C[:,2*n:]=F;E=np.zeros((dim,len(F)),complex);E[2*n:]=F.T
    K=np.block([[A,E],[C,np.zeros((len(F),len(F)),complex)]]);fv=np.zeros(len(F),complex)if phase_frame_value is None else np.asarray(phase_frame_value,complex)
    solve,balance=_balanced_solver(K);right=np.r_[rhs,fv];z=solve(right);u=z[:dim]
    eta=np.r_[(x0+u[:n])/2,u[2*n:]];gradient=H@eta+g
    original=np.r_[u[:n]-x0-h*u[2*n:3*n],u[n:2*n]-p0-h*gradient[:n],gradient[n:2*n]-(p0+u[n:2*n])/2,gradient[2*n:]]
    # The supplied left test is kept literal, with no Hilbert conjugation.
    normal=np.eye(n)[-1]if normal_covector is None else np.asarray(normal_covector,complex)
    if normal.shape!=(n,):raise ValueError('same final normal covector required')
    test=np.zeros(len(K),complex);test[:n]=normal;left=solve(test,True)
    return dict(original358_matrix=A,framed_midpoint_matrix=K,original_rhs=rhs,solution=z,
        stage_variation=eta,x_final=u[:n],Pi_final=u[n:2*n],original358_rows=original,
        framed_rows=K@z-right,frame_reactions=z[dim:],literal_left_test=test,literal_transpose_solution=left,
        literal_transpose_rows=K.T@left-test,transpose_pairing=left@right,test_pairing=test@z,
        initial_action_dual=h*gradient[:n]/2-gradient[n:2*n],final_action_dual=h*gradient[:n]/2+gradient[n:2*n],
        source_midpoint=g,boundary_reset_rows_not_loaded_in_bulk=True,balanced_condition=float(np.linalg.cond(balance)))
