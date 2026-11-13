"""Both source-energy legs of the complete chronological current transfer.

The clock is the retained analytic proper-clock source chart, and the
energy variable is its continued Lorentz-energy germ at E=0.  Changing
this source variable does not change the fixed-background field KKT
operator.  Its initial and free-final faces are kept.  This application
does not turn the computational tests into on-shell exterior spinors.
"""
from __future__ import annotations
import numpy as np


def literal_point_energy_sources(point_sources, proper_clock):
    """Differentiate exp(+E*tau) left and exp(-E*tau) right sources.

    The same clock and the same unconjugated coefficient directions enter
    both analytic placements.  For real proper frequency the caller
    multiplies the resulting whole first derivative by i, once.
    """
    R,L=(np.asarray(point_sources[k],complex) for k in
         ('literal_right_source','literal_left_transpose_source'))
    tau=complex(proper_clock)
    if R.ndim!=2 or L.shape!=R.shape or not np.isfinite(tau):
        raise ValueError('complete literal source columns and one finite owned clock required')
    return dict(literal_right_energy_source=-tau*R,
                literal_left_energy_source=tau*L,
                literal_right_source=R,literal_left_transpose_source=L)


def chronological_energy_transfer_chunk(left_source,right_source,response,adjoint,
                                        left_energy_source,right_energy_source):
    """Apply both ordered energy legs with the original transpose adjoint.

    C=L^T K^-1 R, C_E=L_E^T u+p^T R_E, K^T p=L.  No Hermitian
    replacement, source Gram inverse, negative-band deletion or exterior
    pole normalization is used.  All saddle rows are contracted.
    """
    arrays=tuple(np.asarray(x,complex) for x in
                 (left_source,right_source,response,adjoint,
                  left_energy_source,right_energy_source))
    L,R,u,p,LE,RE=arrays
    if L.ndim!=3 or any(x.shape!=L.shape or not np.isfinite(x).all() for x in arrays):
        raise ValueError('all original rows and common complete source columns required')
    n,d,c=L.shape
    mat=lambda x:x.reshape(n*d,c)
    base=mat(L).T@mat(u)
    transpose=mat(p).T@mat(R)
    left=mat(LE).T@mat(u)
    right=mat(p).T@mat(RE)
    return dict(source_transfer=base,independent_transpose_transfer=transpose,
                left_energy_leg=left,right_energy_leg=right,
                continued_energy_first=left+right,
                real_proper_frequency_first=1j*(left+right))


def clock_origin_energy_contacts(source_transfer,transpose_transfer,origin_shift):
    """The opposite energy-leg clock-origin contacts cancel exactly.

    The numerical defect is shift*(C-C_transpose), so an energy-origin
    choice cannot be used to remove the same-background current value.
    """
    C,Ct=(np.asarray(x,complex) for x in(source_transfer,transpose_transfer))
    s=complex(origin_shift)
    if C.ndim!=2 or Ct.shape!=C.shape or not np.isfinite(s):
        raise ValueError('complete source transfer and its independent transpose required')
    return dict(left_origin_contact=s*C,right_origin_contact=-s*Ct,
                clock_origin_cancellation=s*(C-Ct))
