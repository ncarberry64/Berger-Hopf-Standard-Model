"""Charged/neutral local pole equation of the full reached C6 energy jet.

This retains the neutral Schur return before a mass or residue projection.
A coefficient graph supplies a matching load; its Euclidean/Lorentz and
external-domain identification is not supplied by this algebra.
"""
from __future__ import annotations
import numpy as np
from .muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian
from .muon_magnetic_open_lepton_vertex import charged_dirac_injection


def external_c6_pole_application(H,self_energy_zero,self_energy_first,*,
        family,matched_mass_action):
    """Evaluate S(E)=E*(I-Sigma_E)-M_fixedY(H)-Sigma_0 at matched E.

    The bare round/gauge connection is removed at the point by the normal
    covariant frame. Its derivatives remain in the current/soft maps.
    Complex analytic coefficients and the literal left placement are kept.
    """
    h=np.asarray(H,complex);S0=np.asarray(self_energy_zero,complex);S1=np.asarray(self_energy_first,complex)
    m=np.asarray(matched_mass_action)
    if (type(family)is not int or family not in(1,2)or h.shape!=(2,)
            or S0.shape!=(6,6)or S1.shape!=(6,6)or not np.isrealobj(m)
            or m.shape!=()or not np.isfinite(m)or m<=0
            or any(not np.isfinite(x).all()for x in(h,S0,S1))):
        raise ValueError('actual full C6 coefficient jet and positive real matched mass required')
    m=float(m);ids=np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])
    injection=charged_dirac_injection(h,family=family)
    J=injection['charged'][ids];K=injection['neutral'][ids];U=np.column_stack((J,K))
    if np.max(abs(U.conj().T@U-np.eye(6)))>8e-14:raise ArithmeticError('full charged/neutral current injection lost normalization')
    M=fixed_y_higgs_hamiltonian(h[None])[0][np.ix_(ids,ids)]
    G=np.eye(6)-S1;raw=m*G-M-S0;d_raw=G
    A=U.conj().T@raw@U;D=U.conj().T@d_raw@U
    inv=np.linalg.inv(A[4:,4:]);X=inv@A[4:,:4]
    schur=A[:4,:4]-A[:4,4:]@X
    d_schur=(D[:4,:4]-D[:4,4:]@X-A[:4,4:]@inv@D[4:,:4]
        +A[:4,4:]@inv@D[4:,4:]@X)
    beta=np.diag([1.,1.,-1.,-1.]);reference=m*(np.eye(4)-beta)
    effective_sigma=reference-schur;effective_Sigma_E=np.eye(4)-d_schur
    positive=schur[:2,:2];mass_load=np.trace(positive)/2
    # This is a diagnosed local mass counterterm/source load. It is not
    # silently inserted into the fixed-Y microscopic action.
    remaining=positive-mass_load*np.eye(2)
    rhs=np.r_[np.eye(4),np.zeros((2,4))]
    inverse_identity=U.conj().T@np.linalg.solve(raw,U@rhs)
    return dict(full_C6_inverse_symbol=raw,full_C6_energy_derivative=d_raw,
        charged_neutral_inverse_symbol=A,charged_neutral_energy_derivative=D,
        charged_effective_inverse_symbol=schur,charged_effective_energy_derivative=d_schur,
        neutral_Schur_return=A[:4,4:]@X,
        charged_effective_self_energy=effective_sigma,
        charged_effective_self_energy_energy_derivative=effective_Sigma_E,
        matched_positive_band_inverse=positive,
        isotropic_mass_matching_load=mass_load,
        surviving_positive_band_pole_matrix=remaining,
        full_C6_to_charged_inverse_identity_residual=inverse_identity[:4]-np.linalg.inv(schur),
        neutral_inverse_condition_number=float(np.linalg.cond(A[4:,4:])),
        mass_matching_load_applied_to_fixed_Y_action=False,
        charged_Green_and_residue_use_full_neutral_return=True,
        interacting_pole_or_LSZ_certified=False,
        pole_equation='det S_charged(E)=0 after neutral Schur return; at matched E=m, require the complete two-dimensional positive pole block, not only its trace',
        residue_equation='Z_pole^{-1}=l*S_charged_prime(m)*r on actual left/right null vectors; this application exports S_prime without inventing those null vectors',
        physical_a_mu=None,physical_g_mu=None)
