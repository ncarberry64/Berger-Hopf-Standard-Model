"""Local charged-current daughter instrument, not a completed physical S matrix.

Weyl ordering agrees with the retained BHSM gamma_LR: gamma0=(0,I;I,0),
gammai=(0,sigmai;-sigmai,0), PL=diag(I,0).  C[a,b,c,d] multiplies
(nu_mu^dagger[a] mu[b]) (e^dagger[c] anti_nu_e[d]).  Neutrinos are massless.
All returned spin kernels retain parent/electron coherence.  No initial
parent spin average is built into them.  A supplied rho has trace one.
"""
from __future__ import annotations
import numpy as np
from numpy.polynomial.legendre import leggauss

PAULI=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
I2=np.eye(2,dtype=complex)
GAMMA=np.array([np.block([[np.zeros((2,2)),I2],[I2,np.zeros((2,2))]])]+[
    np.block([[np.zeros((2,2)),s],[-s,np.zeros((2,2))]]) for s in PAULI])
GAMMA5=1j*GAMMA[0]@GAMMA[1]@GAMMA[2]@GAMMA[3]
PL=(np.eye(4)-GAMMA5)/2
METRIC=np.array([1.,-1.,-1.,-1.])

def _check(C,M,m,E,n):
    C=np.asarray(C,complex);n=np.asarray(n,float)
    if C.shape!=(2,4,4,2) or not np.isfinite(C).all():
        raise ValueError('finite complete local tensor shape(2,4,4,2) required')
    if not np.isfinite([M,m,E]).all() or not 0<=m<M or not m<=E<=(M*M+m*m)/(2*M):
        raise ValueError('positive ordered masses and on-shell daughter energy required')
    if n.shape!=(3,) or not np.isfinite(n).all() or abs(n@n-1)>2e-13:
        raise ValueError('real unit electron direction required')
    return C,n

def va_tensor(coefficient=1.):
    """Unit coefficient g gives Gamma=|g|^2 M^5 f(r)/(1536 pi^3).

    The textbook GF convention is g=2 sqrt(2) GF.  This equality is a
    normalization dictionary, never a replacement of an actual BHSM tensor.
    """
    B=np.concatenate((I2[None],-PAULI),axis=0)
    C=np.zeros((2,4,4,2),complex)
    C[:,:2,:2,:]=coefficient*np.einsum('u,uab,ucd->abcd',METRIC,B,B)
    return C

def charged_spinor(M,p):
    """Positive-energy Weyl u columns with u^dagger u=2E I."""
    p=np.asarray(p,float);E=np.sqrt(M*M+p@p)
    if M<0 or E==0:raise ValueError('nonzero on-shell charged particle required')
    if M==0:
        # Canonical massive limit; square-root expression remains nonsingular E>0.
        t=np.sqrt(E)
    else:t=np.sqrt(E+M)
    sp=np.einsum('i,ijk->jk',p,PAULI)
    return np.vstack((t*I2-sp/t,t*I2+sp/t))/np.sqrt(2)

def neutrino_pair_moment(q):
    """Exact normalized two-body angular average rho_n[e,a] rho_a[d,h].

    <pn^alpha pa^beta>=q^alpha q^beta/6 + q^2 eta^alpha beta/12.
    This formula is valid for a momentum-independent local C.  A temporal
    symbol C(pn) requires its higher neutrino moments, not this static moment.
    """
    q=np.asarray(q,float)
    if q.shape!=(4,) or not np.isfinite(q).all():raise ValueError('finite real q required')
    s=q[0]**2-q[1:]@q[1:]
    if q[0]<0 or s < -2e-13*max(1.,q[0]**2):raise ValueError('future timelike/null pair q required')
    Q=q[0]*I2-np.einsum('i,ijk->jk',q[1:],PAULI)
    return (np.einsum('ea,dh->eadh',Q,Q)/6 + max(0.,s)/12*(
        np.einsum('ea,dh->eadh',I2,I2)-np.einsum('iea,idh->eadh',PAULI,PAULI)))

