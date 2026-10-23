"""Analytic left/right fermion action on the retained canonical contour.

Independent Grassmann left variables use an analytic transpose.  No
Hermitian reality relation is imposed on them along the complex contour.
The signed Lorentz action, contour measure, Green contacts, and canonical
current are composed before taking an inverse.
"""
from __future__ import annotations

import numpy as np
from scipy.sparse import bmat, csc_matrix, diags, eye, kron
from scipy.sparse.linalg import splu


def analytic_midpoint_action(weights, body, *, contour_rotation=1j):
    """Evaluate both Euler actions and the exact finite Green identity.

For dτ=r dt, w_E=r hN, A=Δ/w_E+H midpoint and
A_flat=−Δ/w_E+H^T midpoint.  The latter is the independent left
Euler action, not a Hermitian conjugate on a complex contour.

The executed r=i application uses actual changing Hcan(t) values on
τ=i(t−t0). Other r with H held fixed are principal/anchor checks only;
they do not provide H(t0+τ/r) on another finite contour.
"""
    w,H=np.asarray(weights,float),np.asarray(body,complex)
    r=complex(contour_rotation)
    if w.ndim!=1 or H.ndim!=3 or H.shape[0]!=len(w) or H.shape[1]!=H.shape[2]:
        raise ValueError('same complete proper-clock cell weights and body required')
    if np.any(w<=0)or not np.isfinite(w).all()or not np.isfinite(H).all()or not np.isfinite(r)or r==0:
        raise ValueError('finite nonzero contour and positive proper weights required')
    n,m=H.shape[:2];blocks=[[None]*(n+1)for _ in range(n)]
    average=[[None]*(n+1)for _ in range(n)]
    left=[[None]*(n+1)for _ in range(n)]
    for j in range(n):
        derivative=np.eye(m)/(r*w[j]);h=csc_matrix(H[j]/2);ht=csc_matrix(H[j].T/2)
        blocks[j][j]=h-csc_matrix(derivative);blocks[j][j+1]=h+csc_matrix(derivative)
        left[j][j]=ht+csc_matrix(derivative);left[j][j+1]=ht-csc_matrix(derivative)
        average[j][j]=average[j][j+1]=eye(m,format='csc')/2
    A=bmat(blocks,format='csc');flat=bmat(left,format='csc');B=bmat(average,format='csc')
    G=diags(np.repeat(r*w,m),format='csc')
    endpoint=diags(np.r_[-np.ones(m),np.zeros((n-1)*m),np.ones(m)],format='csc')
    green=B.T@G@A-flat.T@G@B-endpoint
    right=A[:,m:].tocsc();left_test=B[:,:-m].tocsc()
    F=(left_test.T@G@right).tocsc()
    doubled=bmat([[None,F],[-F.T,None]],format='csc')
    lorentz=(-left_test.T@diags(np.repeat(w,m),format='csc')@right).tocsc()
    return dict(A_full=A,left_Euler_full=flat,midpoint_full=B,contour_source_Gram=G,
        A_right_initial_zero=right,left_midpoint_final_zero=left_test,action=F,
        doubled_Grassmann_action=doubled,oriented_endpoint_contact=endpoint,
        original_Green_rows=green,
        Green_identity_max=float(np.max(abs(green.data)))if green.nnz else 0.,
        doubled_skew_max=float(np.max(abs((doubled+doubled.T).data)))if(doubled+doubled.T).nnz else 0.,
        lorentz_action=lorentz,lorentz_contour_action_identity_max=float(np.max(abs((lorentz+F/r).data)))if(lorentz+F/r).nnz else 0.,
        signed_action_rule='S_L=-S_contour/r; S_L=i*S_contour at r=i',
        weights=w,body=H,contour_rotation=r,dimension=m,
        left_domain='left independent field final trace zero',right_domain='right field initial trace zero',
        original_free_final_right_trace_retained=True,
        independent_left_field_is_Hermitian_conjugate=False)


