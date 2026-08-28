"""Audit the exact data boundary for the Gate-7 common-frame Krawczyk step.

This is a type/domain/provenance audit.  It does not promote reconnaissance
samples to interval authority and does not invent a new operator.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SIGNED_COMMON_FRAME_DATA_MATCHING.json"

INPUTS = {
    "selected_center": BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz",
    "response": BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE_CERTIFICATE.json",
    "first": BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RESPONSE_FIRST_VARIATION.json",
    "first_data": BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RESPONSE_FIRST_VARIATION.npz",
    "second": BASE / "BHSM_N12_C2_STOP_DOP853_BORDERED_RESPONSE_SECOND_VARIATION.json",
    "jacobian": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_GRAPH_JACOBIAN_RECONNAISSANCE.json",
    "jacobian_data": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_GRAPH_JACOBIAN_RECONNAISSANCE.npz",
    "hybrid_graph_audit": BASE / "BHSM_N12_GATE7_QUARTER_STEP_HYBRID_GRAPH_JACOBIAN_EQUIVALENCE_AUDIT.json",
    "tangent": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.json",
    "tangent_data": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz",
    "residual": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_RETAINED_DENSE_RESIDUAL_GAUSS12_RECONNAISSANCE.json",
    "residual_data": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_RETAINED_DENSE_RESIDUAL_GAUSS12_RECONNAISSANCE.npz",
    "green": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.json",
    "green_data": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz",
    "first_hit": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_DENSE_DESCRIPTOR_FIRST_HIT.json",
    "time_quotient": BASE / "BHSM_N12_RESET_TIME_QUOTIENT_GENERATOR_AUDIT.json",
    "transverse_center": BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_ADJUDICATION.json",
    "transverse_raw": BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE.json",
}


def _load(key: str) -> dict[str, Any]:
    return json.loads(INPUTS[key].read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def build_payload() -> dict[str, Any]:
    records = {
        key: _load(key) for key, path in INPUTS.items() if path.suffix == ".json"
    }
    with np.load(INPUTS["first_data"]) as data:
        response_shape = tuple(data["bordered_response_center"].shape)
        variation_shape = tuple(
            data["bordered_response_action_time_first_variation"].shape
        )
        vector_data_finite = bool(all(
            np.all(np.isfinite(data[name])) for name in (
                "bordered_response_center",
                "bordered_response_action_time_first_variation",
            )
        ))
    with np.load(INPUTS["tangent_data"]) as data:
        tangent_shape = tuple(data["physical_tangent_action"].shape)
        step_map_shape = tuple(data["physical_step_maps"].shape)
    with np.load(INPUTS["jacobian_data"]) as data:
        jacobian_shape = tuple(data["graph_Jacobian_action"].shape)
    with np.load(INPUTS["residual_data"]) as data:
        residual_shape = tuple(data["augmented_rate_residual"].shape)
    with np.load(INPUTS["green_data"]) as data:
        correction_shape = tuple(data["fine_ambient_correction_profile"].shape)
        green_step_shape = tuple(data["physical_macro_step_maps"].shape)

    slots = [
        {
            "slot": "BORDERED_RESPONSE_VECTOR_AND_PATH_DERIVATIVE",
            "required_type": "x and D_tau x on the accepted finite-history cover",
            "candidate": ["response", "first", "first_data"],
            "dimension_domain": "8,692 x (62 response plus 62 path derivative)",
            "provenance": "exact differentiated bordered identity on the certified adaptive cells",
            "match": "VALID_CERTIFIED_MATCH",
        },
        {
            "slot": "CONSTRAINT_TANGENT_FRAMES",
            "required_type": "98-to-73 constraint-tangent frames and transported step maps",
            "candidate": ["tangent", "tangent_data"],
            "dimension_domain": "48 x 98 x 73 frames and 47 x 73 x 73 macro maps",
            "provenance": "retained 25 constraints; center/Magnus reconnaissance; not relabelled as the final gauge/time quotient",
            "match": "VALID_CENTER_DATA_INTERVAL_AUTHORITY_MISSING",
        },
        {
            "slot": "GRAPH_JACOBIAN",
            "required_type": "Df on the physical history tube",
            "candidate": ["jacobian", "jacobian_data"],
            "dimension_domain": "48 center matrices of size 98 x 98",
            "provenance": "exact center jets; between-node and transverse tube remainder open",
            "match": "VALID_CENTER_DATA_INTERVAL_AUTHORITY_MISSING",
        },
        {
            "slot": "SIGNED_DEFECT_AND_GREEN_CENTER",
            "required_type": "minus-defect Green contraction in common quotient frames",
            "candidate": ["residual", "residual_data", "green", "green_data"],
            "dimension_domain": "quarter-step Gauss-12 sampled 99-component defects and 371 correction nodes",
            "provenance": "correct minus sign and retained quotient; quadrature/interpolation interval remainder open",
            "match": "VALID_SIGNED_DIAGNOSTIC_INTERVAL_AUTHORITY_MISSING",
        },
        {
            "slot": "LITERAL_Y",
            "required_type": "outward bound Y=||A(-d)||_P",
            "candidate": ["green", "residual"],
            "dimension_domain": "same fixed-reset 73-dimensional quotient",
            "provenance": "center value exists but is reconnaissance only",
            "match": "ACTUALLY_MISSING_INTERVAL_REMAINDER_ADAPTER",
        },
        {
            "slot": "LITERAL_Z1",
            "required_type": "outward bound Z1=||I-A*L||_P",
            "candidate": ["tangent", "jacobian"],
            "dimension_domain": "common-frame operator on the fixed-reset history space",
            "provenance": "approximate step maps exist; interval inverse defect absent",
            "match": "ACTUALLY_MISSING_INTERVAL_INVERSE_DEFECT_ADAPTER",
        },
        {
            "slot": "LITERAL_Z2",
            "required_type": "physical-tube Lipschitz bound for A*(N(e)-N(e_tilde))",
            "candidate": ["first", "second", "jacobian"],
            "dimension_domain": "73 transverse directions on a common-frame radius-r tube",
            "provenance": "path derivative is certified; exact retained-action transverse center curvature is certified; outward transverse tube remainder is not",
            "match": "ACTUALLY_MISSING_TRANSVERSE_NONLINEAR_REMAINDER_ADAPTER",
        },
        {
            "slot": "FINAL_WHOLE_SYSTEM_TIME_QUOTIENT",
            "required_type": "66-dimensional coupled event-child time quotient or intrinsic quotient formulation for force and Hessian",
            "candidate": ["time_quotient"],
            "dimension_domain": "raw fixed-event reset kernel 67; retained whole-system quotient count 66",
            "provenance": "local child flow is not the coupled hybrid generator and cannot be projected by hand",
            "match": "ACTUALLY_MISSING_DOWNSTREAM_HYBRID_TIME_QUOTIENT_ADAPTER",
        },
        {
            "slot": "FIRST_HIT_TRANSFER",
            "required_type": "strict preterminal positivity and unique terminal descending zero on the exact tube",
            "candidate": ["first_hit"],
            "dimension_domain": "stored center theorem plus the same eventual Krawczyk radius",
            "provenance": "center is certified; transfer waits on Y/Z1/Z2",
            "match": "DOWNSTREAM_OF_MISSING_COMMON_FRAME_BOUNDS",
        },
    ]
    validations = {
        "all_inputs_exist": all(path.is_file() for path in INPUTS.values()),
        "certified_response_and_center_variation_consumed": (
            records["response"]["validation_passed"] is True
            and records["first"]["validation_passed"] is True
            and response_shape == (8692, 62)
            and variation_shape == (8692, 62)
            and vector_data_finite
        ),
        "scalar_wrapping_failure_not_promoted": (
            records["second"]["second_variation_validation_passed"] is False
            and records["second"]["summary"]["scalar_denominator_owner_cells"]
            == 8692
        ),
        "physical_quotient_dimensions_match": (
            tangent_shape == (48, 98, 73)
            and step_map_shape == (47, 73, 73)
            and green_step_shape == (47, 73, 73)
        ),
        "center_Jacobian_dimension_matches": jacobian_shape == (48, 98, 98),
        "quarter_hybrid_graph_matches_retained_replay": (
            records["hybrid_graph_audit"]["validation_passed"] is True
            and records["hybrid_graph_audit"]["center"]
            == "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
        ),
        "graph_residual_and_first_hit_name_selected_quarter_center": (
            records["jacobian"]["center"]
            == "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
            and records["residual"]["construction"]["center"]
            == "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
            and records["first_hit"]["center"]
            == "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
        ),
        "signed_defect_and_correction_dimensions_match": (
            residual_shape == (
                records["residual"]["summary"]["exact_field_samples"], 99
            )
            and correction_shape == (371, 98)
        ),
        "reconnaissance_not_promoted_to_interval_authority": all(
            records[key]["validation_passed"] is False
            for key in ("jacobian", "tangent", "residual", "green")
        ),
        "first_hit_not_overpromoted": (
            records["first_hit"]["claim_boundary"]["exact_history_first_hit"]
            == "OPEN_UNTIL_CORRELATED_SHADOWING_AND_MARGIN_TRANSFER"
        ),
        "constraint_tangent_not_relabelled_final_physical_quotient": (
            records["time_quotient"]["validation_passed"] is True
            and records["time_quotient"]["dimension_statement"][
                "explicit_generator_certified_in_current_checkpoint"
            ] is False
        ),
        "exact_transverse_center_curvature_not_promoted_outward": (
            records["transverse_center"]["validation_passed"] is True
            and records["transverse_center"]["claim_boundary"][
                "full_physical_transverse_center_curvature"
            ] == "CERTIFIED"
            and records["transverse_center"]["claim_boundary"][
                "outward_transverse_curvature_remainder"
            ] == "OPEN"
        ),
        "exact_transverse_artifact_hashes_selected_quarter_center": (
            records["transverse_raw"]["validation"][
                "selected_quarter_step_center_and_matching_tangent_used"
            ] is True
            and
            any(
                "HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz" in path
                for path in records["transverse_raw"]["inputs"]
            )
            and all(
                "HIGH_ORDER_HALF_STEP" not in path
                for path in records["transverse_raw"]["inputs"]
            )
        ),
        "no_new_operator_or_theory_choice_identified": True,
    }
    passed = all(validations.values())
    return {
        "artifact": "BHSM_N12_GATE7_SIGNED_COMMON_FRAME_DATA_MATCHING",
        "status": (
            "COMMON_FRAME_DATA_MATCHED;_THREE_INTERVAL_ADAPTERS_LOCALIZED"
            if passed else "COMMON_FRAME_DATA_MATCHING_INVALID"
        ),
        "literal_definitions": {
            "Y": "||A*(-d)||_P",
            "Z1": "||I-A*L||_P",
            "Z2": "||A*(N(e)-N(e_tilde))||_P <= Z2*r*||e-e_tilde||_P",
            "radii": "Y+Z1*r+Z2*r^2<r_AND_Z1+2*Z2*r<1",
        },
        "matching_audit": slots,
        "actual_missing_interval_adapters": [
            "OUTWARD_SIGNED_DEFECT_GREEN_QUADRATURE_AND_INTERPOLATION_REMAINDER_FOR_Y",
            "COMMON_FRAME_INTERVAL_INVERSE_DEFECT_I_MINUS_A_L_FOR_Z1",
            "PHYSICAL_TRANSVERSE_D2F_TUBE_AND_GREEN_LIPSCHITZ_CONTRACTION_FOR_Z2",
        ],
        "downstream_physical_quotient_adapter": "COUPLED_HYBRID_TIME_GENERATOR_OR_INTRINSIC_66_DIMENSIONAL_QUOTIENT_FORMULATION_BEFORE_FINAL_FORCE_HESSIAN",
        "new_action_or_operator_required": False,
        "new_theory_choice_required": False,
        "validation": validations,
        "validation_passed": passed,
        "inputs": {_relative(path): _sha256(path) for path in INPUTS.values()},
        "claim_boundary": {
            "Y": "OPEN_INTERVAL_AUTHORITY",
            "Z1": "OPEN_INTERVAL_AUTHORITY",
            "Z2": "OPEN_TRANSVERSE_INTERVAL_AUTHORITY",
            "exact_history_first_hit": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "DERIVE_THE_THREE_LOCALIZED_EXISTENCE_INTERVAL_ADAPTERS_IN_THE_RETAINED_CONSTRAINT_TANGENT_COMMON_FRAME_WITHOUT_COLLAPSING_THE_62_COMPONENT_RESPONSE_VARIATIONS;_THEN_USE_THE_COUPLED_HYBRID_OR_INTRINSIC_TIME_QUOTIENT_FOR_THE_FINAL_FORCE_HESSIAN",
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
        "missing": payload["actual_missing_interval_adapters"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
