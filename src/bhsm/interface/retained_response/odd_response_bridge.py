"""Actual retained magnetic source -> existing odd angular representation.

This is a source/domain-component application, NOT an outgoing Green solve.
Original spatial magnetic arrays are reused; none are tightened/replaced.
The diagnostic gradient/coexact split is an ordinary unit-S3 geometric split,
not the physical background-covariant Gauss/BRST quotient.
"""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np
from .retained_magnetic_application import FRAME, fields, rule8, rule24
from .action_magnetic_kernel import local_hessian, bracket, epsilon
from .compatible_source import real_transform, real_labels, scalar_values, haar_rule


def finite_real(a, shape, name):
    x=np.asarray(a)
    if x.shape!=shape or not np.isfinite(x).all() or np.iscomplexobj(x):
        raise ValueError(f'{name} needs finite real {shape}')
    return x


def odd_isometry():
    """Cart n1 harmonic-major80 -> owned (field5,internal4,odd20)400.

    Ycart=(2x0,2x1,2x2,2x3).
    Yowned_n1=(2x0,-2x1,2x2,-2x3) from normalized conjugate Wigner.
    This is an exact signed permutation/inclusion, not a new physical domain.
    Both source and target use the same unit Haar pairing; no Riesz factor
    for a different physical measure is inferred.
    """
    u=np.zeros((400,80),dtype=float)
    for h,f,c in np.ndindex(4,5,4):
        u[(f*4+c)*20+h,h*20+f*4+c]=(1,-1,1,-1)[h]
    return u


def original_scalar_derivatives(max_level=3):
    """Read-owner formula: E=2i J on active m, spectator k; real transform."""
    count=sum((n+1)**2 for n in range(max_level+1))
    out=np.zeros((3,count,count),complex);start=0
    for n in range(max_level+1):
        j=n/2;plus=np.zeros((n+1,n+1),complex)
        for col in range(1,n+1):
            m=j-col;plus[col-1,col]=np.sqrt((j-m)*(j+m+1))
        spin=np.array([(plus+plus.T)/2,(plus-plus.T)/(2j),np.diag(np.arange(n,-n-1,-2)/2)])
        width=(n+1)**2
        for a in range(3):out[a,start:start+width,start:start+width]=np.kron(2j*spin[a],np.eye(n+1))
        start+=width
    transform=real_transform(max_level)
    full=transform.conj().T@out@transform
    if np.max(abs(full.imag))>1e-12:raise ArithmeticError('original real harmonic derivative failed')
    idx=[i for i,l in enumerate(real_labels(max_level)) if l[0]%2]
    return full.real[:,idx][:,:,idx]


def ordinary_n1_split():
    """Exact unit-S3 spatial curl and gradient in (spatial3,harmonic4)."""
    E=FRAME.transpose(0,2,1).copy()
    grad=np.vstack(E)
    C=2*np.eye(12);ep=epsilon()
    for i,j,k in np.argwhere(ep):
        C[4*i:4*i+4,4*k:4*k+4]+=ep[i,j,k]*E[j]
    longitudinal=grad@grad.T/3
    coexact=C/3
    return dict(curl=C,gradient=grad,longitudinal=longitudinal,coexact=coexact)


def magnetic_source_image(magnetic):
    k=finite_real(magnetic,(3,100,100),'retained spatial K_B')
    # Coefficient blocks are action covectors, not physical field solutions.
    mixed=k[:,20:,:20]
    source=np.einsum('ij,ajk->aik',odd_isometry(),mixed)
    cart=mixed.reshape(3,4,5,4,20)[:,:,2:,:].transpose(0,2,1,3,4).reshape(3,12,4,20)
    split=ordinary_n1_split()
    co=np.einsum('ij,ajkc->aikc',split['coexact'],cart)
    lo=np.einsum('ij,ajkc->aikc',split['longitudinal'],cart)
    return dict(mixed80x20=mixed,source400x20=source,spatial_source12x4x20=cart,
                coexact_source=co,longitudinal_source=lo)


