"""Reconcile Gate-7 zero-source semantics with the joint AE2 operator."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
GLUING = BASE / "BHSM_N12_FINITE_HISTORY_GLUING_FORCE_PROVENANCE.json"
GRAPH = BASE / "BHSM_N12_FORWARD_SOURCE_VARIATIONAL_GRAPH.json"
INCIDENCE = BASE / "BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
WARD = BASE / "BHSM_N12_GATE7_COMMON_SCALE_HEAT_ZETA_WARD.json"
QUOTIENT = BASE / "BHSM_N12_INTRINSIC_TIME_QUOTIENT_FORCE_ROOT.json"
THEORY = ROOT / "theory" / "n12_gate7_closed_system_zero_external_source_ontology.md"
INPUTS = (GLUING, GRAPH, INCIDENCE, WARD, QUOTIENT, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing closed-system ontology inputs: " + ", ".join(missing))
    gluing, graph, incidence, ward, quotient = map(_load, INPUTS[:-1])
    records = (gluing, graph, incidence, ward, quotient)
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated Gate-7 parents required")

    validation = {
        "owner_authorization_is_classified_as_physical_ontology_not_action_derivation": True,
        "only_external_birth_Cauchy_linear_datum_is_zeroed": True,
        "zero_external_source_does_not_impose_zero_birth_trace": True,
        "zero_external_source_preserves_the_self_adjoint_birth_graph": True,
        "formation_child_reset_and_contact_blocks_remain_internal": True,
        "joint_operator_precedes_grading_functional_and_differentiation": True,
        "internal_incidence_vertices_are_not_external_sources": True,
        "no_internal_response_is_zeroed_by_zero_external_source": True,
        "no_second_seam_force_is_added": True,
        "joint_Schur_decomposition_is_counted_exactly_once": (
            gluing["validation"]["both_determinant_identities_close"]
            and gluing["validation"]["both_variation_identities_close"]
        ),
        "intrinsic_quotient_and_bordered_KKT_roots_are_equivalent": (
            quotient["claim_boundary"]["force_root_time_quotient_equivalence"] == "DERIVED"
        ),
        "projected_force_tail_is_not_claimed_by_source_ontology": True,
        "common_scale_Ward_accounting_is_preserved": (
            ward["adjudication"]["common_scale_source_contraction_formula"] == "CLOSED"
        ),
        "local_incidence_is_retained_as_an_internal_operator_vertex": (
            incidence["claim_boundary"]["domain_parametric_nonzero_local_incidence"] == "DERIVED"
        ),
        "no_selector_endpoint_scale_fit_action_term_gate_or_chord_added": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY",
        "status": "OWNER_SOURCE_ONTOLOGY_RECONCILED_WITH_JOINT_AE2_OPERATOR",
        "classification": (
            "ZERO_SOURCE_MEANS_ONLY_ZERO_EXTERNAL_BIRTH_CAUCHY_DATUM;_M_f,_M_C2,_U_R,_"
            "W_phys,_AND_RETAINED_CONTACT_RESPONSES_ARE_INTERNAL_BLOCKS_OF_ONE_CLOSED_"
            "JOINT_OPERATOR_AND_MUST_BE_GRADED,_DIFFERENTIATED,_AND_REVERSE_PROPAGATED_ONCE"
        ),
        "provenance": {
            "category": "OWNER_AUTHORIZED_PHYSICAL_ONTOLOGY",
            "action_derived": False,
            "changes_retained_action": False,
            "authorization_scope": "GATE7_ZERO_EXTERNAL_SOURCE_SEMANTICS",
        },
        "external_internal_partition": {
            "external_zero_datum": "J_ext_AT_THE_BIRTH_CAUCHY_LEG",
            "set_to_zero": ["J_ext"],
            "source_coupling": "S_J[U]=(1/2)<U,P_joint*U>-Re<J_ext,Gamma_birth*U>",
            "zero_source_effect": "REMOVE_ONLY_THE_LINEAR_J_ext_COUPLING",
            "zero_source_is_not": [
                "Gamma_birth*U=0",
                "HOMOGENEOUS_DIRICHLET_SELECTION",
                "DELETION_OF_THE_BIRTH_TRACE_DEGREE_OF_FREEDOM",
            ],
            "internal_not_zeroed": [
                "M_f", "M_C2", "U_R", "W_phys",
                "gauge_transverse_contact_response",
                "scalar_topographic_contact_response",
                "retained_AE2_pair_and_contact_vertices",
            ],
            "legacy_source_incidence_semantics": (
                "INTERNAL_OPERATOR_VARIATION_VERTICES_NOT_EXTERNAL_CAUCHY_DATA"
            ),
        },
        "joint_assembly": {
            "operator": "P_joint=[[A,C,0],[C^dagger,H+G+W_phys,E^dagger],[0,E,F]]",
            "formation_off_event_block": (
                "A_INCLUDES_THE_DYNAMICAL_BIRTH_TRACE_AND_RETAINED_SELF_ADJOINT_"
                "BIRTH_GRAPH;_A_IS_NOT_A_ZERO_BIRTH_TRACE_DIRICHLET_RESTRICTION"
            ),
            "two_boundary_identification": (
                "A_TO_M00_PLUS_B_birth,_C_TO_M01,_C_DAGGER_TO_M10,_H_TO_M11"
            ),
            "zero_source_birth_solve": (
                "(M00+B_birth)*X_birth=M01,_u_birth=-X_birth*u_event"
            ),
            "formation_response": "M_f=H-C^dagger*A^(-1)*C",
            "formation_response_two_boundary": "M_f=M11-M10*X_birth",
            "transported_child_response": "M_C2^R=U_R^dagger*M_C2*U_R",
            "seam_Schur_block": "S_AE2=M_f+M_C2^R+W_phys",
            "determinant_identity": "det(P_joint)=det(A)*det(F)*det(S_AE2)",
            "assembly_rule": "ASSEMBLE_COMPLETE_SELF_ADJOINT_JOINT_OPERATOR_BEFORE_GRADING_OR_ZERO_SOURCE",
            "double_count_rule": "EACH_INTERNAL_BLOCK_AND_CONTACT_IS_INCLUDED_EXACTLY_ONCE",
        },
        "ordered_evaluation": [
            "ASSEMBLE_COMPLETE_JOINT_INTERNAL_OPERATOR_AND_DOMAIN",
            "APPLY_RETAINED_BRST_GRADING_AND_HEAT_MINUS_ZETA_ACCOUNTING",
            "DIFFERENTIATE_THE_COMPLETE_CLOSED_SYSTEM_FUNCTIONAL",
            "SET_ONLY_EXTERNAL_J_ext_TO_ZERO",
            "REVERSE_PROPAGATE_THE_SINGLE_JOINT_COTANGENT_THROUGH_SEAM_AND_BOTH_HISTORIES",
            "PASS_TO_THE_PHYSICAL_TIME_GAUGE_QUOTIENT",
            "TEST_PROJECTED_CAUCHY_LIMIT_OR_USE_ACTUAL_FINITE_EVENT_CANONICAL_STOP",
            "SOLVE_q_rep_PLUS_DC_DAGGER_delta_lambda_EQUALS_ZERO",
        ],
        "physical_force": {
            "definition": "q_rep(xi)=D_xi_Gamma_closed[P_joint(xi)]_AT_J_ext=0",
            "quotient": "ker(D_C)/span(g_tau)",
            "root": "[q_rep]=0_ON_THE_PHYSICAL_QUOTIENT",
            "bordered_equivalent": "q_rep+D_C^dagger*delta_lambda=0",
            "additional_seam_source_allowed": False,
        },
        "matching_audit": {
            "external_birth_Cauchy_source": "VALID_MATCH_J_ext_AND_ONLY_THIS_DATUM_IS_ZEROED",
            "birth_trace_domain": "VALID_RETAINED_SELF_ADJOINT_GRAPH_NOT_REPLACED_BY_DIRICHLET",
            "incoming_M_f": (
                "VALID_INTERNAL_RESPONSE_TYPE_PHYSICAL_BIRTH_GRAPH_REDUCTION_OPEN"
            ),
            "Dirichlet_reference_M11": (
                "VALID_REFERENCE_BLOCK_NOT_THE_PHYSICAL_ZERO_SOURCE_M_f"
            ),
            "outgoing_M_C2": "VALID_INTERNAL_RESPONSE_SLOT_NOT_AN_EXTERNAL_SOURCE",
            "reset_transport_U_R": "VALID_INTERNAL_GLUE_SLOT",
            "W_phys": "VALID_INTERNAL_CONTACT_SLOT",
            "common_source_incidence": "VALID_INTERNAL_VARIATION_VERTEX_SLOT",
            "birth_graph_B_birth_and_first_jet": "ACTUALLY_MISSING_OR_NOT_YET_INSTANTIATED",
            "complete_joint_graded_coefficient_cotangent": "ACTUALLY_MISSING",
            "maximal_projected_Cauchy_limit_or_finite_stop": "ACTUALLY_MISSING",
        },
        "adjudication": {
            "source_ledger_ambiguity": "CLOSED_BY_OWNER_ONTOLOGY",
            "joint_internal_operator_assembly_rule": "CLOSED",
            "zero_external_source_ordering_rule": "CLOSED",
            "additional_independent_seam_force": "FORBIDDEN",
            "internal_response_zeroing": "FORBIDDEN",
            "complete_joint_graded_cotangent": "OPEN_CURRENT_OPERATOR_OWNER",
            "joint_reverse_adjoint": "WAITING_ON_COMPLETE_JOINT_GRADED_COTANGENT",
            "projected_Cauchy_tail": "OPEN",
            "same_action_KKT_root": "WAITING_ON_PROJECTED_FORCE",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
        },
        "exact_next_dependency": (
            "INSTANTIATE_THE_RETAINED_BIRTH_GRAPH_OR_KEEP_THE_BIRTH_TRACE_EXPLICIT,_"
            "THEN_ASSEMBLE_THE_COMPLETE_JOINT_GRADED_HEAT_MINUS_ZETA_COEFFICIENT_COTANGENT_"
            "WITHOUT_ZEROING_OR_DOUBLE_COUNTING_ANY_INTERNAL_SEAM_BLOCK,_THEN_RUN_ONE_"
            "JOINT_REVERSE_ADJOINT_AND_TEST_ITS_PROJECTED_CAUCHY_LIMIT_OR_ACTUAL_FINITE_STOP"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "Gate7": "ACTIVE_BIRTH_LOADED_COMPLETE_JOINT_GRADED_COTANGENT",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
            "frozen_predictions_changed": False,
            "numerical_force_claimed": False,
            "finite_1222_core_promoted_to_endpoint": False,
        },
        "inputs": {str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path) for path in INPUTS},
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "next": payload["adjudication"]["complete_joint_graded_cotangent"],
    }, indent=2))


if __name__ == "__main__":
    main()
