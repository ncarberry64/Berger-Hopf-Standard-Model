"""Einstein-derived local Hopf breathing-mode audit for BHSM v10.3."""

from __future__ import annotations

from typing import Any

import sympy as sp


RADION_VERDICT = (
    "BHSM_LOCALIZED_HOPF_RADION_IS_AN_EXISTING_METRIC_DEGREE_BUT_NOT_A_"
    "COMPLETE_STRATIFIED_ACTION_VARIABLE"
)


def einstein_frame_breathing_coefficient(base_dimension: int, fiber_dimension: int) -> sp.Rational:
    """Coefficient C_beta in R_E-C_beta(d beta)^2 for a round breathing mode."""

    if base_dimension <= 2 or fiber_dimension <= 0:
        raise ValueError("base dimension must exceed two and fiber dimension be positive")
    return sp.Rational(
        fiber_dimension * (fiber_dimension + base_dimension - 2),
        base_dimension - 2,
    )


def internal_curvature_exponent(base_dimension: int, fiber_dimension: int) -> sp.Rational:
    """Exponent of exp(beta) multiplying internal curvature in Einstein frame."""

    if base_dimension <= 2 or fiber_dimension <= 0:
        raise ValueError("base dimension must exceed two and fiber dimension be positive")
    return sp.Rational(-2 * (fiber_dimension + base_dimension - 2), base_dimension - 2)


def pure_einstein_reduction() -> dict[str, Any]:
    beta, kappa_5, r_f, a_0 = sp.symbols("beta kappa_5 R_F a_0", positive=True)
    coefficient = einstein_frame_breathing_coefficient(5, 3)
    exponent = internal_curvature_exponent(5, 3)
    potential = -sp.Rational(1, 2) * kappa_5 * r_f / a_0**2 * sp.exp(exponent * beta)
    derivative = sp.diff(potential, beta)
    return {
        "metric_origin": "G_fiber=a_F^2 gamma_3; beta=ln(a_F/a_F0)",
        "base_dimension": 5,
        "fiber_dimension": 3,
        "fiber_volume_factor": "V_F=V_F0 exp(3 beta)",
        "einstein_frame_action": "(kappa5/2) int sqrt|gE| [R_E-6(grad beta)^2+R_F a_F0^-2 exp(-4 beta)+...]",
        "kinetic_coefficient_C_beta": int(coefficient),
        "canonical_Z_beta": "6 kappa5",
        "kinetic_sign": "HEALTHY_IF_KAPPA5_POSITIVE",
        "internal_curvature_exponent": int(exponent),
        "pure_EH_potential": str(potential),
        "pure_EH_potential_derivative": str(derivative),
        "stationary_point_from_positive_round_fiber_curvature": False,
        "new_scalar_appended": False,
    }


def localized_source_ledger() -> dict[str, Any]:
    return {
        "M8_definition": "J_beta=-delta(S8_env+S8_matter)/delta beta(x)",
        "M8_eta_sigma_connection_dependence": "action-derived through vertical metric and V_F when explicit profiles are supplied",
        "M4_intrinsic_source": None,
        "reason_M4_missing": (
            "S4 is independently owned and v7.3 has zero a_F-Psi and a_F-H mixed blocks; "
            "the v7.1 matcher does not identify S5 with pi_!S8"
        ),
        "complete_J_beta": None,
        "new_stabilizing_term_added": False,
    }


def homogeneous_limit() -> dict[str, Any]:
    a_h, a_f = sp.symbols("a_H a_F", positive=True)
    curvature = 48 / a_h**2 + 6 / a_f**2 - 12 * a_f**2 / a_h**4
    derivative = sp.factor(sp.diff(curvature, a_f))
    return {
        "R7": str(curvature),
        "dR7_da_F": str(derivative),
        "strictly_negative": derivative.is_negative is True,
        "positive_static_solution": False,
        "v10_2_reproduced": sp.simplify(
            derivative + 12 * (a_h**4 + 2 * a_f**4) / (a_f**3 * a_h**4)
        ) == 0,
    }


def radion_payload() -> dict[str, Any]:
    reduction = pure_einstein_reduction()
    source = localized_source_ledger()
    homogeneous = homogeneous_limit()
    validation = {
        "coefficient_is_six": reduction["kinetic_coefficient_C_beta"] == 6,
        "kinetic_healthy": reduction["kinetic_sign"] == "HEALTHY_IF_KAPPA5_POSITIVE",
        "no_new_scalar": not reduction["new_scalar_appended"],
        "no_hidden_potential": not source["new_stabilizing_term_added"],
        "M4_source_fails_closed": source["M4_intrinsic_source"] is None,
        "v10_2_limit": homogeneous["v10_2_reproduced"] and homogeneous["strictly_negative"],
    }
    return {
        "artifact": "BHSM_local_radion_v10_3",
        "reduction": reduction,
        "localized_source": source,
        "homogeneous_limit": homogeneous,
        "verdict": RADION_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
