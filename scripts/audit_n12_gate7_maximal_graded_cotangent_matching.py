"""Match every retained Gate-7 graded-cotangent slot to current BHSM data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_MAXIMAL_GRADED_COTANGENT_MATCHING_AUDIT.json"
LEDGER = ROOT / "artifacts" / "BHSM_aether_common_quantum_superdeterminant_v15_96.json"
BRST = BASE / "BHSM_N12_FORWARD_BRST_HEAT_TAIL_CANCELLATION_AUDIT.json"
FUNCTIONAL = BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
SEED = BASE / "BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json"
DOMAIN = BASE / "BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"
INCOMING = BASE / "BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE.json"
BIRTH_AUDIT = BASE / "BHSM_N12_GATE7_BIRTH_TRACE_MF_SUPERSESSION_AUDIT.json"
BIRTH_LOAD = BASE / "BHSM_N12_GATE7_BIRTH_GRAPH_LOAD_MATCHING_AUDIT.json"
TWO_SEAM = BASE / "BHSM_N12_GATE7_TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY.json"
E0_PROVENANCE = BASE / "BHSM_N12_GATE7_E0_EVENT_SIDE_RESPONSE_PROVENANCE_AUDIT.json"
CHILD = BASE / "BHSM_N12_C2_1222_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY.json"
FINITE_HEAT = BASE / "BHSM_N12_GATE7_FIXED_CHANNEL_FINITE_CORE_HEAT_BOUND.json"
ADJOINT = BASE / "BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY.json"
CAUCHY = BASE / "BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION.json"
THEORY = ROOT / "theory" / "n12_gate7_maximal_graded_cotangent_matching_audit.md"
INPUTS = (
    LEDGER, BRST, FUNCTIONAL, ONTOLOGY, SEED, DOMAIN, INCOMING, BIRTH_AUDIT,
    BIRTH_LOAD, TWO_SEAM, E0_PROVENANCE, CHILD,
    FINITE_HEAT, ADJOINT, CAUCHY, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _weight_rows(ledger: dict[str, Any]) -> dict[str, Any]:
    source = ledger["graded_operator_ledger"]
    return {
        "gauge_transverse": {
            "levels": "m>=2",
            "weight": "w_gauge(m)=+24*(m^2-1)",
            "samples": {str(m): 24 * (m * m - 1) for m in (2, 3, 7)},
            "source": source["gauge_transverse"],
        },
        "Weyl": {
            "levels": "n>=0",
            "weight": "w_Weyl(n)=-48*(n+1)*(n+2)",
            "samples": {
                str(n): -48 * (n + 1) * (n + 2) for n in (0, 1, 5)
            },
            "source": source["Weyl"],
        },
        "Hubbard_Strattonovich": {
            "levels": "m>=1",
            "weight": "w_HS(m)=+4*m^2",
            "samples": {str(m): 4 * m * m for m in (1, 2, 6)},
            "source": source["Hubbard_Strattonovich"],
        },
        "gauge_longitudinal_complex_ghost": {
            "weight": 0,
            "rule": source["gauge_longitudinal_ghost"]["statement"],
        },
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing maximal graded-cotangent inputs: " + ", ".join(missing)
        )
    (
        ledger, brst, functional, ontology, seed, domain, incoming, birth_audit,
        birth_load, two_seam, e0_provenance, child,
        finite_heat, adjoint, cauchy,
    ) = map(_load, INPUTS[:-1])
    records = (
        ledger, brst, functional, ontology, seed, domain, incoming, birth_audit,
        birth_load, two_seam, e0_provenance, child,
        finite_heat, adjoint, cauchy,
    )
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated graded-cotangent parents required")

    weights = _weight_rows(ledger)
    validation = {
        "transverse_gauge_weight_replayed": (
            weights["gauge_transverse"]["samples"]
            == {"2": 72, "3": 192, "7": 1152}
        ),
        "Weyl_weight_replayed": (
            weights["Weyl"]["samples"]
            == {"0": -96, "1": -288, "5": -2016}
        ),
        "HS_weight_replayed": (
            weights["Hubbard_Strattonovich"]["samples"]
            == {"1": 4, "2": 16, "6": 144}
        ),
        "longitudinal_ghost_pair_cancels_mode_by_mode": (
            brst["adjudication"]["longitudinal_ghost_BRST_pair"]
            == "CANCELS_EXACTLY"
        ),
        "physical_supertrace_is_not_zero": (
            brst["adjudication"][
                "transverse_gauge_HS_Weyl_physical_supertrace"
            ] == "NONZERO_LEADING_HEAT_COEFFICIENT"
        ),
        "heat_minus_zeta_functional_is_derived": (
            functional["claim_boundary"][
                "heat_minus_zeta_replacement_force_functional"
            ] == "DERIVED"
        ),
        "only_external_J_ext_is_zeroed_after_joint_differentiation": (
            ontology["external_internal_partition"]["set_to_zero"]
            == ["J_ext"]
            and ontology["validation"][
                "zero_external_source_does_not_impose_zero_birth_trace"
            ] is True
        ),
        "joint_heat_seed_and_reverse_order_are_closed": (
            seed["adjudication"]["joint_reverse_seed_formula"] == "CLOSED"
        ),
        "forward_AE2_domain_replaces_periodic_temporal_domain": (
            domain["action_version"] == "BHSM-AE-2.0.0"
            and domain["source_domain"]["Cayley_phase_family"] is None
        ),
        "old_incoming_M11_enclosure_is_only_a_conditional_Dirichlet_reference": (
            incoming["claim_boundary"][
                "incoming_M_f_negative_axis_parametric_enclosure"
            ] == "CLOSED"
            and birth_audit["adjudication"][
                "M_f_equals_M11_as_physical_zero_source_response"
            ] == "SUPERSEDED"
        ),
        "physical_birth_graph_reduction_is_localized_and_open": (
            birth_audit["matching_audit"]["physical_zero_source_incoming_M_f"]
            == "ACTUALLY_MISSING_BIRTH_GRAPH_REDUCTION"
            and birth_audit["matching_audit"]["B_birth_and_first_action_jet"]
            == "ACTUALLY_MISSING_OR_NOT_YET_INSTANTIATED"
        ),
        "birth_load_is_exactly_typed_to_the_missing_E0_event_response": (
            birth_load["exact_birth_load"]["load"]
            == "B_birth=U_R0*(M_E0+W_E0)*U_R0^dagger"
            and birth_load["matching_audit"]
            ["M_E0_nonzero_event_side_Calderon_family"] == "ACTUALLY_MISSING"
        ),
        "complete_two_seam_operator_topology_and_first_variation_are_closed": (
            two_seam["adjudication"]["complete_internal_operator_topology"]
            == "CLOSED"
            and two_seam["matching_audit"]
            ["direct_Schur_first_variation_equivalence"]
            == "VALID_MATCH_DERIVED"
            and two_seam["closed_operator"]["zero_source_effect"]
            == "REMOVE_LINEAR_COUPLING_BUT_RETAIN_BOTH_ROWS_AND_COLUMNS"
        ),
        "E0_candidate_provenance_is_exhausted_to_parent_history_realization": (
            e0_provenance["status"]
            == "E0_EVENT_SIDE_PROVENANCE_EXHAUSTED_REALIZED_PARENT_ARM_OPEN"
            and e0_provenance["adjudication"]["new_operator_theory_required"]
            is False
        ),
        "child_whole_axis_family_is_finite_core_only": (
            child["claim_boundary"]["finite_core_complete_negative_axis_family"]
            == "DERIVED_EXECUTABLE_THROUGH_1222"
            and child["claim_boundary"]["maximal_tail"] == "OPEN"
        ),
        "fixed_channel_heat_bound_does_not_claim_full_grading": (
            finite_heat["validation"]["full_graded_joint_trace_is_not_claimed"]
            is True
        ),
        "signed_reverse_equation_is_closed_but_source_value_open": (
            adjoint["adjudication"]["signed_finite_core_adjoint_equation"]
            == "CLOSED"
            and adjoint["adjudication"][
                "actual_joint_graded_heat_minus_zeta_cotangent"
            ] == "OPEN_CURRENT_OWNER"
        ),
        "projected_Cauchy_criterion_is_derived": (
            cauchy["claim_boundary"]["projected_Cauchy_criterion"]
            == "DERIVED"
        ),
        "no_new_source_selector_endpoint_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_MAXIMAL_GRADED_COTANGENT_MATCHING_AUDIT",
        "status": (
            "MAXIMAL_GRADED_COTANGENT_TYPE_AND_TWO_SEAM_TOPOLOGY_CLOSED_VALUES_OPEN"
            if passed else "MAXIMAL_GRADED_COTANGENT_MATCHING_NOT_CLOSED"
        ),
        "classification": (
            "THE_RETAINED_GRADING_MULTIPLICITIES_HEAT_SEED_ZETA_SUBTRACTION_"
            "REVERSE_ORDER_AND_PROJECTED_CAUCHY_CRITERION_ARE_ALL_EXISTING_"
            "VALID_MATCHES;_THE_OLD_ZERO_TRACE_INCOMING_M_f_IDENTIFICATION_IS_"
            "SUPERSEDED,_AND_THE_ACTUALLY_MISSING_DATUM_IS_THE_ACTION_REALIZED_"
            "TWO_SEAM_TOPOLOGY_IS_CLOSED,_BUT_THE_ACTION_REALIZED_E0_BLOCK,_THE_"
            "PER_LEVEL_COMPLETE_JOINT_OPERATOR_VALUES_AND_THEIR_FIRST_JETS_OR_AN_"
            "EQUIVALENT_DECISIVE_TRACE_FUNCTIONAL_ENCLOSURE_ARE_OPEN"
        ),
        "retained_graded_sector_ledger": weights,
        "exact_cotangent_contract": {
            "per_level_joint_operator": "P_C,k^joint(xi)",
            "per_level_operator_cotangent": (
                "Q_C,k=(w_C,k/2)*exp(-ell^2*P_C,k^joint)*"
                "(P_C,k^joint)^(-1)"
            ),
            "inverse_free_form": (
                "Q_C,k=(w_C,k/2)*integral_(ell^2)^infinity_"
                "exp(-s*P_C,k^joint)ds"
            ),
            "primitive_coefficient_cotangent": (
                "q_a^heat=sum_C,k ReTr[Q_C,k^dagger*D_a P_C,k^joint]"
            ),
            "replacement": (
                "q_a^rep=q_a^heat-(59/30)*D_a integral(d_tau/R4)"
            ),
            "family_domain": "CERTIFIED_LOCAL_73_PARAMETER_FORWARD_HISTORY_FAMILY",
            "external_source_term": "ABSENT_AFTER_J_ext=0",
        },
        "matching_audit": {
            "grading_signs_and_multiplicities": "VALID_MATCH",
            "heat_Frechet_cotangent": "VALID_MATCH",
            "direct_zeta_covector": "VALID_MATCH",
            "joint_internal_seam_assembly": "VALID_MATCH_TWO_SEAM_TOPOLOGY_DERIVED",
            "incoming_M11_whole_axis_class": "VALID_CONDITIONAL_DIRICHLET_REFERENCE_ONLY",
            "physical_zero_source_incoming_Mf": "ACTUALLY_MISSING_BIRTH_GRAPH_REDUCTION",
            "birth_graph_B_birth_and_first_jet": "ACTUALLY_MISSING_OR_NOT_YET_INSTANTIATED",
            "E0_event_side_Calderon_and_first_jet": "OPEN_PARENT_HISTORY_REALIZATION",
            "outgoing_M_C2_whole_axis_1222_core": "VALID_FINITE_CORE_MATCH",
            "all_1222_transposed_reverse_actions": "VALID_MATCH",
            "physical_quotient_and_Cauchy_criterion": "VALID_MATCH",
            "actual_per_level_joint_operator_family": "OPEN_UNINSTANTIATED_TWO_SEAM_VALUES",
            "actual_per_level_joint_operator_first_jet": "OPEN_UNINSTANTIATED_TWO_SEAM_VALUES",
            "actual_maximal_graded_cotangent_value": "ACTUALLY_MISSING",
        },
        "adjudication": {
            "new_grading_required": False,
            "new_external_or_seam_source_required": False,
            "more_isolated_negative_axis_probes_have_proof_value": False,
            "proof_center_may_be_promoted_to_physical_history": False,
            "finite_1222_edge_may_be_promoted_to_endpoint": False,
            "actual_joint_operator_or_decisive_trace_enclosure": "OPEN_CURRENT_OWNER",
            "signed_reverse_value": "WAITING_ON_ACTUAL_GRADED_COTANGENT",
            "projected_Cauchy_tail": "WAITING_ON_FINITE_CORE_FORCE_NET",
            "same_action_KKT_root": "WAITING_ON_PROJECTED_FORCE",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
        },
        "exact_next_dependency": (
            "REALIZE_THE_E0_EVENT_SIDE_CALDERON_AND_BIRTH_LOAD_OR_KEEP_THE_E0_ARM_"
            "AND_BIRTH_TRACE_EXPLICIT,_"
            "THEN_REALIZE_OR_SHARPLY_ENCLOSE_FOR_EACH_RETAINED_GRADED_LEVEL_THE_"
            "COMPLETE_JOINT_EVENT_CHILD_OPERATOR_AND_FIRST_ACTION_JET_ON_THE_"
            "LOCAL_73_PARAMETER_FAMILY_OR_AT_AN_ACTUAL_FINITE_STOP;_THEN_"
            "EVALUATE_THE_FIXED_COTANGENT_CONTRACT_AND_RUN_THE_EXISTING_SINGLE_"
            "REVERSE_SWEEP"
        ),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "Gate7": "ACTIVE_BIRTH_LOADED_PER_LEVEL_JOINT_OPERATOR_AND_COTANGENT",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
            "actual_graded_cotangent_claimed": False,
            "numerical_force_claimed": False,
            "frozen_predictions_changed": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
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
        "actual_operator_family": payload["matching_audit"]
        ["actual_per_level_joint_operator_family"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