def joint_spin_kernel(C,*,M,m,E,direction,left_tensor=None):
    """K[r,l,s,t]=average A[r,s] conjugate(A[l,t]) for mu-minus.

    Electron output rho'[r,l]=K[r,l,s,t] rho_mu[s,t].  The rate density
    wrt dE dOmega/(4pi) is p/(64 pi^3 M) times trace(rho').
    left_tensor is the INDEPENDENT analytic left coefficient: physical
    values use conjugate(C), but complex source axes are not conjugated
    implicitly when an explicit left tensor is supplied.
    """
    C,n=_check(C,M,m,E,direction)
    L=C.conj() if left_tensor is None else np.asarray(left_tensor,complex)
    if L.shape!=C.shape or not np.isfinite(L).all():raise ValueError('complete finite left tensor required')
    if E==0:return np.zeros((2,2,2,2),complex)
    p=np.sqrt(max(0.,E*E-m*m));U=charged_spinor(M,np.zeros(3));V=charged_spinor(m,p*n)
    N=neutrino_pair_moment(np.r_[M-E,-p*n])
    return np.einsum('abcd,efgh,bs,ft,cr,gl,eadh->rlst',C,L,U,U.conj(),V.conj(),V,N,optimize=True)

def joint_spin_kernel_first(C,dC,*,M,m,E,direction,left_tensor=None,left_first=None):
    """Exact coefficient functional derivative; no outgoing/domain derivative."""
    C=np.asarray(C,complex);dC=np.asarray(dC,complex)
    if dC.shape!=C.shape or not np.isfinite(dC).all():raise ValueError('complete finite coefficient direction required')
    L=C.conj() if left_tensor is None else np.asarray(left_tensor,complex)
    dL=dC.conj() if left_first is None else np.asarray(left_first,complex)
    return (joint_spin_kernel(dC,M=M,m=m,E=E,direction=direction,left_tensor=L)+
            joint_spin_kernel(C,M=M,m=m,E=E,direction=direction,left_tensor=dL))

def joint_spin_kernel_kinematic_first(C,dC,*,M,m,E,direction,
        M_first,m_first,E_first,direction_first,left_tensor=None,left_first=None):
    """Complete real-kinematic-family JVP of the local static tensor kernel.

    The five supplied firsts are explicit, not guessed zero.  Source tensors
    may have independent analytic left firsts.  Endpoint spin-frame limits
    require a regular parameterization rather than division by p=0 here.
    Return (K_first, phase_first), phase=p/(64pi^3 M).
    """
    C,n=_check(C,M,m,E,direction);dC=np.asarray(dC,complex)
    dn=np.asarray(direction_first,float)
    if (dC.shape!=C.shape or not np.isfinite(dC).all() or dn.shape!=(3,) or
        not np.isfinite(dn).all() or abs(dn@n)>2e-12 or
        not np.isfinite([M_first,m_first,E_first]).all()):
        raise ValueError('complete coefficient and real tangent kinematic firsts required')
    L=C.conj() if left_tensor is None else np.asarray(left_tensor,complex)
    dL=dC.conj() if left_first is None else np.asarray(left_first,complex)
    if L.shape!=C.shape or dL.shape!=C.shape or not np.isfinite(L).all() or not np.isfinite(dL).all():
        raise ValueError('complete left value/first required')
    p=np.sqrt(E*E-m*m)
    if p==0:raise ValueError('regular interior momentum required for this kinematic chart')
    dp=(E*E_first-m*m_first)/p;pv=p*n;dpv=dp*n+p*dn
    U=charged_spinor(M,np.zeros(3));dU=M_first*U/(2*M)
    V=charged_spinor(m,pv);t=np.sqrt(E+m);dt=(E_first+m_first)/(2*t)
    sp=np.einsum('i,ijk->jk',pv,PAULI);dsp=np.einsum('i,ijk->jk',dpv,PAULI)
    dV=np.vstack((dt*I2-dsp/t+sp*dt/t**2,dt*I2+dsp/t-sp*dt/t**2))/np.sqrt(2)
    q=np.r_[M-E,-pv];dq=np.r_[M_first-E_first,-dpv]
    Q=q[0]*I2-np.einsum('i,ijk->jk',q[1:],PAULI)
    dQ=dq[0]*I2-np.einsum('i,ijk->jk',dq[1:],PAULI)
    ds=2*(q[0]*dq[0]-q[1:]@dq[1:])
    N=neutrino_pair_moment(q)
    dN=(np.einsum('ea,dh->eadh',dQ,Q)+np.einsum('ea,dh->eadh',Q,dQ))/6+ds/12*(
        np.einsum('ea,dh->eadh',I2,I2)-np.einsum('iea,idh->eadh',PAULI,PAULI))
    F=np.einsum('abcd,bs,cr->adrs',C,U,V.conj())
    G=np.einsum('efgh,ft,gl->ehlt',L,U.conj(),V)
    dF=(np.einsum('abcd,bs,cr->adrs',dC,U,V.conj())+
        np.einsum('abcd,bs,cr->adrs',C,dU,V.conj())+
        np.einsum('abcd,bs,cr->adrs',C,U,dV.conj()))
    dG=(np.einsum('efgh,ft,gl->ehlt',dL,U.conj(),V)+
        np.einsum('efgh,ft,gl->ehlt',L,dU.conj(),V)+
        np.einsum('efgh,ft,gl->ehlt',L,U.conj(),dV))
    result=(np.einsum('adrs,ehlt,eadh->rlst',dF,G,N)+
            np.einsum('adrs,ehlt,eadh->rlst',F,dG,N)+
            np.einsum('adrs,ehlt,eadh->rlst',F,G,dN))
    return result,(dp/M-p*M_first/M**2)/(64*np.pi**3)

