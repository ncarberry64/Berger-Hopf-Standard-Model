"""Coherent daughter sources and gauged Schur reduction.

Finite, explicitly supplied operators only. This module does not construct
physical BHSM packet sections, quantum domains, charges, or a magnetic moment.
All left amplitude leaves are explicit inputs; no analytic source is conjugated.
"""
from __future__ import annotations
from dataclasses import dataclass, fields
import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.complex128]


def _array(x, name: str, shape=None) -> Array:
    if x is None:
        raise ValueError(f"{name} is required, not implicitly zero")
    out = np.asarray(x, dtype=complex)
    if not np.all(np.isfinite(out)) or (shape is not None and out.shape != shape):
        raise ValueError(f"invalid finite {name}; expected shape {shape}")
    return out


@dataclass(frozen=True)
class DaughterData:
    right: Array              # (nodes, legs, neutrino2, muon4)
    field_return: Array       # (nodes, legs, legs); not the multiparticle resolvent
    left: Array               # (nodes, legs, electron4, antineutrino2)
    muon: Array               # (nodes, 4, parent_spin2)
    neutrino_left: Array      # (nodes, 2), explicit analytic left leaf
    electron_left: Array      # (nodes, electron_spin2, 4)
    antineutrino: Array       # (nodes, 2)
    weight: NDArray[np.float64]  # actual joint-channel measure, including normalization


def validate(data: DaughterData, *, derivative=False) -> DaughterData:
    r = _array(data.right, 'right')
    if r.ndim != 4 or r.shape[2:] != (2, 4) or not r.shape[0] or not r.shape[1]:
        raise ValueError('right requires (nodes, legs, 2, 4)')
    n, a = r.shape[:2]
    arrays = dict(right=r,
        field_return=_array(data.field_return, 'field_return', (n,a,a)),
        left=_array(data.left, 'left', (n,a,4,2)),
        muon=_array(data.muon, 'muon', (n,4,2)),
        neutrino_left=_array(data.neutrino_left, 'neutrino_left', (n,2)),
        electron_left=_array(data.electron_left, 'electron_left', (n,2,4)),
        antineutrino=_array(data.antineutrino, 'antineutrino', (n,2)))
    w = np.asarray(data.weight)
    if np.iscomplexobj(w) or w.shape != (n,) or not np.isfinite(w).all():
        raise ValueError('real finite node weights or their real derivatives required')
    if not derivative and np.any(w <= 0):
        raise ValueError('base joint-channel weights must be positive')
    return DaughterData(**arrays, weight=np.asarray(w,float))


def amplitude(data: DaughterData) -> Array:
    """Keep both electron and parent spins and all interaction legs."""
    d=validate(data)
    jmu=np.einsum('ni,naij,njs->nas',d.neutrino_left,d.right,d.muon,optimize=True)
    je=np.einsum('nrc,nbcd,nd->nbr',d.electron_left,d.left,d.antineutrino,optimize=True)
    return np.einsum('nas,nab,nbr->nrs',jmu,d.field_return,je,optimize=True)


def coherent_source_and_first(data: DaughterData, first: DaughterData):
    """Differentiate all seven amplitude factors plus the joint measure.

    Columns map two parent spin coordinates into joint daughter nodes times
    electron spin. This is not a real classical Maxwell expectation current.
    The domain represented by the measure must be supplied by the caller.
    """
    d, h=validate(data),validate(first,derivative=True)
    if d.right.shape!=h.right.shape:
        raise ValueError('base/first shapes differ')
    def contract(nu,r,mu,el,l,anti,g):
        jm=np.einsum('ni,naij,njs->nas',nu,r,mu,optimize=True)
        je=np.einsum('nrc,nbcd,nd->nbr',el,l,anti,optimize=True)
        return np.einsum('nas,nab,nbr->nrs',jm,g,je,optimize=True)
    factors=[d.neutrino_left,d.right,d.muon,d.electron_left,d.left,d.antineutrino,d.field_return]
    derivatives=[h.neutrino_left,h.right,h.muon,h.electron_left,h.left,h.antineutrino,h.field_return]
    a=contract(*factors)
    placements=[]
    for j in range(len(factors)):
        ff=factors.copy();ff[j]=derivatives[j]
        placements.append(contract(*ff))
    da=sum(placements,np.zeros_like(a))
    root=np.sqrt(d.weight)[:,None,None]
    source=(root*a).reshape(-1,2)
    first_source=(root*da+0.5*(h.weight/d.weight)[:,None,None]*root*a).reshape(-1,2)
    return dict(amplitude=a,amplitude_first=da,source=source,source_first=first_source,
                amplitude_first_placements=np.stack(placements))


def real_parameter_rate(source, source_first):
    """Hermitian rate Gram and its REAL-parameter derivative, not analytic gauging."""
    v=_array(source,'source');dv=_array(source_first,'source_first',v.shape)
    if v.ndim!=2 or v.shape[1]!=2:raise ValueError('two parent spin columns required')
    return v.conj().T@v, dv.conj().T@v+v.conj().T@dv


