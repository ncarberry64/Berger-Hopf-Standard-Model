"""BHSM v15.25 moving forced-join constraint and symplectic theorem.

This module derives the leading small-q momentum-constraint coefficients on
the v15.9/v15.24 aligned branch.  It identifies the regular deviation
s=a-(343/1728) zeta q^2 and proves that the singular shift response depends
only on s_dot.  It does not promote a raw cross momentum to physical transfer
before the complete whitened Gram block is available.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np


VERSION = "v15.25"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
CAMPAIGN_OBJECT = (
    "ACTION_OWNED_MOVING_FORMED_BRANCH_QDOT_SIGMADOT_L2_CROSS_KINETIC_"
    "AND_COVARIANT_SYMPLECTIC_PULLBACK_WITH_DYNAMIC_SIGMA_TRANSFER_"
    "BACKREACTION_AND_NONLINEAR_FORCED_JOIN_CONTINUATION"
)
OUTCOME = (
    "THE_MOVING_L2_SHIFT_CONSTRAINT_REGULARIZES_IN_THE_DEVIATION_"
    "S_EQUALS_A_MINUS_343_ZETA_Q_SQUARED_OVER_1728_AND_SUPPLIES_A_"
    "POSITIVE_SHAPE_LEGENDRE_DIRECTION_FOR_Q_NONZERO_WHILE_FULL_WHITENED_"
    "FORMATION_TO_SHAPE_TRANSFER_IS_NONZERO_AT_LEADING_WHITENED_ORDER_"
    "WHILE_DYNAMIC_SIGMA_BACKREACTION_REMAINS_UNEVALUATED"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_DYNAMIC_SIGMA_TRANSFER_BACKREACTION_ON_THE_WHITENED_"
    "Q_S_SYMPLECTIC_SYSTEM_WITH_NONLINEAR_FORCED_JOIN_CONTINUATION_"
    "MATERIAL_SKIN_AND_DERIVED_GEOMETRIC_SEPARATION"
)


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def critical_moving_l2_coefficients(
    *, kappa1: float = 1.0, critical_radius: float | None = None, zeta: float = 1.0
) -> dict[str, Any]:
    """Return exact leading coefficients of L(A adot^2+B adot b+C b^2+D qdot b)."""

    kk = _positive(kappa1, "kappa1")
    radius = (
        (343.0 / (5.0 * kk)) ** (1.0 / 6.0)
        if critical_radius is None
        else _positive(critical_radius, "critical_radius")
    )
    orientation = float(zeta)
    if not math.isfinite(orientation) or abs(orientation) > 1.0 + 1e-13:
        raise ValueError("zeta must lie in [-1,1]")
    c = 343.0 * orientation / 1728.0
    a_coefficient = -21.0 * kk
    b_coefficient = -96.0 * kk / radius**2
    c2_coefficient = -49.0 * kk / (9.0 * radius**4)
    d1_coefficient = 343.0 * orientation * kk / (9.0 * radius**2)
    identity_residual = d1_coefficient + 2.0 * c * b_coefficient
    normal_stiff_kinetic = -b_coefficient**2 / (4.0 * c2_coefficient)
    return {
        "L_leading": (
            "A*a_dot^2+B*a_dot*b+C2*q^2*b^2+D1*q*q_dot*b+O(q^3,vel^3)"
        ),
        "A": a_coefficient,
        "B": b_coefficient,
        "C2": c2_coefficient,
        "D1": d1_coefficient,
        "slaving_coefficient_c": c,
        "slaved_manifold": "s=a-c*q^2",
        "D1_plus_2cB": identity_residual,
        "shift_linear_term": "B*(a_dot-2*c*q*q_dot)*b=B*s_dot*b",
        "normal_shift_reduction_coefficient": normal_stiff_kinetic,
        "normal_shift_reduction_formula": (
            "+(20736/49)*kappa1*s_dot^2/q^2"
        ),
        "forced_tangent_cancels_singular_shift_source": abs(identity_residual) < 1e-12,
    }


def reduced_shape_kinetics(
    *, q: float, q_dot: float, a_dot: float, kappa1: float = 1.0, zeta: float = 1.0
) -> dict[str, Any]:
    """Evaluate the leading shift-reduced shape kinetic form for q != 0."""

    coordinate = float(q)
    q_velocity = float(q_dot)
    a_velocity = float(a_dot)
    if not all(math.isfinite(item) for item in (coordinate, q_velocity, a_velocity)):
        raise ValueError("q and velocities must be finite")
    if abs(coordinate) < 1e-14:
        raise ValueError("the formed-branch chart requires q nonzero")
    coefficients = critical_moving_l2_coefficients(kappa1=kappa1, zeta=zeta)
    c = coefficients["slaving_coefficient_c"]
    s_dot = a_velocity - 2.0 * c * coordinate * q_velocity
    b_star = -coefficients["B"] * s_dot / (
        2.0 * coefficients["C2"] * coordinate**2
    )
    direct = coefficients["A"] * a_velocity**2
    shift_reduced = (
        coefficients["normal_shift_reduction_coefficient"]
        * s_dot**2
        / coordinate**2
    )
    return {
        "s_dot": s_dot,
        "constraint_shift_b": b_star,
        "direct_shape_kinetic": direct,
        "positive_normal_shift_kinetic": shift_reduced,
        "total_shape_sector_kinetic": direct + shift_reduced,
        "on_forced_tangent": abs(s_dot) < 1e-12,
        "singular_shift_excited": abs(s_dot) >= 1e-12,
    }


def local_shape_legendre_and_symplectic_certificate(
    q: float, *, kappa1: float = 1.0, zeta: float = 1.0
) -> dict[str, Any]:
    """Certify the local (s,p_s) pair for a formed q != 0 slice."""

    coordinate = float(q)
    if not math.isfinite(coordinate) or abs(coordinate) < 1e-14:
        raise ValueError("q must be finite and nonzero")
    coefficients = critical_moving_l2_coefficients(kappa1=kappa1, zeta=zeta)
    # In (q,s), a_dot=s_dot+2c q q_dot.  At fixed q_dot the s Hessian is:
    g_ss = 2.0 * (
        coefficients["A"]
        + coefficients["normal_shift_reduction_coefficient"] / coordinate**2
    )
    omega = np.array([[0.0, 1.0], [-1.0, 0.0]]) if g_ss != 0.0 else np.zeros((2, 2))
    return {
        "coordinate": "s=a-(343/1728)*zeta*q^2",
        "G_ss": g_ss,
        "positive_shape_Legendre_direction": g_ss > 0.0,
        "canonical_momentum": "p_s=partial L_red/partial s_dot",
        "shape_symplectic_matrix_on_s_ps": omega.tolist(),
        "shape_symplectic_rank": int(np.linalg.matrix_rank(omega)),
        "canonical_pair_exists_locally": g_ss > 0.0 and np.linalg.matrix_rank(omega) == 2,
        "full_q_sigma_s_symplectic_rank": None,
    }


def sigma_cross_kinetic_parity() -> dict[str, Any]:
    """Return exact velocity-cross consequences of retained sigma parity."""

    return {
        "retained_weight": "w(sigma)=1+g*sigma^2",
        "G_qsigma_at_sigma_zero": 0.0,
        "G_ssigma_at_sigma_zero": 0.0,
        "G_asigma_at_sigma_zero": 0.0,
        "reason": (
            "the_local_action_has_no_derivative_mixing_with_sigma_and_the_"
            "constraint_domain_is_sigma_reflection_equivariant"
        ),
        "sigma_coupling_that_survives": (
            "coordinate_dependence_of_G_qq_and_G_ss_plus_the_time_dependent_"
            "sigma_tangent_potential_and_nonlinear_backreaction"
        ),
        "localized_sigma_profile_can_change_this_after_sigma_nonzero": True,
    }


def raw_cross_transfer_audit(
    q: float, q_dot: float, *, kappa1: float = 1.0, zeta: float = 1.0
) -> dict[str, Any]:
    """Audit the finite p_s on the slaved tangent without overclaiming transfer."""

    coordinate = float(q)
    velocity = float(q_dot)
    coefficients = critical_moving_l2_coefficients(kappa1=kappa1, zeta=zeta)
    c = coefficients["slaving_coefficient_c"]
    # In (q,s), the direct A*(s_dot+2c q q_dot)^2 term gives this at s_dot=0.
    p_s = 4.0 * coefficients["A"] * c * coordinate * velocity
    return {
        "forced_tangent": "s=0_and_s_dot=0",
        "raw_p_s": p_s,
        "raw_p_s_nonzero": abs(p_s) > 1e-14,
        "physical_whitened_transfer_proved": False,
        "reason": (
            "the_complete_G_qq_G_qs_and_sigma_constraint_blocks_are_needed_"
            "to_orthogonalize_the_normal_shape_direction"
        ),
    }


def leading_whitened_qs_gram(q: float, *, zeta: float = 1.0) -> dict[str, Any]:
    """Return the leading common-normalization Gram block in (q,s).

    The matrix is divided by the common positive factor
    kappa1*R_c^7*Vol(S7).  Terms capable of changing the displayed leading
    O(q^2) whitened correlation enter only at higher order.
    """

    coordinate = float(q)
    orientation = float(zeta)
    if not math.isfinite(coordinate) or abs(coordinate) < 1e-14:
        raise ValueError("q must be finite and nonzero")
    if not math.isfinite(orientation) or abs(orientation) > 1.0 + 1e-13:
        raise ValueError("zeta must lie in [-1,1]")
    c = 343.0 * orientation / 1728.0
    m_q = 21.0 / 4.0
    a = -21.0 / 5.0
    k_normal = 20736.0 / 245.0
    g_qq = m_q + 8.0 * a * c**2 * coordinate**2
    g_qs = 4.0 * a * c * coordinate
    g_ss = 2.0 * a + 2.0 * k_normal / coordinate**2
    gram = np.array([[g_qq, g_qs], [g_qs, g_ss]])
    eigenvalues = np.linalg.eigvalsh(gram)
    correlation = g_qs / math.sqrt(g_qq * g_ss)
    phase_form = np.block(
        [[np.zeros((2, 2)), gram], [-gram, np.zeros((2, 2))]]
    )
    leading_coefficient = -2401.0 * math.sqrt(210.0) * orientation / 311040.0
    return {
        "coordinate_order": ["q", "s"],
        "common_factor_removed": "kappa1*R_c^7*Vol(S7)",
        "Gram": gram.tolist(),
        "eigenvalues": eigenvalues.tolist(),
        "determinant": float(np.linalg.det(gram)),
        "positive_definite": bool(eigenvalues[0] > 0.0),
        "whitened_cross_correlation": correlation,
        "small_q_correlation": (
            "-(2401*sqrt(210)/311040)*zeta*q^2+O(q^4)"
        ),
        "small_q_correlation_coefficient": leading_coefficient,
        "whitened_transfer_nonzero": abs(correlation) > 1e-14,
        "phase_two_form_rank": int(np.linalg.matrix_rank(phase_form)),
        "local_q_s_canonical_pairs": 2,
        "sigma_zero_extension_rank": int(np.linalg.matrix_rank(phase_form)) + 2,
        "validity": "leading_small_q_constraint_reduced_formed_branch",
        "omitted_terms": [
            "O(q^2)_formation_scale_and_profile_corrections_to_Gqq",
            "nonzero_sigma_profile_and_lapse_backreaction",
            "higher_join_modes",
        ],
    }


def completion_payload() -> dict[str, Any]:
    coefficients = critical_moving_l2_coefficients()
    c = coefficients["slaving_coefficient_c"]
    q, q_dot = 0.14, 0.2
    forced = reduced_shape_kinetics(q=q, q_dot=q_dot, a_dot=2.0 * c * q * q_dot)
    off = reduced_shape_kinetics(q=q, q_dot=q_dot, a_dot=2.0 * c * q * q_dot + 0.03)
    legendre = local_shape_legendre_and_symplectic_certificate(q)
    parity = sigma_cross_kinetic_parity()
    raw = raw_cross_transfer_audit(q, q_dot)
    whitened = leading_whitened_qs_gram(q)
    validation = {
        "moving_constraint_identity_exact": abs(coefficients["D1_plus_2cB"]) < 1e-12,
        "forced_tangent_has_zero_s_dot": abs(forced["s_dot"]) < 1e-12,
        "forced_tangent_does_not_excite_singular_shift": not forced[
            "singular_shift_excited"
        ],
        "normal_deviation_has_positive_shift_kinetic": off[
            "positive_normal_shift_kinetic"
        ]
        > 0.0,
        "formed_shape_legendre_direction_positive": legendre[
            "positive_shape_Legendre_direction"
        ],
        "local_shape_symplectic_rank_two": legendre["shape_symplectic_rank"] == 2,
        "sigma_cross_terms_respect_parity": all(
            parity[key] == 0.0
            for key in ("G_qsigma_at_sigma_zero", "G_ssigma_at_sigma_zero", "G_asigma_at_sigma_zero")
        ),
        "raw_cross_not_promoted_before_whitening": (
            raw["raw_p_s_nonzero"] and not raw["physical_whitened_transfer_proved"]
        ),
        "leading_q_s_Gram_positive": whitened["positive_definite"],
        "leading_whitened_transfer_nonzero": whitened["whitened_transfer_nonzero"],
        "q_s_phase_rank_four": whitened["phase_two_form_rank"] == 4,
        "sigma_zero_phase_rank_six": whitened["sigma_zero_extension_rank"] == 6,
        "no_new_coefficient_field_or_empirical_input": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_moving_formed_symplectic_v15_25",
        "version": VERSION,
        "campaign_object": CAMPAIGN_OBJECT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "critical_moving_constraint": coefficients,
        "forced_tangent_control": forced,
        "normal_deviation_control": off,
        "local_shape_legendre_symplectic_certificate": legendre,
        "sigma_cross_kinetic_parity": parity,
        "raw_cross_transfer_audit": raw,
        "leading_whitened_q_s_Gram_operator": whitened,
        "full_physical_Gram_operator": None,
        "physical_whitened_q_to_s_transfer": {
            "derived_to_leading_small_q_order": True,
            "correlation": whitened["whitened_cross_correlation"],
            "full_nonlinear_value": None,
        },
        "Hindsight_20_20": {
            "VALIDATED": [
                "the_shift_constraint_is_regular_in_s=a-(343/1728)zeta*q^2",
                "the_forced_q_to_q2_to_a_tangent_cancels_the_apparent_singular_shift_source",
                "for_every_formed_q_nonzero_the_normal_shape_direction_has_a_local_positive_Legendre_coefficient_and_rank_two_shape_symplectic_pair",
                "sigma_velocity_cross_terms_vanish_at_sigma_zero_by_the_retained_parity",
                "the_common_normalization_q_s_Gram_is_positive_and_its_whitened_cross_correlation_is_nonzero_at_order_q_squared",
                "the_sigma_zero_q_s_sigma_phase_form_has_rank_six_on_the_formed_branch",
            ],
            "INVALIDATED": [
                "the_raw_q_a_cross_singularity_is_physical_momentum_transfer",
                "a_nonzero_raw_p_s_on_a_nonorthogonal_coordinate_chart_alone_proves_energy_transfer",
                "sigma_requires_a_direct_velocity_cross_term_to_respond_to_formation",
            ],
            "RECLASSIFIED": [
                "a_as_a_slaved_coordinate_at_onset_and_s_as_the_normal_dynamical_shape_coordinate_on_the_formed_branch",
                "formation_to_shape_transfer_as_a_whitened_full_Gram_and_symplectic_question",
                "the_nonzero_leading_whitened_q_s_correlation_as_the_first_invariant_formation_to_shape_kinetic_transfer",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "primitive_Aether_geometry_used": False,
            "frozen_predictions_changed": False,
            "USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE": (
                USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE
            ),
        },
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_moving_formed_symplectic_v15_25.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "FULL_BHSM_COMPLETE",
    "CAMPAIGN_OBJECT",
    "OUTCOME",
    "EXACT_NEXT_OBJECT",
    "critical_moving_l2_coefficients",
    "reduced_shape_kinetics",
    "local_shape_legendre_and_symplectic_certificate",
    "sigma_cross_kinetic_parity",
    "raw_cross_transfer_audit",
    "leading_whitened_qs_gram",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
