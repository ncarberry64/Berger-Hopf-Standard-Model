"""Exact parent-spin neutrino marginals of ANY static local charged tensor.

This consumes the same mu-minus C[a,b,c,d] convention as daughter_spin_math.
It sums the charged-daughter spin, keeps all parent coherence, includes
the electron mass exactly, and neglects neutrino masses.  It is not an
outgoing derivative or a selection of a physical BHSM local operator.
"""
from __future__ import annotations
import numpy as np
from daughter_spin_math import I2,PAULI,charged_spinor

ETA=np.array([1.,-1.,-1.,-1.])
H=np.array([np.eye(4)]+[np.block([[-a,np.zeros((2,2))],[np.zeros((2,2)),a]])for a in PAULI],complex)
B=np.concatenate((I2[None],-PAULI),axis=0)
J=np.block([[np.zeros((2,2)),I2],[I2,np.zeros((2,2))]])

def _data(C,*,M,m,E,direction,species,left_tensor):
    C=np.asarray(C,complex);n=np.asarray(direction,float)
    L=C.conj()if left_tensor is None else np.asarray(left_tensor,complex)
    if C.shape!=(2,4,4,2)or L.shape!=C.shape or not np.isfinite(C).all()or not np.isfinite(L).all():
        raise ValueError('complete finite right/left static local tensors required')
    if not np.isfinite([M,m,E]).all()or not 0<=m<M or not 0<=E<=(M*M-m*m)/(2*M):
        raise ValueError('on-shell ordered masses and tagged neutral energy required')
    if n.shape!=(3,)or not np.isfinite(n).all()or abs(n@n-1)>2e-13:
        raise ValueError('real unit tagged-neutral direction required')
    if species not in ('nu_mu','anti_nu_e'):raise ValueError('actual mu-minus neutral daughter species required')
    q=np.r_[M-E,-E*n];s=M*M-2*M*E
    z=m*m/s if s>0 else 0.
    # An exactly specified massive threshold has zero two-body phase space.
    if m>0 and E==(M*M-m*m)/(2*M):z=1.
    rho=E*I2-E*np.einsum('i,ijk->jk',n,PAULI)
    U=charged_spinor(M,np.zeros(3))
    return C,L,q,s,z,rho,U

def electron_other_neutrino_moment(q,s,z,m):
    """P[g,c,d,h]=<rho_e[g,c] rho_other[d,h]> in pair CM angles.

    <ke^alpha pother^beta>=(1-z)(1+2z) q^alpha q^beta/6
        +s(1-z)^2 eta^alpha beta/12,
    <pother^alpha>=(1-z)q^alpha/2, z=m^2/s.
    The m off-diagonal electron term is retained with that FIRST moment.
    """
    Q4=np.einsum('u,ugc->gc',q,H);Q2=np.einsum('u,udh->dh',q,B)
    return ((1-z)*(1+2*z)/6*np.einsum('gc,dh->gcdh',Q4,Q2)+
        s*(1-z)**2/12*np.einsum('u,ugc,udh->gcdh',ETA,H,B)+
        m*(1-z)/2*np.einsum('gc,dh->gcdh',J,Q2))

def neutrino_parent_analyzer(C,*,M,m,E,direction,species,left_tensor=None):
    """Unweighted 2x2 D: rate=prefactor*trace(rho_parent D).

    prefactor=E(1-m^2/q^2)/(64pi^3 M), relative to dE dOmega/(4pi).
    The returned D[t,s] retains all parent off-diagonal spin entries.
    Explicit left_tensor is analytically independent, not auto-conjugated.
    """
    C,L,q,s,z,rho,U=_data(C,M=M,m=m,E=E,direction=direction,species=species,left_tensor=left_tensor)
    P=electron_other_neutrino_moment(q,s,z,m)
    if species=='nu_mu':
        return np.einsum('abcd,efgh,bs,ft,ea,gcdh->ts',C,L,U,U.conj(),rho,P,optimize=True)
    return np.einsum('abcd,efgh,bs,ft,gcea,dh->ts',C,L,U,U.conj(),P,rho,optimize=True)

def neutrino_phase_prefactor(*,M,m,E):
    """Density wrt dE dOmega/(4pi); no initial-spin average included."""
    if not np.isfinite([M,m,E]).all()or not 0<=m<M or not 0<=E<=(M*M-m*m)/(2*M):
        raise ValueError('ordered masses and tagged-neutral energy required')
    s=M*M-2*M*E;z=m*m/s if s>0 else 0.
    if m>0 and E==(M*M-m*m)/(2*M):return 0.
    return E*(1-z)/(64*np.pi**3*M)

def neutrino_parent_analyzer_first(C,dC,*,M,m,E,direction,species,left_tensor=None,left_first=None):
    """Exact coefficient functional first at HELD kinematics only."""
    C=np.asarray(C,complex);dC=np.asarray(dC,complex)
    L=C.conj()if left_tensor is None else np.asarray(left_tensor,complex)
    dL=dC.conj()if left_first is None else np.asarray(left_first,complex)
    if dC.shape!=C.shape or dL.shape!=C.shape or not np.isfinite(dC).all()or not np.isfinite(dL).all():
        raise ValueError('complete finite coefficient firsts required')
    kw=dict(M=M,m=m,E=E,direction=direction,species=species)
    return (neutrino_parent_analyzer(dC,left_tensor=L,**kw)+
            neutrino_parent_analyzer(C,left_tensor=dL,**kw))
