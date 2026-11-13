"""Lorentz current numerator and energy jets on the actual changing phase.

This applies i D_tau-W, not an energy substitution into a finite tent
eigenvalue. A zero inhomogeneous retarded initial response is an inverse
domain, not a selected fermion state. The finite endpoint remainder is
retained, so no translation-invariant Feynman propagator is inferred.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp
from .muon_magnetic_mixed_green import _finite
from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample


def canonical_retarded_energy_response(evaluator,interval,energy,*,rtol=2e-11,atol=2e-13,max_step=None):
    """Execute the canonical retarded source equation and its energy jet.

    chi_dot=-i N Hcan chi-i N exp(-i E tau)I, tau_dot=N.
    R(E)=exp(i E tau_final)chi_final; its derivative includes BOTH
    the differentiated forcing and the final Fourier phase. The
    evaluator binds actual N,Hcan,Omega_tau; no W/P input is accepted.
    """
    endpoints=_finite(interval,'actual increasing-time interval',real=True)
    E=_finite(energy,'explicit real energy probe',real=True)
    if endpoints.shape!=(2,)or endpoints[1]<=endpoints[0]or E.shape!=()or not callable(evaluator):
        raise ValueError('actual coefficient evaluator, chronological interval and real energy required')
    if not np.isfinite([rtol,atol]).all()or min(rtol,atol)<=0:raise ValueError('positive integration tolerances required')
    a,b=endpoints;E=float(E);first=evaluator(float(a));H=_finite(first['H_can'],'actual canonical Lorentz operator')
    if H.ndim!=2 or H.shape[0]!=H.shape[1]:raise ValueError('complete square current fiber required')
    n=len(H);n2=n*n;I=np.eye(n,dtype=complex);z=np.zeros((n,n),complex)
    y=np.r_[0j,I.reshape(-1),z.reshape(-1),z.reshape(-1),I.reshape(-1)]
    if max_step is None:max_step=(b-a)/4
    if not np.isfinite(max_step)or max_step<=0:raise ValueError('positive explicit temporal resolution required')
    checks=[]
    def rhs(t,q):
        op=evaluator(float(t));N=float(op['N']);H=_finite(op['H_can'],'actual Hcan');O=_finite(op['Omega_tau'],'actual temporal connection')
        if H.shape!=(n,n)or O.shape!=H.shape or not np.isfinite(N)or N<=0:raise ValueError('same complete actual current/proper-clock operator required')
        scale=max(1.,np.max(abs(H)),np.max(abs(O)))
        if np.max(abs(H-H.conj().T))>256*n*np.finfo(float).eps*scale or np.max(abs(O+O.conj().T))>256*n*np.finfo(float).eps*scale:
            raise ValueError('canonical Hermitian Hcan and anti-Hermitian temporal connection required')
        tau=q[0].real;U=q[1:1+n2].reshape(n,n);X=q[1+n2:1+2*n2].reshape(n,n)
        XE=q[1+2*n2:1+3*n2].reshape(n,n);T=q[1+3*n2:].reshape(n,n)
        ph=np.exp(-1j*E*tau)
        checks.append((t,N))
        return np.r_[N+0j,(-1j*N*H@U).reshape(-1),
            (-1j*N*H@X-1j*N*ph*I).reshape(-1),
            (-1j*N*H@XE-N*tau*ph*I).reshape(-1),(-N*O@T).reshape(-1)]
    sol=solve_ivp(rhs,(float(a),float(b)),y,method='DOP853',rtol=rtol,atol=atol,max_step=max_step)
    if not sol.success or not np.isfinite(sol.y).all():raise RuntimeError('actual canonical retarded energy application failed')
    q=sol.y[:,-1];tau=float(q[0].real);U=q[1:1+n2].reshape(n,n);X=q[1+n2:1+2*n2].reshape(n,n)
    XE=q[1+2*n2:1+3*n2].reshape(n,n);T=q[1+3*n2:].reshape(n,n);phase=np.exp(1j*E*tau)
    R=phase*X;dR=1j*tau*R+phase*XE
    return dict(canonical_propagator=U,retarded_energy_response=R,retarded_energy_first_jet=dR,
        temporal_unitary_frame=T,temporal_normal_frame_retarded_response=T.conj().T@R,
        temporal_normal_frame_energy_first_jet=T.conj().T@dR,
        proper_time_span=tau,energy=E,interval=endpoints,
        canonical_current_unitarity_defect=float(np.linalg.norm(U.conj().T@U-I)),
        temporal_frame_unitarity_defect=float(np.linalg.norm(T.conj().T@T-I)),
        integration=dict(method='DOP853',rtol=rtol,atol=atol,evaluations=sol.nfev,steps=len(sol.t)-1,max_step=float(max_step)),
        source_equation='(i d_tau-Hcan)chi=exp(-i E tau)I; retarded chi(initial)=0',
        no_fermion_state_or_covariance_selected=True,
        static_Fourier_pencil_or_infinite_endpoint_limit_assumed=False,
        Feynman_loop_or_native_factor_Wick_identification_completed=False,
        physical_a_mu=None,physical_g_mu=None)


def corrected_phase_retarded_energy_response(phase,energy,**kwargs):
    """Bind the reached full eighteen-component owned phase coefficients."""
    span=float(phase['receipt']['span']);interval=(min(0.,span),max(0.,span))
    def actual(t):return profile_preserving_lepton_sample(phase,t)['operator']
    return canonical_retarded_energy_response(actual,interval,energy,**kwargs)


def static_normal_frame_energy_identity(spatial_mass,energy,proper_span):
    """Exact static NORMAL temporal-frame numerator and finite boundary law.

    A_E=i omega+W, P_E=omega²+W². At omega=i(E+i0),
    G_L=-P_E^-1 A_E†=(E-W)^-1. This is a conditional symbol
    identity; it does not replace the actual changing native cell by it.
    """
    from scipy.linalg import expm
    W=_finite(spatial_mass,'complete normal-frame Hermitian spatial mass operator')
    E=_finite(energy,'explicit real energy',real=True);L=_finite(proper_span,'proper-time interval',real=True)
    if W.ndim!=2 or W.shape[0]!=W.shape[1]or E.shape!=()or L.shape!=()or float(L)<=0:
        raise ValueError('complete normal-frame symbol and explicit positive proper interval required')
    n=len(W);I=np.eye(n);D=float(E)*I-W;U=expm(-1j*float(L)*W);boundary=np.exp(1j*float(E)*float(L))*U
    # An augmented exponential evaluates the integral even exactly on
    # a rest pole; no epsilon width or inverse/pseudoinverse is chosen.
    block=np.zeros((2*n,2*n),complex);block[:n,:n]=1j*D;block[:n,n:]=-1j*I
    R=expm(float(L)*block)[:n,n:]
    return dict(Lorentz_inverse_symbol=D,Lorentz_numerator=float(E)*I+W,
        analytic_Euclidean_square_at_imaginary_frequency=W@W-float(E)**2*I,
        numerator_product_difference=D@(float(E)*I+W)-(float(E)**2*I-W@W),
        finite_retarded_energy_response=R,finite_endpoint_term=boundary,
        finite_source_equation_remainder=D@R-I+boundary,
        Wick_equation='G_L(E)=-[P_E(omega)^-1 A_E(omega)^dagger] at omega=i(E+i0), ONLY in static temporal normal frame',
        finite_endpoint_equation='(E-W)R_L=I-exp(i E L)exp(-i W L)',
        native_cell_discrete_kappa_is_Fourier_frequency=False)
