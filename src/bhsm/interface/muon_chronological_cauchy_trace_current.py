"""Complete C6 Cauchy traces on the original chronological current tests.

The structural Kronecker map acts on the external C6 coordinate only.
All48 internal FE2/C6/n1 tests remain. The independent analytic left map
is supplied by the owned Cauchy application, not taken as a dagger here.
"""
from __future__ import annotations
import numpy as np


def cauchy_trace_point_sources(point_sources,proper_clock,*,right_trace,
        left_trace,right_trace_energy_first,left_trace_energy_first):
    """Apply kron(trace,I48) at E=0 without a dense288 square product.

    The envelope maps have their own energy jets. Both those contacts and
    the opposite explicit source phase contacts are evaluated. Their sum
    is not assigned zero numerically; the receipt records the cancellation
    defect. No exterior band, residue or pole is selected by these maps.
    """
    R,L=(np.asarray(point_sources[k],complex)for k in
        ('literal_right_source','literal_left_transpose_source'))
    Fr,Fl,Fre,Fle=map(lambda x:np.asarray(x,complex),(
        right_trace,left_trace,right_trace_energy_first,left_trace_energy_first))
    tau=complex(proper_clock)
    if (R.ndim!=2 or R.shape[1]!=288 or L.shape!=R.shape
        or any(a.shape!=(6,6)for a in(Fr,Fl,Fre,Fle))
        or not all(np.isfinite(a).all()for a in(R,L,Fr,Fl,Fre,Fle))
        or not np.isfinite(tau)):
        raise ValueError('complete independent C6 point traces and energy jets required')
    def action(S,F):
        return np.einsum('afk,fg->agk',S.reshape(len(S),6,48),F,
                         optimize=True).reshape(len(S),288)
    Jr=action(R,Fr);Jl=action(L,Fl)
    tr=action(R,Fre);tl=action(L,Fle)
    pr=-tau*Jr;pl=tau*Jl
    return dict(literal_right_source=Jr,literal_left_transpose_source=Jl,
        right_energy_source=tr+pr,left_energy_source=tl+pl,
        right_trace_energy_contact=tr,left_trace_energy_contact=tl,
        right_phase_energy_contact=pr,left_phase_energy_contact=pl,
        structural_right_map='kron(C6_trace,I48)',
        structural_left_map='kron(independent_analytic_C6_trace,I48)',
        source_columns=np.array([6,2,6,4]),
        source_or_trace_coefficients_conjugated=False,
        physical_exterior_band_or_LSZ_selected=False)
