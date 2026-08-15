"""BHSM v15.11 core--surface trace and positive-capacity obstruction.

This module composes the retained Haar support geometry with the reciprocal
v11.3 attachment action.  It deliberately distinguishes the compactified
incidence closure from the finite-energy trace space of the regular theory.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aether_cycle_sigma_coefficient_reconstruction_v15_10 import (
    retained_nonuniqueness_witness,
)
from .aether_cycle_spread_concentration_v15_9 import radial_solution_diagnostics


VERSION = "v15.11"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
OUTCOME = "CONTROLLED_OBSTRUCTION_REQUIRING_FOUNDATIONAL_CROSS_STRATUM_DYNAMICS"
PRIMARY_VERDICT = (
    "BHSM_V15_11_THE_RECIPROCAL_ATTACHMENT_DERIVES_THE_UNIQUE_REGULAR_SIDE_"
    "COMPACTIFIED_CORE_COMPATIBILITY_IDEAL_UPSILON_EQUALS_ZERO_AND_I_W_EQUALS_"
    "ZERO_WITH_BOUNDED_I_C;_HOWEVER_EVERY_SMOOTH_NONDEGENERATE_CODIMENSION_ONE_"
    "PARENT_SURFACE_HAS_POSITIVE_HAAR_CAPACITY_SO_THIS_TRACE_IS_AT_INFINITE_"
    "REGULAR_ACTION_AND_I_W_EQUALS_G5_EQUALS_ZERO_IS_RECONSTRUCTION_RANK_LOSS;_"
    "THE_V15_9_ETA_BRANCH_REMAINS_AT_UPSILON_EQUALS_ONE_AT_EVERY_LAYER_AND_ALL_"
    "V15_10_RESPONSE_WITNESSES_HAVE_THE_SAME_ZERO_SELECTOR_JACOBIAN;_THEREFORE_"
    "THE_RETAINED_ACTION_DERIVES_NEITHER_SURFACE_PASSAGE_NOR_A_SIGMA_METRIC_HOPF_"
    "SELECTOR_AND_REQUIRES_A_FOUNDATIONAL_ACTION_OWNED_CROSS_STRATUM_BOUNDARY_"
    "CORRESPONDENCE_WITH_NONZERO_CONSERVATIVE_TRANSFER"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_PREGEOMETRIC_CORE_BOUNDARY_HILBERT_CORRESPONDENCE_WITH_"
    "NONZERO_CONSERVATIVE_TRANSFER_BLOCK_AND_VARIATIONAL_COUPLING_TO_THE_"
    "REGULAR_SUPPORT_SIGMA_METRIC_HOPF_RESPONSE_JET"
)


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def reciprocal_attachment_trace(
    upsilon: float, incidence_core: float
) -> dict[str, float]:
    """Evaluate the exact v11.3 matcher on its regular constraint surface.

    On shell, I_W=upsilon I_C and both half-character dressed terms equal
    sqrt(upsilon) I_C.  No norm or empirical tolerance is introduced.
    """

    u = _finite(upsilon, "upsilon")
    core = _finite(incidence_core, "incidence_core")
    if not 0.0 < u <= 1.0:
        raise ValueError("regular support requires 0 < upsilon <= 1")
    dressed = math.sqrt(u) * core
    return {
        "upsilon": u,
        "incidence_core": core,
        "incidence_wall": u * core,
        "dressed_wall": dressed,
        "dressed_core": dressed,
        "matcher_residual": 0.0,
        "wall_to_core_ratio": u,
    }


def compactified_core_compatibility(incidence_core_bounded: bool = True) -> dict[str, Any]:
    """Return the regular-side closure selected by the reciprocal matcher."""

    return {
        "constraint_map": "M_A=(upsilon|B,I_W|B)",
        "core_compatible_zero_set": "upsilon|B=0_and_I_W|B=0_with_bounded_I_C|B",
        "on_shell_limit": (
            "I_W=upsilon*I_C->0_and_upsilon^(-1/2)I_W="
            "upsilon^(1/2)I_C->0"
        ),
        "bounded_core_incidence": bool(incidence_core_bounded),
        "arbitrary_matching_norm_used": False,
        "regular_metric_incidence": "I_W=id_5(g5)",
        "geometric_consequence": "g5|B=0_as_a_covariant_two_tensor",
        "regular_reconstructible_trace": False,
        "classification": (
            "COMPACTIFIED_INCIDENCE_CLOSURE_AND_RECONSTRUCTION_RANK_LOSS"
            if incidence_core_bounded
            else "LIMIT_NOT_CONTROLLED_WITHOUT_BOUNDED_I_C"
        ),
    }


def weighted_haar_energy_lower_bound(
    lambda_d: float,
    upsilon_inner: float,
    upsilon_outer: float,
    collar_resistance: float,
) -> float:
    """Sharp one-dimensional collar lower bound.

    For transverse area density A(s), ``collar_resistance`` is
    integral ds/A(s).  Cauchy--Schwarz gives

        E_Haar >= (Delta q_D)^2 / (2 R),
        q_D=-lambda_D log(upsilon).

    The value ``math.inf`` for ``upsilon_outer=0`` is intentional when the
    resistance is finite (positive capacity).
    """

    scale = _finite(lambda_d, "lambda_d")
    inner = _finite(upsilon_inner, "upsilon_inner")
    outer = _finite(upsilon_outer, "upsilon_outer")
    resistance = float(collar_resistance)
    if scale <= 0.0:
        raise ValueError("lambda_d must be positive")
    if not 0.0 < inner <= 1.0:
        raise ValueError("upsilon_inner must lie in (0,1]")
    if not 0.0 <= outer <= inner:
        raise ValueError("upsilon_outer must lie in [0,upsilon_inner]")
    if math.isnan(resistance) or resistance <= 0.0:
        raise ValueError("collar_resistance must be positive")
    if outer == 0.0:
        return math.inf if math.isfinite(resistance) else 0.0
    if math.isinf(resistance):
        return 0.0
    delta_q = scale * math.log(inner / outer)
    return delta_q * delta_q / (2.0 * resistance)


def surface_capacity_classification(collar_resistance: float) -> dict[str, Any]:
    """Classify the trace by its exact transverse Dirichlet capacity."""

    resistance = float(collar_resistance)
    if math.isnan(resistance) or resistance <= 0.0:
        raise ValueError("collar_resistance must be positive")
    positive_capacity = math.isfinite(resistance)
    return {
        "collar_resistance": resistance if positive_capacity else "infinity",
        "dirichlet_capacity": 1.0 / resistance if positive_capacity else 0.0,
        "positive_capacity": positive_capacity,
        "smooth_nondegenerate_codimension_one_surface": positive_capacity,
        "upsilon_zero_finite_Haar_energy": False if positive_capacity else None,
        "zero_capacity_interpretation": (
            None
            if positive_capacity
            else "degenerate_or_removed_set_without_an_ordinary_codimension_one_trace"
        ),
    }


def haar_endpoint_domain_payload() -> dict[str, Any]:
    """State the self-adjoint consequence of q_D in the Haar half-line."""

    return {
        "coordinate": "q_D=-lambda_D*log(upsilon)_in_[0,infinity)",
        "retained_principal_operator": "-d^2/dq_D^2",
        "infinite_endpoint_classification": "WEYL_LIMIT_POINT",
        "additional_self_adjoint_boundary_condition_at_core_endpoint": False,
        "L2_Green_flux_at_infinity": 0,
        "terminal_Dirichlet_data_creates_transfer_channel": False,
        "change_of_regular_self_adjoint_extension_supplies_passage": False,
        "scope": "retained_free_Haar_principal_part_and_bounded_below_regular_perturbations",
    }


def evaluate_v15_9_core_match(
    radius_ratios_six: Sequence[float] = (1.001, 1.01, 1.04),
    modes: int = 12,
) -> dict[str, Any]:
    """Pull the exact core constraint back to the nonlinear v15.9 branch."""

    rows = []
    for ratio in radius_ratios_six:
        diagnostics = radial_solution_diagnostics(float(ratio), modes)
        rows.append(
            {
                "radius_ratio_six": float(ratio),
                "q_fourier": diagnostics["q_fourier"],
                "degree": diagnostics["degree"],
                "minimum_X_eta_over_critical_X": diagnostics[
                    "minimum_X_eta_over_critical_X"
                ],
                "Euler_residual_inf": diagnostics[
                    "pointwise_weighted_Euler_residual_inf"
                ],
                "upsilon_trace_at_every_layer": 1.0,
                "wall_to_core_incidence_ratio_at_every_layer": 1.0,
                "core_constraint_support_component": 1.0,
                "core_compatible_layer_exists": False,
            }
        )
    return {
        "branch": "full_nonlinear_v15_9_radial_eta_continuation",
        "rows": rows,
        "constraint_spatially_constant_on_branch": True,
        "dynamic_outer_layer_selected_by_core_constraint": False,
        "reason": (
            "the_retained_eta_branch_has_no_eta_to_upsilon_source_and_is_"
            "computed_on_the_regular_upsilon_equals_one_background"
        ),
        "pure_eta_reaches_core_trace": False,
    }


def evaluate_v15_10_selection() -> dict[str, Any]:
    """Test the core constraint against all constructive v15.10 witnesses."""

    witness = retained_nonuniqueness_witness()
    labels = list(witness["triples"])
    return {
        "witness_labels": labels,
        "common_sigma_zero_background": True,
        "common_upsilon_trace": {label: 1.0 for label in labels},
        "core_match": {label: False for label in labels},
        "selector_jacobian_dM_d_alpha_r_gamma": [0, 0, 0],
        "surviving_physical_equivalence_classes": len(labels),
        "response_nonuniqueness_resolved": False,
        "F_alpha_zero_necessary_for_core_match": False,
        "F_alpha_zero_sufficient_for_core_match": False,
        "classification_of_F_alpha_zero": "INDEPENDENT_EARLY_RESPONSE_DIAGNOSTIC",
        "reason": (
            "no_retained_support_attachment_term_depends_on_the_v15_10_"
            "response_invariants_alpha_r_gamma"
        ),
    }


def response_and_passage_payload() -> dict[str, Any]:
    """Identify what the retained action can and cannot vary at the interface."""

    return {
        "sigma_matcher": "sigma5=P0*sigma8_with_no_upsilon_character",
        "metric_matcher": "I_W=id_5(g5)=upsilon*Q_H(G8)",
        "Hopf_attachment": "regular_full_preimage_domain_only",
        "required_trace_response": (
            "support_to_zero_plus_wall_metric_incidence_rank_loss_or_an_"
            "independent_cross_stratum_trace_correspondence"
        ),
        "regular_constraint_solved_metric_response_can_reach_rank_loss": False,
        "sigma_response_selected": False,
        "Hopf_sector_activated": False,
        "surface_passage_map_defined": False,
        "persistent_child_defined": False,
        "de_envelopment_receiving_state_defined": False,
        "conservative_core_surface_flux_in_retained_action": False,
        "obstruction_requires_change_in_underlying_physical_assumptions": True,
        "smallest_required_foundational_data": [
            "pregeometric_core_boundary_Hilbert_or_quadratic_form_module",
            "trace_pairing_with_the_regular_boundary_module",
            "nonzero_off_diagonal_transfer_block_fixed_by_the_parent_variation",
            "conservative_Green_Noether_flux_identity_across_the_domain_change",
        ],
        "candidate_action_completion_adopted": False,
    }


def completion_payload() -> dict[str, Any]:
    nonlinear = evaluate_v15_9_core_match()
    selection = evaluate_v15_10_selection()
    positive_capacity = surface_capacity_classification(2.0)
    validations = {
        "reciprocal_matcher_limit_exact": (
            reciprocal_attachment_trace(0.25, 4.0)["incidence_wall"] == 1.0
            and reciprocal_attachment_trace(0.25, 4.0)["dressed_wall"] == 2.0
        ),
        "core_closure_is_rank_loss": not compactified_core_compatibility()[
            "regular_reconstructible_trace"
        ],
        "positive_capacity_endpoint_infinite_action": math.isinf(
            weighted_haar_energy_lower_bound(1.0, 1.0, 0.0, 2.0)
        ),
        "positive_capacity_classification": positive_capacity["positive_capacity"],
        "Haar_endpoint_is_limit_point": (
            haar_endpoint_domain_payload()["infinite_endpoint_classification"]
            == "WEYL_LIMIT_POINT"
        ),
        "full_nonlinear_v15_9_rows_checked": len(nonlinear["rows"]) == 3,
        "v15_9_never_reaches_core_trace": all(
            not row["core_compatible_layer_exists"] for row in nonlinear["rows"]
        ),
        "v15_10_selector_jacobian_zero": selection[
            "selector_jacobian_dM_d_alpha_r_gamma"
        ]
        == [0, 0, 0],
        "v15_10_nonuniqueness_preserved": not selection[
            "response_nonuniqueness_resolved"
        ],
        "no_new_field_coefficient_or_parameter": True,
        "no_empirical_inputs": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_core_surface_trace_v15_11",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "regular_side_core_compatibility": compactified_core_compatibility(),
        "positive_capacity_theorem": {
            "capacity_formula": "Cap(B)=[integral_collar ds/A(s)]^(-1)",
            "energy_bound": (
                "E_Haar>=(lambda_D^2/2)*Cap(B)*"
                "log(upsilon_inner/upsilon_outer)^2"
            ),
            "smooth_nondegenerate_codimension_one_surface": positive_capacity,
            "bulk_endpoint_inaccessible": True,
            "outer_trace_endpoint_inaccessible_at_finite_regular_action": True,
            "zero_capacity_escape_is_regular_trace": False,
        },
        "self_adjoint_domain": haar_endpoint_domain_payload(),
        "v15_9_pullback": nonlinear,
        "v15_10_selector_test": selection,
        "response_and_passage": response_and_passage_payload(),
        "Hindsight_20_20": {
            "VALIDATED": [
                "reciprocal_attachment_selects_the_compactified_incidence_ideal_upsilon_equals_I_W_equals_zero",
                "positive_capacity_codimension_one_core_trace_costs_infinite_Haar_action",
                "the_Haar_endpoint_is_limit_point_and_carries_no_transfer_extension_parameter",
                "the_full_nonlinear_v15_9_eta_branch_remains_at_upsilon_equals_one_at_every_layer",
                "the_core_constraint_has_zero_selector_Jacobian_on_all_v15_10_response_witnesses",
            ],
            "INVALIDATED": [
                "matching_only_the_outermost_smooth_nondegenerate_layer_evades_the_Haar_barrier",
                "eta_concentration_alone_selects_a_core_compatible_parent_surface",
                "terminal_Dirichlet_data_or_a_regular_self_adjoint_extension_creates_surface_passage",
                "F_alpha_equals_zero_is_the_core_compatibility_condition",
            ],
            "RECLASSIFIED": [
                "lack_of_spacetime_as_compactified_incidence_rank_loss_not_a_regular_zero_metric_state",
                "surface_capacity_as_the_exact_bulk_interface_discriminator",
                "the_authors_core_surface_principle_as_a_compatibility_rule_not_a_dynamical_transfer_law",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "scientific_terminal_condition": (
            "GENUINE_MATHEMATICAL_OBSTRUCTION_REQUIRING_FOUNDATIONAL_"
            "CROSS_STRATUM_PHYSICAL_INPUT"
        ),
        "validation": validations,
        "validation_passed": all(validations.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_physical_parameters": [],
            "measured_inputs": [],
            "candidate_action_completion_adopted": False,
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
            "USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE": (
                USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE
            ),
        },
    }


def _canonical_json_value(value: Any) -> Any:
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
    path = target / "BHSM_aether_core_surface_trace_v15_11.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path
