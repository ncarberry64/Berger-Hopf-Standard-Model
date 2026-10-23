"""Original coupled field Hessian on a homogeneous chronological germ.

The scalar harmonic transform is a constant change of computational basis.
Its angular dual is E^dagger, while all continued field coefficients keep
their analytic transpose.  No dagger of the continued background is used.
At/Gauss, the four radial gauge profiles and induced H remain original.
"""
from __future__ import annotations
import numpy as np
from .muon_nonlinear_chronological_n0_action import _ad_batch,analytic_constant_maxwell_batch
from .muon_matched_mechanical_source import epsilon
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation

VOLUME=2*np.pi**2


def analytic_homogeneous_original_field_forms(row,value,coordinate_rate,lifts,angular_derivatives):
    """Literal M, B_forward, B_reverse, K on every original84*nh row.

    E^dagger is the inverse constant real-to-complex harmonic basis dual;
    it does not conjugate any field, source, coframe or tangent coefficient.
    B_reverse is exported independently: in complex harmonics it need not
    equal B_forward^T, although the original real harmonic action is symmetric.
    """
    v,t,E=[np.asarray(q,complex)for q in(value,coordinate_rate,angular_derivatives)]
    if v.shape!=(84,)or t.shape!=(84,)or E.ndim!=3 or E.shape[0]!=3 or E.shape[1]!=E.shape[2]or any(not np.isfinite(q).all()for q in(v,t,E)):
        raise ValueError('full homogeneous fields and a complete finite angular block required')
    nh=E.shape[1];I=np.eye(nh);ep=np.r_[I[None],E];n=len(lifts['P']);eps=epsilon()
    P,Pr,Pt,W,hv=(lifts[k]for k in('P','Pr','Pt','W','hv'))
    A=row['A']+(P@v).reshape(n,5,4);At=row['At']+(Pt@t).reshape(n,5,4);Ar=row['Ar']+(Pr@v).reshape(n,5,4)
    p=P.reshape(n,5,4,84);pr=Pr.reshape(n,5,4,84);pt=Pt.reshape(n,5,4,84)
    ad=_ad_batch(A);e,r,d,k,beta=np.asarray(row['densities'],complex).T
    X=np.zeros((4,n,4,84),complex);Y=np.zeros((4,n,12,84),complex);R=Y.copy();B=Y.copy()
    X[0]=ad[:,0]@p[:,1]-ad[:,1]@p[:,0]-pr[:,0]
    JT=np.zeros((n,40,84),complex);JT[:,:4]=pt[:,1]
    for i in range(3):
        sl=slice(4*i,4*i+4)
        R[0,:,sl]=ad[:,1]@p[:,2+i]-ad[:,2+i]@p[:,1]+pr[:,2+i]
        R[i+1,:,sl]=-p[:,1]
        Y[0,:,sl]=ad[:,0]@p[:,2+i]-ad[:,2+i]@p[:,0]-beta[:,None,None]*R[0,:,sl]
        Y[i+1,:,sl]=-p[:,0]+beta[:,None,None]*p[:,1]
        B[0,:,sl]=2*p[:,2+i];JT[:,4+4*i:8+4*i]=pt[:,2+i]
    for i,j,h in np.argwhere(eps):
        B[0,:,4*i:4*i+4]+=eps[i,j,h]*(ad[:,2+j]@p[:,2+h])
        B[j+1,:,4*i:4*i+4]+=eps[i,j,h]*p[:,2+h]
    J=np.concatenate((X,Y,R,B),axis=2)
    weights=MAXWELL_TO_CAP*lifts['radial_weights'][:,None]*np.c_[np.repeat(k[:,None],4,axis=1),
        np.repeat(e[:,None],12,axis=1),np.repeat(-r[:,None],12,axis=1),np.repeat(-d[:,None],12,axis=1)]
    # Build the angular right and left once; BLAS sums all original radial
    # profiles and curvature components before temporal FE assembly.
    right=np.einsum('prca,pij->rciaj',J,ep,optimize=True).reshape(n*40*nh,84*nh)
    left=np.einsum('prca,pji->ajrci',J,ep.conj().transpose(0,2,1),optimize=True).reshape(84*nh,n*40*nh)
    rate=np.einsum('rca,ij->rciaj',JT,I).reshape(n*40*nh,84*nh)
    rate_left=np.einsum('rca,ji->ajrci',JT,I).reshape(84*nh,n*40*nh)
    weight=np.repeat(weights.ravel(),nh)
    K=(left*weight[None])@right;BF=(left*weight[None])@rate
    BR=(rate_left*weight[None])@right;M=(rate_left*weight[None])@rate
    q=analytic_constant_maxwell_batch(A,At,Ar,row['densities'])
    contact=np.einsum('ria,rij,rjb,r->ab',P,q['curvature_contact'],P,
        MAXWELL_TO_CAP*lifts['radial_weights'],optimize=True)
    K+=np.kron(contact,I)
    H=row['H']+hv@v;Hd=row['Hdot']+hv@t;Aw=row['wall_A']+(W@v).reshape(5,4)
    T=higgs_u2_real_representation()['real_generators'];O=np.einsum('fc,cij->fij',Aw,T);U=np.einsum('cij,j->ic',T,H)
    size=84*nh;VH=np.c_[np.kron(hv,I),np.zeros((4*nh,size),complex)]
    VT=np.c_[np.zeros((4*nh,size),complex),np.kron(hv,I)]
    VG=np.array([np.c_[np.kron(w,I),np.zeros((4*nh,size),complex)]for w in W.reshape(5,4,84)])
    DH=np.r_[(Hd+O[0]@H)[None],np.einsum('fij,j->fi',O[2:],H)]
    SH=np.zeros((2*size,2*size),complex)
    for j,(f,w)in enumerate(zip((0,2,3,4),(row['weights'][0],-row['weights'][1],-row['weights'][1],-row['weights'][1]))):
        ordinary=VT if f==0 else np.kron(np.eye(4),E[f-2])@VH
        ordinary_dual=VT.T if f==0 else VH.T@np.kron(np.eye(4),E[f-2].conj().T)
        C=ordinary+np.kron(O[f],I)@VH+np.kron(U,I)@VG[f]
        CD=ordinary_dual+VH.T@np.kron(O[f].T,I)+VG[f].T@np.kron(U.T,I)
        cross=np.einsum('i,cij->jc',DH[j],T);cc=np.kron(cross,I)
        SH+=2*w/VOLUME*(CD@C+VH.T@cc@VG[f]+VG[f].T@cc.T@VH)
    potential=row['lambda_H']*(8*np.outer(H,H)+4*(H@H-row['nu_squared_action'])*np.eye(4))
    SH-=row['weights'][2]/VOLUME*VH.T@np.kron(potential,I)@VH
    K+=SH[:size,:size];BF+=SH[:size,size:];BR+=SH[size:,:size];M+=SH[size:,size:]
    return dict(M=M,B_forward=BF,B_reverse=BR,K=K,
        wall_value_map=np.kron(np.r_[W,hv],I),frame_rows=np.kron(lifts['frame_rows'],I),
        original_At_Gauss_count=16*nh,all_original_H_and_four_radial_profiles_retained=True,
        angular_basis_dual_conjugates_continued_coefficients=False)
