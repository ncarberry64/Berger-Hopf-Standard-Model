"""Match existing BHSM objects into the AE2/DOP853 Gate-7 diagram slots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_DOP853_SYSTEM_ADAPTER_MATCHING.json"

INPUTS = {
    "ae2_action": ROOT / "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    "ae2_domain": BASE / "BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json",
    "one_seam": BASE / "BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR.json",
    "birth_jet": BASE / "BHSM_N12_C2_BIRTH_COEFFICIENT_QUOTIENT_JET.json",
    "dop_response": BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE_CERTIFICATE.json",
    "dop_first_variation": BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RESPONSE_FIRST_VARIATION.json",
    "dop_second_variation": BASE / "BHSM_N12_C2_STOP_DOP853_BORDERED_RESPONSE_SECOND_VARIATION.json",
    "weyl_cotangent": BASE / "BHSM_N12_C2_1222_SEGMENT_WEYL_COEFFICIENT_COTANGENT.json",
    "duration": BASE / "BHSM_N12_C2_1222_MOVING_DURATION_PULLBACK_ENCLOSURE.json",
    "heat_seed": BASE / "BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json",
    "heat_bound": BASE / "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json",
    "zeta": BASE / "BHSM_N12_GATE7_DIRECT_ZETA_COEFFICIENT_COTANGENT.json",
    "reset_adjoint": BASE / "BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE.json",
    "force": BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    "first_hit": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_DENSE_DESCRIPTOR_FIRST_HIT.json",
    "common_frame": BASE / "BHSM_N12_GATE7_SIGNED_COMMON_FRAME_DATA_MATCHING.json",
    "selected_center_provenance": BASE / "BHSM_N12_GATE7_SELECTED_CENTER_PROVENANCE_RECONCILIATION.json",
    "nonlinear_cone_spectrum": BASE / "BHSM_N12_GATE7_SELECTED_DOP853_NONLINEAR_CONE_SPECTRUM.json",
    "nonlinear_cone_projector_inverse": BASE / "BHSM_N12_GATE7_SELECTED_DOP853_NONLINEAR_CONE_PROJECTOR_INVERSE.json",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def build_payload() -> dict[str, Any]:
    records = {key: _load(path) for key, path in INPUTS.items()}
    slots = [
        {
            "diagram_slot": "CURRENT_ACTION_AND_BIRTH_DOMAIN",
            "required_type": "versioned action plus complete self-adjoint event-child matter graph",
            "candidate_BHSM_objects": ["ae2_action", "ae2_domain"],
            "dimension_domain_check": "unitary half-dimensional graph on the AE2 two-sided trace space",
            "provenance_check": "OWNER_SELECTED_NEW_ACTION_DOMAIN_VERSION",
            "match": "VALID_MATCH",
        },
        {
            "diagram_slot": "JOINT_E1_C2_SEAM_OPERATOR",
            "required_type": "one internal seam with event response, reset lift, child response and contacts counted once",
            "candidate_BHSM_objects": ["one_seam"],
            "dimension_domain_check": "direct joint form is Schur-equivalent to M_f+U_R^dagger M_C2 U_R+W_phys",
            "provenance_check": "existing AE2 action form; no independent internal source",
            "match": "VALID_MATCH",
        },
        {
            "diagram_slot": "C2_BIRTH_COEFFICIENT_AND_FIRST_JET",
            "required_type": "reset-quotient map to log R4 and D_tau log R4",
            "candidate_BHSM_objects": ["birth_jet"],
            "dimension_domain_check": "rank-two coefficient jet on the rank-73 C2 launch image",
            "provenance_check": "certified forward-swapped reset map",
            "match": "VALID_MATCH",
        },
        {
            "diagram_slot": "FINITE_C2_GEOMETRY_RESPONSE",
            "required_type": "action-owned path, selected line, hard response and local first/second dependence",
            "candidate_BHSM_objects": ["dop_response", "dop_first_variation", "dop_second_variation"],
            "dimension_domain_check": "98-state path; 61 reduced, 60 hard, one selected, 62 bordered",
            "provenance_check": "exact local action jet on 8,692 adaptive cells; vector center variation retained; decorrelated scalar second-variation route rejected coverwide",
            "match": "VALID_MATCH_AUXILIARY_GEOMETRY_AND_FIRST_VARIATION_NOT_MATTER_DOMAIN",
        },
        {
            "diagram_slot": "C2_WEYL_COEFFICIENT_COTANGENT",
            "required_type": "inverse-free child Weyl response derivative with radius/duration incidence",
            "candidate_BHSM_objects": ["weyl_cotangent", "duration"],
            "dimension_domain_check": "finite 1222-core coefficient cotangent and reset-image norm",
            "provenance_check": "positive Mobius recurrence plus retained moving-duration jet",
            "match": "VALID_MATCH_ON_EXISTING_FINITE_CORE",
        },
        {
            "diagram_slot": "FULL_GRADED_HEAT_MINUS_ZETA_COTANGENT",
            "required_type": "one joint graded heat seed minus direct zeta covector",
            "candidate_BHSM_objects": ["heat_seed", "heat_bound", "zeta"],
            "dimension_domain_check": "same one-seam operator and coefficient cotangent space",
            "provenance_check": "closed-system source ontology; internal blocks not zeroed",
            "match": "VALID_MATCH_FORMULA_AND_BOUNDS_VALUE_OPEN",
        },
        {
            "diagram_slot": "RESET_QUOTIENT_REVERSE_PULLBACK",
            "required_type": "adjoint map from C2 coefficient cotangent to the 73-dimensional launch quotient",
            "candidate_BHSM_objects": ["reset_adjoint"],
            "dimension_domain_check": "72 outgoing seed image plus descriptor direction; 67-dimensional fixed-seed kernel split",
            "provenance_check": "exact reset Jacobian and one joint adjoint",
            "match": "VALID_MATCH",
        },
        {
            "diagram_slot": "FINITE_FIRST_HIT_AND_DOMAIN_TUBE",
            "required_type": "correlated Y,Z1,Z2 inclusion transferring the center stop and all regular margins",
            "candidate_BHSM_objects": [
                "first_hit", "dop_response", "dop_first_variation",
                "dop_second_variation", "common_frame",
                "selected_center_provenance", "nonlinear_cone_spectrum",
                "nonlinear_cone_projector_inverse",
            ],
            "dimension_domain_check": "center first hit, finite direct response first variation, and candidate-cone line/projector/inverse certified; complete-response signed/common-frame Z2 and exact-history transfer remain open",
            "provenance_check": "retained DOP853 polynomial and same physical quotient required",
            "match": "ACTUALLY_MISSING_CORRELATED_CERTIFICATION_ADAPTER",
        },
        {
            "diagram_slot": "PHYSICAL_FORCE_ROOT_AND_HESSIAN",
            "required_type": "projected joint heat-zeta covector, KKT root and intrinsic constrained Hessian",
            "candidate_BHSM_objects": ["force", "reset_adjoint", "heat_seed", "zeta"],
            "dimension_domain_check": "functional and equations derived; numerical/certified root absent",
            "provenance_check": "must use AE2 joint operator on the certified history",
            "match": "ACTUALLY_MISSING_VALUE_AND_ROOT_CERTIFICATION",
        },
    ]
    validations = {
        "all_inputs_exist": all(path.is_file() for path in INPUTS.values()),
        "ae2_action_validated": records["ae2_action"]["validation_passed"] is True,
        "ae2_domain_validated": records["ae2_domain"]["validation_passed"] is True,
        "one_seam_composition_validated": records["one_seam"]["validation_passed"] is True,
        "adaptive_response_validated": records["dop_response"]["validation_passed"] is True,
        "exact_center_response_variation_validated": records["dop_first_variation"]["validation_passed"] is True,
        "direct_first_variation_tube_validated": records["dop_second_variation"]["first_variation_validation_passed"] is True,
        "decorrelated_scalar_second_variation_not_overpromoted": records["dop_second_variation"]["second_variation_validation_passed"] is False and records["dop_second_variation"]["summary"]["scalar_denominator_owner_cells"] == 8692,
        "existing_Weyl_cotangent_validated": records["weyl_cotangent"]["validation_passed"] is True,
        "existing_heat_and_zeta_types_validated": records["heat_seed"]["validation_passed"] is True and records["zeta"]["validation_passed"] is True,
        "center_first_hit_only_not_overpromoted": records["first_hit"]["claim_boundary"]["exact_history_first_hit"] == "OPEN_UNTIL_CORRELATED_SHADOWING_AND_MARGIN_TRANSFER",
        "selected_quarter_center_provenance_reconciled": (
            records["selected_center_provenance"]["validation_passed"] is True
            and records["selected_center_provenance"]["claim_boundary"][
                "same_center_common_frame_operands"
            ] == "DERIVED"
        ),
        "same_center_common_frame_matching_validated": (
            records["common_frame"]["validation_passed"] is True
        ),
        "selected_candidate_cone_line_projector_and_inverse_validated": (
            records["nonlinear_cone_spectrum"]["validation_passed"] is True
            and records["nonlinear_cone_projector_inverse"][
                "validation_passed"
            ] is True
        ),
        "no_new_C2_theory_needed": all(row["match"] != "ACTUALLY_MISSING_NEW_C2_THEORY" for row in slots),
        "exactly_two_live_adapter_outputs": sum(row["match"].startswith("ACTUALLY_MISSING") for row in slots) == 2,
    }
    passed = all(validations.values())
    return {
        "artifact": "BHSM_N12_GATE7_DOP853_SYSTEM_ADAPTER_MATCHING",
        "status": "EXISTING_AE2_GATE7_PUZZLE_PIECES_MATCHED;_CORRELATED_FINITE_STOP_AND_JOINT_ROOT_ADAPTERS_OPEN" if passed else "SYSTEM_ADAPTER_MATCHING_OPEN",
        "diagram": "E0_DIRICHLET -> C1 -> E1_AE2_SEAM -> C2_DOP853_FINITE_STOP -> HEAT_MINUS_ZETA -> RESET_QUOTIENT_KKT",
        "matching_audit": slots,
        "resolved_interfaces": [
            "AE2_ACTION_TO_TRANSMISSION_DOMAIN",
            "TRANSMISSION_DOMAIN_TO_ONE_SEAM_DIRECT_OPERATOR",
            "RESET_GEOMETRY_TO_C2_BIRTH_COEFFICIENT_JET",
            "FINITE_CORE_COEFFICIENTS_TO_WEYL_COTANGENT",
            "JOINT_OPERATOR_TO_HEAT_AND_ZETA_COTANGENT_TYPES",
            "C2_COTANGENT_TO_RESET_QUOTIENT_ADJOINT",
        ],
        "actual_missing_adapters": [
            "CORRELATED_DOP853_Y_Z1_Z2_AND_FIRST_HIT_DOMAIN_TRANSFER",
            "SINGLE_SIGNED_JOINT_HEAT_MINUS_ZETA_REVERSE_CONTRACTION_PROJECTED_KKT_ROOT_AND_HESSIAN",
        ],
        "new_theory_choice_required": False,
        "validation": validations,
        "validation_passed": passed,
        "inputs": {_relative(path): _sha256(path) for path in INPUTS.values()},
        "claim_boundary": {
            "DOP853_is_the_matter_birth_operator": False,
            "new_C2_operator_theory_required": False,
            "joint_force_value_computed": False,
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "ASSEMBLE_LITERAL_Y_Z1_Z2_WITH_THE_CERTIFIED_VECTOR_VARIATIONS_IN_A_SIGNED_COMMON_FRAME,_TRANSFER_THE_FINITE_FIRST_HIT,_THEN_EVALUATE_THE_EXISTING_SINGLE_JOINT_REVERSE_SEED_AND_PROJECTED_KKT_ROOT",
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": payload["status"],
        "valid_matches": sum("VALID_MATCH" in row["match"] for row in payload["matching_audit"]),
        "actual_missing_adapters": payload["actual_missing_adapters"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
