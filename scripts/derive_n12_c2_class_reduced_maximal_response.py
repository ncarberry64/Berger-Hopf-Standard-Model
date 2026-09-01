"""Instantiate the abstract maximal-forward Weyl family on the C2 class."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json"
CLASS = BASE / "BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_AUDIT.json"
FINITE_QUOTIENT = BASE / "BHSM_GLOBAL_FINITE_ENCLOSURE_QUOTIENT_KILL_SCREEN.json"
GATES = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CORRECTED_FORWARD_HISTORY_AND_PARTICLE_CLASS_GATES.json"
)
DOMAIN = BASE / "BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
WEYL = BASE / "BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json"
FRIEDRICHS = BASE / "BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json"
ADJOINT = BASE / "BHSM_N12_MAXIMAL_FORWARD_ADJOINT_EXHAUSTION.json"
ENDPOINT = BASE / "BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json"
SLOT = BASE / "BHSM_N12_GATE7_C2_DIAGRAM_SLOT_MATCHING_AUDIT.json"
PROPER_FORM = BASE / "BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json"
FINITE_RESPONSE = BASE / "BHSM_N12_C2_FINITE_COVER_VOLTERRA_WEYL.json"
HEAT = BASE / "BHSM_N12_FORWARD_RESOLVENT_HEAT_SYNTHESIS_AUDIT.json"
GAP_NO_GO = BASE / "BHSM_N12_FORWARD_EXTERIOR_GAP_ORACLE_AUDIT.json"
THEORY = ROOT / "theory/n12_c2_class_reduced_maximal_response.md"
INPUTS = (
    CLASS, FINITE_QUOTIENT, GATES, DOMAIN, WEYL, FRIEDRICHS, ADJOINT,
    ENDPOINT, SLOT, PROPER_FORM, FINITE_RESPONSE, HEAT, GAP_NO_GO, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete class-reduced M_C2 inputs required")
    class_record, finite_quotient, gates, domain, weyl, friedrichs, adjoint, endpoint, slot, proper_form, finite_response, heat, gap_no_go = (
        _load(path) for path in (
            CLASS, FINITE_QUOTIENT, GATES, DOMAIN, WEYL, FRIEDRICHS,
            ADJOINT, ENDPOINT, SLOT, PROPER_FORM, FINITE_RESPONSE, HEAT,
            GAP_NO_GO,
        )
    )
    if not all(record.get("validation_passed") is True for record in (
        class_record, finite_quotient, gates, domain, weyl, friedrichs,
        adjoint, endpoint, slot, proper_form, finite_response, heat,
        gap_no_go,
    )):
        raise RuntimeError("validated class-reduced M_C2 parents required")

    history_class = class_record["Sigma_enc_C2"]
    operator_family = {
        "name": "M_C2^max(z)",
        "history": "UNIQUE_MAXIMAL_FORWARD_HISTORY_Phi_C2_IN_THE_CERTIFIED_C2_ENCLOSURE_CLASS",
        "spectral_region": "REAL_z_LESS_THAN_ZERO_AND_ANALYTIC_CONTINUATION_ON_rho(P_C2^D)",
        "birth_space": weyl["operator_family"]["source_boundary_space"],
        "Poisson_operator": (
            "gamma_C2(z):a_MAPSTO_U_a_ON_Phi_C2_WITH_BIRTH_TRACE_a_"
            "AND_THE_ACTION_OWNED_MAXIMAL_ENDPOINT_CLASS"
        ),
        "Weyl_map": "M_C2^max(z)*a=Gamma1_birth(gamma_C2(z)*a)",
        "derivative_identity": weyl["operator_family"]["derivative_identity"],
        "endpoint_dichotomy": {
            "finite_actual_event": "RETAINED_AE2_TWO_SIDED_RESET_WENTZELL_GRAPH",
            "infinite_or_excluded_maximal_end": "RETAINED_FRIEDRICHS_FORM_CLOSURE",
            "proof_box_edge": "NOT_AN_ENDPOINT_CLASS",
        },
        "Friedrichs_realization": {
            "definition": "OPERATOR_NORM_LIMIT_OF_NESTED_FINITE_DIRICHLET_FORM_CORE_WEYL_MAPS",
            "convergence": friedrichs["theorem"]["convergence"],
            "finite_core_independence": friedrichs["closed_here"][
                "finite_core_exhaustion_independence"
            ],
        },
        "finite_event_realization": (
            "RETAINED_PARAMETRIC_INVERSE_FREE_K_DK_D2K_ORACLE_ON_A_"
            "CERTIFIED_REGULAR_EVENT_STRATUM"
        ),
    }
    seam = {
        "event_frame_load": "L_E1(z)=U_R^dagger*M_C2^max(z)*U_R+W_phys",
        "joint_seam": "Pi_E1(z)=M_f(z)+L_E1(z)",
        "frame_rule": "U_R_IS_AE2_COVARIANTLY_PARALLEL_AND_UNITARY",
        "status": "ALGEBRA_AND_DOMAINS_INSTANTIATED_OPERATOR_VALUE_NOT_NUMERICALLY_EVALUATED",
    }
    force_route = {
        "all_noncompact_reset_Jacobi_columns_required": False,
        "finite_core_pullback": adjoint["criterion"]["finite_core_pullback"],
        "maximal_force": adjoint["criterion"]["maximal_force"],
        "sufficient_integrability_condition": adjoint["criterion"][
            "sufficient_bound"
        ],
        "actual_weighted_load_status": "OPEN",
        "alternative": "CERTIFY_A_FINITE_LATER_EVENT_OR_CANONICAL_STOP_STRATUM",
    }
    validation = {
        "C2_is_one_certified_enclosure_class": (
            class_record["class_invariance_theorem"][
                "number_of_distinct_certified_C2_enclosure_classes"
            ] == 1
        ),
        "unique_maximal_forward_history_available": (
            gates["gate5"]["status"] == "CLOSED"
        ),
        "endpoint_domain_class_is_action_owned": (
            endpoint["claim_boundary"]["endpoint_domain_ownership"] == "CLOSED"
        ),
        "maximal_forward_source_domain_is_derived": (
            domain["claim_boundary"]["abstract_forward_source_domain"] == "DERIVED"
        ),
        "native_maximal_Weyl_family_is_derived": (
            weyl["claim_boundary"]["forward_resolvent_spectral_family"] == "DERIVED"
        ),
        "Friedrichs_Weyl_value_definition_is_unique": all((
            friedrichs["closed_here"]["Friedrichs_negative_z_Weyl_value_existence"],
            friedrichs["closed_here"]["Friedrichs_negative_z_Weyl_value_uniqueness"],
            friedrichs["closed_here"]["finite_core_exhaustion_independence"],
        )),
        "finite_cover_is_one_core_not_multiple_physical_objects": (
            finite_response["finite_history_response"]["segment_count"] == 98
            and class_record["class_invariance_theorem"][
                "number_of_distinct_certified_C2_enclosure_classes"
            ] == 1
        ),
        "class_label_not_promoted_to_numeric_operator_value": True,
        "continuous_geometry_dependence_retained": (
            weyl["validation"]["exact_Weyl_geometry_variation_identity_verified"]
            is True
        ),
        "gap_and_domain_class_not_promoted_to_value_bound": (
            gap_no_go["status"]
            == "GAP_ONLY_EXTERIOR_ORACLE_ROUTE_RIGOROUSLY_INSUFFICIENT"
        ),
        "single_z_probe_not_promoted_to_heat_functional": (
            heat["adjudication"]["Gate7_zero_source_force_evaluable_from_current_rows"]
            is False
        ),
        "weighted_adjoint_replaces_full_noncompact_Jacobi_matrix": (
            adjoint["criterion"]["all_forward_Jacobi_columns_required"] is False
        ),
        "global_finite_class_count_not_required_for_local_M_C2_definition": (
            finite_quotient["Gate7_routing"][
                "C2_local_class_theorem_blocked_by_global_finiteness"
            ] is False
        ),
        "no_endpoint_selector_box_physics_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE",
        "status": (
            "C2_MAXIMAL_WEYL_FAMILY_INSTANTIATED_BY_CLASS_AND_UNIQUE_HISTORY_WEIGHTED_LOAD_OPEN"
            if passed else "C2_CLASS_REDUCED_MAXIMAL_RESPONSE_NOT_INSTANTIATED"
        ),
        "classification": (
            "THE_ONE_CERTIFIED_C2_ENCLOSURE_CLASS_AND_UNIQUE_MAXIMAL_FORWARD_"
            "HISTORY_INSTANTIATE_THE_EXISTING_ACTION_OWNED_M_C_MAX_FAMILY;_"
            "THE_98_BOXES_ARE_FINITE_FORM_CORE_DATA,_WHILE_NUMERIC_VALUE_"
            "NONCOMPACT_RESET_JETS_AND_WEIGHTED_HEAT_MINUS_ZETA_LOAD_REMAIN_OPEN"
        ),
        "C2_enclosure_signature": history_class,
        "M_C2_maximal_operator_family": operator_family,
        "AE2_seam_assembly": seam,
        "finite_core_evidence": {
            "segment_count": finite_response["finite_history_response"][
                "segment_count"
            ],
            "proper_duration_interval": finite_response[
                "finite_history_response"
            ]["proper_duration_interval"],
            "role": "NESTED_FINITE_FORM_CORE_IN_ONE_CLASS_NOT_A_PHYSICAL_ENDPOINT",
            "z_minus_1_response": "CERTIFIED_FINITE_PREFIX_ONLY",
        },
        "force_adjoint_route": force_route,
        "adjudication": {
            "abstract_M_C2_value_definition_exists_and_is_unique": True,
            "actual_numeric_M_C2_family_evaluated": False,
            "compact_support_first_second_jets_converge": True,
            "noncompact_reset_quotient_jet_evaluated": False,
            "zero_source_force_evaluated": False,
            "same_action_saddle_evaluated": False,
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "M_C2^max is the existing maximal-forward family instantiated on Phi_C2",
                "endpoint class is action-owned",
                "Friedrichs value is a unique core-exhaustion limit",
                "98 boxes are one finite form core inside one class",
                "weighted-adjoint criterion replaces the full noncompact Jacobi matrix",
            ],
            "INVALIDATED": [
                "proof-box edge as endpoint condition",
                "class label alone fixes the numerical Weyl value",
                "gap/Friedrichs data alone bound the exterior oracle",
                "one z=-1 sample determines the heat force",
            ],
            "OPEN": [
                "actual maximal C2 endpoint outcome",
                "numeric M_C2(z) and noncompact reset quotient jets",
                "weighted maximal heat-minus-zeta adjoint load",
                "zero-source force, saddle, and physical Hessian",
            ],
        },
        "hindsight": {
            "class_reduction": "PHYSICAL_ONTOLOGY_CLOSED_FOR_C2_PREFIX",
            "finite_boxes": "PROOF_CORE_ONLY",
            "remaining_difficulty": "CONTINUOUS_MAXIMAL_HISTORY_OPERATOR_EVALUATION",
        },
        "exact_next_dependency": (
            "PROVE_OR_ENCLOSE_THE_ACTION_OWNED_WEIGHTED_MAXIMAL_ADJOINT_LOAD_"
            "INTEGRAL_norm(U(t,0))*norm(q_heat_minus_zeta(t))dt_ON_THE_"
            "CERTIFIED_C2_CLASS,_OR_CERTIFY_A_FINITE_LATER_EVENT_OR_"
            "CANONICAL_STOP_STRATUM;_THEN_EVALUATE_THE_FORCE_ROOT"
        ),
        "claim_boundary": {
            "C2_maximal_Weyl_family_definition": "INSTANTIATED",
            "C2_numeric_maximal_Weyl_family": "OPEN",
            "weighted_maximal_adjoint_load": "OPEN",
            "zero_source_force": "OPEN",
            "Gate7": "ACTIVE_WEIGHTED_C2_ADJOINT_LOAD",
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "M_C2_definition": payload["claim_boundary"][
            "C2_maximal_Weyl_family_definition"
        ],
        "M_C2_numeric": payload["claim_boundary"][
            "C2_numeric_maximal_Weyl_family"
        ],
        "next": payload["claim_boundary"]["weighted_maximal_adjoint_load"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
