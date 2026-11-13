"""Exact additive-LR symbol identities and conditional carrier form bounds.

The symbol calculation uses the adopted (+---) Dirac convention.  Its
algebraic partner is distinguished from the geometric L2 adjoint.  The bounds
below require a separately verified insertion A1=A0+E on the full one-end
carrier form domain; they do not identify or bound the physical incoming E.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

import sympy as sp


def _exact_nonnegative(value: Fraction, name: str, *, positive: bool = False) -> Fraction:
    if not isinstance(value, Fraction):
        raise TypeError(name + " must be an exact Fraction")
    if value < 0 or (positive and value == 0):
        raise ValueError(name + (" must be positive" if positive else " must be nonnegative"))
    return value


def _dirac_gammas() -> tuple[sp.Matrix, ...]:
    """Exact version of foundational_dirac_spin_glue_v14_45 lines 79--89."""
    eye, zero = sp.eye(2), sp.zeros(2)
    pauli = (
        sp.Matrix([[0, 1], [1, 0]]),
        sp.Matrix([[0, -sp.I], [sp.I, 0]]),
        sp.diag(1, -1),
    )
    beta = sp.diag(eye, -eye)
    return (beta,) + tuple(sp.BlockMatrix([[zero, s], [-s, zero]]).as_explicit()
                          for s in pauli)


def exact_lr_symbol_identity() -> dict[str, Any]:
    """Prove coefficient identities, without numerical fields or momenta.

    For M=r I+i j gamma5 and Dkin=i gamma^a nabla_a, the cancelling
    algebraic partner is Dkin+M^dagger.  The actual positive symbol uses
    (Dkin-M)^dagger(Dkin-M).  Real momenta suffice to expose its surviving
    normal first-order cross coefficient -2 p0 B(m), with B=beta M.
    Lower-order connection, moving pairing, source and boundary terms are
    not assigned values by this local principal/coefficient calculation.
    """
    gamma = _dirac_gammas()
    beta = gamma[0]
    gamma5 = sp.I * gamma[0] * gamma[1] * gamma[2] * gamma[3]
    r, j = sp.symbols("m_real m_imag", real=True)
    momenta = sp.symbols("p0 p1 p2 p3", real=True)
    mass = r * sp.eye(4) + sp.I * j * gamma5
    bilinear = beta * mass
    kinetic = sum((p * g for p, g in zip(momenta, gamma)), sp.zeros(4))
    full = kinetic - mass
    algebraic = (kinetic + mass.H) * full
    positive = full.H * full
    positive_cross = positive - kinetic.H * kinetic - mass.H * mass
    expected_cross = -2 * momenta[0] * bilinear

    def reduced(matrix: sp.MatrixBase) -> sp.Matrix:
        return matrix.applyfunc(sp.expand)

    def zero(matrix: sp.MatrixBase) -> bool:
        return reduced(matrix) == sp.zeros(matrix.rows, matrix.cols)

    intertwiners = [g * mass - mass.H * g for g in gamma]
    residuals = {
        "gamma_mass_intertwining": [zero(item) for item in intertwiners],
        "beta_mass_is_Hermitian": zero(bilinear - bilinear.H),
        "mass_norm_square": zero(mass.H * mass - (r*r + j*j) * sp.eye(4)),
        "algebraic_partner_principal_cancellation": zero(
            algebraic - kinetic*kinetic + mass.H*mass),
        "positive_adjoint_cross_identity": zero(positive_cross - expected_cross),
        "literal_antisymmetric_mass_absorption": zero(-beta*mass + mass.H*beta),
    }
    real_normal_cross = reduced(expected_cross.subs(j, 0))
    return {
        "classification": "EXACT_ACTION_SPECIFIC_LOCAL_SYMBOL_IDENTITY",
        "signature": "(+---)",
        "symbolic_operands": [str(r), str(j), *map(str, momenta)],
        "gamma5": str(gamma5),
        "covariant_mass": "M=m_real I+i m_imag gamma5=m P_R+conjugate(m) P_L",
        "ordered_bilinear": "B(m)=beta M; B(m)^dagger=B(m)",
        "algebraic_partner_equation": (
            "(Dkin+M^dagger)(Dkin-M)=Dkin^2-i gamma^a(nabla_a M)-M^dagger M"
        ),
        "algebraic_partner_is_positive_adjoint": False,
        "positive_symbol_equation": (
            "(gamma.p-M)^dagger(gamma.p-M)=(gamma.p)^dagger(gamma.p)"
            "+|m|^2 I-2 p0 B(m)"
        ),
        "positive_normal_cross_matrix": str(reduced(expected_cross)),
        "real_mass_normal_cross_matrix": str(real_normal_cross),
        "real_mass_beta_positive_entry": str(real_normal_cross[0, 0]),
        "normal_cross_is_identically_zero": zero(expected_cross),
        "zero_residuals": residuals,
        "residual_validation_passed": all(
            all(value) if isinstance(value, list) else value for value in residuals.values()
        ),
        "physical_incoming_mass_or_direction_evaluated": False,
        "positive_carrier_embedding_established": False,
        "source_conventions": {
            "gamma": "completion/foundational_dirac_spin_glue_v14_45.dirac_gamma_matrices",
            "additive_action": "completion/foundational_dirac_spin_glue_v14_45.foundational_action_payload",
            "Euler_mass": "ae31_c2_intrinsic_m4_lepton_action.first_variation_and_pole_gate",
            "positive_owner": "ae4_stratified_dirac_zeta_induced_owner.microscopic_owner_contract",
        },
    }


def conditional_squared_extension_form_bound(
    *, duration_upper: Fraction, superpotential_upper: Fraction,
    insertion_norm_upper: Fraction, seam_inverse_upper: Fraction | None = None,
) -> dict[str, Fraction | bool | str | None]:
    """Bound q1-q0 if A1=A0+E is verified in the inherited pairing/domain.

    q0=||A0 u||^2+kappa^2||u||^2, A0=partial_tau+W, ||W||<=S.
    Every u in the form domain vanishes at the birth endpoint; its terminal
    trace may be nonzero.  One-end Poincare yields ||u||<=ell*q0[u]^(1/2).
    The exact difference is 2 Re<A0u,Eu>+||Eu||^2, so eta=2w+w^2, w=a ell.
    No derivative of E or integration by parts is used.  This retains all
    derivative cross terms and the E-dependent conormal of the new square.
    """
    t = _exact_nonnegative(duration_upper, "duration_upper", positive=True)
    s = _exact_nonnegative(superpotential_upper, "superpotential_upper")
    a = _exact_nonnegative(insertion_norm_upper, "insertion_norm_upper")
    b = None if seam_inverse_upper is None else _exact_nonnegative(
        seam_inverse_upper, "seam_inverse_upper", positive=True)
    denominator = Fraction(3, 2) - s*t
    if denominator <= 0:
        raise ValueError("one-end form bound requires S*T < 3/2")
    ell = t / denominator
    w = a * ell
    eta = 2*w + w*w
    closed = eta < 1
    return {
        "classification": "CONDITIONAL_COMMON_DOMAIN_SQUARED_EXTENSION_FORM_BOUND",
        "one_end_L2_over_form_upper": ell,
        "relative_insertion_upper": w,
        "relative_form_upper": eta,
        "relative_coercivity_lower": 1-eta,
        "coercivity_criterion_satisfied": closed,
        "rational_sufficient_insertion_threshold": Fraction(2, 5)/ell,
        "rational_sufficient_criterion_satisfied": w < Fraction(2, 5),
        "rational_threshold_relative_form_upper": Fraction(24, 25),
        "sharp_symbolic_insertion_threshold": "(sqrt(2)-1)/ell",
        "completed_seam_inverse_upper": b/(1-eta) if closed and b is not None else None,
        "physical_incoming_LR_bound_established": False,
        "positive_carrier_embedding_required": True,
    }


def conditional_amplitude_weighted_form_bound(
    *, duration_coefficient_upper: Fraction, lambda_upper: Fraction,
    superpotential_upper: Fraction, lambda_squared_insertion_norm_upper: Fraction,
    seam_inverse_upper: Fraction | None = None,
) -> dict[str, Fraction | bool | str | None]:
    """Use sup(lambda^2 ||E_lambda||) over the unselected amplitude family.

    T_lambda<=a_duration*lambda^2.  Thus w<=a_duration*e_weighted/
    (3/2-S*a_duration*lambda_upper^2), without an unweighted mass bound.
    No amplitude member is evaluated or selected.
    """
    coefficient = _exact_nonnegative(
        duration_coefficient_upper, "duration_coefficient_upper", positive=True)
    limit = _exact_nonnegative(lambda_upper, "lambda_upper", positive=True)
    weighted = _exact_nonnegative(
        lambda_squared_insertion_norm_upper, "lambda_squared_insertion_norm_upper")
    result = conditional_squared_extension_form_bound(
        duration_upper=coefficient*limit*limit,
        superpotential_upper=superpotential_upper,
        insertion_norm_upper=weighted/(limit*limit),
        seam_inverse_upper=seam_inverse_upper,
    )
    result["classification"] = "CONDITIONAL_AMPLITUDE_WEIGHTED_SQUARED_EXTENSION_FORM_BOUND"
    result["lambda_squared_insertion_rational_threshold"] = (
        result["rational_sufficient_insertion_threshold"]*limit*limit
    )
    result["amplitude_member_selected"] = False
    return result


def exact_squared_form_and_conormal_identity() -> dict[str, str | bool]:
    """Record the exact common-domain form identity and its boundary contact."""
    return {
        "classification": "CONDITIONAL_COMMON_DOMAIN_IDENTITY",
        "hypothesis": "A1=A0+E in the same geometric L2 pairing; A0=partial_tau+W",
        "form_domain": "u in H1; u(0)=0; arbitrary terminal trace u(T)",
        "form_difference": "q1[u]-q0[u]=2 Re<A0 u,E u>+<E u,E u>",
        "polarized_difference": "r(u,v)=<A0u,Ev>+<Eu,A0v>+<Eu,Ev>",
        "interior_differential_difference": (
            "A1^dagger A1-A0^dagger A0=(E^dagger-E)partial_tau"
            "-partial_tau(E)+W^dagger E+E^dagger W+E^dagger E"
        ),
        "interior_expression_scope": "normalized d_tau L2; regular E; fixed common trivialization",
        "first_order_cross_cancels_iff": "E^dagger=E for this normalized derivative principal symbol",
        "terminal_conormal": "Gamma1,1 u=(A0+E)u(T)=Gamma1,0 u+E(T)u(T)",
        "terminal_form_contact": "<u(T),E(T)v(T)>",
        "contact_in_already_polarized_form_counted_again": False,
        "squared_operator_flux_graph_must_use_new_conormal": True,
        "physical_incoming_LR_embedding_established": False,
    }


__all__ = [
    "exact_lr_symbol_identity", "conditional_squared_extension_form_bound",
    "conditional_amplitude_weighted_form_bound", "exact_squared_form_and_conormal_identity",
]
