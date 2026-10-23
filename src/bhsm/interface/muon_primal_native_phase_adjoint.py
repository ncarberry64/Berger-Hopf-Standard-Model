"""Direct native-target contraction on the saved full-action phase cell.

The input load is the executed weak action derivative, not a prescribed
replacement for an unavailable classical response.  The finite native
target supplies its complete raw cotangent.  Both are mapped to the same
saved phase Jacobian; no instantaneous kinetic inverse is constructed.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import lu_factor, lu_solve

from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_trace_enriched_charged_current_response import enriched_central_profiles


def native_phase_midpoint_map(representation):
    """The unchanged phase solve consumes eta=(x_mid,v_mid,y_mid)."""
    coordinates=generic_coordinate_lift(representation['gauge_labels'])
    n=coordinates['x_count'];m=coordinates['y_count'];P=coordinates['lift']
    M=np.zeros((2*n+m,3*n+m))
    M[:n,:n]=np.eye(n)/2
    M[n:2*n,2*n:3*n]=np.eye(n)
    M[2*n:,3*n:]=np.eye(m)
    return dict(raw_from_phase=P@M,master_from_phase=M,coordinates=coordinates)


def native_phase_load_rows(raw_load,representation,step):
    """Differentiate every Euler, Legendre and multiplier/Gauss row.

    A signed action load changes the residual by
    (0,-h*b_x,b_v,b_y).  The incoming negative h is retained.  The
    current pair axes survive in their recorded order without doubling.
    """
    maps=native_phase_midpoint_map(representation);P=maps['coordinates']['lift']
    n=maps['coordinates']['x_count'];m=maps['coordinates']['y_count']
    a=np.asarray(raw_load)
    if not np.isrealobj(a) or a.ndim<1 or a.shape[0]!=P.shape[0] or not np.isfinite(a).all():
        raise ValueError('complete real same-action raw load required')
    if not np.isfinite(step) or step==0:raise ValueError('oriented nonzero phase step required')
    shape=a.shape[1:];b=P.T@a.reshape(P.shape[0],-1)
    rows=np.vstack((np.zeros_like(b[:n]),-step*b[:n],b[n:2*n],b[2*n:]))
    return rows.reshape((3*n+m,)+shape)


def chronological_native_phase_jacobian(jacobian,representation,oriented_step):
    """Reuse the identical variational cell in increasing physical time.

    A stored incoming step starts at birth and ends in the past.  Its
    chronological application starts at that past endpoint and ends at
    birth, retaining v_mid, y_mid and the midpoint action.  Only the
    h-dependent kinematic-v and canonical-force Hessian blocks change
    sign.  The Legendre, Gauss and multiplier blocks do not change.
    """
    maps=native_phase_midpoint_map(representation);n=maps['coordinates']['x_count']
    size=maps['raw_from_phase'].shape[1];J=np.asarray(jacobian)
    h=float(oriented_step)
    if not np.isrealobj(J) or J.shape!=(size,size) or not np.isfinite(J).all() or not np.isfinite(h) or h==0:
        raise ValueError('complete saved variational phase Jacobian and nonzero step required')
    checks=(J[:n,:n]-np.eye(n),J[:n,2*n:3*n]+h*np.eye(n),
        J[n:2*n,n:2*n]-np.eye(n),J[2*n:3*n,n:2*n]+np.eye(n)/2)
    if any(np.max(abs(x))!=0 for x in checks):raise ValueError('same unchanged action-generated midpoint row contract required')
    out=J.copy()
    if h<0:
        out[:n,2*n:3*n]*=-1
        out[n:2*n,:n]*=-1
        out[n:2*n,2*n:]*=-1
    return dict(jacobian=out,step=abs(h),stored_oriented_step=h,
        incoming_time_direction_reversed=bool(h<0),
        midpoint_fields_rates_and_Legendre_Gauss_rows_unchanged=True,
        endpoint_rule='incoming: initial saved past x/p, final saved birth x/p; outgoing: saved initial birth x/p and final future x/p',
        no_boundary_or_physical_current_selected=True)


def native_phase_named_border(jacobian,representation,*,frame):
    """Retain all original rows and the two explicit central frame reactions."""
    maps=native_phase_midpoint_map(representation);coords=maps['coordinates']
    n=coords['x_count'];m=coords['y_count'];size=3*n+m
    J=np.asarray(jacobian)
    if not np.isrealobj(J) or J.shape!=(size,size) or not np.isfinite(J).all():
        raise ValueError('complete real saved phase Jacobian required')
    if frame not in ('temporal','radial'):raise ValueError('named temporal or radial central frame required')
    profiles=enriched_central_profiles(representation);labels=representation['gauge_labels']
    at=[j for j,i in enumerate(coords['At_indices']) if labels[i]['internal']==3]
    ar=[j for j,i in enumerate(coords['dynamic_gauge_indices'])
        if labels[i]['field']=='A_rho' and labels[i]['internal']==3]
    if len(at)!=4 or len(ar)!=4:raise ValueError('complete actual enriched central bands required')
    R=np.zeros((size,2));R[3*n+24+np.array(at)]=profiles['theta_coefficients']
    C=np.zeros((2,size))
    if frame=='temporal':C[:,3*n+24+np.array(at)]=profiles['theta_coefficients'].T
    else:C[:,2*n+38+np.array(ar)]=profiles['radial_derivative_coefficients'].T
    K=np.block([[J,R],[C,np.zeros((2,2))]])
    return dict(matrix=K,original_J=J,auxiliary_Gauss_column=R,
        frame_matrix=C,midpoint_maps=maps,frame=frame)


def contract_phase_native_target(jacobian,representation,step,raw_target,raw_load,*,frame='temporal'):
    """Apply one target adjoint directly to every reached source-pair load.

    If J dz=-F and G=dGamma/dz, the contraction is -p^T F with
    K^T(p,rho)=(G,0).  Two additional adjoints evaluate every auxiliary
    Gauss reaction; those reactions are not silently treated as zero.
    This binary64 finite-cell application is not a continuum certificate
    or a completed relative native Pauli result.
    """
    border=native_phase_named_border(jacobian,representation,frame=frame)
    rawmap=border['midpoint_maps']['raw_from_phase'];target=np.asarray(raw_target)
    if not np.isrealobj(target) or target.shape!=(rawmap.shape[0],) or not np.isfinite(target).all():
        raise ValueError('complete real raw native-target cotangent required')
    load_rows=native_phase_load_rows(raw_load,representation,step)
    shape=load_rows.shape[1:];F=load_rows.reshape(rawmap.shape[1],-1)
    G=target@rawmap;K=border['matrix'];size=len(G)
    row=1/np.maximum(np.max(abs(K),axis=1),np.finfo(float).tiny)
    col=1/np.maximum(np.max(abs(row[:,None]*K),axis=0),np.finfo(float).tiny)
    A=row[:,None]*K*col[None,:]
    # K^T p=g follows from A^T z=diag(col)g and p=diag(row)z.
    readouts=np.zeros((size+2,3));readouts[:size,0]=G;readouts[size:,1:]=np.eye(2)
    factor=lu_factor(A)
    adjoints=row[:,None]*lu_solve(factor,col[:,None]*readouts,trans=1)
    contraction=-adjoints[:size,0]@F
    reactions=-adjoints[:size,1:].T@F
    original_adjoint_defect=border['original_J'].T@adjoints[:size,0]-G
    source_incompatible_rows=-border['auxiliary_Gauss_column']@reactions
    return dict(native_mean_response_pair=contraction.reshape(shape),
        target_adjoint=adjoints[:,0],auxiliary_reaction_adjoints=adjoints[:,1:],
        phase_source_rows=load_rows,phase_target_row=G,
        auxiliary_Gauss_reactions=reactions.reshape((2,)+shape),
        original_Euler_Gauss_reaction_rows=source_incompatible_rows.reshape((size,)+shape),
        target_frame_contact=adjoints[size:,0],
        original_adjoint_defect=original_adjoint_defect,
        bordered_adjoint_residual_norm=float(np.linalg.norm(K.T@adjoints-readouts)),
        scaled_bordered_adjoint_residual_norm=float(np.linalg.norm(col[:,None]*(K.T@adjoints-readouts))),
        original_adjoint_defect_norm=float(np.linalg.norm(original_adjoint_defect)),
        auxiliary_Gauss_reaction_norm=float(np.linalg.norm(reactions)),
        balanced_condition_number=float(np.linalg.cond(A)),
        oriented_step=float(step),frame=frame,
        all_original_Euler_Legendre_constraint_Gauss_rows_retained=True,
        instantaneous_Legendre_inverse_used=False,pseudoinverse_used=False,
        source_pair_axes_doubled=False,full_forward_mean_response_materialized=False,
        error_scope='binary64 complete saved finite-cell Jacobian, target and action load; linear residuals only, no continuum/relative-completion/Pauli enclosure')
