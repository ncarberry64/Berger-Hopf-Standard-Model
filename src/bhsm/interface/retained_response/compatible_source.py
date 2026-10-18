"""Source-derived even-harmonic lepton wall load and explicit first/mixed jets.

Source anchor: BHSM PR465 00f9d781feb96914f5a1226cba70d12ae252837b.
This module constructs finite operator maps; it does not choose physical packets,
an inherited state, an outgoing/native domain, or a coupled solution.
All primitive jets are explicit. No missing derivative is filled with zero.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import itertools
import math
import numpy as np
from sympy import Rational
from sympy.physics.wigner import clebsch_gordan

SOURCE_REVISION = '00f9d781feb96914f5a1226cba70d12ae252837b'
ROW_ORDER = 'radial4,material_field5(At,Ar,A1,A2,A3),unitTr16_generator4,real_even_harmonic10'

@dataclass(frozen=True)
class Jet:
    """Value, two first variations and the mixed variation; all required."""
    value: np.ndarray
    h: np.ndarray
    k: np.ndarray
    hk: np.ndarray
    def __post_init__(self):
        arrays = [np.asarray(x) for x in (self.value,self.h,self.k,self.hk)]
        if any(x.shape != arrays[0].shape or not np.isfinite(x).all() for x in arrays):
            raise ValueError('finite equal-shaped value/h/k/hk operands required')
        for key,x in zip(('value','h','k','hk'),arrays):
            object.__setattr__(self,key,x)
    def slots(self):
        return (self.value,self.h,self.k,self.hk)


def constant(x):
    """Use only when this variable is explicitly fixed on the chosen path."""
    v=np.asarray(x)
    return Jet(v,np.zeros_like(v),np.zeros_like(v),np.zeros_like(v))


def einsum_jet(equation, *factors):
    """Leibniz rule, including both orders of the two distinct variations."""
    if not factors or any(not isinstance(x,Jet) for x in factors):
        raise TypeError('every factor must carry all four jets')
    vals=[x.value for x in factors]
    call=lambda a: np.einsum(equation,*a,optimize=True)
    zero=call(vals)
    first=[]
    for key in ('h','k'):
        total=np.zeros_like(zero,dtype=np.result_type(zero,complex))
        for i,f in enumerate(factors):
            v=list(vals);v[i]=getattr(f,key);total+=call(v)
        first.append(total)
    mixed=np.zeros_like(first[0])
    for i,fi in enumerate(factors):
        for j,fj in enumerate(factors):
            v=list(vals)
            if i==j:v[i]=fi.hk
            else:v[i]=fi.h;v[j]=fj.k
            mixed+=call(v)
    return Jet(zero,first[0],first[1],mixed)


def scalar_labels(nmax):
    return [(n,m,k) for n in range(nmax+1) for m in range(n,-n-1,-2) for k in range(n,-n-1,-2)]


def real_labels(nmax):
    seen=set();out=[]
    for n,m,k in scalar_labels(nmax):
        if (n,m,k) in seen:continue
        seen.update(((n,m,k),(n,-m,-k)))
        out.extend([(n,m,k,'self')] if m==k==0 else [(n,m,k,'real'),(n,m,k,'imag')])
    return out


def real_transform(nmax):
    labels=scalar_labels(nmax);index={v:i for i,v in enumerate(labels)}
    u=np.zeros((len(labels),len(labels)),complex)
    for col,(n,m,k,part) in enumerate(real_labels(nmax)):
        i=index[n,m,k]
        if part=='self':u[i,col]=1;continue
        j=index[n,-m,-k];sgn=(-1)**((m-k)//2)
        if part=='real':u[i,col]=1/math.sqrt(2);u[j,col]=sgn/math.sqrt(2)
        else:u[i,col]=-1j/math.sqrt(2);u[j,col]=1j*sgn/math.sqrt(2)
    return u


def scalar_values(points, nmax):
    """Same normalized conjugate Wigner convention as the repository."""
    g=np.asarray(points,complex);a,b,c,d=g[:,0,0],g[:,0,1],g[:,1,0],g[:,1,1]
    if g.shape[1:]!=(2,2) or np.max(abs(g.conj().swapaxes(-1,-2)@g-np.eye(2)))>2e-12:
        raise ValueError('unitary SU2 point matrices required')
    all_values=[]
    for n in range(nmax+1):
        D=np.zeros((len(g),n+1,n+1),complex)
        for row in range(n+1):
            for col in range(n+1):
                scale=math.sqrt(math.comb(n,col)/math.comb(n,row))
                for ell in range(max(0,row-(n-col)),min(row,col)+1):
                    p=row-ell
                    D[:,row,col]+=scale*math.comb(n-col,p)*math.comb(col,ell)*(
                        a**(n-col-p)*c**p*b**(col-ell)*d**ell)
        all_values.append(math.sqrt(n+1)*D.conj().reshape(len(g),-1))
    return np.concatenate(all_values,axis=1)


def su2_from_quaternions(q):
    q=np.asarray(q,float);z1=q[:,0]+1j*q[:,1];z2=q[:,2]+1j*q[:,3]
    g=np.empty((len(q),2,2),complex)
    g[:,0,0]=z1;g[:,0,1]=z2;g[:,1,0]=-z2.conj();g[:,1,1]=z1.conj()
    return g


def quadrature24():
    q=np.array(list(itertools.product([-.5,.5],repeat=4))+list(np.eye(4))+list(-np.eye(4)))
    return su2_from_quaternions(q),np.full(24,1/24),q


def haar_rule(degree):
    """Degree-requested product Haar rule, not an error enclosure for packets."""
    if degree<0:raise ValueError('nonnegative polynomial degree required')
    p=(degree//2+2)//2;nt=degree+1
    x,w=np.polynomial.legendre.leggauss(max(1,p));x=(x+1)/2;w=w/2
    angles=2*np.pi*np.arange(nt)/nt
    X,A,B=np.meshgrid(x,angles,angles,indexing='ij')
    q=np.column_stack((np.sqrt(X.ravel())*np.cos(A.ravel()),np.sqrt(X.ravel())*np.sin(A.ravel()),
                       np.sqrt(1-X.ravel())*np.cos(B.ravel()),np.sqrt(1-X.ravel())*np.sin(B.ravel())))
    return su2_from_quaternions(q),np.repeat(w,nt*nt)/(nt*nt),q


def even_values(points):
    indices=[i for i,x in enumerate(real_labels(2)) if x[0] in (0,2)]
    y=scalar_values(points,2)@real_transform(2)
    if np.max(abs(y[:,indices].imag))>2e-12:raise ArithmeticError('real even harmonics not real')
    return y[:,indices].real

@lru_cache(None)
def cg(n1,m1,n2,m2,nt,mt):
    return clebsch_gordan(Rational(n1,2),Rational(n2,2),Rational(nt,2),
                         Rational(m1,2),Rational(m2,2),Rational(mt,2))


def even_multiplication(nin=1):
    """All reached outputs n<=nin+2; no projection back into input space."""
    source=scalar_labels(nin);target=scalar_labels(nin+2)
    gauge=scalar_labels(2);u=real_transform(2)
    ids=[i for i,l in enumerate(real_labels(2)) if l[0]%2==0]
    raw=np.zeros((len(gauge),len(target),len(source)),complex)
    for gi,(ng,mg,kg) in enumerate(gauge):
        if ng%2:continue
        for si,(ns,ms,ks) in enumerate(source):
            for ti,(nt,mt,kt) in enumerate(target):
                if not abs(ns-ng)<=nt<=ns+ng or (ns+ng-nt)%2:continue
                if mt!=ms+mg or kt!=ks+kg:continue
                raw[gi,ti,si]=math.sqrt((ns+1)*(ng+1)/(nt+1))*float(
                    cg(ns,ms,ng,mg,nt,mt)*cg(ns,ks,ng,kg,nt,kt))
    real=np.einsum('gh,gts->hts',u[:,ids],raw)
    return dict(tensor=real,input_labels=source,output_labels=target,
                source_labels=[real_labels(2)[i] for i in ids])


def right_mode_values(q):
    """Repository right-frame formulas, retained mode order and axes."""
    m=np.array([
        [[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]],
        [[0,0,-1,0],[0,0,0,1],[1,0,0,0],[0,-1,0,0]],
        [[0,-1,0,0],[1,0,0,0],[0,0,0,1],[0,0,-1,0]],
        [[0,0,-1,0],[0,0,0,-1],[1,0,0,0],[0,1,0,0]]],float)
    generic=np.concatenate((m[:2],np.array([[[0,0,0,-1],[0,0,-1,0],[0,1,0,0],[1,0,0,0]]])),axis=0)
    l=-generic[[2,1,0]];c=np.einsum('aij,kil->akjl',m,l)
    return np.einsum('pi,akij,pj->pak',q,c,q)


def mode_coefficients():
    g,w,q=quadrature24();y=even_values(g);v=right_mode_values(q)
    return np.einsum('ph,p,pai->hai',y,w,v)


def retained_representation():
    """Live unit-Tr16 full18 owner; no state or pole is selected."""
    from ..muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    from ..muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    G=lepton_unit_trace_gauge_representation()['generators']
    alpha=lepton_current_hilbert_representation()['alpha']
    action=np.zeros((5,4,18,18),complex)
    action[0]=1j*G
    action[2:]=1j*np.einsum('aij,cjk->acik',alpha,G)
    return G,alpha,action



def original_pair_algebra():
    """Exact one-electron/one-positron unpolarized finite pair density."""
    annih=np.zeros((4,16,16),complex)
    for i in range(4):
        for state in range(16):
            if (state>>i)&1:
                annih[i,state^(1<<i),state]=(-1)**((state&((1<<i)-1)).bit_count())
    rho=np.zeros((16,16),complex)
    for s,t in itertools.product(range(2),repeat=2):
        state=(1<<s)|(1<<(2+t));rho[state,state]=.25
    eta=np.array([annih[0],annih[1],annih[2].conj().T,annih[3].conj().T])
    ref=np.diag([0.,0.,1.,1.])
    B=np.array([[eta[i].conj().T@eta[j]-ref[i,j]*np.eye(16) for j in range(4)]for i in range(4)])
    mean=np.einsum('ab,ijba->ij',rho,B)
    second=np.einsum('ab,ijbc,klca->ijkl',rho,B,B)
    return dict(rho=rho,eta=eta,B=B,reference=ref,mean=mean,second=second)


def ratio_jet(n,r):
    """Exact N/R two-jet with independent nonzero radius input."""
    if np.any(r.value==0):raise ValueError('nonzero radius required')
    inv=Jet(1/r.value,-r.h/r.value**2,-r.k/r.value**2,
            2*r.h*r.k/r.value**3-r.hk/r.value**2)
    return einsum_jet('p,p->p',n,inv)


def action_vertices(n,r,base_vertices):
    """Material At has no lapse; Ar has no direct intrinsic pullback.

    Valid for the bound material trace convention At_ref, unit-S3 Ai.
    A general moving trace/incidence must be supplied in the input maps.
    """
    if n.value.shape!=r.value.shape or n.value.ndim!=1:
        raise ValueError('matching pointwise lapse/radius jets required')
    base=np.asarray(base_vertices,complex)
    if base.shape!=(5,4,18,18):raise ValueError('source-defined full18 action vertices required')
    ratio=ratio_jet(n,r);values=[]
    for i,x in enumerate(ratio.slots()):
        v=np.zeros((len(x),5,4,18,18),complex)
        if i==0:v[:,0]=base[0]
        v[:,2:]=x[:,None,None,None,None]*base[2:][None]
        values.append(v)
    return Jet(*values)


def wall_source_jet(*,left_packets,right_packets,weights,wall_values,harmonics,
                    lapse,radius,base_vertices,pair_mean):
    """Evaluate direct intrinsic lepton action load in all 800 original rows.

    Shapes: L(p,4,18), R(p,18,4), weights(p), wall(p,4), Y(p,10).
    L is an independent analytic dual jet; do not conjugate a complex parameter.
    weights must contain each action/clock/density factor exactly once. They
    are not automatically the source-free bulk Maxwell normalization.
    All fields, maps, density and response jets are mandatory inputs.
    """
    p=len(weights.value)
    shapes=((left_packets,(p,4,18)),(right_packets,(p,18,4)),
            (wall_values,(p,4)),(harmonics,(p,10)),(pair_mean,(4,4)))
    if any(a.value.shape!=s for a,s in shapes):raise ValueError('incompatible wall/current row ordering')
    gamma=action_vertices(lapse,radius,base_vertices)
    result=einsum_jet('p,pb,ph,pia,pfcad,pdj,ij->bfch',
        weights,wall_values,harmonics,left_packets,gamma,right_packets,pair_mean)
    return dict(value_load=Jet(*(a.reshape(800) for a in result.slots())),
                rate_load=constant(np.zeros(800,complex)),
                rate_zero_scope='direct intrinsic matter variation at fixed sections has no connection-time-derivative',
                physical_admission=False,
                excluded_terms=['native relative current','inherited absolute reference current',
                                'full moving two-trace/interface response','other action-coupled currents'])


def seed_pullback(inclusion, original_load):
    """Both inclusion motion and full source motion; not the old eight source."""
    if inclusion.value.shape!=(800,16) or original_load.value.shape!=(800,):
        raise ValueError('new sixteen-column source and original 800 rows required')
    return einsum_jet('ia,i->a',inclusion,original_load)


def check_cauchy_jet(left,right,weights,tolerance=2e-10):
    gram=einsum_jet('p,pia,paj->ij',weights,left,right)
    residuals=[float(np.max(abs(gram.value-np.eye(4))))]+[float(np.max(abs(a)))for a in gram.slots()[1:]]
    return {'residuals_value_h_k_hk':residuals,'passes_at_tested_scope':max(residuals)<=tolerance,
            'physical_polarization_or_Dirac_solution_proved':False}


def require_complete_physical_operands(receipt):
    """Never promote this finite current derivative to full outgoing admission."""
    names=('physical_packet_sections','physical_packet_jets','collision_incidence_jets',
           'moving_interface_jets','native_relative_source_jets','inherited_reference_or_bound',
           'compatible_retarded_history_solution','independent_full_outgoing_derivative')
    missing=[name for name in names if receipt.get(name) is not True]
    return {'complete_physical_source_application':not missing,'unresolved':missing,
            'coupled_correction_permitted':not missing}


def reciprocal_jet(x):
    if np.any(x.value==0):raise ValueError('nonzero denominator required')
    return Jet(1/x.value,-x.h/x.value**2,-x.k/x.value**2,
               2*x.h*x.k/x.value**3-x.hk/x.value**2)


def higgs_charge_jet(right,left):
    """Normalized Higgs axis in the existing unit-Tr16 generator coordinates.

    Independent left leaf is required under analytic continuation. This is
    a local homogeneous fiber map, not bulk polarization or state selection.
    """
    if right.value.shape!=(2,) or left.value.shape!=(2,):raise ValueError('H doublet leaves required')
    norm=einsum_jet('a,a->',left,right)
    outer=einsum_jet('a,b->ab',right,left)
    projector=einsum_jet('ab,->ab',outer,reciprocal_jet(norm))
    sigma=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    bloch=einsum_jet('cab,ba->c',constant(sigma),projector)
    slots=[]
    for j,b in enumerate(bloch.slots()):slots.append(np.r_[-np.sqrt(2)*b,np.sqrt(10/3) if j==0 else 0.])
    return Jet(*slots)


def make_seed_inclusion(charge, coefficients):
    """Same 800x16 ordering as electromagnetic_inclusion in the source."""
    coeff=np.asarray(coefficients)
    if coeff.shape!=(10,4,3):raise ValueError('actual even right-frame mode coefficients required')
    slots=[]
    for ch in charge.slots():
        s=np.zeros((4,5,4,10,16),complex)
        for r in range(4):
            for a in range(4):s[r,2:,:,:,4*r+a]=np.einsum('hi,c->ich',coeff[:,a],ch)
        slots.append(s.reshape(800,16))
    return Jet(*slots)
