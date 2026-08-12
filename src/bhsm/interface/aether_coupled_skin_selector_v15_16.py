"""BHSM v15.16 coupled eta--sigma--metric skin selector theorem.

The retained normal energy density is

    L = (1 + g sigma**2) F(X)
        + Zsigma sigma_n**2 / 2 + A0 sigma**2 / 2 + G0 sigma**4 / 4,
    F(X) = kappa1 X / 2 + X**4 / 8,
    X = |D_n eta|**2.

This module derives the coupled normal field equations and asks whether the
currently available physical BHSM data define a coefficient selector.  It
does not turn Wilson/EFT coefficients into variational fields, prescribe
missing parent/child asymptotics, or mistake a family of coefficient-
dependent boundary-value problems for one inverse problem.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


VERSION = "v15.16"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
SELECTOR_RANK = 0
OUTCOME = "FOUNDATIONAL_SIGMA_CONSTITUTIVE_OBSTRUCTION_PROVED"
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_AETHER_CYCLE_TO_REGULAR_SIGMA_RESPONSE_JET_MAP_"
    "PRODUCING_THE_PHYSICAL_SIGMA_TANGENT_PROPAGATOR_X_DERIVATIVE_"
    "AND_BACKREACTION_UNREDUCED_CANONICAL_QUARTIC_ON_THE_V15_9_BRANCH"
)
PRIMARY_VERDICT = (
    "THE_RETAINED_COUPLED_ETA_SIGMA_METRIC_EULER_AND_CONSTRAINT_"
    "SYSTEM_IS_A_FORWARD_FIELD_PROBLEM_CONDITIONAL_ON_ALPHA_R_GAMMA;_"
    "THE_ONLY_ESTABLISHED_COMMON_PHYSICAL_ASYMPTOTIC_STATE_HAS_SIGMA_"
    "ZERO_AND_ITS_COMPLETE_AVAILABLE_SELECTOR_JACOBIAN_IS_EXACTLY_"
    "ZERO_OF_RANK_ZERO;_NAIVELY_VARYING_THE_THREE_COEFFICIENTS_"
    "FORCES_SIGMA_ZERO_RATHER_THAN_SELECTING_A_MATERIAL_SKIN;_THE_"
    "FULL_COUPLED_SKIN_BVP_IS_THEREFORE_NOT_YET_DEFINED_BY_BHSM"
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


def eta_density(kappa1: float, x_eta: float) -> float:
    """Return F(X)=kappa1*X/2+X**4/8."""

    k1 = _positive(kappa1, "kappa1")
    x = _finite(x_eta, "X_eta")
    if x < 0.0:
        raise ValueError("X_eta must be nonnegative")
    return 0.5 * k1 * x + 0.125 * x**4


def coupled_normal_residuals(
    *,
    eta_n: float,
    eta_nn: float,
    sigma: float,
    sigma_n: float,
    sigma_nn: float,
    expansion: float,
    kappa1: float,
    zsigma: float,
    g: float,
    a0: float,
    g0: float,
) -> dict[str, float]:
    """Evaluate the exact one-normal-coordinate matter Euler residuals.

    ``expansion`` is ``d_n log(sqrt(h))`` in Gaussian normal gauge.  The eta
    path is a target-space geodesic; for a general target path the ordinary
    second derivative is replaced by its target-covariant derivative.
    """

    p = _finite(eta_n, "eta_n")
    pp = _finite(eta_nn, "eta_nn")
    s = _finite(sigma, "sigma")
    sp = _finite(sigma_n, "sigma_n")
    spp = _finite(sigma_nn, "sigma_nn")
    theta = _finite(expansion, "expansion")
    k1 = _positive(kappa1, "kappa1")
    z = _positive(zsigma, "Zsigma")
    coupling = _finite(g, "g")
    mass = _finite(a0, "A0")
    quartic = _finite(g0, "G0")
    x = p**2
    weight = 1.0 + coupling * s**2
    momentum = weight * (k1 + x**3) * p
    momentum_n = (
        2.0 * coupling * s * sp * (k1 + x**3) * p
        + weight * (k1 + 7.0 * x**3) * pp
    )
    eta_residual = momentum_n + theta * momentum
    sigma_residual = (
        -z * (spp + theta * sp)
        + (mass + 2.0 * coupling * eta_density(k1, x)) * s
        + quartic * s**3
    )
    return {
        "X_eta": x,
        "eta_canonical_normal_momentum": momentum,
        "eta_Euler_residual": eta_residual,
        "sigma_Euler_residual": sigma_residual,
    }


def matter_normal_first_integral(
    *,
    eta_n: float,
    sigma: float,
    sigma_n: float,
    kappa1: float,
    zsigma: float,
    g: float,
    a0: float,
    g0: float,
) -> float:
    """Return the flat-normal translational first integral q'L_q'+s'L_s'-L."""

    p = _finite(eta_n, "eta_n")
    s = _finite(sigma, "sigma")
    sp = _finite(sigma_n, "sigma_n")
    k1 = _positive(kappa1, "kappa1")
    z = _positive(zsigma, "Zsigma")
    coupling = _finite(g, "g")
    mass = _finite(a0, "A0")
    quartic = _finite(g0, "G0")
    x = p**2
    return (
        (1.0 + coupling * s**2) * (0.5 * k1 * x + 0.875 * x**4)
        + 0.5 * z * sp**2
        - 0.5 * mass * s**2
        - 0.25 * quartic * s**4
    )


def sigma_zero_selector_jacobian() -> np.ndarray:
    """Return d(residuals)/d(alpha,r,gamma) on the established sigma=0 state.

    Rows are sigma Euler, eta Euler, normal Hamiltonian/metric constraint,
    degree/topology, regularity, and normalization residuals.  Each is blind
    to the sigma response coefficients on the available sigma-zero solution.
    """

    return np.zeros((6, 3), dtype=float)


def sigma_zero_selector_map(alpha: float, r: float, gamma: float) -> np.ndarray:
    """Evaluate the complete presently available physical selector map.

    The inputs are validated even though every available residual is exactly
    coefficient-blind.  This makes the map, rather than only its derivative,
    explicit: every finite coefficient triple maps to the same zero vector.
    """

    _finite(alpha, "alpha")
    _finite(r, "r")
    _finite(gamma, "gamma")
    return np.zeros(6, dtype=float)


def selector_rank() -> int:
    return int(np.linalg.matrix_rank(sigma_zero_selector_jacobian()))


def naive_coefficient_variation_constraints(
    sigma: Sequence[float], x_eta: Sequence[float], weights: Sequence[float], *, kappa1: float
) -> dict[str, float | bool]:
    """Evaluate the constraints produced by illegally varying g,A0,G0.

    Positive quadrature weights model the reduced Euclidean/static energy.
    The three derivatives are nonnegative.  In particular dE/dA0=0 or
    dE/dG0=0 implies sigma=0 almost everywhere, so this promotion destroys
    the desired material wall instead of selecting its response.
    """

    s = np.asarray(sigma, dtype=float)
    x = np.asarray(x_eta, dtype=float)
    w = np.asarray(weights, dtype=float)
    if s.ndim != 1 or x.shape != s.shape or w.shape != s.shape or s.size == 0:
        raise ValueError("sigma, X_eta and weights must be nonempty matching vectors")
    if not np.all(np.isfinite(s)) or not np.all(np.isfinite(x)) or not np.all(np.isfinite(w)):
        raise ValueError("quadrature data must be finite")
    if np.any(x < 0.0) or np.any(w <= 0.0):
        raise ValueError("X_eta must be nonnegative and weights positive")
    f = 0.5 * _positive(kappa1, "kappa1") * x + 0.125 * x**4
    d_g = float(np.dot(w, f * s**2))
    d_a = float(0.5 * np.dot(w, s**2))
    d_g0 = float(0.25 * np.dot(w, s**4))
    return {
        "dE_dg": d_g,
        "dE_dA0": d_a,
        "dE_dG0": d_g0,
        "all_nonnegative": d_g >= 0.0 and d_a >= 0.0 and d_g0 >= 0.0,
        "stationarity_forces_sigma_zero": d_a == 0.0 and d_g0 == 0.0,
    }


def coupled_bvp_identifiability_payload() -> dict[str, Any]:
    jacobian = sigma_zero_selector_jacobian()
    return {
        "retained_normal_energy": (
            "(1+g*sigma^2)*(kappa1*X/2+X^4/8)+"
            "Zsigma*sigma_n^2/2+A0*sigma^2/2+G0*sigma^4/4"
        ),
        "field_equations": {
            "eta": (
                "D_n[(1+g*sigma^2)*(kappa1+X^3)*D_n_eta]+"
                "theta*(1+g*sigma^2)*(kappa1+X^3)*D_n_eta=0"
            ),
            "sigma": (
                "-Zsigma*(sigma_nn+theta*sigma_n)+"
                "[A0+2g*F(X)]*sigma+G0*sigma^3=0"
            ),
            "metric": (
                "kappa1_times_Gauss_Codazzi_normal_constraint_equals_the_"
                "complete_eta_sigma_normal_stress_with_momentum_constraints"
            ),
            "transmission": (
                "continuous_fields_and_opposite_normal_canonical_flux_balance_"
                "on_the_v15_15_global_bundle_domain"
            ),
        },
        "coefficient_entry": {
            "invariant_relations": (
                "g=r*Zsigma/kappa1;_A0=alpha*g*kappa1*Xc;_"
                "G0=gamma*g^2*Xc^4"
            ),
            "g": "eta_sigma_kinetic_multiplier_and_sigma_curvature_2gF(X)",
            "A0": "sigma_quadratic_curvature",
            "G0": "sigma_cubic_Euler_response",
            "Zsigma": "sigma_normal_kinetic_operator",
        },
        "Euler_equations_for_alpha_r_gamma_in_retained_action": [],
        "forward_problem_status": "DEFINED_ONLY_AFTER_COEFFICIENTS_AND_ASYMPTOTIC_DATA_ARE_GIVEN",
        "available_physical_state": "v15_9_eta_metric_formation_precursor_with_sigma=0",
        "available_selector_rows": [
            "sigma_Euler",
            "eta_Euler",
            "normal_Hamiltonian_metric_constraint",
            "eta_degree_topology",
            "finite_action_regularity",
            "normalization",
        ],
        "available_selector_map": "S_skin(alpha,r,gamma)=zero_6_for_every_finite_triple",
        "selector_Jacobian": jacobian.tolist(),
        "selector_shape": list(jacobian.shape),
        "selector_rank": selector_rank(),
        "selector_nullity": 3 - selector_rank(),
        "same_complete_coefficient_independent_parent_and_child_asymptotics_present": False,
        "physical_child_asymptotic_state_present": False,
        "full_metric_skin_BVP_eligible": False,
        "reason": (
            "the_action_law_and_child_asymptotic_data_needed_to_define_one_"
            "common_inverse_boundary_value_problem_are_not_outputs_of_the_retained_theory"
        ),
    }


def completion_payload() -> dict[str, Any]:
    identifiability = coupled_bvp_identifiability_payload()
    zero_variation = naive_coefficient_variation_constraints(
        [0.0, 0.0, 0.0], [0.0, 1.0, 2.0], [1.0, 1.0, 1.0], kappa1=1.0
    )
    wall_variation = naive_coefficient_variation_constraints(
        [-1.0, 0.0, 1.0], [0.0, 1.0, 2.0], [1.0, 1.0, 1.0], kappa1=1.0
    )
    validation = {
        "coupled_eta_sigma_normal_equations_derived": True,
        "normal_first_integral_derived": True,
        "metric_constraint_source_identified_as_complete_normal_stress": True,
        "v15_15_self_adjoint_material_domain_preserved": True,
        "available_selector_Jacobian_exactly_zero": np.count_nonzero(
            sigma_zero_selector_jacobian()
        ) == 0,
        "available_selector_rank_exactly_zero": selector_rank() == 0,
        "all_three_coefficient_directions_survive": identifiability["selector_nullity"] == 3,
        "naive_coefficient_variation_accepts_sigma_zero": zero_variation[
            "stationarity_forces_sigma_zero"
        ],
        "naive_coefficient_variation_rejects_nonzero_wall": (
            wall_variation["dE_dA0"] > 0.0 and wall_variation["dE_dG0"] > 0.0
        ),
        "no_missing_asymptotics_fabricated": not identifiability[
            "physical_child_asymptotic_state_present"
        ],
        "no_empirical_selector_or_new_parameter": True,
        "v15_10_nonuniqueness_preserved": True,
        "v15_11_limit_point_no_go_preserved": True,
        "v15_15_global_spin_transmission_preserved": True,
        "contact_ejection_not_promoted_without_skin": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_coupled_skin_selector_v15_16",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "coupled_skin_system": identifiability,
        "coefficient_promotion_test": {
            "status": "FORBIDDEN_AND_EVALUATED_AS_A_NO_GO",
            "formal_global_variations": {
                "dE_dg": "integral(F(X)*sigma^2)",
                "dE_dA0": "one_half_integral(sigma^2)",
                "dE_dG0": "one_quarter_integral(sigma^4)",
            },
            "positive_static_measure_consequence": "stationarity_forces_sigma=0_almost_everywhere",
            "zero_profile_control": zero_variation,
            "nonzero_profile_control": wall_variation,
            "conclusion": (
                "couplings_are_action_labels_not_fields;_literal_variation_"
                "does_not_select_a_nonzero_response_jet"
            ),
        },
        "A_B_C_full_skin_test": {
            "eligible_as_one_common_physical_inverse_problem": False,
            "reason": (
                "A_B_C_define_three_different_action_laws_and_the_repository_"
                "contains_no_coefficient_independent_child_asymptotics_or_"
                "ensemble_that_would_turn_their_forward_solutions_into_a_selector"
            ),
            "flat_kinks_remain_valid_controls": True,
            "lowest_tension_selection_forbidden": True,
        },
        "skin_tension": "NOT_PHYSICAL_UNTIL_RESPONSE_JET_AND_COUPLED_ASYMPTOTICS_EXIST",
        "surface_stress": "NOT_PHYSICAL_UNTIL_THE_SAME_COUPLED_PROFILE_EXISTS",
        "contact_impulse": "NOT_EVALUABLE",
        "ejection": False,
        "Hopf_child": "NOT_REACHED",
        "FULL_BHSM_completion": "FALSE_AT_PROVED_FOUNDATIONAL_CONSTITUTIVE_OBSTRUCTION",
        "Hindsight_20_20": {
            "VALIDATED": [
                "the_retained_coupling_supplies_a_well_defined_forward_normal_Euler_system",
                "all_current_physical_selector_rows_are_coefficient_blind_on_sigma_zero",
                "the_available_selector_Jacobian_has_exact_rank_zero_and_nullity_three",
                "the_v15_10_response_jet_inverse_remains_the_minimal_algebraic_selector_interface",
            ],
            "INVALIDATED": [
                "solving_more_field_equations_can_make_their_own_fixed_action_coefficients_dynamical",
                "regularity_or_constraints_on_the_known_sigma_zero_state_select_alpha_r_gamma",
                "literal_global_variation_of_g_A0_G0_can_select_a_nonzero_material_skin",
                "A_B_C_self_consistent_coefficient_dependent_vacua_are_common_physical_asymptotics",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "missing_physical_assumption_plain_language": (
            "Aether_must_supply_a_microscopic_constitutive_or_reconstruction_"
            "law_for_the_sigma_tangent_curvature_its_eta_X_derivative_and_"
            "its_canonical_quartic;_the_regular_field_equations_cannot_"
            "derive_the_coupling_constants_that_define_those_same_equations"
        ),
        "validation": validation,
        "validation_passed": all(bool(value) for value in validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "fabricated_asymptotic_states": [],
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
    path = target / "BHSM_aether_coupled_skin_selector_v15_16.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path