def positive_muon_joint_spin_kernel(C,*,M,m,E,direction):
    """Hermitian-conjugate contact with PHYSICAL antiparticle spin labels.

    v_s=i gamma2 u_s^*.  Incoming antimuon uses v_s^dagger and outgoing
    positron uses v_r.  This conjugate placement is essential: a canonical
    negative-mass completeness alone does not define physical spin labels.
    """
    C,n=_check(C,M,m,E,direction)
    if E==0:return np.zeros((2,2,2,2),complex)
    p=np.sqrt(max(0.,E*E-m*m));B=1j*GAMMA[2]
    U=B@charged_spinor(M,np.zeros(3)).conj();V=B@charged_spinor(m,p*n).conj()
    N=neutrino_pair_moment(np.r_[M-E,-p*n])
    return np.einsum('abcd,efgh,bs,ft,cr,gl,aehd->rlst',C.conj(),C,U.conj(),U,V,V.conj(),N,optimize=True)

def parent_analyzer(K):
    """D[t,s]=sum_r K[r,r,s,t], hence trace(rho D) is the spin sum."""
    K=np.asarray(K,complex)
    if K.shape!=(2,2,2,2):raise ValueError('complete joint two-spin kernel required')
    return np.einsum('rrst->ts',K)

def va_parent_analyzer(*,M,m,E,direction,coefficient=1.,charge=-1):
    """Exact finite-electron-mass V-A analyzer; mu+ follows CP.

    Mu+ is expressed in its PHYSICAL spin frame, not in an unconverted
    negative-energy v-column label.  Its spin-scalar term is unchanged and
    its parity-asymmetric term is the opposite of mu-minus.
    """
    _,n=_check(va_tensor(),M,m,E,direction)
    if charge not in (-1,1):raise ValueError('charge +/-1 required')
    p=np.sqrt(max(0.,E*E-m*m))
    a=M*(E*(3*M*M+3*m*m-4*M*E)-2*M*m*m)
    b=M*p*(M*M+3*m*m-4*M*E)
    return (2*abs(coefficient)**2/3)*(a*I2-charge*b*np.einsum('i,ijk->jk',n,PAULI))

def va_phase_factor(r):
    if not 0<=r<1:raise ValueError('mass-squared ratio in [0,1) required')
    return 1-8*r+8*r**3-r**4-12*r*r*np.log(r) if r else 1.

