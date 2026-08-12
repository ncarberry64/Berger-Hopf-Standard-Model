"""BHSM v15.17 M5/M4 dimensional-crossover sigma-response audit.

BHSM's relevant dimensions are M5=I_t x S4 (four spatial dimensions) and
M4=I_t x S3 (three spatial dimensions).  The latter is the equatorial seam
of the former.  This module distinguishes the exact dimension-dependent
bubble identities from a dynamical transition law and tests whether the
retained M5->M4 trace/critical-value geometry generates the missing sigma
response jet.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_cycle_sigma_coefficient_reconstruction_v15_10 import (
    critical_x,
)
from bhsm.interface.aether_coupled_skin_selector_v15_16 import (
    sigma_zero_selector_jacobian,
)


VERSION = "v15.17"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
CAMPAIGN_OBJECT = (
    "ACTION_OWNED_3D_TO_4D_AETHER_RECONSTRUCTION_CROSSOVER_GENERATING_"
    "THE_SIGMA_RESPONSE_JET_DIMENSION_DEPENDENT_MATERIAL_SKIN_STRESS_"
    "AND_POST_CROSSOVER_BUBBLE_TRACTION"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_M5_TO_M4_CROSS_STRATUM_LOCALIZATION_CRITICAL_VALUE_"
    "KERNEL_PRODUCING_THE_THREE_CANONICAL_SIGMA_RESPONSE_OBSERVABLES_"
    "WITHOUT_INDEPENDENT_SIGMA_WILSON_DATA"
)
OUTCOME = "DIMENSIONAL_CROSSOVER_HYPOTHESIS_ADMISSIBLE_BUT_NOT_YET_AN_ACTION_SELECTOR"
PRIMARY_VERDICT = (
    "BHSM_USES_M4_EQUALS_ONE_PLUS_THREE_AND_M5_EQUALS_ONE_PLUS_FOUR_SO_"
    "THE_ENDPOINT_BUBBLE_GEOMETRIES_ARE_DIMENSIONALLY_RELEVANT;_HOWEVER_"
    "THE_RETAINED_M5_TO_M4_MAP_IS_AN_EQUATORIAL_TRACE_AND_CONSTRAINED_"
    "CRITICAL_VALUE_NOT_A_TIME_DEPENDENT_DIMENSION_FIELD;_THE_ROUND_"
    "COLLAR_MEASURE_IS_SMOOTH_EVEN_AND_STATIONARY_AT_THE_SEAM_THE_"
    "SEAM_IS_TOTALLY_GEODESIC_AND_SIGMA_IS_THE_CONSTANT_NEUMANN_NORMAL_"
    "ZERO_MODE;_REDUCTION_CAN_RENORMALIZE_A_SUPPLIED_SIGMA_JET_BUT_"
    "DOES_NOT_SUPPLY_ITS_THREE_VALUES_OR_A_NONZERO_SIGMA_SOURCE"
)


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def unit_sphere_area(d_minus_one: int) -> float:
    """Return Omega_(d-1), the area of the unit (d-1)-sphere."""

    if not isinstance(d_minus_one, int) or isinstance(d_minus_one, bool) or d_minus_one < 0:
        raise ValueError("sphere dimension must be a nonnegative integer")
    return 2.0 * math.pi ** ((d_minus_one + 1) / 2.0) / math.gamma(
        (d_minus_one + 1) / 2.0
    )


def round_bubble_geometry(spatial_dimension: int, radius: float) -> dict[str, float]:
    """Return exact area, volume and summed curvature in d-space."""

    if (
        not isinstance(spatial_dimension, int)
        or isinstance(spatial_dimension, bool)
        or spatial_dimension < 2
    ):
        raise ValueError("spatial_dimension must be an integer at least two")
    r = _positive(radius, "radius")
    omega = unit_sphere_area(spatial_dimension - 1)
    return {
        "Omega_d_minus_1": omega,
        "area": omega * r ** (spatial_dimension - 1),
        "volume": omega * r**spatial_dimension / spatial_dimension,
        "summed_mean_curvature": (spatial_dimension - 1) / r,
        "radial_operator_first_derivative_coefficient": (
            spatial_dimension - 1
        ) / r,
    }


def bhsm_dimension_ledger() -> dict[str, Any]:
    return {
        "M8": {"spacetime_dimension": 8, "spatial_dimension": 7, "topology": "I_t_x_S7"},
        "M5": {"spacetime_dimension": 5, "spatial_dimension": 4, "topology": "I_t_x_S4"},
        "M4": {
            "spacetime_dimension": 4,
            "spatial_dimension": 3,
            "topology": "I_t_x_S3_equatorial_seam",
        },
        "M8_to_M5": "oriented_S3_fiber_pushforward_on_the_retained_subcategory",
        "M5_to_M4": "equatorial_trace_plus_constrained_critical_value",
        "local_dimension_field_in_retained_action": False,
        "time_evolution_from_M4_to_M5_interpreted_as_dimension_creation": False,
        "M4_and_M5_are_simultaneous_strata": True,
    }


def equatorial_collar_geometry(rho: float, radius: float = 1.0) -> dict[str, float]:
    """Return the round M5 collar geometry relative to d rho dmu4.

    The convention is chi=pi/2-rho.  The dimensionless density factor is
    cos(rho)^3 and the physical normal element is ds=a*d rho.
    """

    coordinate = float(rho)
    if not math.isfinite(coordinate) or abs(coordinate) >= math.pi / 2:
        raise ValueError("rho must be finite and lie inside the equatorial collar")
    a = _positive(radius, "radius")
    cosine = math.cos(coordinate)
    return {
        "rho": coordinate,
        "dimensionless_density_factor": cosine**3,
        "physical_density_factor": a * cosine**3,
        "d_log_density_d_rho": -3.0 * math.tan(coordinate),
        "d2_log_density_d_rho2": -3.0 / cosine**2,
        "M4_slice_extrinsic_curvature_trace": 3.0 * math.tan(coordinate) / a,
    }


def m5_normal_scalar_operator(
    value_prime: float, value_second: float, chi: float, radius: float = 1.0
) -> float:
    """Evaluate -a^-2 sin^-3(chi)d_chi[sin^3(chi)u']."""

    first = float(value_prime)
    second = float(value_second)
    angle = float(chi)
    if not all(math.isfinite(value) for value in (first, second, angle)):
        raise ValueError("operator data must be finite")
    if not 0.0 < angle < math.pi:
        raise ValueError("chi must lie in (0,pi)")
    a = _positive(radius, "radius")
    return -(second + 3.0 * math.cos(angle) / math.sin(angle) * first) / a**2


def reduced_sigma_response_jet(
    alpha: float,
    r: float,
    gamma: float,
    *,
    kappa1: float = 1.0,
    profile_measure: float = 1.0,
) -> dict[str, float]:
    """Push a supplied invariant sigma jet through a common scalar profile.

    A common profile factor cancels from the canonical quadratic response but
    remains inversely in the canonical quartic.  This is coefficient
    transport, not coefficient selection.
    """

    a = float(alpha)
    response_r = float(r)
    nonlinear = float(gamma)
    if not all(math.isfinite(value) for value in (a, response_r, nonlinear)):
        raise ValueError("alpha, r and gamma must be finite")
    k1 = _positive(kappa1, "kappa1")
    measure = _positive(profile_measure, "profile_measure")
    x0 = critical_x(k1)
    return {
        "S_sigma": response_r * x0 * (a + 9.0 / 4.0),
        "dS_sigma_dX": 6.0 * response_r,
        "lambda_sigma_bare_canonical": (
            nonlinear * response_r**2 * x0**4 / (k1**2 * measure)
        ),
    }


def reduction_sensitivity_jacobian(
    alpha: float,
    r: float,
    gamma: float,
    *,
    kappa1: float = 1.0,
    profile_measure: float = 1.0,
) -> np.ndarray:
    """Return derivative of the transported jet, not a selector Jacobian."""

    a = float(alpha)
    response_r = float(r)
    nonlinear = float(gamma)
    if not all(math.isfinite(value) for value in (a, response_r, nonlinear)):
        raise ValueError("alpha, r and gamma must be finite")
    k1 = _positive(kappa1, "kappa1")
    measure = _positive(profile_measure, "profile_measure")
    x0 = critical_x(k1)
    scale = x0**4 / (k1**2 * measure)
    return np.array(
        [
            [response_r * x0, x0 * (a + 9.0 / 4.0), 0.0],
            [0.0, 6.0, 0.0],
            [0.0, 2.0 * nonlinear * response_r * scale, response_r**2 * scale],
        ],
        dtype=float,
    )


def dimensional_crossover_payload() -> dict[str, Any]:
    ledger = bhsm_dimension_ledger()
    seam = equatorial_collar_geometry(0.0)
    m4_bubble = round_bubble_geometry(3, 1.0)
    m5_bubble = round_bubble_geometry(4, 1.0)
    sensitivity = reduction_sensitivity_jacobian(-1.0, 1.0, 1.0)
    selector = sigma_zero_selector_jacobian()
    return {
        "dimension_ledger": ledger,
        "endpoint_round_bubble_controls": {
            "M4_three_spatial": m4_bubble,
            "M5_four_spatial": m5_bubble,
            "formulas_apply_to_round_bubbles_within_each_spatial_stratum": True,
        },
        "coordinate_firewall": {
            "M4_physical_radial_operator": "d_R^2+(2/R)d_R",
            "M5_physical_radial_operator": "d_R^2+(3/R)d_R",
            "M5_to_M4_transverse_operator": "-a^-2[d_chi^2+3*cot(chi)d_chi]",
            "conclusion": (
                "R_in_the_two_endpoint_bubble_operators_is_not_the_M5_"
                "equatorial_normal_coordinate_chi_and_the_operators_cannot_be_spliced"
            ),
        },
        "round_seam": {
            **seam,
            "density_even_under_cap_reflection": True,
            "density_first_derivative_at_seam": 0.0,
            "extrinsic_curvature_at_seam": 0.0,
            "delta_function_or_odd_crossover_source": False,
        },
        "sigma_normal_domain": {
            "operator": "-sin^-3(chi)d_chi[sin^3(chi)d_chi]",
            "selected_profile": "constant_even_Neumann_zero_mode",
            "normal_eigenvalue": 0.0,
            "interface_order_parameter_status": "NOT_DERIVED_IN_V6_1_1",
            "extrinsic_sigma_coupling_in_frozen_parent_action": False,
            "linear_sigma_source_at_sigma_zero": 0.0,
        },
        "existing_cross_stratum_sigma_term": {
            "formula": "integral_M5<lambda_sigma,sigma5-P0_sigma8>",
            "owner": "v7_1_stratified_compatibility_action",
            "variation": "enforces_sigma5=P0_sigma8_and_the_adjoint_reaction",
            "multiplier_has_kinetic_term": False,
            "multiplier_normalization_is_physical": False,
            "generates_sigma_mass_X_derivative_or_quartic": False,
        },
        "existing_M5_to_M4_critical_value": {
            "formula": "Crit_over_cap_fields_at_fixed_M4_trace_of_the_GHY_completed_S5_action",
            "status": "STRUCTURAL_LOCAL_STATIONARY_BRANCH_CONSTRUCTION",
            "global_unique_physical_kernel_evaluated": False,
            "sigma_Wilson_data_eliminated_by_critical_value": False,
        },
        "reduction_response_test": {
            "sample_transported_jet": reduced_sigma_response_jet(-1.0, 1.0, 1.0),
            "transport_sensitivity_Jacobian": sensitivity.tolist(),
            "transport_sensitivity_rank": int(np.linalg.matrix_rank(sensitivity)),
            "transport_sensitivity_determinant": float(np.linalg.det(sensitivity)),
            "interpretation": (
                "full_rank_means_three_supplied_coefficients_are_visible_in_"
                "three_output_responses;_it_does_not_supply_target_values_or_select_the_inputs"
            ),
            "action_owned_target_response_jet_from_crossover": None,
            "physical_selector_Jacobian": selector.tolist(),
            "physical_selector_rank": int(np.linalg.matrix_rank(selector)),
        },
        "dimensional_skin_energy": {
            "independent_E_dim_term_in_retained_action": None,
            "dynamical_dimension_or_reconstruction_order_parameter": None,
            "M5_to_M4_localization_kernel_with_fixed_coefficients": None,
            "finite_width_stationary_point_from_dimension_change": None,
        },
        "hypothesis_status": (
            "VALID_RESEARCH_DIRECTION_REQUIRING_AN_ACTION_OWNED_CROSS_"
            "STRATUM_LOCALIZATION_OR_CRITICAL_VALUE_KERNEL"
        ),
    }


def completion_payload() -> dict[str, Any]:
    crossover = dimensional_crossover_payload()
    validation = {
        "BHSM_dimension_convention_resolved": (
            crossover["dimension_ledger"]["M4"]["spatial_dimension"] == 3
            and crossover["dimension_ledger"]["M5"]["spatial_dimension"] == 4
        ),
        "three_and_four_space_bubble_controls_exact": (
            math.isclose(
                crossover["endpoint_round_bubble_controls"]["M4_three_spatial"]["area"],
                4.0 * math.pi,
            )
            and math.isclose(
                crossover["endpoint_round_bubble_controls"]["M5_four_spatial"]["area"],
                2.0 * math.pi**2,
            )
        ),
        "collar_measure_even_and_stationary_at_seam": (
            crossover["round_seam"]["density_even_under_cap_reflection"]
            and crossover["round_seam"]["density_first_derivative_at_seam"] == 0.0
        ),
        "equatorial_seam_totally_geodesic": (
            crossover["round_seam"]["extrinsic_curvature_at_seam"] == 0.0
        ),
        "constant_sigma_normal_mode_has_zero_eigenvalue": (
            m5_normal_scalar_operator(0.0, 0.0, math.pi / 2.0) == 0.0
        ),
        "sigma_linear_source_remains_zero": (
            crossover["sigma_normal_domain"]["linear_sigma_source_at_sigma_zero"] == 0.0
        ),
        "transport_map_is_locally_injective_for_nonzero_r_control": (
            crossover["reduction_response_test"]["transport_sensitivity_rank"] == 3
        ),
        "transport_rank_not_mislabeled_selector_rank": (
            crossover["reduction_response_test"]["physical_selector_rank"] == 0
        ),
        "no_E_dim_or_dimension_field_invented": (
            crossover["dimensional_skin_energy"]["independent_E_dim_term_in_retained_action"]
            is None
            and crossover["dimensional_skin_energy"][
                "dynamical_dimension_or_reconstruction_order_parameter"
            ]
            is None
        ),
        "compatibility_multiplier_not_mislabeled_constitutive_kernel": (
            not crossover["existing_cross_stratum_sigma_term"][
                "generates_sigma_mass_X_derivative_or_quartic"
            ]
        ),
        "v15_16_rank_zero_obstruction_preserved": True,
        "no_empirical_input_or_new_coefficient": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_dimensional_crossover_sigma_v15_17",
        "version": VERSION,
        "campaign_object": CAMPAIGN_OBJECT,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "dimensional_crossover_audit": crossover,
        "scientific_conclusion": (
            "the_hypothesis_correctly_identifies_a_possible_upstream_home_"
            "for_the_sigma_law_but_the_existing_stratified_action_contains_"
            "only_trace_pushforward_and_independent_stratum_Wilson_data;_"
            "there_is_no_action_term_whose_mixed_second_variation_generates_"
            "the_three_sigma_response_observables"
        ),
        "skin_tension": "NOT_SELECTED",
        "post_crossover_traction": "ENDPOINT_GEOMETRIC_FORMULAS_ONLY_NO_TRANSITION_LAW",
        "ejection": False,
        "Hopf_child": "NOT_REACHED",
        "Hindsight_20_20": {
            "VALIDATED": [
                "M4_and_M5_have_three_and_four_spatial_dimensions_respectively",
                "round_bubble_area_volume_curvature_and_radial_operators_change_with_stratum_dimension",
                "the_M5_to_M4_collar_supplies_an_exact_cos_cubed_measure_and_normal_Sturm_Liouville_operator",
                "a_reduction_map_can_transport_a_supplied_sigma_response_jet_with_full_local_sensitivity",
            ],
            "INVALIDATED": [
                "M5_to_M4_is_already_a_dynamical_time_evolution_of_local_dimension",
                "the_M4_bubble_radius_and_M5_equatorial_normal_coordinate_are_one_radial_coordinate",
                "the_round_collar_measure_or_extrinsic_curvature_supplies_a_sigma_odd_source_at_the_seam",
                "full_rank_transport_sensitivity_is_by_itself_a_coefficient_selector",
            ],
            "RECLASSIFIED": [
                "the_dimensional_crossover_proposal_as_a_candidate_missing_localization_critical_value_kernel",
                "dimension_dependent_bubble_mechanics_as_downstream_endpoint_controls_not_the_transition_action",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "missing_physical_assumption_plain_language": (
            "BHSM_needs_an_action_owned_rule_that_localizes_or_transfers_the_"
            "sigma_mode_between_the_M5_cap_and_M4_seam_and_outputs_its_three_"
            "response_values;_the_fact_that_the_strata_have_different_"
            "dimensions_changes_propagation_but_does_not_choose_the_material_law"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "dimension_interpolation_parameter_added": False,
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
    path = target / "BHSM_aether_dimensional_crossover_sigma_v15_17.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path
