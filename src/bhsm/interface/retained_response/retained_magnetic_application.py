"""Spatial magnetic third variation on published BHSM wall backgrounds.

Not a full field/retarded/quantum operator. Imports source-defined curvature
routines from the preceding supplied package. Reconstructs the original wall
geometry from the archived raw268, preserving the nonlinear normal map.
Matrices are per e_can; e_can is NOT assigned a physical value here.
"""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np
from .action_magnetic_kernel import FieldJet, magnetic_hessian, local_action, epsilon, curvature, curvature_first, curvature_second

RADIUS0=(343./5.)**(1./6.)
M=np.sqrt(8)*np.column_stack([np.eye(3),np.zeros(3)])
FRAME=np.array([
 [[0,0,0,1],[0,0,1,0],[0,-1,0,0],[-1,0,0,0]],
 [[0,0,1,0],[0,0,0,-1],[-1,0,0,0],[0,1,0,0]],
 [[0,1,0,0],[-1,0,0,0],[0,0,0,1],[0,0,-1,0]]],float)

def wall_data(raw):
    r=np.asarray(raw)
    if r.shape!=(268,) or not np.isfinite(r).all():raise ValueError('actual finite raw268 required')
    q,v,m=r[:37],r[37:74],r[74:98]
    s,sd=r[98:100]
    ks=np.arange(1,13);js=np.arange(12)
    cstar=RADIUS0*np.exp(q[0]+q[1:13]@((-1.)**ks)+q[13:25]@((-1.)**js))
    lcstar=v[0]+v[1:13]@((-1.)**ks)+v[13:25]@((-1.)**js)
    chi=np.pi/4+s/cstar
    wallrate=(sd-lcstar*s)/cstar
    ck,cj=np.cos(4*ks*chi),np.cos(4*js*chi)
    sk,sj=np.sin(4*ks*chi),np.sin(4*js*chi)
    window=np.sin(2*chi)**2
    u=q[1:13]@ck;w=window*(q[13:25]@cj);vb=window*(q[25:37]@cj)
    radius=RADIUS0*np.exp(q[0]);C=radius*np.exp(u+w)
    A=radius*np.exp(u+vb)*np.cos(chi);B=radius*np.exp(u-vb)*np.sin(chi)
    N=np.exp(m[:12]@ck);bet=np.sin(4*chi)*(m[12:]@cj)
    LF=np.sqrt(A*A+B*B);R4=A*B/LF;lam=A*A/(LF*LF)
    U=C*(wallrate+bet)/N;lapse=N*np.sqrt(1-U*U)
    ak=-1/(16*cstar)
    sigma0=-.5+2*chi/np.pi-np.sin(4*chi)/(2*np.pi)
    sigma1=ak*(52*np.sin(2*chi)-14*np.sin(6*chi)-2*np.sin(10*chi))/np.pi
    sigma2=ak*ak*(982*np.sin(4*chi)-256*np.sin(8*chi)-140*np.sin(12*chi)-12.5*np.sin(16*chi))/np.pi
    sigma=sigma0+s*sigma1+s*s*sigma2/2
    material_jac=4*chi/np.pi
    common=2*np.pi**4*LF**5*(1-4*sigma*sigma)
    dang=material_jac*common*N*(C/2)/R4
    independent=r[100:180].reshape(4,5,4)[3].copy()
    conn=independent.copy();conn[2:]+=M*(lam-1)
    # Analytic continuation of real H coordinates; do not conjugate a complex source.
    a,b,c,d=r[260:264];nH=a*a+b*b+c*c+d*d
    bloch=np.array([2*(a*b+c*d),2*(a*d-c*b),a*a+c*c-b*b-d*d])/nH
    charge=np.r_[-np.sqrt(2)*bloch,np.sqrt(10/3)]
    return dict(R4=R4,lapse=lapse,A=A,B=B,C=C,ambient_lapse=N,lam=lam,
                chi=chi,wallrate=wallrate,dang=dang,sigma=sigma,charge=charge,
                bloch=bloch,connection=conn,independent_connection=independent,
                prefactor_per_e=dang*R4**2)


def rule24():
    import itertools
    return np.array(list(itertools.product([-.5,.5],repeat=4))+list(np.eye(4))+list(-np.eye(4))),np.full(24,1/24)


def rule8():
    return np.r_[np.eye(4),-np.eye(4)],np.full(8,1/8)


def fields(raw,points):
    d=wall_data(raw);x=np.asarray(points);p=len(x)
    base=np.broadcast_to(d['connection'],(p,1,1,5,4)).copy()
    z=np.zeros_like(base)
    base=FieldJet(base,z,z.copy(),np.zeros((p,1,1,3,5,4),complex))
    # Source's q=(-x3,-x2,-x1) in the owned right frame.
    quat=-x[:,[3,2,1]];dq=-np.einsum('aij,pj->pai',FRAME,x)[:,:,[3,2,1]]
    ep=epsilon();probes=[]
    for axis in range(3):
        b=np.zeros((p,1,1,5,4),complex);ea=np.zeros((p,1,1,3,5,4),complex)
        b[:,0,0,2:]=-0.5*d['R4']**2*np.einsum('ij,pj,c->pic',ep[:,:,axis],quat,d['charge'])
        ea[:,0,0,:,2:]=-0.5*d['R4']**2*np.einsum('ij,paj,c->paic',ep[:,:,axis],dq,d['charge'])
        probes.append(FieldJet(b,np.zeros_like(b),np.zeros_like(b),ea))
    y=np.c_[np.ones(p),2*x]
    ey=np.concatenate([np.zeros((p,3,1)),2*np.einsum('aij,pj->pai',FRAME,x)],axis=-1)
    ident=np.eye(20).reshape(20,5,4)
    tv=np.einsum('ph,afc->phafc',y,ident).reshape(p,100,5,4)
    te=np.einsum('pjh,afc->pjhafc',ey,ident).reshape(p,3,100,5,4).transpose(0,2,1,3,4)
    tests_left=FieldJet(tv[:,:,None],np.zeros_like(tv[:,:,None]),np.zeros_like(tv[:,:,None]),te[:,:,None])
    tests_right=FieldJet(tv[:,None],np.zeros_like(tv[:,None]),np.zeros_like(tv[:,None]),te[:,None])
    dens=np.array([0,0,d['dang'],0,0],dtype=complex)
    return d,base,probes,tests_left,tests_right,dens


def angular_matrix(raw,rule=rule8):
    x,w=rule();d,b,p,u,v,den=fields(raw,x)
    matrices=np.array([np.einsum('p,pij->ij',w,magnetic_hessian(b,s,u,v,den)) for s in p])
    return matrices,d


def unpack_point(field,p,left_index=None,right_index=None):
    if left_index is None and right_index is None: idx=(p,0,0)
    elif left_index is not None: idx=(p,left_index,0)
    else:idx=(p,0,right_index)
    return FieldJet(*(getattr(field,k)[idx] for k in ('value','time','radial','angular')))


def source_vector_application(raw,coefficients,rule=rule8):
    """Original cubic magnetic forcing for an explicitly supplied test vector.

    These coefficients are gauge variation amplitudes, not physical spin states.
    No implicit momentum, state, or retarded solve is supplied by this map.
    """
    c=np.asarray(coefficients)
    if c.shape!=(100,):raise ValueError('all 100 angular/value coefficient entries required')
    matrix,_=angular_matrix(raw,rule)
    return matrix@c
