"""Conditional daughter-sector elimination and magnetic pole/readout identities.

These functions consume supplied, common-domain quantum inverse-operator blocks.
They do not select BHSM fields, a retarded domain, an inherited state, a cutoff,
or a physical muon. Transposes below implement an independently supplied
analytic left leaf; they are not automatically Hermitian adjoints.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
import numpy as np


def _matrix(value: object, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=complex)
    if result.ndim != 2 or not result.size or not np.isfinite(result).all():
        raise ValueError(f'{name}: a nonempty finite matrix is required')
    return result


@dataclass(frozen=True)
class Blocks:
    """Inverse operator [[A,B],[C,D]], retained muon plus complement sectors."""
    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: np.ndarray

    def checked(self) -> 'Blocks':
        A, B, C, D = (_matrix(getattr(self, key), key) for key in 'ABCD')
        n, m = A.shape[0], D.shape[0]
        if A.shape != (n,n) or D.shape != (m,m) or B.shape != (n,m) or C.shape != (m,n):
            raise ValueError('incompatible muon/complement block dimensions')
        return Blocks(A,B,C,D)


@dataclass(frozen=True)
class ContractedReturn:
    base: Blocks
    left: np.ndarray
    right: np.ndarray
    right_response: np.ndarray
    left_response: np.ndarray
    reduced: np.ndarray


def prepare_return(base: Blocks, left: object, right: object) -> ContractedReturn:
    """Two source solves for a two-spin pair, and the independent left solves.

    For an actual continuum outgoing problem, replace the finite solves with
    the admitted solution applications on its full domain. This finite helper
    never certifies that such a continuum realization has been obtained.
    """
    base = base.checked()
    L, R = _matrix(left,'left'), _matrix(right,'right')
    if L.shape[1] != len(base.A) or R.shape[0] != len(base.A) or L.shape[0] != R.shape[1]:
        raise ValueError('incompatible left/right retained leaves')
    u = np.linalg.solve(base.D, base.C @ R)
    p = np.linalg.solve(base.D.T, (L @ base.B).T)
    return ContractedReturn(base,L,R,u,p, L @ base.A @ R - L @ base.B @ u)


def contracted_first(prepared: ContractedReturn, jet: Blocks) -> np.ndarray:
    """L (A-B D^-1 C)_s R using fixed base null leaves and full block jets.

    The jets must already include source, state, moving pairing/domain, unit,
    event-time, and projection effects that the underlying problem requires.
    This is not proof of the completeness of externally supplied jets.
    At an off-shell residual, moving the left/right test leaves requires their
    own additional terms; pole sensitivity uses null leaves at the admitted pole.
    """
    jet = jet.checked()
    if any(getattr(jet,k).shape != getattr(prepared.base,k).shape for k in 'ABCD'):
        raise ValueError('jet and value blocks have different shapes')
    L,R,u,p = prepared.left,prepared.right,prepared.right_response,prepared.left_response
    return L@jet.A@R - L@jet.B@u - p.T@jet.C@R + p.T@jet.D@u


def pole_first(prepared: ContractedReturn, energy_jet: Blocks,
               source_jets: Mapping[str, Blocks]) -> dict[str, np.ndarray]:
    """Return Z and -Z^-1 L Gamma_s R; no physical units or g are selected."""
    Z = contracted_first(prepared, energy_jet)
    result = {'Z': Z}
    for label, jet in source_jets.items():
        result[label] = np.linalg.solve(Z, -contracted_first(prepared, jet))
    return result


def event_sensitivity(*, f_before: object, f_after: object,
                      reset_x: object, reset_t: object, reset_parameter: object,
                      guard_x: object, guard_t: float, guard_parameter: object,
                      transversality_floor: float) -> dict[str, np.ndarray | float]:
    """Event-time-aware saltation derivative at a supplied transverse event.

    Dimensions of before/after states may differ. This does NOT provide the
    event guard or reset law and must not be added twice if a fully resolved
    history derivative already contains event-time motion. No deterministic
    rupture rule is imposed on quantum decay by this utility.
    """
    fm,fp,rt,n = (np.asarray(x,dtype=float) for x in
                  (f_before,f_after,reset_t,guard_x))
    rx,rp = (np.asarray(x,dtype=float) for x in (reset_x,reset_parameter))
    gp = np.atleast_1d(np.asarray(guard_parameter,dtype=float))
    if rx.shape != (fp.size,fm.size) or rt.shape != fp.shape or n.shape != fm.shape:
        raise ValueError('incompatible event state dimensions')
    if rp.shape != (fp.size,gp.size):
        raise ValueError('incompatible event parameter dimensions')
    if not all(np.isfinite(x).all() for x in (fm,fp,rt,n,rx,rp,gp)):
        raise ValueError('event inputs must be finite')
    if not np.isfinite(guard_t) or not np.isfinite(transversality_floor) or transversality_floor <= 0:
        raise ValueError('finite guard time derivative and positive explicit numerical floor required')
    denom = float(guard_t + n@fm)
    if abs(denom) <= transversality_floor:
        raise ValueError('event is not transverse at the declared floor; no smooth jump derivative admitted')
    delta_f = fp-rx@fm-rt
    return {'state':rx+np.outer(delta_f,n)/denom,
            'parameter':rp+np.outer(delta_f,gp)/denom,
            'event_time_state':-n/denom, 'event_time_parameter':-gp/denom,
            'transversality':denom}


PAULI = np.array([[[0,1],[1,0]], [[0,-1j],[1j,0]], [[1,0],[0,-1]]],complex)


def stationary_analyzer_signal(D: object, polarization: object, *,
                               omega: float, decay_rate: float,
                               times: object) -> np.ndarray:
    """Exact conditional signal for H=omega*sigma_z/2 and scalar loss.

    D is a fixed parent 2x2 analyzer, not a magnetic Hamiltonian. If loss is
    spin dependent, the history is nonstationary, or the analyzer itself has
    explicit time dependence, this specialized identity is not applicable.
    """
    d = _matrix(D,'D')
    P = np.asarray(polarization,dtype=float)
    t = np.asarray(times,dtype=float)
    if d.shape != (2,2) or P.shape != (3,) or not np.isfinite(P).all() or np.linalg.norm(P)>1+1e-12:
        raise ValueError('physical 2x2 analyzer and three-component polarization required')
    if np.max(abs(d-d.conj().T))>1e-12 or np.linalg.eigvalsh(d)[0]<-1e-12:
        raise ValueError('analyzer must be positive Hermitian')
    if not np.isfinite(t).all() or not np.isfinite([omega,decay_rate]).all() or decay_rate<0:
        raise ValueError('finite times/frequency and nonnegative scalar loss required')
    d0=np.trace(d).real/2
    dv=np.einsum('aij,ji->a',PAULI,d).real/2
    c=dv[0]*P[0]+dv[1]*P[1]
    s=dv[1]*P[0]-dv[0]*P[1]
    return np.exp(-decay_rate*t)*(d0+dv[2]*P[2]+c*np.cos(omega*t)+s*np.sin(omega*t))
