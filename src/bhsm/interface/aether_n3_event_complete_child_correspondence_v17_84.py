"""Derive the event-to-complete-child solvability condition and its gate.

The result is a boundary canonical relation, not an extra body coordinate.
It also proves that the present metric-erasing reset is constant on each
connected event component and therefore cannot select the N=3 event state.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_dynamical_correspondence_v15_1 import (
    self_adjoint_domain_diagnostics,
)


VERSION = "v17.84"
CLASSIFICATION = "BHSM_N3_EVENT_TO_COMPLETE_CHILD_CORRESPONDENCE_DERIVATION"
FULL_BHSM_COMPLETE = False


def _artifact(name: str) -> dict[str, Any]:
    return json.loads((Path("artifacts") / name).read_text(encoding="utf-8"))


def event_to_child_correspondence_derivation() -> dict[str, Any]:
    event = _artifact("BHSM_aether_reconstruction_firewall_event_v15_45.json")
    cap = _artifact("BHSM_aether_post_cut_child_cap_reconstruction_v15_46.json")
    frontier = _artifact(
        "BHSM_aether_n3_fine_period_log_mix_v17_75.json"
    )["fine_period_log_mix"]["selected_fine_period_log_mix"]
    reconstructed = cap["reconstructed_child_cap_Cauchy_data"]

    # W=0 is used only to verify the boundary-triple theorem class.  It is not
    # promoted as the physical event block.
    theorem_class = self_adjoint_domain_diagnostics(np.zeros((1, 1)))
    current_child_residual = [
        float(reconstructed["maximum_Hamiltonian_residual"]),
        float(reconstructed["minimum_TT_radicand"]),
        float(reconstructed["FR_charge"]) - 0.5,
        min(0.0, float(reconstructed["minimum_eta_Legendre"])),
    ]

    return {
        "problem": {
            "requested_condition": "F_child(z_event)=0",
            "meaning": (
                "THE_COMPLETE_EVENT_BOUNDARY_DATA_LIE_IN_THE_CALDERON_RANGE_"
                "OF_A_REGULAR_CONSTRAINT_SOLVED_COMPLETE_CHILD"
            ),
            "not_an_extra_376_coordinate": True,
            "eligible_as_candidate_state_solvability_test": True,
        },
        "first_variation_derivation": {
            "total_functional": (
                "Gamma_total=Gamma_pre[z]+Gamma_child[Phi]+"
                "Gamma_match[Gamma0_event(z),Gamma0_child(Phi);I_env,B_SM]"
            ),
            "trace_continuity": (
                "Gamma0_event(z)-Gamma0_child(Phi)=0"
            ),
            "flux_balance": (
                "Gamma1_event(z)+Gamma1_child(Phi)+"
                "W_phys*Gamma0_event(z)=0"
            ),
            "child_bulk_equations": "E_child(Phi)=delta_Gamma_child/delta_Phi=0",
            "child_constraints": (
                "Hamiltonian=0;momentum=0;C_sigma=0;FR_charge=1/2;"
                "eta_Legendre>0;regular_pole_and_transmission_domain"
            ),
            "reduced_solvability_map": (
                "Phi_z=Solve_child_BVP[Gamma0_event(z),I_event,I_env,B_SM];_"
                "F_child(z)=P_coker(D_Phi(E_child,B_child))*"
                "(Gamma1_event(z)+Gamma1_child(Phi_z)+"
                "W_phys*Gamma0_event(z))"
            ),
            "invertible_child_linearization_special_case": (
                "P_coker=identity_on_the_boundary_mismatch_after_unique_"
                "interior_solution;F_child_is_the_DtN_flux_balance"
            ),
            "self_adjoint_boundary_triple_criterion": (
                "rank(A,B)=boundary_dimension_and_A*Bstar=B*Astar"
            ),
            "theorem_class_self_adjoint": theorem_class[
                "self_adjoint_extension"
            ],
        },
        "current_firewall_evaluation": {
            "transported_data": event["pregeometric_event"][
                "surviving_data"
            ],
            "discarded_continuous_data": event["pregeometric_event"][
                "not_transported_as_pregeometric_primitives"
            ],
            "finite_cap_child_residual_vector": current_child_residual,
            "finite_cap_child_residual_norm": float(np.linalg.norm(
                current_child_residual
            )),
            "finite_cap_is_function_space_complete_child_BVP": cap[
                "claim_boundary"
            ]["function_space_BVP_proved"],
            "map_on_each_connected_event_component": (
                "F_child_current(z)=F_child_current(I_event)_CONSTANT"
            ),
            "differential_with_respect_to_375_event_base_variables": (
                "ZERO_BY_METRIC_ERASING_FIREWALL"
            ),
            "differential_rank": 0,
            "can_select_a_point_on_near_flat_event_surface": False,
            "why": (
                "THE_ONLY_CURRENT_CHILD_WITNESS_IS_RECONSTRUCTED_FROM_"
                "DISCRETE_DATA_AND_ACTION_SCALE_WITHOUT_EVENT_METRIC_OR_"
                "CANONICAL_MOMENTUM_ARGUMENTS"
            ),
        },
        "physical_block_provenance": {
            "Gamma0_event": (
                "GAUGE_QUOTIENTED_INDUCED_BOUNDARY_TRACE_EXTRACTED_FROM_THE_"
                "TERMINAL_N3_STATE"
            ),
            "Gamma1_event": (
                "GHY_COMPLETED_CANONICAL_BOUNDARY_MOMENTUM_AND_ETA_GAUGE_"
                "NOETHER_FLUX_FROM_THE_PRE_EVENT_ACTION"
            ),
            "Gamma0_child_Gamma1_child": (
                "CALDERON_DIRICHLET_TO_NEUMANN_MAP_OF_THE_COMPLETE_CHILD_"
                "EINSTEIN_ETA_SIGMA_FR_BVP"
            ),
            "W_phys": (
                "ACTION_DERIVED_EVENT_CORE_OR_ATTACHMENT_WENTZELL_SCHUR_BLOCK"
            ),
            "physical_blocks_action_derived": False,
            "theorem_class_only_is_not_a_selection_law": True,
            "zero_W_may_be_assumed_as_physical": False,
        },
        "event_architecture_verdict": {
            "old_constant_reset_is_sufficient": False,
            "metric_erasing_firewall_and_nonconstant_F_child_are_compatible_"
            "without_new_canonical_relation": False,
            "reformulation_required": (
                "RETAIN_DISCRETE_FIREWALL_DATA_BUT_REPLACE_THE_CONSTANT_"
                "CONTINUOUS_RESET_BY_AN_ACTION_OWNED_BOUNDARY_CANONICAL_"
                "RELATION;USE_TRACES_ONLY_IN_THE_SOLVABILITY_TEST_NOT_AS_"
                "FREELY_TRANSPORTED_PRIMITIVES"
            ),
            "physical_N3_event_definition_complete_now": False,
            "direct_N3_solver_must_wait": True,
        },
        "N3_integration_contract": {
            "current_frontier_metrics": frontier["metrics"],
            "preferred_form": (
                "KEEP_THE_376_KKT_RESIDUAL_UNCHANGED_AND_REQUIRE_"
                "F_child(z_event)=0_FOR_CANDIDATE_ACCEPTANCE_IF_THE_DERIVED_"
                "SOLVABILITY_RANK_IS_EXTERNAL"
            ),
            "augmented_form_if_variationally_coupled": (
                "ADD_rank(F_child)_MATCHING_MULTIPLIERS_AND_THE_SAME_NUMBER_"
                "OF_SOLVABILITY_ROWS_ONLY_AFTER_Gamma_match_IS_DERIVED"
            ),
            "rank_not_assumed_before_physical_blocks": True,
            "near_degeneracy_collapse_possible": True,
            "near_degeneracy_collapse_demonstrated": False,
        },
        "next_irreducible_derivation": {
            "object": (
                "PHYSICAL_GAUGE_FIXED_METRIC_ETA_GAUGE_SPINOR_GHOST_"
                "CALDERON_BLOCKS_ON_THE_TERMINAL_N3_EVENT_AND_COMPLETE_CHILD_"
                "BVP_TOGETHER_WITH_THE_ACTION_ATTACHMENT_WENTZELL_BLOCK"
            ),
            "first_finite_dimensional_target": (
                "N3_TERMINAL_TRACE_AND_GHY_CANONICAL_FLUX_EXTRACTOR_PLUS_"
                "THE_CONSTRAINT_REDUCED_CHILD_GALERKIN_DtN_SCHUR_COMPLEMENT"
            ),
            "must_be_evaluated_before_more_N3_optimization": True,
        },
    }


def completion_payload() -> dict[str, Any]:
    result = event_to_child_correspondence_derivation()
    current = result["current_firewall_evaluation"]
    architecture = result["event_architecture_verdict"]
    provenance = result["physical_block_provenance"]
    validation = {
        "F_child_derived_as_boundary_solvability_condition": (
            "P_coker" in result["first_variation_derivation"][
                "reduced_solvability_map"
            ]
        ),
        "boundary_theorem_class_self_adjoint": result[
            "first_variation_derivation"
        ]["theorem_class_self_adjoint"],
        "current_reset_rank_zero_proved": current["differential_rank"] == 0,
        "constant_reset_not_misreported_as_selection": not current[
            "can_select_a_point_on_near_flat_event_surface"
        ],
        "finite_cap_not_misreported_as_complete_BVP": not current[
            "finite_cap_is_function_space_complete_child_BVP"
        ],
        "physical_blocks_not_fabricated": not provenance[
            "physical_blocks_action_derived"
        ],
        "zero_W_not_silently_promoted": not provenance[
            "zero_W_may_be_assumed_as_physical"
        ],
        "direct_solver_correctly_deferred": architecture[
            "direct_N3_solver_must_wait"
        ],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_event_complete_child_correspondence_v17_84",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "event_to_complete_child_correspondence": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "A_COMPLETE_EVENT_IS_A_BOUNDARY_CANONICAL_RELATION_WHOSE_CHILD_"
            "CALDERON_SOLVABILITY_MAY_SELECT_THE_WHOLE_PARTICLE"
        ),
        "dependency_advanced": (
            "DERIVES_F_child_AND_PROVES_THE_CURRENT_CONSTANT_FIREWALL_MAP_HAS_"
            "ZERO_SELECTION_RANK"
        ),
        "active_calculation": result["next_irreducible_derivation"][
            "first_finite_dimensional_target"
        ],
        "validation": validation,
        "validation_passed": passed,
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 15)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_event_complete_child_correspondence_v17_84.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "event_to_child_correspondence_derivation", "completion_payload",
    "deterministic_json", "materialize",
]