def va_neutrino_analyzer(y,direction,*,mass_squared_ratio=0.,species='nu_mu',charge=-1):
    """dGamma/(dy dOmega/(4pi))/Gamma0 including finite daughter m.

    y=2E_neutral/M, Gamma0=|g|^2 M^5/(1536pi^3).  Only neutrino
    masses are neglected.  Neither spectrum is normalized by f(r) here.
    """
    r=float(mass_squared_ratio);n=np.asarray(direction,float)
    if not 0<=r<1 or not 0<=y<=1-r or n.shape!=(3,) or abs(n@n-1)>2e-13:
        raise ValueError('on-shell neutral reduced energy, mass ratio and unit direction required')
    if charge not in (-1,1):raise ValueError('charge +/-1 required')
    if y==1 and r==0:
        z=0.
    else:z=r/(1-y)
    if species=='nu_mu':
        a=2*y*y*(1-z)**2*((3-2*y)+z*(3-y))
        b=2*y*y*(1-z)**2*((1-2*y)-z*(1+y))
    elif species=='anti_nu_e':
        a=12*y*y*(1-y-r)**2/(1-y) if y!=1 else 0.
        b=a
    else:raise ValueError('actual mu-minus daughter species nu_mu or anti_nu_e required')
    return a*I2-charge*b*np.einsum('i,ijk->jk',n,PAULI)

def normalized_electron_state(K,parent_density,*,kernel_first=None,parent_first=None):
    """Conditional electron spin density and its exact quotient derivative.

    K is the Choi kernel of an instrument, not a surviving-parent density.
    It can act on one half of a correlated parent-pair spin density.
    """
    rho=np.asarray(parent_density,complex)
    if rho.shape!=(2,2) or not np.isfinite(rho).all():raise ValueError('parent 2x2 density required')
    out=np.einsum('rlst,st->rl',K,rho);weight=np.trace(out)
    if abs(weight)==0:raise ValueError('zero local event weight has no conditional spin state')
    state=out/weight
    if kernel_first is None and parent_first is None:return state,weight
    first=np.zeros((2,2),complex)
    if kernel_first is not None:first+=np.einsum('rlst,st->rl',kernel_first,rho)
    if parent_first is not None:first+=np.einsum('rlst,st->rl',K,parent_first)
    dw=np.trace(first)
    return state,weight,(first-state*dw)/weight,dw

def slash(p):
    return np.einsum('u,u,uij->ij',METRIC,np.asarray(p),GAMMA)

def literal_gamma_analyzer(p,k,pn,pa,*,M,m,coefficient=1.):
    """Independent 4x4 gamma trace; no C contraction or pair moment used."""
    U=charged_spinor(M,np.asarray(p)[1:]);rho=slash(k)+m*np.eye(4)
    out=np.zeros((2,2),complex)
    for mu in range(4):
        for nu in range(4):
            # sum e,anti spins of (bar e gamma_mu PL v)(bar v gamma_nu PL e)
            e_trace=np.trace(rho@GAMMA[mu]@PL@slash(pa)@GAMMA[nu]@PL)*METRIC[mu]*METRIC[nu]
            parent=U.conj().T@GAMMA[0]@GAMMA[nu]@PL@slash(pn)@GAMMA[mu]@PL@U
            out+=abs(coefficient)**2*e_trace*parent
    return out

def literal_invariant_analyzer(p,k,pn,pa,*,M,coefficient=1.):
    dot=lambda a,b:np.sum(METRIC*np.asarray(a)*np.asarray(b))
    p=np.asarray(p);pa=np.asarray(pa)
    if np.max(abs(p[1:]))>1e-14:raise ValueError('this spin basis formula is in the parent rest frame')
    # (p-Ms).pa=M pa0 I+M pa_vec.sigma.
    return 8*abs(coefficient)**2*dot(k,pn)*M*(pa[0]*I2+np.einsum('i,ijk->jk',pa[1:],PAULI))

def pair_momenta(*,M,m,E,n,u):
    """Boost a unit pair-CM direction u into the parent rest frame."""
    n=np.asarray(n);u=np.asarray(u);p=np.sqrt(max(0.,E*E-m*m));q0=M-E
    s=M*M+m*m-2*M*E;root=np.sqrt(max(0.,s));b=-n;d=b@u
    pnvec=root*u/2+((q0-root)*d+p)*b/2
    pn=np.r_[q0/2+p*d/2,pnvec];pa=np.r_[q0-pn[0],-p*n-pnvec]
    return pn,pa

def sphere_rule(order=5):
    z,w=leggauss(order);phi=np.arange(2*order)*np.pi/order
    normals=np.array([[np.sqrt(1-t*t)*np.cos(f),np.sqrt(1-t*t)*np.sin(f),t]for t in z for f in phi])
    return normals,np.repeat(w/(4*order),2*order)