def analytic_action_current(action, source, target_left):
    """Apply the same signed action with its literal source/current dual."""
    a=action;n=len(a['weights']);m=a['dimension']
    R,L=np.asarray(source,complex),np.asarray(target_left,complex)
    if R.shape[:2]!=(n,m)or R.ndim!=3 or L.shape!=(n,R.shape[-1],m):
        raise ValueError('same action source and literal current required')
    flat_R=R.reshape(n*m,-1)
    q=a['left_midpoint_final_zero'].T@a['contour_source_Gram']@flat_R
    factor=splu(a['action']);u=factor.solve(q)
    weighted=a['contour_rotation']*a['weights'][:,None,None]*L/2
    weighted[:-1]+=a['contour_rotation']*a['weights'][1:,None,None]*L[1:]/2
    target=weighted.transpose(1,0,2).reshape(L.shape[1],n*m)
    bar=splu(a['action'].T.tocsc()).solve(target.T)
    direct=splu(a['A_right_initial_zero']).solve(flat_R)
    value=target@u
    return dict(right_solution=u,left_solution=bar,source_dual=q,current_target=target,
        contour_current=value,physical_coordinate_current=value/a['contour_rotation'],
        transpose_pairing=bar.T@q,current_pairing_max=float(np.max(abs(value-bar.T@q))),
        original_right_Euler_rows=a['A_right_initial_zero']@u-flat_R,
        original_action_rows=a['action']@u-q,
        inverse_action_identity_max=float(np.max(abs(u-direct))),
        action_Hermitian_dual_mismatch_norm=float(np.linalg.norm((a['action'].T-a['action'].conj().T).data)),
        physical_current_phase_rule='C_contour=r*C_coordinate; r=i on the actual contour')


def directed_action_contact(source_action,target_action,delta_midpoint_body):
    """Differentiate the action including both endpoint-adjacent halves."""
    v=np.asarray(delta_midpoint_body,complex)
    n=len(source_action['weights']);ms=source_action['dimension'];mt=target_action['dimension']
    if v.shape!=(n,mt,ms)or not np.array_equal(source_action['weights'],target_action['weights'])or source_action['contour_rotation']!=target_action['contour_rotation']:
        raise ValueError('actual directed body contact in identical temporal pairing required')
    blocks=[[None]*(n+1)for _ in range(n)]
    for j in range(n):blocks[j][j]=blocks[j][j+1]=csc_matrix(v[j]/2)
    dA=bmat(blocks,format='csc')[:,ms:].tocsc()
    dF=(target_action['left_midpoint_final_zero'].T@target_action['contour_source_Gram']@dA).tocsc()
    return dict(delta_right_operator=dA,delta_action=dF,delta_left_Euler_action=dF.T,
        delta_doubled_Grassmann_action=bmat([[None,dF],[-dF.T,None]],format='csc'))


def analytic_magnetic_current(source_action,target_action,source_current,target_left,contact):
    """Consume the actual doubled action contact and original domain rows."""
    u=source_current['right_solution'];dF=contact['delta_action']
    reaction=-dF@u
    solution=splu(target_action['action']).solve(reaction)
    n=len(target_action['weights']);m=target_action['dimension'];L=np.asarray(target_left)
    weighted=target_action['contour_rotation']*target_action['weights'][:,None,None]*L/2
    weighted[:-1]+=target_action['contour_rotation']*target_action['weights'][1:,None,None]*L[1:]/2
    target=weighted.transpose(1,0,2).reshape(L.shape[1],n*m)
    left=splu(target_action['action'].T.tocsc()).solve(target.T)
    current=target@solution
    direct=splu(target_action['A_right_initial_zero']).solve(-contact['delta_right_operator']@u)
    return dict(response=solution,source_dual=reaction,contour_current=current,
        physical_coordinate_current=current/target_action['contour_rotation'],
        analytic_transpose_current=left.T@reaction,
        original_action_rows=target_action['action']@solution-reaction,
        original_right_Euler_rows=target_action['A_right_initial_zero']@solution+contact['delta_right_operator']@u,
        current_pairing_max=float(np.max(abs(current-left.T@reaction))),
        inverse_operator_contact_identity_max=float(np.max(abs(solution-direct))))


def principal_heat_contour_condition(rotation, cutoff):
    """Necessary high-frequency sectorial condition, not a full contour proof.

The Euclidean formal time-adjoint product has principal eigenvalue
rotation^-2 k² on this contour. Heating it with fixed positive c requires
Re(c rotation^-2)>0. This does not identify A^T with A† or define the full
Dirac/seam adjoint. It records the scalar principal-symbol obstruction to
relabeling the imaginary-time canonical graph as a real positive heat.
"""
    r,c=complex(rotation),complex(cutoff)
    if r==0 or not np.isfinite(r)or not np.isfinite(c):raise ValueError('finite contour required')
    coefficient=c/r**2
    return dict(principal_cutoff_phase=coefficient,
        necessary_positive_high_frequency_decay=coefficient.real>0,
        full_sectorial_or_relative_contour_theorem=False)