def scalar_action_hessian(raw, rule=rule8):
    """New lower-order spatial Hessian used only in the differentiated Ward check.

    Original retained K_B is supplied separately, never recomputed here.
    This spatial action is NOT a new surface term or complete cap operator.
    """
    points,w=rule();data,base,probes,u,v,dens=fields(raw,points)
    K=np.einsum('p,pij->ij',w,local_hessian(base,u,v,dens))
    return K,data,points,w,probes


def differentiated_spatial_gauge_identity(raw, magnetic, rule=rule8):
    """K_b[D_A alpha,v]+K[[b,alpha],v]+K[b,[v,alpha]]=0.

    All16 n1 gauge parameter directions, all20 constant one-form directions,
    and all3 actual magnetic axes are tested. Scalar action only, fixed metric.
    [b,alpha] contains n0,n2; its n0 projection is sufficient ONLY for pairing
    with the constant v through this homogeneous lower-order Hessian.
    """
    K,data,x,w,probes=scalar_action_hessian(raw,rule)
    y=2*x; yall=np.c_[np.ones(len(x)),y]
    ey=2*np.einsum('aij,pj->pai',FRAME,x)
    alpha=np.einsum('ph,ic->phic',y,np.eye(4)).reshape(len(x),16,4)
    dalpha=np.einsum('pah,ic->phiac',ey,np.eye(4)).reshape(len(x),16,3,4)
    # Construct values then normalize in the same Haar coefficient chart.
    tangent=np.zeros((len(x),16,5,4),complex)
    tangent[:,:,2:]=dalpha+bracket(data['connection'][None,None,2:],alpha[:,:,None])
    tc=np.einsum('p,ph,pqfc->hfcq',w,yall,tangent).reshape(100,16)
    # [v_const,alpha] is exactly n1; index convention h,f,c,v,gauge.
    constant=np.eye(20).reshape(20,5,4)
    va=bracket(constant[None,:,None],alpha[:,None,:,None]) # p,v,q,f,c
    vac=np.einsum('p,ph,pvqfc->hfcvq',w,yall,va).reshape(100,20,16)
    outputs=[]
    for axis,probe in enumerate(probes):
        bv=probe.value[:,0,0]
        bc=np.einsum('p,ph,pfc->hfc',w,yall,bv).reshape(100)
        ba=bracket(bv[:,None],alpha[:,:,None]) # p,q,f,c
        mean=np.einsum('p,pqfc->fcq',w,ba).reshape(20,16)
        term1=tc.T@magnetic[axis,:,:20]
        term2=mean.T@K[:20,:20]
        term3=np.einsum('i,ivq->qv',bc@K,vac)
        scale=float(abs(data['prefactor_per_e']))
        outputs.append(dict(first=term1,source_gauge_motion=term2,
            test_gauge_motion=term3,residual=term1+term2+term3,
            naive_max=float(np.max(abs(term1))),
            completed_max=float(np.max(abs(term1+term2+term3))),
            normalized_max=float(np.max(abs(term1+term2+term3)))/scale))
    return outputs, K, tc


def retarded_odd_forcing(*, insertion_oe, even_response, source_first_odd,
                        domain_first_odd):
    """Assemble RHS only, in one already-identified common weak domain.

    Caller must provide the full INTEGRATED insertion and actual response;
    saved wall-density matrices are not valid substitutes. This function
    supplies no Green function, terminal map or missing source data.
    """
    B,u,f,d=map(np.asarray,(insertion_oe,even_response,source_first_odd,domain_first_odd))
    if B.ndim!=2 or u.shape[0]!=B.shape[1] or f.shape!=d.shape or (B@u).shape!=f.shape:
        raise ValueError('compatible complete weak-domain operands required')
    if any(not np.isfinite(v).all() for v in (B,u,f,d)):
        raise ValueError('explicit finite weak-domain operands required')
    return f+d-B@u
