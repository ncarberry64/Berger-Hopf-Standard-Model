"""Exact endpoint amputation on a represented nonstationary current chain.

The retained first-order operator is A=d_tau+H=-D_L on the owned
continued proper-clock graph.  Finite sources do not acquire poles by
inverting A with an initial-zero trace.  Exterior pole data enter the
explicit boundary matrix B_in(E)+B_out(E)U_E, with the same trace/frame.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm


def _exponential_moments(Z,h):
    """Entire int exp(Z*r)dr and its Z+E*I derivative, no pole division."""
    d=len(Z);a=np.zeros((3*d,3*d),complex)
    a[:d,:d]=Z;a[:d,d:2*d]=np.eye(d);a[d:2*d,2*d:]=np.eye(d)
    e=expm(h*a);I0=e[:d,d:2*d]
    return I0,h*I0-e[:d,2*d:]


def nonstationary_endpoint_amputation(proper_steps,body,*,energy=0.,endpoint_body=None):
    """Apply the full noncommuting body and both endpoint amputation sides.

    R(E)=-int exp(E*(tau_f-tau))U(tau_f,tau)dtau.  For a piecewise
    constant represented body, every segment is integrated exactly by a
    matrix exponential, even at a coincident local body eigenvalue.

    (E-H_f)R=I-B+C_left; R(E-H_f)=I-B+C_right,
    B=exp(E*L)U(f,i).  The nonstationarity contacts and final face are
    exported, so replacing the finite R by (E-H_f)^-1 is testable.
    """
    h,H=np.asarray(proper_steps,complex),np.asarray(body,complex);E=complex(energy)
    if (h.ndim!=1 or H.ndim!=3 or H.shape[0]!=len(h) or H.shape[1]!=H.shape[2]
            or not len(h) or not np.isfinite(h).all() or not np.isfinite(H).all()
            or not np.isfinite(E) or np.any(h==0)):
        raise ValueError('all directed finite proper-clock steps and full current body required')
    d=H.shape[-1];I=np.eye(d,dtype=complex)
    Hf=H[-1] if endpoint_body is None else np.asarray(endpoint_body,complex)
    if Hf.shape!=(d,d) or not np.isfinite(Hf).all():raise ValueError('same full endpoint current body required')
    L=complex(sum(h));after=I.copy();remaining=0j
    R=np.zeros_like(I);RE=R.copy();CL=R.copy();CR=R.copy()
    for step,Hj in zip(h[::-1],H[::-1]):
        M,ME=_exponential_moments(E*I-Hj,step)
        F=np.exp(E*remaining)*after;T=F@M
        R-=T;RE-=remaining*T+F@ME
        CL-=T@Hj-Hf@T;CR-=T@(Hj-Hf)
        after=after@expm(-step*Hj);remaining+=step
    B=np.exp(E*L)*after;D=E*I-Hf
    # chi=e^-E*tau phi removes the external plane phase; the homogeneous
    # envelope obeys phi'+(H-E)phi=0 on this SAME source-energy variable.
    U_E=B;U_E_first=L*U_E
    return dict(canonical_core_trace=after,energy_shifted_core_trace=U_E,
        energy_shifted_core_trace_first=U_E_first,continued_source_response=R,
        continued_source_energy_first=RE,final_endpoint_return=B,
        nonstationary_left_amputation_contact=CL,nonstationary_right_amputation_contact=CR,
        local_endpoint_inverse_symbol=D,proper_clock_span=np.asarray(L),
        left_amputation_original_rows=D@R-I+B-CL,
        right_amputation_original_rows=R@D-I+B-CR,
        temporal_source_equation='A=d_tau+H=-D_L; A chi=-exp(-E*tau)I; right initial trace0',
        energy_envelope_equation='chi=exp(-E*tau)phi; (d_tau+H-E)phi=0; U_E=exp(E*L)U',
        endpoint_equation='(E-Hf)R=I-exp(E*L)U+nonstationary_left_contact, with literal right counterpart',
        finite_interval_response_entire_in_energy=True,terminal_endpoint_return_removed=False)


def exterior_current_pole_matrix(core_trace,core_trace_first,boundary_initial,boundary_final,
                                  *,boundary_initial_first=None,boundary_final_first=None):
    """The exact retained boundary equation for exterior pole/residue matching.

    A homogeneous exterior-compatible trace obeys
    [B_in(E)+B_out(E)U_E]chi_initial=0.  Neither B_out nor its derivative
    is inferred from the finite initial-zero/free-final inverse.  This
    interface keeps the entire charged/neutral and negative-band space.
    """
    U,UE,Bi,Bf=map(lambda a:np.asarray(a,complex),
        (core_trace,core_trace_first,boundary_initial,boundary_final))
    if U.ndim!=2 or U.shape[0]!=U.shape[1] or any(x.shape!=U.shape for x in(UE,Bi,Bf)):
        raise ValueError('same complete action trace and original exterior boundary maps required')
    Bip=np.zeros_like(Bi)if boundary_initial_first is None else np.asarray(boundary_initial_first,complex)
    Bfp=np.zeros_like(Bf)if boundary_final_first is None else np.asarray(boundary_final_first,complex)
    if Bip.shape!=U.shape or Bfp.shape!=U.shape or any(not np.isfinite(x).all()for x in(U,UE,Bi,Bf,Bip,Bfp)):
        raise ValueError('same finite analytic exterior boundary jets required')
    return dict(exterior_pole_matrix=Bi+Bf@U,
        exterior_pole_matrix_energy_first=Bip+Bfp@U+Bf@UE,
        pole_equation='det(Bin(E)+Bout(E)U_E)=0',
        residue_equation='ell^T(Bin_prime+Bout_prime*U_E+Bout*U_E_prime)r at actual left/right null traces',
        finite_source_Gram_used_as_exterior_pole=False)