def schur_lifts(full, retained: int):
    """Analytic left and right eliminations on a declared finite common domain."""
    x=_array(full,'full inverse operator')
    if x.ndim!=2 or x.shape[0]!=x.shape[1] or not 0<retained<len(x):
        raise ValueError('square operator and nonempty retained/complement split required')
    a,b,c,d=x[:retained,:retained],x[:retained,retained:],x[retained:,:retained],x[retained:,retained:]
    u=np.linalg.solve(d,c)
    p=np.linalg.solve(d.T,b.T).T
    right=np.vstack((np.eye(retained),-u))
    left=np.hstack((np.eye(retained),-p))
    return dict(reduced=a-b@u,right=right,left=left,
                right_residual=d@u-c,left_residual=p@d-b)


def projected_photon_vertex(full_out, full_in, photon, retained: int):
    """Photon insertion at two momentum/frequency arguments, not a static derivative.

    photon has shape (components, full_size, full_size) or (full_size, full_size).
    Its construction, charge normalization and physical domain are NOT selected.
    """
    outgoing=schur_lifts(full_out,retained)
    incoming=schur_lifts(full_in,retained)
    j=_array(photon,'complete photon insertion')
    n=np.asarray(full_in).shape[0]
    if j.shape[-2:]!=(n,n) or j.ndim not in (2,3):
        raise ValueError('compatible photon insertion required')
    reduced=outgoing['left']@j@incoming['right']
    return dict(vertex=reduced,outgoing=outgoing,incoming=incoming)


def ward_residual(full_out,full_in,photon,q,charge,retained:int):
    """Convention: q_mu J^mu = Gamma_out Q - Q Gamma_in.

    Requires a block-diagonal charge on the declared retained/complement split.
    This is a consistency check, not a construction of missing transverse J.
    """
    x1,x0=_array(full_out,'Gamma_out'),_array(full_in,'Gamma_in')
    q=np.asarray(q,dtype=complex);j=_array(photon,'photon')
    Q=_array(charge,'charge',x0.shape)
    if x1.shape!=x0.shape or j.shape!=(len(q),*x0.shape):
        raise ValueError('incompatible Ward arrays')
    if np.max(abs(Q[:retained,retained:]))>1e-13 or np.max(abs(Q[retained:,:retained]))>1e-13:
        raise ValueError('charge must respect the retained/complement split')
    result=projected_photon_vertex(x1,x0,j,retained)
    full_target=x1@Q-Q@x0
    smallQ=Q[:retained,:retained]
    small_target=result['outgoing']['reduced']@smallQ-smallQ@result['incoming']['reduced']
    full_error=np.einsum('a,aij->ij',q,j)-full_target
    reduced_error=np.einsum('a,aij->ij',q,result['vertex'])-small_target
    return dict(full_residual=full_error,reduced_residual=reduced_error,**result)


def pole_firsts(full, energy_first, field_firsts, retained:int, right_pole, left_pole):
    """Admitted pole leaves and true total E/B derivatives must be supplied.

    This finite consumer returns slopes, NOT g or a_mu without physical matching.
    """
    lift=schur_lifts(full,retained)
    r=_array(right_pole,'right pole');l=_array(left_pole,'left pole')
    if r.shape!=(retained,2) or l.shape!=(2,retained):
        raise ValueError('two-spin right and left pole arrays required')
    ge=lift['left']@_array(energy_first,'energy_first',np.shape(full))@lift['right']
    gb=_array(field_firsts,'field_firsts')
    if gb.shape!=(3,*np.shape(full)):raise ValueError('three magnetic source directions required')
    z=l@ge@r
    b=l@(lift['left']@gb@lift['right'])@r
    matrices=np.stack([-np.linalg.solve(z,item) for item in b])
    return dict(Z=z,magnetic_matrices=matrices,
                right_pole_residual=lift['reduced']@r,
                left_pole_residual=l@lift['reduced'])


def double_spectral_return(energies, left_coupling, right_coupling, field_insertion, z):
    """V_L R(z) H_B R(z) V_R, retaining off-diagonal energy transitions.

    Finite self-adjoint daughter spectral chart only. Couplings and H_B supplied.
    """
    e=np.asarray(energies,float);n=len(e)
    vL=_array(left_coupling,'left coupling');vR=_array(right_coupling,'right coupling')
    h=_array(field_insertion,'H_B',(n,n))
    if vL.shape[1]!=n or vR.shape[0]!=n:raise ValueError('incompatible spectral couplings')
    if not np.isfinite(e).all() or np.any(z-e==0):raise ValueError('resolvent point on a finite eigenvalue')
    inv=1/(z-e)
    return (vL*inv[None,:])@h@(inv[:,None]*vR)
