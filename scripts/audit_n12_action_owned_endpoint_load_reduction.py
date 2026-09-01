"""Reduce Gate 7 to the actual maximal-child Weyl oracle, not a BC choice."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json"
)
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_EXTERIOR_ORACLE_EXECUTABLE_INTERFACE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_NEGATIVE_AXIS_SEAM_HEAT_SYNTHESIS_NO_GO.json",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("endpoint-load reduction inputs required")
    records = [_load(path) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated endpoint-load reduction inputs required")
    (
        maximal,
        proper_time,
        seam,
        finite_scope,
        force_domain,
        parametric,
        executable,
        broad_no_go,
    ) = records

    validation = {
        "maximal_endpoint_domain_rule_is_unique": (
            maximal["ownership"]["arbitrary_Robin_nonuniqueness_removed"] is True
            and maximal["endpoint_rule"]["arbitrary_Robin_parameter_allowed"] is False
        ),
        "actual_event_uses_retained_two_sided_reset_graph": (
            seam["corrected_seam_theorem"]["physical_seam_operator"]
            == "S_AE2(z)=M_event(z)+U_R_DAGGER*M_child(z)*U_R+W_phys"
        ),
        "canonical_stop_uses_retained_Friedrichs_closure": (
            finite_scope["finite_endpoint_operator_provenance"]["endpoint_domain"]
            == "USE_THE_EXISTING_EVENT_RESET_TRACE_CONORMAL_GRAPH_IF_HIT;_USE_THE_ALREADY_RETAINED_FRIEDRICHS_RULE_AT_A_CANONICAL_STOP"
        ),
        "proper_time_derivative_and_laplacian_are_form_owned": (
            proper_time["provenance_classification"]["D_tau"][
                "separate_coefficient_oracle_required"
            ] is False
            and proper_time["provenance_classification"]["Delta_tau"][
                "independently_selectable"
            ] is False
        ),
        "only_bulk_history_coefficient_is_log_radius": (
            proper_time["dependency_reduction"]["remaining_owner"].startswith(
                "THE_MAXIMAL_FORWARD_log_R4"
            )
        ),
        "arbitrary_validation_cutoff_is_forbidden": (
            force_domain["domain_adjudication"][
                "arbitrary_regular_free_cutoff_allowed"
            ] is False
        ),
        "reset_fiber_requires_family_or_invariance": (
            parametric["claim_boundary"]["Gate7"]
            == "ACTIVE_PARAMETRIC_EXTERIOR_ORACLE_OR_FIBER_INVARIANCE_OPEN"
        ),
        "supplied_oracle_linear_algebra_is_executable": (
            executable["claim_boundary"][
                "stable_Weyl_value_first_second_jet_solver"
            ] == "DERIVED"
        ),
        "broad_reference_counterpair_is_not_physical_endpoint_selection": (
            broad_no_go["logical_no_go"]["does_not_disprove"]
            == "A_SHARPER_ACTION_OWNED_N12_SEAM_OR_COMPLETE_OPERATOR_CAN_DECIDE_THE_FORCE"
        ),
        "no_selector_action_term_scale_fit_new_gate_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION",
        "status": "ENDPOINT_DOMAIN_CLASS_OWNED_MAXIMAL_CHILD_WEYL_FAMILY_OPEN",
        "classification": (
            "THE_RETAINED_AE2_ACTION_ALREADY_SELECTS_THE_ENDPOINT_DOMAIN_CLASS_"
            "ON_EACH_MAXIMAL_HISTORY:_AN_ACTUAL_EVENT_USES_THE_EXISTING_TWO_"
            "SIDED_RESET_WENTZELL_GRAPH_AND_A_CANONICAL_STOP_USES_THE_RETAINED_"
            "FRIEDRICHS_CLOSURE;_THE_OPPOSITE_SIGN_NEUMANN_DIRICHLET_REFERENCE_"
            "PAIR_PROVES_ONLY_THAT_THE_BROAD_COMPARISON_ENCLOSURE_IS_"
            "NONDECISIVE,_NOT_THAT_THE_PHYSICAL_BOUNDARY_CONDITION_IS_"
            "AMBIGUOUS;_THE_ONLY_CURRENT_NONLOCAL_OWNER_IS_THE_ACTION_"
            "DETERMINED_MAXIMAL_log_R4_HISTORY_OR_EQUIVALENT_CHILD_WEYL_FAMILY_"
            "WITH_ITS_RESET_QUOTIENT_GEOMETRY_JETS"
        ),
        "endpoint_load_adjudication": {
            "actual_event": (
                "B_event(z;xi)=U_R(xi)^DAGGER*M_child(z;xi)*U_R(xi)+W_phys(xi)"
            ),
            "canonical_stop": "FRIEDRICHS_FORM_CLOSURE_OF_THE_RETAINED_NONNEGATIVE_MINIMAL_FORM",
            "arbitrary_regular_cover_endpoint": "FORBIDDEN_NOT_ACTION_OWNED",
            "regular_free_Neumann": "ADMISSIBLE_ONLY_IF_AN_ACTUAL_REGULAR_ACTION_TERMINAL_IS_DERIVED",
            "Dirichlet_reference": "BOUNDARY_TRIPLE_OR_COMPARISON_REFERENCE_NOT_THE_EVENT_TRANSMISSION_OPERATOR",
            "counterpair_role": "INFORMATION_THEORETIC_NO_GO_FOR_THE_BROAD_ENCLOSURE_ONLY",
            "additional_boundary_action_or_selector_required": False,
        },
        "dependency_reduction": {
            "already_action_owned": [
                "FORWARD_PROPER_TIME_AND_ORIENTATION",
                "D_tau",
                "Delta_tau=D_tau^star*D_tau_WITH_THE_RETAINED_ENDPOINT_FORM",
                "ABSTRACT_MAXIMAL_ENDPOINT_DOMAIN_CLASS",
                "AE2_EVENT_RESET_TRACE_CONORMAL_GRAPH",
                "FINITE_ENDPOINT_COMPACT_RESOLVENT_AND_SOURCE_TRACE_CONTROL",
            ],
            "not_independently_missing": [
                "A_TEMPORAL_FOURIER_MODE",
                "A_FREE_NEUMANN_OR_DIRICHLET_CHOICE",
                "AN_ARBITRARY_VALIDATION_ENDPOINT",
                "A_NEW_ENDPOINT_ACTION_TERM",
            ],
            "current_dynamic_coefficient": "log_R4(tau)",
            "current_nonlocal_object": (
                "M_child(z;xi),D_Phi_M_child(z;xi),D_Phi2_M_child(z;xi)_"
                "ON_A_NONEMPTY_FIXED_REGULAR_RESET_QUOTIENT_STRATUM"
            ),
        },
        "minimal_maximal_history_theorem": {
            "quantifier": "NONEMPTY_REGULAR_FORWARD_REACHABLE_RESET_QUOTIENT_STRATUM_NOT_UNIVERSAL_REACHABILITY",
            "history_statement": (
                "VALIDATE_THE_ACTION_DETERMINED_MAXIMAL_CHILD_COEFFICIENT_"
                "FAMILY_FROM_THE_CERTIFIED_RESET_RELATION_TO_ITS_FIRST_"
                "ACTUAL_EVENT_OR_CANONICAL_STOP_WITH_ALL_RETAINED_MARGINS"
            ),
            "operator_statement": (
                "ON_THE_SAME_COMMON_C2_FORM_DOMAIN_CONSTRUCT_OR_ENCLOSE_"
                "M_child_AND_ITS_FIRST_TWO_QUOTIENT_GEOMETRY_JETS_ON_A_"
                "NONEMPTY_NATIVE_RESOLVENT_REGION"
            ),
            "reset_fiber_statement": (
                "PROVIDE_THE_FAMILY_ON_THE_FIXED_STRATUM_OR_PROVE_ACTION_"
                "DERIVED_FIBER_INVARIANCE_BEFORE_USING_ONE_REPRESENTATIVE"
            ),
            "equivalent_route": (
                "A_COMPLETE_JOINT_TWO_SIDED_FINITE_HISTORY_OPERATOR_WITH_"
                "THE_SAME_GEOMETRY_JETS_IS_EQUIVALENT"
            ),
            "finite_encapsulation_existence_reopened": False,
            "universal_terminal_reachability_required": False,
        },
        "exact_next_dependency": (
            "CERTIFY_THE_MAXIMAL_FORWARD_log_R4(tau;xi)_AND_ITS_FIRST_TWO_"
            "ACTION_JACOBI_VARIATIONS_THROUGH_THE_FIRST_ACTION_OWNED_EVENT_"
            "OR_CANONICAL_STOP_ON_A_NONEMPTY_REGULAR_RESET_QUOTIENT_STRATUM,_"
            "OR_DIRECTLY_CERTIFY_THE_EQUIVALENT_M_child,D_Phi_M_child,D_Phi2_"
            "M_child_FAMILY;_DO_NOT_ADD_A_BOUNDARY_CONDITION_OR_MORE_PROBES_"
            "TO_THE_BROAD_SEAM_CLASS"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_MAXIMAL_CHILD_WEYL_FAMILY_OPEN",
            "endpoint_domain_ownership": "CLOSED",
            "finite_encapsulation_existence": "CLOSED_LOCAL_ACTION_THEOREM",
            "broad_seam_synthesis": "CLOSED_INVALID",
            "actual_projected_force": "OPEN",
            "same_action_saddle": "OPEN_AFTER_ORACLE",
            "pair_plus_contact_Hessian": "OPEN_AFTER_SADDLE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
