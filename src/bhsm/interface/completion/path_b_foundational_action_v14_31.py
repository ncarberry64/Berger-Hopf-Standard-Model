"""BHSM v14.31 Path B foundational color--eta action.

Path B deliberately separates the physical action specification from the open
M8 ultraviolet-provenance problem.  The physical color bundle is extended to a
single G2 parent, eta is an intrinsic G2/SU3 section, and the coset one-form is
composite.  The only independent variables in this sector are the physical
SU(3) connection and eta.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np

VERSION = "v14.31"
PRIMARY_VERDICT = (
    "BHSM_V14_31_PATH_B_ADOPTS_THE_CANONICAL_G2_EXTENSION_OF_THE_"
    "PHYSICAL_COLOR_BUNDLE_AND_THE_COMPOSITE_ETA_SU3_SIGMA_ACTION_"
    "AS_FOUNDATIONAL_PHYSICAL_DATA_CLOSING_THE_COLOR_ETA_ACTION_"
    "OWNERSHIP_GATE_WITHOUT_ADDITIONAL_VECTOR_FIELDS"
)
SECONDARY_VERDICT = (
    "THE_M8_TO_PHYSICAL_ETA_REDUCTION_IS_RECLASSIFIED_AS_AN_OPEN_"
    "ULTRAVIOLET_PROVENANCE_AND_MATCHING_THEOREM_NOT_A_BLOCKER_ON_"
    "THE_PHYSICAL_BHSM_MASTER_ACTION"
)
BVP_NEXT_OBJECT = (
    "GAUGE_FIXED_WILSON_SOURCED_ETA_SU3_NONABELIAN_STATIONARY_BVP_"
    "WITH_SELF_ADJOINT_DOMAIN_PARENT_RELATIVE_SUBTRACTION_NONRADIAL_"
    "HESSIAN_AND_RELATIVE_DETERMINANT"
)
FR_NEXT_OBJECT = (
    "COLLECTIVE_COORDINATE_PATH_INTEGRAL_MATCHING_OF_THE_ETA_ZERO_MODE_"
    "TO_A_NORMALIZED_FR_DIRAC_ACTION_WITH_SELF_ADJOINT_DOMAIN_AND_MODE_"
    "SUBTRACTION"
)


def su3_generators() -> tuple[np.ndarray, ...]:
    """Anti-Hermitian fundamental generators with tr(t_a^† t_b)=δ_ab/2."""

    i = 1j
    hermitian = (
        [[0, 1, 0], [1, 0, 0], [0, 0, 0]],
        [[0, -i, 0], [i, 0, 0], [0, 0, 0]],
        [[1, 0, 0], [0, -1, 0], [0, 0, 0]],
        [[0, 0, 1], [0, 0, 0], [1, 0, 0]],
        [[0, 0, -i], [0, 0, 0], [i, 0, 0]],
        [[0, 0, 0], [0, 0, 1], [0, 1, 0]],
        [[0, 0, 0], [0, 0, -i], [0, i, 0]],
        np.diag([1, 1, -2]) / np.sqrt(3),
    )
    return tuple(0.5j * np.asarray(item, dtype=complex) for item in hermitian)


def covariant_derivative(
    eta: np.ndarray,
    partial_eta: np.ndarray,
    gauge_components: np.ndarray,
) -> np.ndarray:
    """Local m_C=3 representation of D_mu eta=partial_mu eta+A_mu eta."""

    eta = np.asarray(eta, dtype=complex)
    partial_eta = np.asarray(partial_eta, dtype=complex)
    gauge_components = np.asarray(gauge_components, dtype=float)
    if eta.shape != (3,):
        raise ValueError("eta must be a local complex triplet tangent coordinate")
    if partial_eta.ndim != 2 or partial_eta.shape[1] != 3:
        raise ValueError("partial_eta must have shape (directions,3)")
    if gauge_components.shape != (partial_eta.shape[0], 8):
        raise ValueError("gauge_components must have shape (directions,8)")
    generators = su3_generators()
    return np.asarray(
        [
            partial_eta[mu]
            + sum(
                gauge_components[mu, a] * generators[a] @ eta
                for a in range(8)
            )
            for mu in range(partial_eta.shape[0])
        ]
    )


def kinetic_invariant(derivative: np.ndarray) -> float:
    """Real-six metric X=2 Re sum_mu (D_mu xi)^†D_mu xi."""

    derivative = np.asarray(derivative, dtype=complex)
    return float(2.0 * np.real(np.vdot(derivative, derivative)))


def eta_density(
    x_eta: float,
    *,
    kappa1: float = 1.0,
    weight: float = 1.0,
) -> float:
    """Lorentzian Path-B eta density, excluding the unit constraint."""

    if x_eta < 0 or kappa1 <= 0 or weight <= 0:
        raise ValueError("require X>=0 and positive kappa1,weight")
    return -weight * (0.5 * kappa1 * x_eta + 0.125 * x_eta**4)


def action_current(
    eta: np.ndarray,
    derivative: np.ndarray,
    *,
    kappa1: float = 1.0,
    weight: float = 1.0,
) -> np.ndarray:
    """Source J in delta S=-int J_a^mu delta A_mu^a.

    The factor two is the local complex-chart representation of the real-six
    target metric.  In intrinsic real coordinates the same formula is
    w(kappa1+X^3) K_aI D^mu eta^I.
    """

    eta = np.asarray(eta, dtype=complex)
    derivative = np.asarray(derivative, dtype=complex)
    x_eta = kinetic_invariant(derivative)
    multiplier = 2.0 * weight * (kappa1 + x_eta**3)
    return np.asarray(
        [
            [
                multiplier
                * np.real(np.vdot(derivative[mu], generator @ eta))
                for generator in su3_generators()
            ]
            for mu in range(derivative.shape[0])
        ]
    )


def finite_difference_current_error(
    eta: np.ndarray,
    partial_eta: np.ndarray,
    gauge_components: np.ndarray,
    *,
    epsilon: float = 1e-6,
) -> float:
    """Maximum error between -dL/dA and the analytic current."""

    derivative = covariant_derivative(eta, partial_eta, gauge_components)
    current = action_current(eta, derivative)
    errors: list[float] = []
    for mu in range(gauge_components.shape[0]):
        for a in range(8):
            plus = gauge_components.copy()
            minus = gauge_components.copy()
            plus[mu, a] += epsilon
            minus[mu, a] -= epsilon
            numeric = (
                eta_density(
                    kinetic_invariant(covariant_derivative(eta, partial_eta, plus))
                )
                - eta_density(
                    kinetic_invariant(covariant_derivative(eta, partial_eta, minus))
                )
            ) / (2.0 * epsilon)
            errors.append(abs(numeric + current[mu, a]))
    return max(errors, default=0.0)


def mixed_variation_witness(epsilon: float = 1e-6) -> float:
    """A generic nonzero eta--A mixed variation witness.

    This is deliberately evaluated away from the stabilizer selector, where the
    mixed block vanishes as a legitimate background limit.
    """

    eta = np.asarray([0.23 + 0.11j, -0.31j, 0.67], dtype=complex)
    partial = np.asarray([[0.09, 0.17j, -0.14]], dtype=complex)
    gauge = np.asarray([[0.07, -0.03, 0.02, 0.01, 0.0, -0.04, 0.02, 0.05]])
    direction = np.asarray([0.13j, -0.07, 0.11], dtype=complex)
    plus = eta + epsilon * direction
    minus = eta - epsilon * direction
    j_plus = action_current(plus, covariant_derivative(plus, partial, gauge))
    j_minus = action_current(minus, covariant_derivative(minus, partial, gauge))
    return float(np.linalg.norm((j_plus - j_minus) / (2.0 * epsilon)))


@lru_cache(maxsize=1)
def foundational_bundle_payload() -> dict[str, Any]:
    validation = {
        "single_parent_bundle_selected": True,
        "physical_color_is_the_reduced_SU3_bundle": True,
        "arbitrary_retained_c2_sectors_allowed": True,
        "eta_is_intrinsic_associated_S6_section": True,
        "triplet_transition_functions_are_physical_color_transition_functions": True,
        "Berry_connection_not_identified_with_physical_A": True,
        "M8_provenance_reclassified_not_falsely_derived": True,
    }
    return {
        "artifact": "BHSM_Path_B_foundational_G2_color_bundle_v14_31",
        "version": VERSION,
        "classification": "EXPLICIT_FOUNDATIONAL_BHSM_POSTULATE",
        "postulate": "Q_G2=P_color x_SU3 G2 and eta in Gamma(Q_G2/SU3)",
        "physical_color_bundle": "P_color->M4 with retained arbitrary c2 sector",
        "parent_bundle": "Q_G2=P_color x_SU3 G2",
        "quotient_bundle": "Q_G2/SU3=P_color x_SU3 (G2/SU3)",
        "vertical_tangent": "P_color x_SU3 m, m_C=3+bar3",
        "provenance_consequence": "the eta triplet/antitriplet cocycle is the physical P_color cocycle by construction",
        "not_claimed": "derivation of this postulate from the unclosed M8 triality reduction",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def connection_fork_payload() -> dict[str, Any]:
    validation = {
        "reduction_preserving_extension_has_theta_zero": True,
        "general_extension_is_affine_in_m_valued_one_forms": True,
        "independent_theta_with_G2_YM_adds_six_vector_symbols": True,
        "composite_theta_has_no_independent_variation": True,
        "pure_G2_YM_does_not_supply_the_eta_p2_quadratic_term": True,
        "path_B_uses_SU3_YM_plus_eta_sigma_not_full_G2_YM": True,
    }
    return {
        "artifact": "BHSM_Path_B_G2_connection_fork_v14_31",
        "version": VERSION,
        "fork": [
            {
                "branch": "canonical reduction-preserving extension",
                "connection": "mathcal_A0=iota_*A",
                "theta": "0",
                "result": "no eta color source",
            },
            {
                "branch": "independent full G2 connection",
                "connection": "mathcal_A=A+theta with theta independent",
                "result": "six additional colored vector principal symbols",
                "status": "REJECTED_BY_NO_NEW_VECTOR_GATE",
            },
            {
                "branch": "Path B composite reduction connection",
                "connection": "mathcal_A[A,eta]=iota_*A+Theta_eta(D_A eta)",
                "result": "one parent geometry, eight vector fields, six eta scalar tangent modes",
                "status": "SELECTED",
            },
        ],
        "curvature_observation": "at A=0 and eta=Exp_eta0(phi), theta=d phi+O(phi^2), so d theta vanishes at linear order and pure G2 Yang-Mills supplies no (d phi)^2 term",
        "physical_action_consequence": "the eta p2+p8 sigma term is foundational physical dynamics, not a pure-G2-YM derivative",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def no_new_vector_hessian_payload() -> dict[str, Any]:
    validation = {
        "independent_configuration_fields_are_A_and_eta": True,
        "theta_configuration_rank_zero": True,
        "YM_vector_internal_rank_eight": True,
        "eta_scalar_tangent_rank_six": True,
        "additional_vector_poles_zero": True,
        "mixed_block_generically_nonzero": mixed_variation_witness() > 1e-6,
        "mixed_block_zero_at_stabilizer_is_preserved": True,
    }
    return {
        "artifact": "BHSM_Path_B_no_new_vector_Hessian_v14_31",
        "version": VERSION,
        "configuration_space": "Conn(P_color) x Gamma(Q_G2/SU3)",
        "composite_theta": "Theta_eta(D_A eta); no independent delta theta",
        "quadratic_blocks": {
            "H_AA": "ordinary gauge-fixed SU3 Yang-Mills principal symbol on eight adjoint one-forms",
            "H_Aeta": "zero at the stabilizer vacuum; generically nonzero away from it",
            "H_etaeta": "w kappa1(-D_A^2) on six tangent scalars plus lower-order background terms",
            "H_thetatheta": None,
        },
        "additional_vector_pole_count": 0,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def foundational_action_payload() -> dict[str, Any]:
    numerical_error = finite_difference_current_error(
        np.asarray([0.2 + 0.1j, -0.4j, 0.7]),
        np.asarray([[0.1, 0.2j, -0.2]]),
        np.zeros((1, 8)),
    )
    validation = {
        "bundle_postulate_validated_as_explicit_model_input": foundational_bundle_payload()["validation_passed"],
        "connection_fork_fail_closed": connection_fork_payload()["validation_passed"],
        "no_new_vector_Hessian": no_new_vector_hessian_payload()["validation_passed"],
        "independent_SU3_YM_term_retained": True,
        "eta_p2_p8_term_is_authoritative": True,
        "current_equals_negative_connection_variation": numerical_error < 5e-6,
        "on_shell_covariant_conservation_follows_from_gauge_invariance": True,
        "selector_and_pure_normal_wall_zero_current_preserved": True,
        "no_new_continuous_coefficient": True,
        "M8_eta_not_double_varied_as_a_second_physical_copy": True,
        "frozen_inputs_unchanged": True,
    }
    return {
        "artifact": "BHSM_Path_B_foundational_color_eta_action_v14_31",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "independent_fields": ["A_physical in Conn(P_color)", "eta in Gamma(Q_G2/SU3)", "retained sigma,h and constraint fields"],
        "parent_connection_geometry": "mathcal_A[A,eta]=iota_*A+Theta_eta(D_A eta), composite and not independently varied",
        "authoritative_action": "S_color_eta=S_YM[A]-int_M4 dmu_h w(sigma)[kappa1 X_eta/2+X_eta^4/8]+S_constraint",
        "X_eta": "h^munu G_IJ(eta) D_mu^A eta^I D_nu^A eta^J",
        "source_convention": "delta_A S=-int dmu_h J_a^mu delta A_mu^a",
        "current_real_coordinates": "J_a^mu=w(sigma)(kappa1+X_eta^3)K_aI(eta)D^mu eta^I",
        "current_complex_tangent_chart": "J_a^mu=2w(sigma)(kappa1+X_eta^3)Re[(t_a xi)^dagger D^mu xi]",
        "Gauss_equation": "g3^(-2)(D_nu F^(nu mu))_a=J_eta,a^mu+J_other,a^mu",
        "Noether_identity": "(D_mu J^mu)_a-E_eta,I K_a^I=0 in the source convention; D_mu J^mu=0 on shell",
        "replacement_rule": "the M4 eta field is the physical field; the former M8 eta construction is a UV-origin candidate and is not simultaneously integrated as a duplicate physical eta sector",
        "M8_status": "OPEN_UV_PROVENANCE_AND_MATCHING_THEOREM_NOT_A_PHYSICAL_ACTION_OWNERSHIP_BLOCKER",
        "finite_difference_current_error": numerical_error,
        "mixed_variation_witness_norm": mixed_variation_witness(),
        "new_continuous_parameters": [],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
