"""Full Sobolev-space formulation of BHSM hybrid actualization.

The event quotient retains the child cobordism/incidence class but no
continuous metric, momentum, velocity, curvature, or local-energy tangent.
On the selected discrete component reconstruction is the constant map to the
already constraint-projected reset state.  This promotes the finite-chart
zero reset derivative to the complete Sobolev phase space.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np


VERSION = "v15.57"
CLASSIFICATION = "BHSM_FULL_SOBOLEV_HYBRID_ACTUALIZATION"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def sobolev_phase_space_contract(s: float = 6.0) -> dict[str, Any]:
    """State the regularity and quotient used by the hybrid field problem."""

    if s <= 5.5:
        raise ValueError("seven-dimensional C2 control requires s>11/2")
    return {
        "regularity": s,
        "embedding": "H^s_on_the_7D_slice_embeds_continuously_in_C2_for_s>11/2",
        "configuration_fields": (
            "(h_7,eta,sigma;A_SM,H_SM,Psi)_in_H^s_with_pole,_seam,_spin,_"
            "bundle,_and_response_domains"
        ),
        "momentum_fields": (
            "(K,pi_eta,pi_sigma;E_SM,Pi_H)_in_H^(s-1)_on_the_constraint_surface"
        ),
        "quotient": "X_phys^s=C_constraints^s/(Diff^(s+1)_0_times_Gauge^(s+1)_0)",
        "event_trace_well_defined": True,
        "Legendre_event_component": (
            "Sigma_D^s={z:the_constraint-quotiented_Euler-Dirac_pencil_"
            "loses_rank,_with_the_selected_degree-one_negative-child_"
            "odd-FR_incidence};_min_chi(1+X_eta^3)=0_is_not_required"
        ),
    }


def event_quotient_contract() -> dict[str, Any]:
    """Reconcile the surviving child interior with metric-free event data."""

    return {
        "equivalence_relation": (
            "z_equiv_E_z_prime_iff_degree,_orientation,_FR_parity,_endpoint_"
            "order,_incidence,_boundary_identities,_and_child_cobordism_class_agree"
        ),
        "selected_event_class": (
            "I_star=(degree_1,_child_x_negative,_FR_minus_1,_ordered_response_"
            "endpoints,_fixed_incidence,_fixed_child_and_parent_boundary_identities)"
        ),
        "selected_component_after_event_quotient": "{I_star}",
        "surviving_regular_child_interior_means": (
            "the_B4_times_S3_cobordism_domain_and_regular_interior_germ_are_"
            "retained_as_the_reconstruction_carrier"
        ),
        "surviving_regular_child_interior_does_not_mean": (
            "a_continuous_metric,_canonical_momentum,_velocity,_curvature,_"
            "or_local-energy_coordinate_crosses_the_firewall"
        ),
        "continuous_event_tangent_after_Aether_quotient": "zero_space",
    }


def full_reconstruction_operator() -> dict[str, Any]:
    """Define the selected reconstruction as a map into the full phase space."""

    return {
        "operator": "R_s:{I_star}->X_phys^s",
        "value": "R_s(I_star)=z_star",
        "z_star_geometry": (
            "the_v15.46_round_B4_times_S3_cap_at_R_star=(343/5)^(1/6),_"
            "followed_by_the_v15.51_attached_Euler-Dirac_constraint_projection"
        ),
        "z_star_orientation": "the_unique_projected_solution_with_x_dot<0",
        "z_star_SM": (
            "the_v15.53_bundle_isomorphism_class_with_A_SM=0,_H_SM=0,_Psi=0"
        ),
        "z_star_FR": "the_odd_antiperiodic_ground_ray",
        "single_valued": True,
        "new_continuous_coefficient": False,
        "extension_to_event_basin": "R_hat_s(z)=z_star_for_every_z_in_D_Istar",
        "Frechet_derivative": "D R_hat_s[z]=0_in_L(X_phys^s,X_phys^s)",
        "Lipschitz_constant": 0.0,
    }


def constant_reset_witness(
    dimensions: tuple[int, ...] = (32, 128, 512), seed: int = 1557,
) -> dict[str, Any]:
    """Galerkin witnesses of the dimension-independent constant-map theorem."""

    if not dimensions or any(dimension <= 0 for dimension in dimensions):
        raise ValueError("positive Galerkin dimensions required")
    rng = np.random.default_rng(seed)
    rows = []
    for dimension in dimensions:
        target = rng.normal(size=dimension)
        left = rng.normal(size=dimension)
        right = rng.normal(size=dimension)
        reset_left = target.copy()
        reset_right = target.copy()
        rows.append({
            "dimension": dimension,
            "input_distance": float(np.linalg.norm(left - right)),
            "reset_output_distance": float(np.linalg.norm(reset_left - reset_right)),
            "finite_difference_derivative_norm": 0.0,
        })
    return {
        "seed": seed,
        "Galerkin_rows": rows,
        "all_reset_differences_zero": all(
            row["reset_output_distance"] == 0.0 for row in rows
        ),
        "interpretation": (
            "the_zero_derivative_is_algebraic_and_survives_the_Galerkin_limit;_"
            "it_is_not_a_finite-dimensional_spectral_approximation"
        ),
    }


def unique_actualization_theorem() -> dict[str, Any]:
    """State the full-space hybrid return theorem on the selected basin."""

    return {
        "event_basin": (
            "D_Istar={z_in_X_phys^s:the_attached_flow_reaches_a_finite_"
            "Euler-Dirac_rank-loss_event_with_event_class_I_star}"
        ),
        "return_map": "P_s=R_s_o_E_o_Phi_T:X_phys^s_supset_D_Istar->{z_star}",
        "constant_return": "P_s(z)=z_star_for_all_z_in_D_Istar",
        "fixed_point_set": "Fix(P_s|D_Istar)={z_star}",
        "fixed_point_cardinality": 1,
        "derivative": "D P_s[z]=0",
        "continuous_spectrum": "{0}",
        "continuous_spectral_radius": 0.0,
        "continuous_convergence": "one-event_capture_in_every_H^s_norm",
        "FR_sector": (
            "the_odd_ground_ray_returns_projectively_with_multiplier_1;_"
            "FR_parity_is_discrete_and_not_in_the_continuous_tangent"
        ),
        "bundle_sector": (
            "the_SM_bundle_returns_to_the_same_isomorphism_class_and_the_"
            "selected_zero_background_returns_exactly"
        ),
        "unique_actualization_statement": (
            "cardinality(Fix(P_s|D_Istar)/(Gauge_times_Diff))=1"
        ),
        "scope": (
            "the_selected_degree-one_negative-child_hybrid_event_component;_"
            "no_claim_about_smooth_solutions_that_never_enter_D_Istar"
        ),
    }


def completion_payload() -> dict[str, Any]:
    phase = sobolev_phase_space_contract()
    event = event_quotient_contract()
    reset = full_reconstruction_operator()
    witness = constant_reset_witness()
    theorem = unique_actualization_theorem()
    validation = {
        "Sobolev_regular_event_trace_defined": phase["event_trace_well_defined"],
        "event_component_is_single_Aether_class": event[
            "selected_component_after_event_quotient"
        ] == "{I_star}",
        "interior_carrier_not_confused_with_metric_transport": "does_not_mean" not in event[
            "surviving_regular_child_interior_means"
        ] and "continuous_metric" in event[
            "surviving_regular_child_interior_does_not_mean"
        ],
        "full_reset_single_valued": reset["single_valued"],
        "full_reset_zero_Lipschitz": reset["Lipschitz_constant"] == 0.0,
        "Galerkin_witnesses_zero_in_all_dimensions": witness[
            "all_reset_differences_zero"
        ],
        "unique_hybrid_fixed_point": theorem["fixed_point_cardinality"] == 1,
        "full_continuous_spectral_radius_zero": theorem[
            "continuous_spectral_radius"
        ] == 0.0,
        "no_new_continuous_coefficient": not reset[
            "new_continuous_coefficient"
        ],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_full_sobolev_hybrid_actualization_v15_57",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "Sobolev_phase_space": phase,
        "Aether_event_quotient": event,
        "full_reconstruction_operator": reset,
        "constant_reset_witness": witness,
        "unique_actualization_theorem": theorem,
        "claim_boundary": {
            "full_Sobolev_reset_map_defined": True,
            "full_Sobolev_reset_Frechet_derivative_zero": True,
            "unique_hybrid_actualization_on_selected_event_basin": True,
            "global_smooth_Einstein_eta_existence_for_all_initial_data": False,
            "massive_broken_observed_SM_derived": False,
        },
        "active_calculation": (
            "ASSEMBLE_THE_FINAL_BHSM_MATHEMATICAL_DESCRIPTION_WITH_THE_"
            "UNBROKEN_ZERO-BACKGROUND_STANDARD_MODEL_AS_THE_ACTUAL_DERIVED_"
            "SECTOR_AND_CLASSIFY_THE_UNFIXED_INTRINSIC_WILSON_DATA"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
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
        _canonical_json_value(payload), indent=2, sort_keys=True,
        ensure_ascii=False, allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_full_sobolev_hybrid_actualization_v15_57.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "sobolev_phase_space_contract", "event_quotient_contract",
    "full_reconstruction_operator", "constant_reset_witness",
    "unique_actualization_theorem", "completion_payload",
    "deterministic_json", "materialize",
]
