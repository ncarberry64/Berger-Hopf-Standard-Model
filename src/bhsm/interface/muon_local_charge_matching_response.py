"""The owned local photon kinetic counterterm under charge matching.

An independently matched Thomson charge removes a local, constant F²
coefficient from the current-current exchange. A restricted numerical
matrix proportional to a tested form is only a candidate restriction of
that local coefficient: locality and the full momentum domain do not
follow from the proportionality test.
"""
from __future__ import annotations
import numpy as np
from .muon_magnetic_mixed_green import _finite


def local_charge_matching_identity():
    """Exact local action equation, including both external current factors."""
    import sympy as s
    e,z,k=s.symbols('e_R z k',real=True,nonzero=True)
    matched=(1+z)*e**2/((1+z)*k)
    residual=s.cancel(matched-e**2/k)
    return dict(local_action='-Z_A F_mu_nu F^mu_nu/4 + e_bare J_mu A^mu',
        normalization='A_R=sqrt(Z_A) A; e_R=e_bare/sqrt(Z_A); Z_A=1+deltaZ',
        charge_condition='independently calibrated F1(0)=1 and alpha(0)=e_R²/(4pi)',
        Ward_relation='Z_1=Z_2, so external residue and vertex normalization do not reintroduce deltaZ',
        exchange_equation='e_bare² V [(1+deltaZ) K_Maxwell]^-1 V = e_R² V K_Maxwell^-1 V',
        exact_scalar_residual=str(residual),exact_deltaZ_derivative=str(s.diff(matched,z)),
        Pauli_consequence='this local constant kinetic rescaling has zero independent Pauli correction at fixed matched alpha; momentum-dependent VP is retained',
        local_F_squared_only=True,anisotropic_or_momentum_dependent_terms_canceled=False,
        measured_anomaly_used=False)


def source_form_charge_restriction(Maxwell_form,native_form):
    """Execute the local-coefficient RESTRICTION against reached forms.

    The real constant coefficient minimizes the complex Frobenius
    restriction residual; all imaginary/nonproportional entries survive.
    This does not prove the full native form is a local F² term and
    therefore does not automatically subtract its proportional part.
    """
    K=_finite(Maxwell_form,'actual same-source Maxwell form')
    R=_finite(native_form,'actual same-source native source form')
    if K.ndim!=2 or K.shape[0]!=K.shape[1]or R.shape!=K.shape or not np.any(K):
        raise ValueError('complete nonzero SAME tested source forms required')
    norm=float(np.vdot(K,K).real)
    z=float(np.vdot(K,R).real/norm);proportional=z*K;remainder=R-proportional
    if 1+z<=0:raise ValueError('candidate kinetic normalization is not positive')
    # This is the exact action scalar identity applied to the tested form,
    # not a declaration that its inverse is a quantum photon covariance.
    inverse=np.linalg.solve(K,np.eye(len(K),dtype=complex))
    rescaled=np.linalg.solve((1+z)*K,(1+z)*np.eye(len(K),dtype=complex))
    return dict(real_proportional_coefficient=z,proportional_source_restriction=proportional,
        surviving_nonproportional_complex_source_form=remainder,
        restriction_residual_norm=float(np.linalg.norm(remainder)),native_restriction_norm=float(np.linalg.norm(R)),
        surviving_restriction_relative_norm=float(np.linalg.norm(remainder)/(np.linalg.norm(R)or 1)),
        charge_matched_scaled_inverse=rescaled,original_tested_Maxwell_inverse=inverse,
        scalar_charge_cancellation_arithmetic_defect=float(np.linalg.norm(rescaled-inverse)),
        physical_locality_or_momentum_domain_inferred_from_finite_form=False,
        subtraction_applied=False,Pauli_or_physical_photon_covariance_assigned=False,
        momentum_dependent_VP_overlap_retained=True,physical_a_mu=None,physical_g_mu=None)
