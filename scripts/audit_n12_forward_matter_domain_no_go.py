"""Adjudicate the retained matter-boundary graph needed by Gate 7."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_boundary_phase_resolvent import (  # noqa: E402
    cayley_phase,
    compact_indicator_neumann_to_robin_difference,
    compact_indicator_resolvent_difference,
    half_line_reflection_coefficient,
    phase_distance,
)


FLAGSHIP = ROOT / "artifacts/flagship_integration"
BOUNDARY = ROOT / "artifacts/BHSM_aether_boundary_identity_ejection_v15_13.json"
GAUGE = ROOT / "artifacts/BHSM_aether_full_gauge_dtn_lr_kernel_v15_66.json"
ATTACHMENT = ROOT / "artifacts/BHSM_action_attachment_wentzell_v14_67.json"
COUPLED = ROOT / "artifacts/BHSM_coupled_wentzell_gate_v14_68.json"
TENSOR = ROOT / "artifacts/BHSM_tensor_attachment_incidence_v14_69.json"
PROVENANCE = ROOT / "artifacts/BHSM_provenance_gate_v14_69.json"
CORRESPONDENCE = ROOT / "artifacts/BHSM_aether_n3_event_complete_child_correspondence_v17_84.json"
DYNAMIC = ROOT / "artifacts/BHSM_aether_n3_dynamic_child_wentzell_cauchy_v17_90.json"
EVENT_FLUX = ROOT / "artifacts/BHSM_aether_n3_event_projected_calderon_flux_v17_92.json"
SCALAR = ROOT / "artifacts/BHSM_aether_n3_scalar_complete_child_boundary_solution_v17_96.json"
ZERO = ROOT / "artifacts/BHSM_aether_n3_zero_background_calderon_closure_v17_97.json"
CLASSICAL = ROOT / "artifacts/BHSM_aether_n3_firewall_core_child_ownership_v17_98.json"
PERSISTENCE = ROOT / "artifacts/BHSM_aether_n3_complete_child_persistence_v17_99.json"
INCIDENCE = FLAGSHIP / "BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
THRESHOLD = FLAGSHIP / "BHSM_N12_FORWARD_BIRTH_THRESHOLD_MARGIN_AUDIT.json"
MAXIMAL = FLAGSHIP / "BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_boundary_phase_resolvent.py"
RESULT = FLAGSHIP / "BHSM_N12_FORWARD_MATTER_DOMAIN_NO_GO.json"
INPUTS = (
    BOUNDARY,
    GAUGE,
    ATTACHMENT,
    COUPLED,
    TENSOR,
    PROVENANCE,
    CORRESPONDENCE,
    DYNAMIC,
    EVENT_FLUX,
    SCALAR,
    ZERO,
    CLASSICAL,
    PERSISTENCE,
    INCIDENCE,
    THRESHOLD,
    MAXIMAL,
    MODULE,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite matter-domain audit value")
        return value
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    return value


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all matter-domain adjudication inputs are required")
    (
        boundary,
        gauge,
        attachment,
        coupled,
        tensor,
        provenance,
        correspondence,
        dynamic,
        event_flux,
        scalar,
        zero,
        classical,
        persistence,
        incidence,
        threshold,
        maximal,
    ) = (
        json.loads(path.read_text(encoding="utf-8"))
        for path in INPUTS[:-1]
    )
    for record in (
        boundary,
        gauge,
        correspondence,
        dynamic,
        event_flux,
        scalar,
        zero,
        classical,
        persistence,
        incidence,
        threshold,
        maximal,
    ):
        if record.get("validation_passed") is not True:
            raise RuntimeError("validated retained inputs are required")

    identity = boundary["boundary_identity_and_transport"]
    gauge_block = gauge["full_gauge_DtN_completion"]
    attachment_block = attachment["attachment_wentzell"]
    event = correspondence["event_to_complete_child_correspondence"]
    zero_scope = zero["zero_background_calderon_closure"]["scope"]
    retained = classical["firewall_core_child_ownership"]["complete_retained_F_child"]

    endpoint_scope_reconciliation = {
        "far_maximal_endpoint_rule": maximal["endpoint_rule"],
        "far_endpoint_Friedrichs_scope": (
            "THE_CLOSURE_RULE_SELECTS_THE_OPERATOR_AT_AN_INFINITE_OR_EXCLUDED_"
            "MAXIMAL_FORWARD_END;_IT_DOES_NOT_SUPPLY_THE_DISTINCT_LEFT_BIRTH_"
            "EVENT_INTERFACE_GRAPH"
        ),
        "birth_interface_rule": maximal["endpoint_rule"]["birth_graph"],
        "birth_W_phys_physical_blocks_action_derived": event[
            "physical_block_provenance"
        ]["physical_blocks_action_derived"],
        "local_source_incidence_selects_temporal_graph": incidence["incidence"][
            "temporal_graph_selected_by_this_assembly"
        ],
        "action_derived_nonzero_boundary_block": "TRANSVERSE_GAUGE_ONLY",
        "normal_matter_birth_generator_present": False,
        "conclusion": (
            "NO_CONTRADICTION:_ABSTRACT_FAR_ENDPOINT_FRIEDRICHS_OWNERSHIP_"
            "DOES_NOT_CLOSE_THE_ACTION_UNSELECTED_NORMAL_MATTER_BIRTH_GRAPH"
        ),
    }

    kappa = 1.0
    length = 1.0
    h0 = 0.0
    h1 = 1.0
    direct_difference = compact_indicator_resolvent_difference(
        kappa, length, h0, h1
    )
    closed_difference = compact_indicator_neumann_to_robin_difference(
        kappa, length, h1
    )
    witness = {
        "operator_family": (
            "K_h=-d2/dx2+m2_ON_[0,infinity),_u'(0)=h*u(0),_"
            "kappa=sqrt(m2-z)>0"
        ),
        "compact_source": "f=1_[0,L]",
        "resolvent_kernel": (
            "G_h(x,y;z)=[exp(-kappa*abs(x-y))+r_h*exp(-kappa*(x+y))]/"
            "(2*kappa)"
        ),
        "reflection_coefficient": "r_h=(kappa-h)/(kappa+h)",
        "quadratic_difference_formula": (
            "<f,(R_h1-R_h0)f>=(r_h1-r_h0)*(1-exp(-kappa*L))^2/"
            "(2*kappa^3)"
        ),
        "parameters": {
            "kappa": kappa,
            "support_length": length,
            "reference_h": h0,
            "comparison_h": h1,
        },
        "reference_Cayley_phase": cayley_phase(h0),
        "comparison_Cayley_phase": cayley_phase(h1),
        "Cayley_phase_chordal_distance": phase_distance(h0, h1),
        "reference_reflection_coefficient": half_line_reflection_coefficient(
            kappa, h0
        ),
        "comparison_reflection_coefficient": half_line_reflection_coefficient(
            kappa, h1
        ),
        "compact_source_resolvent_difference": direct_difference,
        "closed_form_neumann_to_robin_difference": closed_difference,
        "nonzero": direct_difference != 0.0,
        "scope": (
            "EXACT_THEOREM_CLASS_WITNESS_THAT_THE_RETAINED_UNSELECTED_"
            "MAXIMAL_ISOTROPIC_PHASE_CHANGES_A_COMPACT_SOURCE_RESOLVENT_"
            "CONTRACTION;_NOT_AN_ADOPTION_OF_EITHER_PHASE_AS_PHYSICAL_N12"
        ),
    }

    sector_ledger = {
        "gravity_eta_scalar_classical_reset": {
            "status": "CLOSED_AT_THE_SELECTED_CLASSICAL_CHILD",
            "source": "v17.96_TO_v17.98",
            "v17_90_initial_open_blocks": dynamic[
                "dynamic_event_to_child_cauchy_law"
            ]["complete_F_child_components"],
            "v17_92_event_metric_eta_scalar_flux": event_flux[
                "event_projected_calderon_flux"
            ]["constraint_preserving_event_attachment_flux"],
            "v17_96_scalar_dynamic_flux_closed": scalar[
                "scalar_complete_child_boundary_solution"
            ]["F_child_scalar"]["closed_to_resolved_derivative_tolerance"],
            "v17_99_positive_duration_witness": persistence[
                "complete_child_persistence"
            ]["persistence"]["positive_duration_witness"],
            "supplies_nonzero_quantum_fluctuation_matrix": False,
        },
        "transverse_gauge_boundary_quadratic_form": {
            "status": "ACTION_DERIVED",
            "source": "v15.66",
            "operator": gauge_block["operator"],
            "quadratic_form": gauge_block["quadratic_form"],
        },
        "gauge_spinor_ghost_HS_zero_background": {
            "status": "CLOSED_ONLY_AT_ZERO_TRACE_AND_ZERO_FLUX",
            "source": "v17.97",
            "full_nonzero_matrices": zero_scope[
                "full_nonzero_fluctuation_Calderon_matrices_derived"
            ],
        },
        "matter_normal_boundary_generator": {
            "status": "ABSENT_FROM_RETAINED_ACTION",
            "source": "v15.13",
            "existing_matter_junction_action": identity[
                "existing_matter_junction_action"
            ],
            "continuous_domain_family": identity["continuous_ambiguity_remains"],
            "family": identity["surviving_domain_witness"][
                "boundary_identity_allowed_group"
            ],
        },
        "v14_67_attachment_response": {
            "status": "POSITIVE_TWO_DIMENSIONAL_RESPONSE_NOT_PHYSICAL_PLACEMENT",
            "physical_incidence_placement": attachment_block[
                "uniform_theorem_lift"
            ]["physical_incidence_placement_claim"],
        },
        "v14_68_coupled_Wentzell": {
            "status": "FINITE_INCIDENCE_LIFT_NOT_FULL_PHYSICAL_TENSOR_SPACE",
            "full_physical_tensor_incidence": coupled[
                "full_physical_tensor_incidence_claim"
            ],
        },
        "v14_69_tensor_Wentzell": {
            "status": "METRIC_SYM2_SUBSPACE_ONLY",
            "rank": tensor["tensor_Wentzell_rank"],
            "dimension": tensor["tensor_Wentzell_dimension"],
            "full_gauge_fixed_space": tensor[
                "full_gauge_fixed_calderon_space_closed"
            ],
            "all_physical_provenance_inputs": provenance[
                "all_physical_provenance_inputs_present"
            ],
        },
        "Gamma_match": {
            "status": "SCHEMATIC_FIRST_VARIATION_RELATION_NOT_EXECUTABLE_ACTION_TERM",
            "source": "v17.84",
            "total_functional": event["first_variation_derivation"][
                "total_functional"
            ],
            "physical_blocks_action_derived": event[
                "physical_block_provenance"
            ]["physical_blocks_action_derived"],
        },
    }

    validation = {
        "all_required_inputs_present": True,
        "matter_junction_action_is_zero": identity[
            "existing_matter_junction_action"
        ] == 0,
        "continuous_identity_preserving_domain_family_survives": (
            identity["continuous_ambiguity_remains"]
            and identity["surviving_domain_witness"][
                "remaining_family_continuous"
            ]
        ),
        "later_classical_closure_is_zero_background_only": (
            retained["boundary_map_closed"]
            and retained["zero_background_gauge_spinor_ghost_HS_block_closed"]
            and not zero_scope["full_nonzero_fluctuation_Calderon_matrices_derived"]
        ),
        "Gamma_match_physical_blocks_remain_unassembled": not event[
            "physical_block_provenance"
        ]["physical_blocks_action_derived"],
        "gauge_block_is_not_used_as_universal_matter_graph": True,
        "v14_attachment_lifts_fail_closed_at_physical_placement": (
            not attachment_block["uniform_theorem_lift"][
                "physical_incidence_placement_claim"
            ]
            and not coupled["full_physical_tensor_incidence_claim"]
            and not tensor["full_gauge_fixed_calderon_space_closed"]
            and not provenance["all_physical_provenance_inputs_present"]
        ),
        "compact_source_resolvent_separation_is_exact": (
            abs(direct_difference - closed_difference) <= 1.0e-15
            and direct_difference < -0.1
        ),
        "local_source_incidence_does_not_select_temporal_graph": incidence[
            "incidence"
        ]["temporal_graph_selected_by_this_assembly"] is False,
        "far_endpoint_Friedrichs_rule_does_not_supply_birth_graph": (
            maximal["ownership"]["abstract_forward_source_domain_action_owned"]
            and maximal["endpoint_rule"]["if_Tmax_is_infinite"]
            == "CLOSE_THE_NONNEGATIVE_MINIMAL_FORM_BY_ITS_FRIEDRICHS_CLOSURE"
            and "W_phys" in maximal["endpoint_rule"]["birth_graph"]["conormal"]
            and not event["physical_block_provenance"][
                "physical_blocks_action_derived"
            ]
            and not incidence["incidence"][
                "temporal_graph_selected_by_this_assembly"
            ]
        ),
        "prior_threshold_obstruction_preserved": threshold["adjudication"][
            "continuous_low_energy_source_measure_exponent"
        ] == "OPEN",
        "no_phase_boundary_term_selector_chord3_gate_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_FORWARD_MATTER_DOMAIN_NO_GO",
        "status": "CANONICAL_UNCHANGED_RETAINED_ACTION_NO_GO",
        "classification": (
            "THE_RETAINED_ACTION_DERIVES_THE_TRANSVERSE_GAUGE_DtN_BLOCK_BUT_"
            "CONTAINS_NO_NORMAL_MATTER_JUNCTION_GENERATOR;_BOUNDARY_IDENTITY_"
            "THEREFORE_LEAVES_A_CONTINUOUS_U1_PARENT_TIMES_U1_CHILD_DOMAIN_"
            "FAMILY._THE_LATER_COMPLETE_CHILD_RESULT_CLOSES_THE_CLASSICAL_"
            "ZERO_BACKGROUND_POINT_ONLY._AN_EXACT_COMPACT_SOURCE_RESOLVENT_"
            "WITNESS_SEPARATES_TWO_ALLOWED_NONNEGATIVE_SELF_ADJOINT_PHASES,_"
            "SO_THE_GATE7_OPERATOR_AND_SOURCE_FUNCTIONAL_ARE_NOT_UNIQUELY_"
            "DEFINED_BY_THE_UNCHANGED_RETAINED_ACTION"
        ),
        "provenance_classification": {
            "normal_matter_domain": "INTERNAL_CONSISTENCY_REQUIRED",
            "nonzero_fluctuation_Calderon_graph": "ACTION_REQUIRED",
            "zero_background_classical_match": "EXISTENCE_ONLY_FOR_THE_FLUCTUATION_DOMAIN",
            "universal_terminal_reachability": "NOT_REQUIRED",
            "arbitrary_phase_selection": "FORBIDDEN_INTERPRETIVE_INPUT",
        },
        "sector_ledger": sector_ledger,
        "endpoint_scope_reconciliation": endpoint_scope_reconciliation,
        "exact_resolvent_separation": witness,
        "theorem": {
            "statement": (
                "DISTINCT_ALLOWED_SELF_ADJOINT_BOUNDARY_PHASES_DEFINE_"
                "DISTINCT_RESOLVENTS;_THE_EXPLICIT_COMPACT_SOURCE_WITNESS_"
                "PROVES_THE_DIFFERENCE_IS_PHYSICALLY_VISIBLE_TO_THE_NATIVE_"
                "PAIR_TERM._SINCE_THE_RETAINED_LOCAL_CONTACT_TERM_CONTAINS_"
                "NO_SELECTED_MATTER_PHASE,_IT_CANNOT_DEFINE_A_UNIQUE_"
                "PAIR_PLUS_CONTACT_FUNCTIONAL_ACROSS_THE_FAMILY"
            ),
            "scope": (
                "NO_GO_FOR_COMPLETING_GATE7_FROM_THE_UNCHANGED_RETAINED_"
                "ACTION;_NOT_A_NO_GO_FOR_AN_EXPLICITLY_VERSIONED_ACTION_"
                "EXTENSION_OR_FOR_A_THEOREM_PROVING_PHASE_INDEPENDENCE_OF_"
                "THE_FULL_GRADED_OBSERVABLE"
            ),
            "routes_invalidated": [
                "INFER_NEUMANN_FROM_THE_ABSENCE_OF_A_MATTER_JUNCTION_TERM",
                "PROMOTE_THE_ZERO_BACKGROUND_POINT_TO_A_NONZERO_GRAPH",
                "TENSOR_THE_GAUGE_DtN_BLOCK_ON_ALL_MATTER_SECTORS",
                "TENSOR_THE_v14_67_ATTACHMENT_RESPONSE_WITHOUT_PHYSICAL_INCIDENCE",
                "USE_SELF_ADJOINTNESS_OR_NONNEGATIVITY_TO_SELECT_THE_PHASE",
                "USE_FAR_ENDPOINT_FRIEDRICHS_CLOSURE_TO_SUPPLY_THE_MISSING_BIRTH_INTERFACE_GRAPH",
            ],
        },
        "adjudication": {
            "retained_action_defines_unique_full_Gate7_operator": False,
            "retained_action_defines_unique_matter_birth_graph": False,
            "zero_source_force_evaluable_without_new_theorem_or_action_data": False,
            "same_action_saddle_evaluable": False,
            "pair_plus_contact_Hessian_evaluable": False,
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "DERIVE_FROM_EXISTING_RETAINED_TERMS_AN_ACTION_OWNED_NORMAL_"
            "MATTER_BOUNDARY_GENERATOR_FIXING_THE_SURVIVING_CAYLEY_PHASES,_"
            "OR_PROVE_THE_COMPLETE_GRADED_GATE7_PAIR_PLUS_CONTACT_FUNCTIONAL_"
            "IS_INDEPENDENT_OF_THE_ENTIRE_SURVIVING_U1_PARENT_TIMES_U1_CHILD_"
            "DOMAIN_FAMILY;_ABSENT_EITHER_THE_UNCHANGED_RETAINED_ACTION_"
            "CANNOT_CLOSE_GATE7"
        ),
        "claim_boundary": {
            "new_action_term_added": False,
            "phase_selected": False,
            "gauge_block_promoted_to_matter": False,
            "full_BHSM_impossibility_beyond_unchanged_action_claimed": False,
            "frozen_predictions_changed": False,
            "new_physics_added": False,
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def materialize() -> Path:
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(_canonical(build_payload()), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return RESULT


if __name__ == "__main__":
    print(materialize())
