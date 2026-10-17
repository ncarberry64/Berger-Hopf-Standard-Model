"""Apply actual exterior trace functions before chronological current inversion.

The original 288 point columns are (external C6, internal FE2, internal
C6, real n1).  Exterior right and left traces may vary at EVERY owned
quadrature point.  This interface never forces their time dependence into
the two internal computational FE functions or chooses a physical band.
"""
from __future__ import annotations
import numpy as np


def exterior_current_point_sources(point_sources,proper_clock,*,continued_energy,
        right_trace_map,left_trace_map,right_trace_map_energy_first,
        left_trace_map_energy_first):
    """Apply independently owned trace/dual maps and both energy contacts.

    R(E)=exp(-E*tau) J_R B_R(tau,E),
    L(E)=exp(+E*tau) J_L B_L(tau,E).
    The caller supplies the ACTUAL pointwise maps and their energy jets.
    A missing trace jet is not silently assigned zero.  Same complex
    tangents enter literal analytic placements without conjugation.
    """
    R,L=(np.asarray(point_sources[k],complex)for k in
         ('literal_right_source','literal_left_transpose_source'))
    Br,Bl,BrE,BlE=map(lambda x:np.asarray(x,complex),(
        right_trace_map,left_trace_map,right_trace_map_energy_first,
        left_trace_map_energy_first))
    tau,E=complex(proper_clock),complex(continued_energy)
    if (R.ndim!=2 or R.shape[1]!=288 or L.shape!=R.shape
        or Br.ndim!=2 or Bl.ndim!=2 or Br.shape[0]!=288 or Bl.shape[0]!=288
        or BrE.shape!=Br.shape or BlE.shape!=Bl.shape
        or not all(np.isfinite(a).all()for a in(R,L,Br,Bl,BrE,BlE))
        or not np.isfinite([tau,E]).all()):
        raise ValueError('all original current columns and independent pointwise exterior trace/energy maps required')
    er,el=np.exp(-E*tau),np.exp(E*tau)
    Jr=er*(R@Br);Jl=el*(L@Bl)
    JrE=er*(R@BrE-tau*(R@Br));JlE=el*(L@BlE+tau*(L@Bl))
    if not all(np.isfinite(a).all()for a in(Jr,Jl,JrE,JlE)):
        raise ArithmeticError('exterior phase/trace application overflowed; no phase clipping permitted')
    return dict(exterior_right_source=Jr,exterior_left_transpose_source=Jl,
                exterior_right_energy_source=JrE,exterior_left_energy_source=JlE,
                right_phase_energy_contact=-tau*Jr,left_phase_energy_contact=tau*Jl,
                right_trace_energy_contact=er*(R@BrE),
                left_trace_energy_contact=el*(L@BlE),
                current_internal_test_shape=np.array([2,6,4]),
                exterior_time_dependence_projected_to_internal_FE2=False,
                exterior_trace_or_source_coefficient_conjugated=False)


def exterior_current_transfer(left_source,right_source,response,transpose_adjoint,
        left_energy_source,right_energy_source,*,operator_energy_response):
    """Contract original weak rows after a sourced exterior application.

    C=L^T K^-1 R and C_E=L_E^T u+p^T R_E-p^T(K_E u).
    operator_energy_response must be supplied explicitly, including an
    explicit zero array for a declared fixed-K source-energy application.
    This preserves actual operator/current contacts without identifying
    the finite field inverse with a physical quantum covariance.
    """
    L,R,u,p,LE,RE,KEu=map(lambda x:np.asarray(x,complex),(
        left_source,right_source,response,transpose_adjoint,
        left_energy_source,right_energy_source,operator_energy_response))
    if (L.ndim!=3 or R.ndim!=3 or L.shape[:2]!=R.shape[:2]
        or u.shape!=R.shape or p.shape!=L.shape or LE.shape!=L.shape
        or RE.shape!=R.shape or KEu.shape!=R.shape
        or not all(np.isfinite(a).all()for a in(L,R,u,p,LE,RE,KEu))):
        raise ValueError('all original rows, independent trace columns and explicit operator-energy action required')
    flat=lambda a:a.reshape(-1,a.shape[-1])
    C=flat(L).T@flat(u);Ct=flat(p).T@flat(R)
    left=flat(LE).T@flat(u);right=flat(p).T@flat(RE)
    operator=-flat(p).T@flat(KEu)
    return dict(exterior_source_transfer=C,independent_transpose_transfer=Ct,
                left_energy_contact=left,right_energy_contact=right,
                operator_energy_contact=operator,
                continued_energy_first=left+right+operator,
                real_proper_frequency_first=1j*(left+right+operator),
                source_transpose_identity_defect=C-Ct,
                exterior_trace_maps_are_supplied_operator_inputs=True,
                physical_exterior_pole_or_LSZ_identified=False)
