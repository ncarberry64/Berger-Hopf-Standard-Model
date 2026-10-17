"""Direct mixed weak-action coordinates, preserving canonical outer tests.

Build from original action coefficients, never from the already formed
h^(-2) nodal matrix. This is a numerical representation change, not a
choice of physical endpoint, covariance, mode or exterior graph.
"""
from __future__ import annotations
import numpy as np


def mixed_chronological_arm_action(hessians, gradients, steps, *, dynamic_count=106, algebraic_count=40):
    H,g,h = (np.asarray(a,complex) for a in (hessians,gradients,steps))
    n,m=int(dynamic_count),int(algebraic_count);nc=len(h);na=2*n+m;dim=(nc+1)*n+nc*m
    if H.shape!=(nc,na,na) or g.shape!=(nc,na) or h.shape!=(nc,) or np.any(h==0):
        raise ValueError('all signed original action jets and nonzero cell clocks required')
    # Mixed coordinates are x0, each independent v_cell, each y_cell.
    nodes=np.zeros((dim,dim),complex);nodes[:n,:n]=np.eye(n)
    for j in range(nc):
        nodes[(j+1)*n:(j+2)*n,:n]=np.eye(n)
        for k in range(j+1):nodes[(j+1)*n:(j+2)*n,(k+1)*n:(k+2)*n]=h[k]*np.eye(n)
    nodes[(nc+1)*n:,(nc+1)*n:]=np.eye(nc*m)
    lifts=[];W=np.zeros((dim,dim),complex);f=np.zeros(dim,complex)
    for j in range(nc):
        E=np.zeros((na,dim),complex);E[:n,:n]=np.eye(n)
        for k in range(j):E[:n,(k+1)*n:(k+2)*n]=h[k]*np.eye(n)
        E[:n,(j+1)*n:(j+2)*n]=h[j]*np.eye(n)/2
        E[n:2*n,(j+1)*n:(j+2)*n]=np.eye(n)
        E[2*n:,(nc+1)*n+j*m:(nc+1)*n+(j+1)*m]=np.eye(m)
        W+=h[j]*E.T@H[j]@E;f+=h[j]*E.T@g[j];lifts.append(E)
    return dict(matrix=W,gradient=f,cell_lifts=np.array(lifts),mixed_to_nodes=nodes,
        steps=h,variable_count=dim,original_coefficients_directly_applied=True,
        formed_nodal_kinetic_matrix_used=False)


def mixed_variation_from_actual_stages(initial_x, stage_variations, *, dynamic_count=106):
    """Use actual stage velocity/y variations, avoiding x-difference/h."""
    n=int(dynamic_count);s=np.asarray(stage_variations,complex);x=np.asarray(initial_x,complex)
    if s.ndim not in (2,3) or s.shape[1]<2*n or x.shape!=(n,)+s.shape[2:]:
        raise ValueError('same original initial x and full stage jets required')
    return np.concatenate((x,*[a[n:2*n] for a in s],*[a[2*n:] for a in s]),axis=0)


def mixed_cell_cotangent(hessians, gradients, steps, stage_variations, *, dynamic_count=106):
    """Original nodal cotangent from cell forces, without an h^-2 matrix.

    The endpoint signs are the chronological left-minus/right-plus
    Legendre signs. Algebraic rows retain their cell measure.
    """
    H,g,h,s=(np.asarray(a,complex) for a in (hessians,gradients,steps,stage_variations))
    n=int(dynamic_count);nc=len(h)
    if (H.ndim!=3 or s.ndim not in (2,3) or s.shape[:2]!=(nc,H.shape[1])
            or g.shape not in ((nc,H.shape[1]),s.shape)):
        raise ValueError('same original cell Hessians, explicit sources and full variations required')
    source=g if g.shape==s.shape else g[(...,)+(None,)*(s.ndim-2)]
    force=np.einsum('kij,kj...->ki...',H,s)+source
    out=np.zeros(((nc+1)*n+nc*(H.shape[1]-2*n),)+s.shape[2:],complex)
    for j in range(nc):
        out[j*n:(j+1)*n]+=h[j]*force[j,:n]/2-force[j,n:2*n]
        out[(j+1)*n:(j+2)*n]+=h[j]*force[j,:n]/2+force[j,n:2*n]
        m=H.shape[1]-2*n
        out[(nc+1)*n+j*m:(nc+1)*n+(j+1)*m]=h[j]*force[j,2*n:]
    return dict(cotangent=out,original_cell_forces=force)
