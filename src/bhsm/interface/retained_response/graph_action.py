"""Field/normal-graph pullback of existing intrinsic Higgs and area actions.

Only the four n=1, fiber-invariant normal graph directions are new. They
remain inputs, not solved physical deformation modes. Geometry q,v,m is fixed
at each actual exported node. No membrane coefficient or new interaction is
selected. This does not contain the bulk gravitational, eta, Maxwell-shape,
GHY/Hayward general-angular, fermion, exterior, or native response.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[4]/'artifacts/muon_retained_response_20261018'
from .build_higgs_response import generators, C_ORBIT, LAM, NU2, gauss_table, save_npz, maxabs
from .retained_magnetic_application import FRAME,RADIUS0,rule8,rule24,wall_data


# Variables = value(h16,g64,s4), rate(h16,s4).  No gauge-rate variable.
NVAL=84
RATE=np.r_[np.arange(16),np.arange(80,84)]

def base(raw):
    raw=np.asarray(raw,float)
    if raw.shape!=(268,) or not np.all(np.isfinite(raw)):
        raise ValueError('finite actual raw268 required')
    q=raw[:37]; v=raw[37:74]; m=raw[74:98]
    ks=np.arange(1,13); js=np.arange(12)
    cs=RADIUS0*np.exp(q[0]+q[1:13]@((-1.)**ks)+q[13:25]@((-1.)**js))
    lc=v[0]+v[1:13]@((-1.)**ks)+v[13:25]@((-1.)**js)
    return dict(q=q,v=v,m=m,cs=cs,lc=lc,s=raw[98],sd=raw[99],
        independent=raw[100:180].reshape(4,5,4)[3][[0,2,3,4]],
        H=raw[260:264],Ht=raw[264:268])

def torch_action(raw,x,rule=rule8, *, diagonal_metric_control=False, frozen_fiber_control=False):
    """Return [original intrinsic Higgs action, selected area action per gamma].

    R4=A B/sqrt(A^2+B^2); graph eta is (s+delta s)/Cstar.  The graph uses
    intrinsic material gauge traces as independent coordinates. No radial
    gauge advection is added, and no off-wall Higgs profile is invented.
    """
    import torch
    b=base(raw)
    c=lambda z: torch.as_tensor(z,dtype=x.dtype,device=x.device)
    pts,ww=rule();Y=c(2*pts); DY=c(2*np.einsum('aij,pj->pai',FRAME,pts))
    sig=b['s']+Y@x[80:84];sigdt=b['sd']+Y@x[100:104]
    grad=torch.einsum('pah,h->pa',DY,x[80:84])/b['cs']
    chi=np.pi/4+sig/b['cs'];chidot=(sigdt-b['lc']*sig)/b['cs']
    q=c(b['q']);m=c(b['m']);ks=c(np.arange(1,13));js=c(np.arange(12))
    ck=torch.cos(4*chi[:,None]*ks);cj=torch.cos(4*chi[:,None]*js)
    window=torch.sin(2*chi)**2
    u=ck@q[1:13]; w=window*(cj@q[13:25]); bb=window*(cj@q[25:37])
    radius=RADIUS0*torch.exp(q[0]);C=radius*torch.exp(u+w)
    A=radius*torch.exp(u+bb)*torch.cos(chi);B=radius*torch.exp(u-bb)*torch.sin(chi)
    N=torch.exp(ck@m[:12]);beta=torch.sin(4*chi)*(cj@m[12:])
    LF=torch.sqrt(A*A+B*B);R=A*B/LF;lam=A*A/(LF*LF)
    v=torch.cat(((chidot+beta)[:,None],grad),1)
    invdiag=torch.stack((1/N**2,-1/R**2,-1/R**2,-1/R**2),1)
    iv=invdiag*v;U=1-C*C*torch.sum(v*iv,1)
    volume=N*R**3*torch.sqrt(U)
    hinv=torch.diag_embed(invdiag)+(C*C/U)[:,None,None]*iv[:,:,None]*iv[:,None,:]
    hden=volume[:,None,None]*hinv
    if diagonal_metric_control:
        hden=torch.diag_embed(torch.diagonal(hden,dim1=1,dim2=2))
    h=c(b['H'])[None]+torch.einsum('ph,ih->pi',Y,x[:16].reshape(4,4))
    ht=c(b['Ht'])[None]+torch.einsum('ph,ih->pi',Y,x[84:100].reshape(4,4))
    ds=torch.einsum('pah,ih->pai',DY,x[:16].reshape(4,4))
    gauge=c(b['independent'])[None]+torch.einsum('ph,fch->pfc',Y,x[16:80].reshape(4,4,4))
    mech=torch.zeros((4,4),dtype=x.dtype);mech[1:,:3]=np.sqrt(8)*torch.eye(3,dtype=x.dtype,device=x.device)
    gauge=gauge+(lam-1)[:,None,None]*mech
    gr=c(generators()[1]);omega=torch.einsum('pfc,cij->pfij',gauge,gr)
    dh=torch.cat((ht[:,None],ds),1)+torch.einsum('pfij,pj->pfi',omega,h)
    kin=torch.einsum('pfk,pfg,pgk->p',dh,hden,dh)
    potential=LAM*(torch.sum(h*h,1)-NU2)**2
    sh=C_ORBIT*torch.dot(c(ww),kin-volume*potential)
    # Fiber-invariant graph of the same M8 area: R4^3 LF^3=A^3 B^3.
    fiber=(torch.sqrt(A*A+B*B))**3
    if frozen_fiber_control:
        w0=wall_data(raw); fiber=torch.full_like(fiber,float((w0['A']**2+w0['B']**2)**1.5))
    area=(-torch.dot(c(ww),volume*fiber) if frozen_fiber_control
          else -torch.dot(c(ww),N*A**3*B**3*torch.sqrt(U)))
    return torch.stack((sh,area))

def unpack_hessian(H):
    K=H[:NVAL,:NVAL]; B=np.zeros((NVAL,NVAL));M=np.zeros_like(B)
    B[:,RATE]=H[:NVAL,NVAL:];M[np.ix_(RATE,RATE)]=H[NVAL:,NVAL:]
    return M,B,K

def blocks(raw,rule=rule8):
    import torch
    x=torch.zeros(104,dtype=torch.float64,requires_grad=True)
    f=lambda v: torch_action(raw,v,rule)
    value=f(x).detach().numpy()
    J=torch.autograd.functional.jacobian(f,x,vectorize=True).detach().numpy()
    # Separate Hessians, while preserving independent original action sectors.
    out={}
    for i,name in enumerate(('Higgs','area_per_gamma')):
        H=torch.autograd.functional.hessian(lambda v:f(v)[i],x,vectorize=True).detach().numpy()
        mm,bb,kk=unpack_hessian(H)
        out.update({name+'_M':mm,name+'_B':bb,name+'_K':kk,name+'_gradient':J[i],name+'_value':value[i]})
    return out

def graph_metric(raw,s,sd,grad):
    """Independent NumPy induced-metric determinant and inverse for checks."""
    b=base(raw);ss=b['s']+s; chi=np.pi/4+ss/b['cs'];qt=b['q'];m=b['m']
    k=np.arange(1,13);j=np.arange(12); ck=np.cos(4*k*chi);cj=np.cos(4*j*chi)
    win=np.sin(2*chi)**2;u=ck@qt[1:13];ww=win*(cj@qt[13:25]);vv=win*(cj@qt[25:37])
    rad=RADIUS0*np.exp(qt[0]); C=rad*np.exp(u+ww);A=rad*np.exp(u+vv)*np.cos(chi);B=rad*np.exp(u-vv)*np.sin(chi)
    N=np.exp(ck@m[:12]);beta=np.sin(4*chi)*(cj@m[12:]);LF=np.sqrt(A*A+B*B);R=A*B/LF
    vel=np.r_[(b['sd']+sd-b['lc']*ss)/b['cs']+beta,np.asarray(grad)/b['cs']]
    h=np.diag([N*N,-R*R,-R*R,-R*R])-C*C*np.outer(vel,vel)
    return h,LF,(A*A/(LF*LF)),(A,B,N,C,R)

def literal_action(raw,coeff,rate,rule=rule24):
    """Independent NumPy complex-doublet evaluation, explicit det/inverse."""
    pts,w=rule();Y=2*pts;DY=2*np.einsum('aij,pj->pai',FRAME,pts)
    b=base(raw);gc=generators()[0];total=np.zeros(2)
    for p in range(len(pts)):
        s=Y[p]@coeff[80:84];sd=Y[p]@rate[80:84];grad=DY[p]@coeff[80:84]
        metric,LF,lam,_=graph_metric(raw,s,sd,grad)
        volume=np.sqrt(-np.linalg.det(metric));hd=volume*np.linalg.inv(metric)
        hr=b['H']+coeff[:16].reshape(4,4)@Y[p]
        htr=b['Ht']+rate[:16].reshape(4,4)@Y[p]
        dsp=np.einsum('ah,ih->ai',DY[p],coeff[:16].reshape(4,4))
        H=hr[:2]+1j*hr[2:];HT=htr[:2]+1j*htr[2:]
        DS=dsp[:,:2]+1j*dsp[:,2:]
        gg=b['independent']+np.einsum('fch,h->fc',coeff[16:80].reshape(4,4,4),Y[p])
        gg[1:,:3]+=np.sqrt(8)*(lam-1)*np.eye(3)
        omega=np.einsum('fc,cij->fij',gg,gc)
        dh=np.vstack((HT,DS))+np.einsum('fij,j->fi',omega,H)
        kinetic=np.einsum('fi,fg,gi',dh.conj(),hd,dh).real
        pot=LAM*(np.vdot(H,H).real-NU2)**2
        total[0]+=w[p]*C_ORBIT*(kinetic-volume*pot)
        total[1]-=w[p]*volume*LF**3
    return total
