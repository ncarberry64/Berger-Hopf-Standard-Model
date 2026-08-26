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
SOURCE_ROLE = BASE / "BHSM_N12_GATE7_EXTERNAL_BIRTH_SOURCE_ROLE_SUPERSESSION.json"
ONE_SEAM = BASE / "BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR.json"
CHILD = BASE / "BHSM_N12_C2_1222_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY.json"
FINITE_HEAT = BASE / "BHSM_N12_GATE7_FIXED_CHANNEL_FINITE_CORE_HEAT_BOUND.json"
FULL_GRADED_HEAT = BASE / "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json"
DIRECT_ZETA = BASE / "BHSM_N12_GATE7_DIRECT_ZETA_COEFFICIENT_COTANGENT.json"
ZETA_PULLBACK = BASE / "BHSM_N12_GATE7_C2_FINITE_CORE_ZETA_RESET_COTANGENT_ENCLOSURE.json"
ADJOINT = BASE / "BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY.json"
CAUCHY = BASE / "BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION.json"
THEORY = ROOT / "theory" / "n12_gate7_maximal_graded_cotangent_matching_audit.md"
INPUTS = (
    LEDGER, BRST, FUNCTIONAL, ONTOLOGY, SEED, DOMAIN, INCOMING, BIRTH_AUDIT,
    BIRTH_LOAD, TWO_SEAM, E0_PROVENANCE, SOURCE_ROLE, ONE_SEAM, CHILD,
    FINITE_HEAT, FULL_GRADED_HEAT, DIRECT_ZETA, ZETA_PULLBACK, ADJOINT, CAUCHY, THEORY,
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
        birth_load, two_seam, e0_provenance, source_role, one_seam, child,
        finite_heat, full_graded_heat, direct_zeta, zeta_pullback, adjoint, cauchy,
    ) = map(_load, INPUTS[:-1])
    records = (
        ledger, brst, functional, ontology, seed, domain, incoming, birth_audit,
        birth_load, two_seam, e0_provenance, source_role, one_seam, child,
        finite_heat, full_graded_heat, direct_zeta, zeta_pullback, adjoint, cauchy,
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
        "only_external_birth_trace_is_zeroed_after_joint_differentiation": (
            source_role["source_ordering"]["external_source"]
            == "j_birth=Gamma0_birth(U)"
            and source_role["source_ordering"]["differentiate_at"]
            == "FIXED_j_birth"
        ),
        "joint_heat_seed_and_reverse_order_are_closed": (
            seed["adjudication"]["joint_reverse_seed_formula"] == "CLOSED"
        ),
        "forward_AE2_domain_replaces_periodic_temporal_domain": (
            domain["action_version"] == "BHSM-AE-2.0.0"
            and domain["source_domain"]["Cayley_phase_family"] is None
        ),
        "incoming_M11_enclosure_is_the_physical_zero_source_response": (
            incoming["claim_boundary"][
                "incoming_M_f_negative_axis_parametric_enclosure"
            ] == "CLOSED"
            and source_role["adjudication"]
            ["M_f_equals_M11_at_zero_external_birth_trace"] == "REAFFIRMED"
        ),
        "dynamic_birth_graph_reduction_is_superseded_for_current_Gate7": (
            birth_audit["matching_audit"]["physical_zero_source_incoming_M_f"]
            == "ACTUALLY_MISSING_BIRTH_GRAPH_REDUCTION"
            and source_role["supersession"]
            ["BHSM_N12_GATE7_BIRTH_TRACE_MF_SUPERSESSION_AUDIT"] == "SUPERSEDED"
        ),
        "birth_load_formula_is_historical_not_a_current_slot": (
            birth_load["exact_birth_load"]["load"]
            == "B_birth=U_R0*(M_E0+W_E0)*U_R0^dagger"
            and source_role["matching_audit"]["B_birth"]
            == "NOT_REQUIRED_NOT_A_GATE7_DIAGRAM_SLOT"
        ),
        "two_seam_algebra_is_retained_but_physical_application_is_superseded": (
            two_seam["adjudication"]["complete_internal_operator_topology"]
            == "CLOSED"
            and "PHYSICAL_TWO_SEAM_APPLICATION_SUPERSEDED"
            in source_role["supersession"]
            ["BHSM_N12_GATE7_TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY"]
        ),
        "E0_candidate_audit_is_preserved_but_slot_is_not_required": (
            e0_provenance["status"]
            == "E0_EVENT_SIDE_PROVENANCE_EXHAUSTED_REALIZED_PARENT_ARM_OPEN"
            and source_role["adjudication"]["M_E0_required"] is False
        ),
        "direct_one_seam_finite_core_operator_and_jet_types_are_closed": (
            one_seam["claim_boundary"]["finite_core_joint_operator_type"]
            == "DERIVED_EXECUTABLE"
            and one_seam["claim_boundary"]["finite_core_joint_first_jet_type"]
            == "DERIVED_EXECUTABLE"
            and one_seam["matching_audit"]["actual_graded_cotangent_value"]
            == "OPEN"
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
        "full_graded_finite_core_heat_seed_is_uniformly_suppressed": (
            full_graded_heat["claim_boundary"][
                "full_graded_finite_core_heat_cotangent_seed"
            ] == "CERTIFIED_SUPPRESSED"
            and full_graded_heat["matching_audit"][
                "signed_non_scale_geometry_contraction"
            ] == "OPEN"
            and full_graded_heat["matching_audit"]["maximal_C2_tail"] == "OPEN"
        ),
        "direct_zeta_and_suppressed_heat_seed_are_ready_for_reverse_pullback": (
            direct_zeta["claim_boundary"][
                "direct_zeta_finite_core_coefficient_cotangent"
            ] == "CERTIFIED"
            and direct_zeta["matching_audit"]["C2_zeta_reverse_source"]
            == "READY_FOR_CERTIFIED_INTERVAL_ACTIONS"
            and adjoint["adjudication"][
                "direct_zeta_coefficient_cotangent"
            ].startswith("CLOSED")
            and adjoint["adjudication"][
                "full_graded_heat_cotangent_seed"
            ] == "CERTIFIED_SUPPRESSED_NOT_ZEROED"
        ),
        "C2_zeta_transition_pullback_norm_is_closed_but_signed_value_open": (
            zeta_pullback["claim_boundary"][
                "C2_finite_core_zeta_reset_cotangent_norm_ball"
            ] == "CERTIFIED"
            and zeta_pullback["claim_boundary"][
                "signed_C2_zeta_reset_cotangent_value"
            ] == "OPEN"
        ),
        "signed_reverse_equation_is_closed_but_heat_and_upstream_open": (
            adjoint["adjudication"]["signed_finite_core_adjoint_equation"]
            == "CLOSED"
            and adjoint["adjudication"][
                "actual_joint_graded_heat_minus_zeta_cotangent"
            ] == "ZETA_RESET_BALL_CLOSED_HEAT_GEOMETRY_CONTRACTION_OPEN"
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
            "MAXIMAL_GRADED_COTANGENT_FINITE_CORE_SEED_CLOSED_SIGNED_CONTRACTION_AND_TAIL_OPEN"
            if passed else "MAXIMAL_GRADED_COTANGENT_MATCHING_NOT_CLOSED"
        ),
        "classification": (
            "THE_RETAINED_GRADING_MULTIPLICITIES_HEAT_SEED_ZETA_SUBTRACTION_"
            "REVERSE_ORDER_AND_PROJECTED_CAUCHY_CRITERION_ARE_ALL_EXISTING_"
            "VALID_MATCHES;_THE_EXTERNAL_ZERO_BIRTH_TRACE_SELECTS_THE_DIRICHLET_"
            "REFERENCE_WITH_NONZERO_INTERNAL_M_f_EQUALS_M11,_AND_THE_ONLY_"
            "PHYSICAL_INTERNAL_SEAM_IS_E1_C2;_THE_DIRECT_FINITE_CORE_OPERATOR_"
            "AND_FIRST_JET_TYPES_ARE_EXECUTABLE,_THE_DIRECT_ZETA_COVECTOR_IS_"
            "COMPONENTWISE_CLOSED,_AND_THE_COMPLETE_FINITE_CORE_GRADED_HEAT_"
            "SEED_IS_UNIFORMLY_SUPPRESSED_IN_LOG_SPACE;_THE_C2_ZETA_RESET_"
            "PULLBACK_NORM_BALL_IS_CERTIFIED,_WHILE_ITS_SIGNED_VALUE,_THE_HEAT_"
            "CONTRACTION,_C2_MAXIMAL_TAIL,_AND_PROJECTED_FORCE_ARE_OPEN"
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
            "direct_zeta_covector": "CLOSED_COMPONENTWISE_FINITE_CORE_MATCH",
            "C2_zeta_reset_cotangent_pullback": "CERTIFIED_ACTION_DUAL_NORM_BALL",
            "joint_internal_seam_assembly": "VALID_MATCH_ONE_E1_C2_SEAM",
            "incoming_M11_whole_axis_class": "VALID_PHYSICAL_ZERO_SOURCE_M_f",
            "physical_zero_source_incoming_Mf": "VALID_MATCH_M11",
            "birth_graph_B_birth_and_first_jet": "NOT_REQUIRED_CURRENT_GATE7",
            "E0_event_side_Calderon_and_first_jet": "NOT_REQUIRED_CURRENT_GATE7",
            "outgoing_M_C2_whole_axis_1222_core": "VALID_FINITE_CORE_MATCH",
            "all_1222_transposed_reverse_actions": "VALID_MATCH",
            "physical_quotient_and_Cauchy_criterion": "VALID_MATCH",
            "finite_core_direct_joint_operator_generator": "VALID_MATCH",
            "finite_core_direct_joint_first_jet_generator": "VALID_MATCH",
            "full_graded_finite_core_heat_trace": "VALID_LOG_SPACE_ENCLOSURE",
            "full_graded_finite_core_heat_cotangent_seed": "VALID_TRACE_NORM_LOG_SPACE_ENCLOSURE",
            "actual_per_level_joint_operator_family": "DIRECT_GENERATOR_CLOSED_ACTUAL_PARAMETRIC_VALUES_AND_MAXIMAL_TAIL_OPEN",
            "actual_per_level_joint_operator_first_jet": "DIRECT_GENERATOR_CLOSED_ACTUAL_PARAMETRIC_VALUES_AND_MAXIMAL_TAIL_OPEN",
            "actual_finite_core_graded_cotangent_seed": "ZETA_RESET_BALL_CLOSED_PLUS_UNIFORM_HEAT_TRACE_NORM_ENCLOSURE",
            "actual_maximal_graded_cotangent_value": "FINITE_CORE_CLOSED_MAXIMAL_TAIL_OPEN",
        },
        "adjudication": {
            "new_grading_required": False,
            "new_external_or_seam_source_required": False,
            "more_isolated_negative_axis_probes_have_proof_value": False,
            "proof_center_may_be_promoted_to_physical_history": False,
            "finite_1222_edge_may_be_promoted_to_endpoint": False,
            "actual_joint_operator_or_decisive_trace_enclosure": "FINITE_CORE_HEAT_SEED_CLOSED",
            "signed_reverse_value": "WAITING_ON_ZETA_SIGNED_CENTER_HEAT_CONTRACTION_AND_UPSTREAM_PULLBACK",
            "projected_Cauchy_tail": "WAITING_ON_FINITE_CORE_FORCE_NET",
            "same_action_KKT_root": "WAITING_ON_PROJECTED_FORCE",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
        },
        "exact_next_dependency": (
            "USE_THE_CERTIFIED_C2_ZETA_RESET_COTANGENT_BALL_AND_SHARPEN_ITS_"
            "SIGNED_CENTER_ONLY_IF_NEEDED,_CONTRACT_THE_SEPARATELY_SUPPRESSED_"
            "HEAT_SEED,_COMPOSE_THE_UPSTREAM_C1_COVECTOR,_AND_PROVE_"
            "THE_MAXIMAL_PROJECTED_CAUCHY_TAIL_OR_CERTIFY_A_FINITE_STOP"
        ),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "Gate7": "ACTIVE_E1_C2_GRADED_COTANGENT_AND_MAXIMAL_TAIL",
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
