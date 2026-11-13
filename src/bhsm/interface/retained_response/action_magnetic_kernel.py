"""Magnetic derivative of the original five-component gauge-action Hessian.

Source: BHSM PR465 revision 70e82fd4, muon_baton_zoo_original_validation.py
and muon_electromagnetic_soft_magnetic_source.py. These formulas reproduce
source-defined local action expressions; they are NOT an imported repository
checkout, a physical base solution, or the native quantum operator.
Analytic bilinear (transpose) pairings are used, never conjugated source jets.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class FieldJet:
    """Local connection and ordinary derivatives, all explicit.

    Each value/time/radial shape is (...,5,4); angular is (...,3,5,4).
    Components are (At,Ar,A1,A2,A3) in the retained unit-Tr16 frame.
    """
    value: np.ndarray
    time: np.ndarray
    radial: np.ndarray
    angular: np.ndarray

    def __post_init__(self):
        names=('value','time','radial','angular')
        data=[np.asarray(getattr(self,k),dtype=complex) for k in names]
        if data[0].shape[-2:]!=(5,4):
            raise ValueError('full five-component/four-generator field required')
        for a in data[1:3]:
            if a.shape!=data[0].shape: raise ValueError('field derivative shape mismatch')
        if data[3].shape!=data[0].shape[:-2]+(3,5,4):
            raise ValueError('angular shape mismatch')
        if any(not np.isfinite(a).all() for a in data):
            raise ValueError('finite field and derivatives required')
        for k,a in zip(names,data): object.__setattr__(self,k,a)

    def plus(self,other,scale=1):
        return FieldJet(*(getattr(self,k)+scale*getattr(other,k)
                          for k in ('value','time','radial','angular')))


def zero_field(shape=()):
    """Explicit zero field for declared algebra controls only."""
    a=np.zeros(tuple(shape)+(5,4),complex)
    return FieldJet(a,a.copy(),a.copy(),np.zeros(tuple(shape)+(3,5,4),complex))


def bracket(a,b):
    """Original unit-Tr16 [H_i,H_j]=eps_ijk H_k/sqrt(2); U(1) central."""
    a,b=np.asarray(a),np.asarray(b)
    out=np.zeros(np.broadcast_shapes(a.shape,b.shape),complex)
    out[...,:3]=np.cross(a[...,:3],b[...,:3])/np.sqrt(2)
    return out


def curvature(j):
    a,at,ar,ea=j.value,j.time,j.radial,j.angular
    x=at[...,1,:]-ar[...,0,:]+bracket(a[...,0,:],a[...,1,:])
    t=at[...,2:,:]-ea[...,:,0,:]+bracket(a[...,0,None,:],a[...,2:,:])
    z=ar[...,2:,:]-ea[...,:,1,:]+bracket(a[...,1,None,:],a[...,2:,:])
    b=2*a[...,2:,:].copy()
    for i,k,l in ((0,1,2),(1,2,0),(2,0,1)):
        b[...,i,:]+=ea[...,k,l+2,:]-ea[...,l,k+2,:]+bracket(a[...,k+2,:],a[...,l+2,:])
    return (x,t,z,b)


def curvature_second(u,v):
    a,b=u.value,v.value
    x=bracket(a[...,0,:],b[...,1,:])+bracket(b[...,0,:],a[...,1,:])
    t=bracket(a[...,0,None,:],b[...,2:,:])+bracket(b[...,0,None,:],a[...,2:,:])
    z=bracket(a[...,1,None,:],b[...,2:,:])+bracket(b[...,1,None,:],a[...,2:,:])
    m=np.zeros(np.broadcast_shapes(a[...,2:,:].shape,b[...,2:,:].shape),complex)
    for i,k,l in ((0,1,2),(1,2,0),(2,0,1)):
        m[...,i,:]=bracket(a[...,k+2,:],b[...,l+2,:])+bracket(b[...,k+2,:],a[...,l+2,:])
    return (x,t,z,m)


def curvature_first(base,u):
    # Exact polynomial polarization: F(A+u)-F(A)-F''(u,u)/2.
    # For improved cancellation use the analytic linear derivative below.
    a,v=base.value,u.value
    at,ar,ea=u.time,u.radial,u.angular
    x=at[...,1,:]-ar[...,0,:]+bracket(v[...,0,:],a[...,1,:])+bracket(a[...,0,:],v[...,1,:])
    t=at[...,2:,:]-ea[...,:,0,:]+bracket(v[...,0,None,:],a[...,2:,:])+bracket(a[...,0,None,:],v[...,2:,:])
    z=ar[...,2:,:]-ea[...,:,1,:]+bracket(v[...,1,None,:],a[...,2:,:])+bracket(a[...,1,None,:],v[...,2:,:])
    b=2*v[...,2:,:].copy()
    for i,k,l in ((0,1,2),(1,2,0),(2,0,1)):
        b[...,i,:]+=ea[...,k,l+2,:]-ea[...,l,k+2,:]+bracket(v[...,k+2,:],a[...,l+2,:])+bracket(a[...,k+2,:],v[...,l+2,:])
    return (x,t,z,b)


def pairing(f,g,densities):
    """k X.X+e(T-beta Z).(T-beta Z)-r Z.Z-d B.B, without conjugation."""
    d=np.asarray(densities,complex)
    if d.shape[-1]!=5 or not np.isfinite(d).all(): raise ValueError('five explicit metric densities required')
    e,r,dang,k,beta=np.moveaxis(d,-1,0)
    x,t,z,b=f;xx,tt,zz,bb=g
    dot=lambda a,c:np.sum(a*c,axis=(-2,-1))
    y=t-beta[...,None,None]*z; yy=tt-beta[...,None,None]*zz
    return k*np.sum(x*xx,axis=-1)+e*dot(y,yy)-r*dot(z,zz)-dang*dot(b,bb)


def pairing_first(f,g,densities,density_first):
    e,r,da,k,beta=np.moveaxis(np.asarray(densities,complex),-1,0)
    eh,rh,dah,kh,betah=np.moveaxis(np.asarray(density_first,complex),-1,0)
    x,t,z,b=f;xx,tt,zz,bb=g
    dot=lambda a,c:np.sum(a*c,axis=(-2,-1))
    y=t-beta[...,None,None]*z;yy=tt-beta[...,None,None]*zz
    return (kh*np.sum(x*xx,axis=-1)+eh*dot(y,yy)
        -e*betah*(dot(z,yy)+dot(y,zz))-rh*dot(z,zz)-dah*dot(b,bb))


def local_action(base,densities):
    f=curvature(base);return pairing(f,f,densities)/2


def local_hessian(base,u,v,densities):
    return (pairing(curvature_first(base,u),curvature_first(base,v),densities)
            +pairing(curvature(base),curvature_second(u,v),densities))


def magnetic_hessian_parts(base,probe,u,v,densities):
    """Three exact placements of one probe in the original local Hessian."""
    return dict(
        probe_left_variation=pairing(curvature_second(probe,u),curvature_first(base,v),densities),
        probe_right_variation=pairing(curvature_first(base,u),curvature_second(probe,v),densities),
        probe_background_curvature=pairing(curvature_first(base,probe),curvature_second(u,v),densities))


def magnetic_hessian(base,probe,u,v,densities):
    return sum(magnetic_hessian_parts(base,probe,u,v,densities).values())


def total_local_hessian_first(*,base,base_first,u,v,u_first,v_first,
                              densities,density_first,weight,weight_first):
    """Total first of this LOCAL weak functional; every changing input supplied.

    Trace/coframe/history/interface/native derivatives must be constructed by
    callers. This function does not certify or silently manufacture them.
    """
    f,fu,fv,fuv=(curvature(base),curvature_first(base,u),curvature_first(base,v),curvature_second(u,v))
    held=magnetic_hessian(base,base_first,u,v,densities)
    met=pairing_first(fu,fv,densities,density_first)+pairing_first(f,fuv,densities,density_first)
    moving_tests=local_hessian(base,u_first,v,densities)+local_hessian(base,u,v_first,densities)
    return weight*(held+met+moving_tests)+weight_first*local_hessian(base,u,v,densities)


def epsilon():
    e=np.zeros((3,3,3),int)
    for i,j,k in ((0,1,2),(1,2,0),(2,0,1)):e[i,j,k]=1;e[i,k,j]=-1
    return e


def higgs_bloch(H):
    h=np.asarray(H,complex)
    if h.shape!=(2,) or not np.isfinite(h).all() or np.vdot(h,h).real<=0:
        raise ValueError('nonzero finite H; no default Higgs state')
    p=np.outer(h,h.conj())/np.vdot(h,h).real
    pauli=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    return np.einsum('aij,ji->a',pauli,p).real


def anchor_photon_contact(bloch):
    """K_B/(angular_density*e*R4^2), in (gauge20,Hreal4) local value order.

    Fixed observation frame and direct fixed-background magnetic probe only.
    A_B=0 at the anchor, F_B=e R4^2 Q_H epsilon. The three source axes
    and charged adjoint directions are kept. Scalar rows are zero ONLY for
    this local gauge-curvature term. This is not the full 24-leg Green.
    """
    n=np.asarray(bloch,float)
    if n.shape!=(3,) or not np.isfinite(n).all() or abs(n@n-1)>1e-11:
        raise ValueError('unit Bloch vector of nonzero actual H required')
    ep=epsilon()
    out=np.zeros((3,24,24))
    for k,i,j,a,b,c in np.ndindex((3,3,3,3,3,3)):
        out[k,4*(2+i)+a,4*(2+j)+b]+=ep[k,i,j]*ep[a,b,c]*n[c]
    return out


def anchored_probe(axis,charge_coefficients):
    """Unit eR4^2 magnetic jet at observation point, not a global field solve."""
    if axis not in (0,1,2):raise ValueError('three magnetic axes only')
    s=np.asarray(charge_coefficients,complex)
    if s.shape!=(4,):raise ValueError('four source-owned charge coefficients required')
    a=np.zeros((5,4),complex);ea=np.zeros((3,5,4),complex);ep=epsilon()
    for j,i in np.ndindex((3,3)): ea[j,i+2]=-.5*ep[i,j,axis]*s
    return FieldJet(a,a.copy(),a.copy(),ea)
