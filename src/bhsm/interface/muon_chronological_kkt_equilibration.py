"""Reversible coordinate equilibration of a supplied chronological KKT.

No gauge quotient, action pairing, stationarity, or source sector is chosen
by this numerical congruence. Every original row and multiplier is retained.
"""
from __future__ import annotations
import numpy as np


def equilibrate_chronological_kkt(diagonal,upper,lower,*,iterations=8):
    D=np.asarray(diagonal,complex).copy();U=np.asarray(upper,complex).copy();L=np.asarray(lower,complex).copy()
    if (D.ndim!=3 or D.shape[1]!=D.shape[2]or U.shape!=(len(D)-1,D.shape[1],D.shape[1])or L.shape!=U.shape
        or type(iterations)is not int or iterations<1 or not np.isfinite(D).all()or not np.isfinite(U).all()or not np.isfinite(L).all()):
        raise ValueError('same complete finite directed KKT blocks required')
    scales=np.ones(D.shape[:2]);history=[]
    for _ in range(iterations):
        norms=np.maximum(np.max(abs(D),axis=2),np.max(abs(D),axis=1))
        if len(U):
            norms[:-1]=np.maximum(norms[:-1],np.maximum(np.max(abs(U),axis=2),np.max(abs(L),axis=1)))
            norms[1:]=np.maximum(norms[1:],np.maximum(np.max(abs(L),axis=2),np.max(abs(U),axis=1)))
        if np.any(norms==0):raise np.linalg.LinAlgError('original zero KKT row requires its owned quotient, not a numerical deletion')
        t=1/np.sqrt(norms);scales*=t
        D*=t[:,:,None]*t[:,None,:]
        U*=t[:-1,:,None]*t[1:,None,:];L*=t[1:,:,None]*t[:-1,None,:]
        history.append(dict(maximum_row_scale=float(np.max(norms)),minimum_row_scale=float(np.min(norms))))
    return dict(diagonal=D,upper=U,lower=L,coordinate_scales=scales,equilibration_history=history,
        original_field_constraint_and_multiplier_rows_retained=True,
        physical_gauge_quotient_or_pairing_changed=False)


def original_chronological_kkt_apply(diagonal,upper,lower,direction):
    D,U,L,x=[np.asarray(v,complex)for v in(diagonal,upper,lower,direction)]
    if x.shape!=D.shape[:2]or U.shape!=L.shape or len(U)!=len(D)-1:raise ValueError('same original directed row coordinates required')
    out=np.einsum('nij,nj->ni',D,x)
    out[:-1]+=np.einsum('nij,nj->ni',U,x[1:]);out[1:]+=np.einsum('nij,nj->ni',L,x[:-1])
    return out
