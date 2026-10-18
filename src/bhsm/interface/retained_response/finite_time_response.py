"""Finite-time response without a selected initial state or a stationary pole.

The retained-data application is a one-particle middle-family action component,
not the physical muon/daughter Fock dynamics or a computed magnetic anomaly.
Hermitian real-time realizations only; analytic-left complex charts need their
own dual evolution, not conjugation of the source parameter.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import sys, math, json, io, zipfile, hashlib
from functools import lru_cache
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

ROOT=Path(__file__).resolve().parents[4]/'artifacts/muon_retained_response_20261018'
from .compatible_source import (retained_representation, scalar_labels, scalar_values,
                              cg, haar_rule)
from .retained_magnetic_application import wall_data, FRAME

PAULI=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
A_SQUASH=1.157054135733433
from ..muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
YUKAWA=np.diag(lepton_current_hilbert_representation()['family_Y']).copy()
LABELS=['lo','q000','q001','q002','q003','hi']


def mx(a):return float(np.max(abs(a))) if np.size(a) else 0.
def dagger(a):return np.asarray(a).conj().swapaxes(-1,-2)
def comm(a,b):return a@b-b@a

def write_npz(path,arrays):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for key,value in sorted(arrays.items()):
            v=np.asarray(value)
            if v.dtype.hasobject or not np.isfinite(v).all():raise ValueError('finite pickle-free arrays required: '+key)
            bio=io.BytesIO();np.lib.format.write_array(bio,v,allow_pickle=False)
            info=zipfile.ZipInfo(key+'.npy',(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,bio.getvalue())
    tmp.replace(path)

def bary_weights(nodes):
    x=np.asarray(nodes,float)
    return np.array([1/np.prod(x[i]-np.delete(x,i)) for i in range(len(x))])

def interpolate(nodes,values,t):
    x=np.asarray(nodes,float);d=t-x
    hit=np.flatnonzero(abs(d)<8*np.finfo(float).eps)
    if len(hit):return np.array(values[hit[0]],copy=True)
    z=bary_weights(x)/d
    return np.tensordot(z/z.sum(),values,axes=(0,0))

def derivatives(nmax):
    size=len(scalar_labels(nmax));E=np.zeros((3,size,size),complex);off=0
    for n in range(nmax+1):
        j=n/2;ms=np.arange(n,-n-1,-2)/2;plus=np.zeros((n+1,n+1),complex)
        for col in range(1,n+1):plus[col-1,col]=math.sqrt((j-ms[col])*(j+ms[col]+1))
        Js=[(plus+plus.T)/2,(plus-plus.T)/(2j),np.diag(ms)]
        width=(n+1)**2
        for a in range(3):E[a,off:off+width,off:off+width]=np.kron(2j*Js[a],np.eye(n+1))
        off+=width
    return E

@lru_cache(None)
def quaternion_multiplication(nmax):
    """Exact source CG multiplication, with polynomial coefficients of q_a.

    Full finite matrices are returned. One n1 insertion on n<=1 input reaches
    n<=2; no first-order output from that input has been deleted at nmax=2.
    Iterated finite-field evolution is still a truncated numerical test.
    """
    labels=scalar_labels(nmax);glabels=scalar_labels(1);idx={x:i for i,x in enumerate(glabels)}
    qcoeff=np.zeros((3,len(glabels)),complex);c=1/(2*np.sqrt(2))
    # q=(-x3,-x2,-x1), source SU2 convention.
    qcoeff[0,idx[1,1,-1]]=-1j*c;qcoeff[0,idx[1,-1,1]]=-1j*c
    qcoeff[1,idx[1,1,-1]]=-c;qcoeff[1,idx[1,-1,1]]=c
    qcoeff[2,idx[1,1,1]]=-1j*c;qcoeff[2,idx[1,-1,-1]]=1j*c
    out=np.zeros((3,len(labels),len(labels)),complex)
    for g,(ng,mg,kg) in enumerate(glabels):
        if ng!=1:continue
        for s,(ns,ms,ks) in enumerate(labels):
            for t,(nt,mt,kt) in enumerate(labels):
                if mt!=ms+mg or kt!=ks+kg or not abs(ns-ng)<=nt<=ns+ng or (ns+ng-nt)%2:continue
                val=math.sqrt((ns+1)*(ng+1)/(nt+1))*float(cg(ns,ms,ng,mg,nt,mt)*cg(ns,ks,ng,kg,nt,kt))
                out[:,t,s]+=qcoeff[:,g]*val
    return out


def full18_point(raw):
    """Live material-clock Hamiltonian; convert At to proper time exactly once."""
    from ..muon_native_dirac_hamiltonian import canonical_lepton_hamiltonian_maps
    raw=np.asarray(raw,float);d=wall_data(raw);G,alpha,_=retained_representation()
    H=raw[260:262]+1j*raw[262:264]
    connection=np.einsum('fc,cij->fij',d['connection'][[0,2,3,4]],G)
    connection[0]/=d['lapse']
    owned=canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],
        spatial_derivative_map=np.zeros((1,3,18,18)),H=H[None],
        R4=d['R4'],gauge_connection=connection[None])
    return d,d['lapse']*owned['hamiltonian_map'][0],G,alpha



def sample_operators(raw,nmax=2,family=1):
    """Only a family-invariant one-particle sector; NOT a muon pole projection."""
    if family not in (0,1,2):raise ValueError('declared family 0,1,2')
    d,point,G18,a18=full18_point(raw)
    ids=np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])
    G=G18[:,ids][:,:,ids];a=a18[:,ids][:,:,ids];D=derivatives(nmax)
    nh=D.shape[1];H=np.kron(np.eye(nh),point[np.ix_(ids,ids)])
    H+=sum((-1j*d['lapse']/d['R4']*np.kron(D[i],a[i]) for i in range(3)),np.zeros_like(H))
    q=quaternion_multiplication(nmax);Qgen=np.einsum('c,cij->ij',d['charge'],G)
    eps=np.zeros((3,3,3));eps[0,1,2]=eps[1,2,0]=eps[2,0,1]=1;eps[0,2,1]=eps[2,1,0]=eps[1,0,2]=-1
    V=[]
    for k in range(3):
        vv=sum((eps[i,j,k]*np.kron(q[j],a[i]@Qgen) for i,j in np.ndindex(3,3)),np.zeros_like(H))
        V.append(.5j*d['lapse']*d['R4']*vv)
    S=np.array([np.kron(np.eye(nh),np.kron(np.eye(3),s/2)) for s in PAULI])
    familyP=np.zeros((18,18));familyP[ids,ids]=1
    return dict(H=H,V=np.array(V),S=S,wall=d,point=point,full18_family_commutator=mx(comm(point,familyP)),
                family_indices=ids)


def actual_history(side,nmax=2):
    meta=json.loads((ROOT/'inputs/history_metadata.json').read_text());rr=meta['sides'][side]
    t=np.array([r['time'] for r in rr]);T=t[-1]-t[0];s=(t-t[0])/T
    with np.load(ROOT/'inputs'/f'{side}_history.npz',allow_pickle=False) as f:
        raw=np.array([f[k+'_raw_fields'] for k in LABELS])
        q=np.array([f[k+'_H_selected_charge_coefficients'] for k in LABELS])
    ops=[sample_operators(r,nmax=nmax) for r in raw]
    check=max(mx(o['wall']['charge']-qq) for o,qq in zip(ops,q))
    H=np.array([o['H'] for o in ops]);V=np.array([o['V'] for o in ops]);N=np.array([o['wall']['lapse'] for o in ops])
    return dict(side=side,t=t,T=T,s=s,H=H,V=V,N=N,S=ops[0]['S'],ops=ops,
                sampled_source_charge_difference=check,nmax=nmax)


def evolve(history,*,strength=0.,axis=None,drive=lambda s:1.,rtol=2e-12,atol=2e-14,indices=None):
    """Continuous causal propagator of the explicitly stated coefficient interpolant.

    Interpolation is a numerical representation, not an unrecorded physical
    history. No two-arm sewing, initial state, lifetime, or exterior is supplied.
    """
    ix=np.arange(6) if indices is None else np.asarray(indices)
    nodes=history['s'][ix];hh=history['H'][ix];vv=history['V'][ix]
    n=hh.shape[-1];T=history['T'];weights=np.zeros(3) if axis is None else np.asarray(axis,float)
    if weights.shape!=(3,):raise ValueError('three fixed Cartesian probe weights')
    def rhs(s,y):
        H=interpolate(nodes,hh,s)
        if strength:
            H=H+strength*drive(s)*np.einsum('a,aij->ij',weights,interpolate(nodes,vv,s))
        return (-1j*T*H@y.reshape(n,n)).ravel()
    sol=solve_ivp(rhs,(0.,1.),np.eye(n,dtype=complex).ravel(),method='DOP853',rtol=rtol,atol=atol,max_step=.125,dense_output=True)
    if not sol.success:raise ArithmeticError(sol.message)
    return lambda s: np.moveaxis(sol.sol(s).reshape(n,n,-1),-1,0) if np.ndim(s) else sol.sol(s).reshape(n,n)


def impulse_operator(Ut,Us,Vs,O):
    """Hermitian response operator at the initial time, for H=H0+B V, hbar=1."""
    VI=dagger(Us)@Vs@Us;OI=dagger(Ut)@O@Ut
    return 1j*comm(VI,OI)


def response_basis(history,U,degree=12):
    """Integrate kernel on two declared time-basis profiles, 1 and s, not a protocol."""
    x,w=np.polynomial.legendre.leggauss(degree);s=(x+1)/2;w=w/2;uu=U(s)
    n=history['H'].shape[-1];J=np.zeros((2,3,n,n),complex)
    for si,wi,ui in zip(s,w,uu):
        vv=interpolate(history['s'],history['V'],si)
        VI=dagger(ui)@vv@ui
        J[0]+=history['T']*wi*VI;J[1]+=history['T']*wi*si*VI
    uf=U(1.);DU=-1j*uf@J
    OI=dagger(uf)@history['S']@uf
    resp=np.array([[np.array([1j*comm(J[j,a],ob) for ob in OI]) for a in range(3)] for j in range(2)])
    return dict(integrated_insertion=J,propagator_first=DU,spin_readout_first=resp,final=uf)


def conditional_response(numerator,probability,delta_num,delta_prob):
    """Derivative of a conditioned observable; no lifetime or projector is selected."""
    if probability<=0 or not np.isfinite(probability):raise ValueError('positive surviving probability required')
    value=numerator/probability
    return (delta_num-value*delta_prob)/probability


def nojump_bloch(r,omega,gamma_vector):
    """Exact algebra for a declared no-return two-spin model only, not BHSM assumption."""
    r=np.asarray(r,float);om=np.asarray(omega,float);g=np.asarray(gamma_vector,float)
    return np.cross(om,r)-g+(g@r)*r


def open_channel_measurement(A,At):
    """Time-local amplitude generator only where A is square and nonsingular.

    A is a supplied amplitude map, NOT automatically a complete reduced density
    channel. It cannot be inferred from a decay analyzer. Initial correlations
    and return flux may require the full joint density/kernel instead.
    """
    A,At=np.asarray(A,complex),np.asarray(At,complex)
    if A.ndim!=2 or A.shape[0]!=A.shape[1] or At.shape!=A.shape:raise ValueError('matching square amplitude matrices')
    if np.linalg.cond(A)>1e12:raise ValueError('local generator unreliable: amplitude map nearly singular')
    Heff=1j*np.linalg.solve(A.T,At.T).T
    H=(Heff+dagger(Heff))/2;loss=1j*(Heff-dagger(Heff))
    return H,loss
