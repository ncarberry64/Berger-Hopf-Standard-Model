"""Rebuild the bordered response and exact fixed-s field at center 1215."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_bordered_hard_response_matrix as bordered  # noqa: E402
import audit_n12_c2_exact_center_fixed_s_field_matrix as field  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
PRIOR = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
PRIOR_DATA = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.npz"
CHART = BASE / "BHSM_N12_C2_LOHNER_RECENTER_1215.json"
GROWTH = BASE / "BHSM_N12_C2_LOHNER_GROWTH_1215.json"
ADAPTER = BASE / "BHSM_N12_C2_LOHNER_CENTER_1215_INPUT.json"
ADAPTER_DATA = BASE / "BHSM_N12_C2_LOHNER_CENTER_1215_INPUT.npz"
BORDERED_RESULT = BASE / "BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1215.json"
BORDERED_RESULT_DATA = BASE / "BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1215.npz"
FIELD_RESULT = BASE / "BHSM_N12_C2_LOHNER_FIXED_S_FIELD_1215.json"
FIELD_RESULT_DATA = BASE / "BHSM_N12_C2_LOHNER_FIXED_S_FIELD_1215.npz"
THEORY = ROOT / "theory" / "n12_c2_lohner_center_1215.md"


def main() -> None:
    inputs = (PRIOR, PRIOR_DATA, CHART, GROWTH, THEORY)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing Lohner center-1215 inputs: " + ", ".join(missing))
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    chart_record = json.loads(CHART.read_text(encoding="utf-8"))
    growth_record = json.loads(GROWTH.read_text(encoding="utf-8"))
    if not all(record["validation_passed"] for record in (
        prior, chart_record, growth_record,
    )):
        raise RuntimeError("validated segment, chart, and growth records required")
    with np.load(PRIOR_DATA) as data:
        center = np.asarray(data["endpoint_predictor_center"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    ADAPTER.write_text(json.dumps({
        "artifact": "BHSM_N12_C2_LOHNER_CENTER_1215_INPUT",
        "continuation": {
            "final_signed_lambda_decimal": prior["segment"]["signed_descriptor_end"],
            "final_endpoint_tube_radius_upper": prior["segment"]["endpoint_tube_radius_upper"],
            "rows": [{
                "hard_Gronwall_exponent_upper": 7.3985974666141106,
                "fixed_s_Jacobi_upper": 2.5646519250254787e24,
                "Delta_lower": prior["domain"]["Delta_interval"][0],
            }],
        },
        "validation_passed": True,
        "FULL_BHSM_COMPLETE": False,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    np.savez_compressed(
        ADAPTER_DATA,
        C2_second_uniform_gap_predictor_centers=np.asarray([center]),
        state_weights=weights,
        branch_reference=reference,
    )

    bordered.CONTINUATION = ADAPTER
    bordered.CONTINUATION_DATA = ADAPTER_DATA
    bordered.CHART = CHART
    bordered.GROWTH = GROWTH
    bordered.RESULT = BORDERED_RESULT
    bordered.DATA_RESULT = BORDERED_RESULT_DATA
    bordered.THEORY = THEORY
    bordered.INPUTS = (ADAPTER, ADAPTER_DATA, CHART, GROWTH, THEORY)
    bordered_payload = bordered.build_payload()
    bordered_payload["artifact"] = "BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1215"
    bordered_payload["status"] = (
        "C2_LOHNER_1215_BORDERED_HARD_RESPONSE_CENTER_MATRIX_CERTIFIED;_"
        "SECOND_VARIATION_REMAINDER_OPEN"
        if bordered_payload["validation_passed"] else "C2_LOHNER_BORDERED_MATRIX_1215_INVALID"
    )
    bordered_payload["exact_next_dependency"] = (
        "ASSEMBLE_THE_COMPLETE_FIXED_s_FIELD_AND_RELATIVE_TANGENT_TENSOR_AT_1215"
    )
    BORDERED_RESULT.write_text(
        json.dumps(bordered_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )

    field.BORDERED = BORDERED_RESULT
    field.BORDERED_DATA = BORDERED_RESULT_DATA
    field.CONTINUATION = ADAPTER
    field.GROWTH = GROWTH
    field.RESULT = FIELD_RESULT
    field.DATA_RESULT = FIELD_RESULT_DATA
    field.THEORY = THEORY
    field.INPUTS = (BORDERED_RESULT, BORDERED_RESULT_DATA, ADAPTER, GROWTH, THEORY)
    field_payload = field.build_payload()
    field_payload["artifact"] = "BHSM_N12_C2_LOHNER_FIXED_S_FIELD_1215"
    field_payload["status"] = (
        "C2_LOHNER_1215_CANCELLATION_PRESERVING_FIXED_s_CENTER_MATRIX_"
        "CERTIFIED;_CONJUGATED_INTERVAL_REMAINDER_OPEN"
        if field_payload["validation_passed"] else "C2_LOHNER_FIXED_s_FIELD_1215_INVALID"
    )
    field_payload["exact_next_dependency"] = (
        "CERTIFY_THE_1215_BORDERED_RESPONSE_AND_CANCELLED_FULL_FIELD_SECOND_"
        "VARIATION_BALL,_THEN_TAKE_THE_NEXT_MATRIX_LOHNER_STEP"
    )
    FIELD_RESULT.write_text(
        json.dumps(field_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "bordered_status": bordered_payload["status"],
        "field_status": field_payload["status"],
        "field_norm": field_payload["center_field"]["field_action_norm"],
        "Dlambda_field": field_payload["center_field"]["Dlambda_field"],
        "tangent_operator": field_payload["fixed_descriptor_matrix"]["partial_tangent_operator_2_norm"],
        "relative_self_consistency": field_payload["fixed_descriptor_matrix"][
            "relative_second_variation_self_consistency"
        ],
        "validation_passed": (
            bordered_payload["validation_passed"] and field_payload["validation_passed"]
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
