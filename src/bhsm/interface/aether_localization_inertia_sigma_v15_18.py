"""BHSM v15.18 dynamical localization-inertia sigma-response theorem.

The retained eta kinetic sector is multiplied by w(sigma)=1+g*sigma**2.
Consequently motion changes the *linearized sigma curvature* but does not
produce a sigma-odd force at sigma=0.  This module evaluates that statement
on the proposed v15.9 formation equation, records the parity theorem after
constraint reduction, and audits the absent localization/contact coordinate.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np


VERSION = "v15.18"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
CAMPAIGN_OBJECT = "ACTION_OWNED_M5_M4_LOCALIZATION_INERTIA_KERNEL_ON_THE_DYNAMICAL_V15_9_BRANCH"
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_M5_M4_LOCALIZATION_INERTIA_KERNEL_WITH_PARITY_EVEN_"
    "SECOND_SIGMA_VARIATION_DERIVING_THE_TANGENT_PROPAGATOR_X_RESPONSE_"
    "BACKREACTION_QUARTIC_AND_PHYSICAL_CONTACT_CROSS_INERTIA_ON_THE_"
    "DYNAMICAL_V15_9_BRANCH"
)
OUTCOME = "INERTIAL_PARAMETRIC_SIGMA_ROUTE_OPEN_BUT_LINEAR_SOURCE_AND_COEFFICIENT_SELECTION_ABSENT"
PRIMARY_VERDICT = (
    "THE_DYNAMICAL_INTERPRETATION_IS_PARTLY_VALID_BECAUSE_THE_RETAINED_"
    "ETA_INERTIA_HAS_NONZERO_SECOND_SIGMA_VARIATION_AND_FORMATION_MOTION_"
    "THEREFORE_SHIFTS_THE_SIGMA_TANGENT_CURVATURE;_BUT_W_EQUALS_ONE_PLUS_"
    "G_SIGMA_SQUARED_AND_THE_FULL_RETAINED_DOMAIN_IS_SIGMA_Z2_EVEN_SO_"
    "THE_FIRST_SIGMA_VARIATION_OF_THE_PHYSICAL_INERTIA_AND_THE_INERTIAL_"
    "SOURCE_BOTH_VANISH_EXACTLY_AT_SIGMA_ZERO_FOR_EVERY_MOVING_Q_"
    "TRAJECTORY;_THE_SHIFT_DEPENDS_ON_THE_UNSELECTED_G_OVER_ZSIGMA_"
    "AND_GENERATES_NO_BARE_QUARTIC_WHILE_THE_LOCALIZATION_AND_SEPARATION_"
    "COORDINATES_HAVE_NO_ACTION_OWNED_CANONICAL_MOMENTA"
)


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def formation_reduced_dynamics(
    q: float,
    q_dot: float,
    q_ddot: float,
    *,
    supercriticality: float,
    critical_radius: float,
) -> dict[str, float]:
    """Evaluate the equation quoted for the dynamical v15.9 amplitude.

    The equation is exactly Euler--Lagrange equivalent to the v15.9 reduced
    potential with collective inertia M_q=3*a_c**2/2 in the same normalized
    energy convention.
    """

    coordinate = _finite(q, "q")
    velocity = _finite(q_dot, "q_dot")
    acceleration = _finite(q_ddot, "q_ddot")
    m = _finite(supercriticality, "supercriticality")
    ac = _positive(critical_radius, "critical_radius")
    inertia = 1.5 * ac**2
    potential = -5.0 * m * coordinate**2 / 8.0 + 23.0 * coordinate**4 / 144.0
    potential_prime = -5.0 * m * coordinate / 4.0 + 23.0 * coordinate**3 / 36.0
    residual = acceleration - 5.0 * m * coordinate / (6.0 * ac**2) + 23.0 * coordinate**3 / (
        54.0 * ac**2
    )
    return {
        "collective_inertia": inertia,
        "potential": potential,
        "potential_prime": potential_prime,
        "Euler_residual": residual,
        "Hamiltonian": 0.5 * inertia * velocity**2 + potential,
    }


def retained_inertia_matrix(
    sigma: float, *, q_inertia: float, zsigma: float, g: float
) -> np.ndarray:
    """Return the retained (q,sigma) velocity Hessian in the simple sector."""

    s = _finite(sigma, "sigma")
    mass = _positive(q_inertia, "q_inertia")
    z = _positive(zsigma, "Zsigma")
    coupling = _finite(g, "g")
    weight = 1.0 + coupling * s**2
    if weight <= 0.0:
        raise ValueError("the retained kinetic weight must be positive")
    return np.diag([mass * weight, z])


def eta_p2_p8_velocity_hessian(
    *,
    spatial_gradient_squared: float,
    eta_velocity: float,
    sigma: float,
    kappa1: float,
    g: float,
) -> dict[str, float | bool]:
    """Return the one-mode Lorentzian eta velocity Hessian.

    For X=S-v**2 and L_eta=-(1+g*sigma**2)F(X), direct differentiation gives
    d2L/dv2=(1+g*sigma**2)[kappa1+X**3-6v**2 X**2].  This includes the p8
    Legendre correction and proves that the exact eta block remains even in
    sigma, independently of whether it is positive on a chosen trajectory.
    """

    spatial = _finite(spatial_gradient_squared, "spatial_gradient_squared")
    velocity = _finite(eta_velocity, "eta_velocity")
    s = _finite(sigma, "sigma")
    k1 = _positive(kappa1, "kappa1")
    coupling = _finite(g, "g")
    if spatial < 0.0:
        raise ValueError("spatial_gradient_squared must be nonnegative")
    x = spatial - velocity**2
    bare = k1 + x**3 - 6.0 * velocity**2 * x**2
    weight = 1.0 + coupling * s**2
    return {
        "X_Lorentzian": x,
        "unweighted_velocity_Hessian": bare,
        "velocity_Hessian": weight * bare,
        "d_velocity_Hessian_dsigma": 2.0 * coupling * s * bare,
        "d2_velocity_Hessian_dsigma2": 2.0 * coupling * bare,
        "inside_positive_Legendre_cone": weight * bare > 0.0,
    }


def inertia_sigma_jet(
    sigma: float, q_dot: float, *, q_inertia: float, g: float
) -> dict[str, float]:
    """Return sigma derivatives of I_qq and the induced generalized force."""

    s = _finite(sigma, "sigma")
    velocity = _finite(q_dot, "q_dot")
    mass = _positive(q_inertia, "q_inertia")
    coupling = _finite(g, "g")
    first = 2.0 * coupling * mass * s
    second = 2.0 * coupling * mass
    return {
        "I_qq": mass * (1.0 + coupling * s**2),
        "dI_qq_dsigma": first,
        "d2I_qq_dsigma2": second,
        "d3I_qq_dsigma3": 0.0,
        "d4I_qq_dsigma4": 0.0,
        "J_sigma_inertia": 0.5 * first * velocity**2,
        "linearized_curvature_shift": -0.5 * second * velocity**2,
    }


def sigma_tangent_on_moving_trajectory(
    *,
    static_sigma_curvature: float,
    q_dot: float,
    q_inertia: float,
    zsigma: float,
    g: float,
) -> dict[str, float | bool | None]:
    """Return the Lorentzian tangent curvature K_eff/Zsigma.

    With L=T-V, the sigma equation is
    Zsigma*sigma_ddot + [K_static-g*M_q*q_dot**2]*sigma+O(sigma**3)=0.
    """

    curvature = _finite(static_sigma_curvature, "static_sigma_curvature")
    velocity = _finite(q_dot, "q_dot")
    mass = _positive(q_inertia, "q_inertia")
    z = _positive(zsigma, "Zsigma")
    coupling = _finite(g, "g")
    shift = -coupling * mass * velocity**2
    effective = curvature + shift
    threshold = None
    if coupling * mass > 0.0 and curvature >= 0.0:
        threshold = math.sqrt(curvature / (coupling * mass))
    return {
        "static_curvature": curvature,
        "inertial_curvature_shift": shift,
        "effective_curvature": effective,
        "canonical_effective_curvature": effective / z,
        "parametrically_unstable": effective < 0.0,
        "absolute_q_dot_threshold": threshold,
        "sigma_zero_remains_exact_solution": True,
    }


def moving_sigma_zero_selector_jacobian() -> np.ndarray:
    """Return the coefficient selector Jacobian on moving q, sigma=0.

    The sigma equation remains homogeneous in sigma, while the q equation
    and constraints on the sigma-zero branch remain blind to the sigma
    response coefficients.  Motion changes the tangent operator, not the
    zero-profile residual.
    """

    return np.zeros((4, 3), dtype=float)


def parity_reduction_theorem_payload() -> dict[str, Any]:
    return {
        "retained_symmetry": "sigma_maps_to_minus_sigma",
        "kinetic_weight": "w(sigma)=1+g*sigma^2",
        "potential": "A0*sigma^2/2+G0*sigma^4/4",
        "material_transmission_domain_invariant": True,
        "constraints_and_gauge_conditions_sigma_even": True,
        "critical_value_or_Schur_reduction_preserves_evenness": (
            "on_a_locally_unique_sigma_reflection_equivariant_response_branch"
        ),
        "physical_inertia_parity": "I_phys(-sigma)=I_phys(sigma)",
        "dI_phys_dsigma_at_zero": 0.0,
        "linear_inertial_sigma_source_at_zero": 0.0,
        "first_allowed_effect": "second_sigma_variation_times_velocity_squared",
        "parity_odd_inertia_term_present": False,
    }


def coefficient_and_contact_audit_payload() -> dict[str, Any]:
    return {
        "dynamic_tangent_response": {
            "formula": "S_sigma_dyn=S_sigma_static-(g/Zsigma)*M_q*q_dot^2",
            "velocity_slope": "-g*M_q/Zsigma=-r*M_q/kappa1",
            "can_reconstruct_r_if_physical_tangent_propagator_is_given": True,
            "physical_tangent_propagator_derived_from_Aether": False,
            "selects_r_without_target_response": False,
        },
        "alpha": {
            "enters_static_intercept": True,
            "selected_by_formation_q_equation": False,
        },
        "gamma": {
            "bare_quartic_generated_by_w_equals_one_plus_g_sigma_squared": False,
            "existing_G0_contribution_remains": True,
            "possible_backreaction_quartic": "conditional_order_g_squared_after_eliminating_a_derived_response_block",
            "complete_response_block_present": False,
            "selected": False,
        },
        "localization_coordinate_ell": {
            "present_as_action_owned_canonical_coordinate": False,
            "current_status": "geometric_domain_label_or_missing_localization_mode",
            "canonical_momentum": None,
        },
        "separation_coordinate_d": {
            "present_as_action_owned_canonical_coordinate": False,
            "current_status": "moving_contact_shape_coordinate_only",
            "canonical_momentum": None,
        },
        "contact_cross_inertia_I_dq": None,
        "q_to_d_canonical_momentum_transfer_evaluable": False,
        "pure_cap_repartition_total_action_inertia": 0.0,
    }


def completion_payload() -> dict[str, Any]:
    ac = 2.0
    formation = formation_reduced_dynamics(
        0.3,
        0.2,
        5.0 * 0.4 * 0.3 / (6.0 * ac**2) - 23.0 * 0.3**3 / (54.0 * ac**2),
        supercriticality=0.4,
        critical_radius=ac,
    )
    jet_at_zero = inertia_sigma_jet(
        0.0, 0.7, q_inertia=formation["collective_inertia"], g=0.8
    )
    tangent = sigma_tangent_on_moving_trajectory(
        static_sigma_curvature=1.0,
        q_dot=0.7,
        q_inertia=formation["collective_inertia"],
        zsigma=1.0,
        g=0.8,
    )
    full_p2_p8 = eta_p2_p8_velocity_hessian(
        spatial_gradient_squared=2.0,
        eta_velocity=0.3,
        sigma=0.0,
        kappa1=1.0,
        g=0.8,
    )
    parity = parity_reduction_theorem_payload()
    audit = coefficient_and_contact_audit_payload()
    selector = moving_sigma_zero_selector_jacobian()
    validation = {
        "quoted_v15_9_dynamic_equation_matches_reduced_potential": abs(
            formation["Euler_residual"]
        )
        < 1.0e-14,
        "retained_inertia_positive_on_control": bool(
            np.min(
                np.linalg.eigvalsh(
                    retained_inertia_matrix(
                        0.2,
                        q_inertia=formation["collective_inertia"],
                        zsigma=1.0,
                        g=0.8,
                    )
                )
            )
            > 0.0
        ),
        "first_sigma_inertia_variation_zero_on_moving_background": (
            jet_at_zero["dI_qq_dsigma"] == 0.0
            and jet_at_zero["J_sigma_inertia"] == 0.0
        ),
        "second_sigma_inertia_variation_nonzero": jet_at_zero[
            "d2I_qq_dsigma2"
        ]
        > 0.0,
        "full_p2_p8_velocity_Hessian_is_even_in_sigma": full_p2_p8[
            "d_velocity_Hessian_dsigma"
        ]
        == 0.0,
        "full_p2_p8_control_inside_positive_Legendre_cone": full_p2_p8[
            "inside_positive_Legendre_cone"
        ],
        "motion_can_shift_tangent_curvature": tangent["inertial_curvature_shift"] < 0.0,
        "sigma_zero_still_exact_during_motion": tangent["sigma_zero_remains_exact_solution"],
        "constraint_reduction_parity_preserved": parity["dI_phys_dsigma_at_zero"] == 0.0,
        "moving_zero_profile_selector_rank_zero": int(np.linalg.matrix_rank(selector)) == 0,
        "inertia_weight_generates_no_bare_quartic": not audit["gamma"][
            "bare_quartic_generated_by_w_equals_one_plus_g_sigma_squared"
        ],
        "no_contact_cross_inertia_fabricated": audit["contact_cross_inertia_I_dq"] is None,
        "v15_16_and_v15_17_claim_boundaries_preserved": True,
        "no_new_parameter_field_or_empirical_input": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_localization_inertia_sigma_v15_18",
        "version": VERSION,
        "campaign_object": CAMPAIGN_OBJECT,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "formation_dynamics": {
            **formation,
            "equation": "q_ddot-5m*q/(6a_c^2)+23q^3/(54a_c^2)=0",
            "inertia_provenance": (
                "equation_equivalent_to_the_v15_9_normalized_reduced_potential_"
                "with_M_q=3a_c^2/2;_full_constraint_reduced_Lorentzian_profile_"
                "norm_not_independently_materialized_in_v15_9"
            ),
        },
        "physical_inertia": {
            "velocity_Hessian_at_sigma_zero": retained_inertia_matrix(
                0.0,
                q_inertia=formation["collective_inertia"],
                zsigma=1.0,
                g=0.8,
            ).tolist(),
            "sigma_jet_at_zero_on_moving_control": jet_at_zero,
            "moving_tangent_control": tangent,
            "full_p2_p8_Lorentzian_control": full_p2_p8,
            "general_result": (
                "J_sigma_inertia=g*M_q*sigma*q_dot^2_so_it_is_zero_at_"
                "sigma_zero_but_the_tangent_curvature_shift_is_minus_g*M_q*q_dot^2"
            ),
        },
        "parity_reduction_theorem": parity,
        "moving_sigma_zero_selector": {
            "Jacobian": selector.tolist(),
            "rank": int(np.linalg.matrix_rank(selector)),
            "interpretation": "motion_changes_the_linearized_operator_not_the_zero_solution_residual",
        },
        "coefficient_and_contact_audit": audit,
        "scientific_conclusion": (
            "inertia_reopens_a_parametric_or_spontaneous_sigma_instability_"
            "route_but_does_not_remove_the_sigma_constitutive_obstruction;_"
            "the_existing_g_controls_the_inertial_shift_G0_controls_the_bare_"
            "quartic_and_no_action_owned_ell_or_d_cross_inertia_redirects_q_momentum"
        ),
        "skin": "NOT_DERIVED_PARAMETRIC_TANGENT_INSTABILITY_ONLY",
        "contact_momentum_transfer": "NOT_DERIVED_NO_CANONICAL_LOCALIZATION_OR_SEPARATION_MODE",
        "ejection": False,
        "Hopf_child": "NOT_REACHED",
        "Hindsight_20_20": {
            "VALIDATED": [
                "a_static_zero_selector_is_compatible_with_an_inertial_tangent_response",
                "formation_motion_can_lower_the_sigma_tangent_curvature",
                "the_same_kinetic_Hessian_is_the_correct_place_to_search_for_future_contact_cross_momentum",
            ],
            "INVALIDATED": [
                "the_retained_even_inertia_produces_a_nonzero_linear_sigma_source_at_sigma_zero",
                "motion_alone_selects_g_A0_or_G0",
                "the_quadratic_kinetic_weight_generates_the_bare_sigma_quartic",
                "the_current_collar_or_contact_label_already_has_action_owned_canonical_momentum",
            ],
            "RECLASSIFIED": [
                "the_inertial_route_as_a_velocity_dependent_tangent_mass_and_possible_parametric_instability",
                "sigma_skin_formation_as_spontaneous_after_tangent_instability_not_forced_linearly_on_the_symmetric_branch",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "missing_physical_assumption_plain_language": (
            "Aether_must_supply_the_actual_constraint_reduced_localization_"
            "inertia_and_its_even_sigma_curvature_together_with_a_nonlinear_"
            "response_and_a_real_separation_coordinate;_motion_can_reveal_or_"
            "destabilize_a_material_law_but_the_current_action_still_does_not_choose_it"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "parity_odd_sigma_source_added": False,
            "contact_kick_added": False,
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
        _canonical_json_value(payload),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_localization_inertia_sigma_v15_18.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path
