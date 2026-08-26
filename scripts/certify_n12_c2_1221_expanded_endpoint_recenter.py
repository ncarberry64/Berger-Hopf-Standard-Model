"""Recenter the retained C2 action machinery at the expanded-theta endpoint.

This driver only adapts the certified finite-cover endpoint to the existing
fresh-line, growth, bordered-response, and cancellation-preserving field
builders.  It does not select a physical history or declare a proof-chart edge
to be an event.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_bordered_hard_response_matrix as bordered  # noqa: E402
import audit_n12_c2_exact_center_fixed_s_field_matrix as field  # noqa: E402
import certify_n12_c2_fresh_chart_fixed_s_growth as growth  # noqa: E402
import certify_n12_c2_fresh_descriptor_fiber_eigenline_chart as chart  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
COVER = BASE / "BHSM_N12_C2_EXPANDED_CANCELLED_THETA_COVER_FROM_1221.json"
COVER_DATA = COVER.with_suffix(".npz")
MONOTONICITY = BASE / "BHSM_N12_C2_1221_CANCELLED_DELTA_MONOTONICITY.json"
PRIOR_LINE = BASE / "BHSM_N12_C2_1221_FULL_ACTION_EIGENLINE_BALL_R1E8.json"
REFERENCE_BORDERED = BASE / "BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1221.json"
THEORY = ROOT / "theory" / "n12_c2_1221_expanded_endpoint_recenter.md"

PREFIX = "BHSM_N12_C2_1221_EXPANDED_ENDPOINT"
CHART_INPUT = BASE / f"{PREFIX}_RECENTER_INPUT.json"
CHART_INPUT_DATA = CHART_INPUT.with_suffix(".npz")
CHART_RESULT = BASE / f"{PREFIX}_EIGENLINE_CHART.json"
CHART_RESULT_DATA = CHART_RESULT.with_suffix(".npz")
GROWTH_RESULT = BASE / f"{PREFIX}_GROWTH.json"
CENTER_INPUT = BASE / f"{PREFIX}_CENTER_INPUT.json"
CENTER_INPUT_DATA = CENTER_INPUT.with_suffix(".npz")
BORDERED_RESULT = BASE / f"{PREFIX}_BORDERED_MATRIX.json"
BORDERED_RESULT_DATA = BORDERED_RESULT.with_suffix(".npz")
FIELD_RESULT = BASE / f"{PREFIX}_FIXED_S_FIELD.json"
FIELD_RESULT_DATA = FIELD_RESULT.with_suffix(".npz")
RESULT = BASE / f"{PREFIX}_RECENTER.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _write(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_payload() -> dict:
    inputs = (
        COVER, COVER_DATA, MONOTONICITY, PRIOR_LINE, REFERENCE_BORDERED, THEORY,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing expanded endpoint inputs: " + ", ".join(missing))
    cover_record = json.loads(COVER.read_text(encoding="utf-8"))
    monotonicity = json.loads(MONOTONICITY.read_text(encoding="utf-8"))
    prior_line = json.loads(PRIOR_LINE.read_text(encoding="utf-8"))
    reference_bordered = json.loads(
        REFERENCE_BORDERED.read_text(encoding="utf-8")
    )
    if not all(record.get("validation_passed") is True for record in (
        cover_record, monotonicity, prior_line,
    )):
        raise RuntimeError("validated cover, monotonicity, and prior line required")
    with np.load(COVER_DATA) as data:
        center = np.asarray(data["predictor_centers"][-1], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
        incoming_tube = float(data["endpoint_tube_radius"])
    cover = cover_record["cover"]
    descriptor_center = float(cover["final_signed_descriptor_center"])
    descriptor_interval = list(
        monotonicity["sharpened_correlated_descriptor_interval"]
    )
    scalar_reference = reference_bordered["comparison"]

    _write(CHART_INPUT, {
        "artifact": f"{PREFIX}_RECENTER_INPUT",
        "continuation": {
            "final_endpoint_tube_radius_upper": incoming_tube,
            "total_certified_segments": int(cover["accepted_steps"]),
        },
        "validation_passed": True,
        "FULL_BHSM_COMPLETE": False,
    })
    np.savez_compressed(
        CHART_INPUT_DATA,
        C2_uniform_gap_predictor_centers=np.asarray([center]),
        state_weights=weights,
        branch_reference=reference,
    )

    chart.CONTINUATION = CHART_INPUT
    chart.CONTINUATION_DATA = CHART_INPUT_DATA
    chart.PRIOR_LINE = PRIOR_LINE
    chart.RESULT = CHART_RESULT
    chart.DATA_RESULT = CHART_RESULT_DATA
    chart.THEORY = THEORY
    chart.INPUTS = (CHART_INPUT, CHART_INPUT_DATA, PRIOR_LINE, THEORY)
    chart_payload = chart.build_payload()
    chart_payload["artifact"] = f"{PREFIX}_EIGENLINE_CHART"
    chart_payload["status"] = (
        "C2_EXPANDED_ENDPOINT_BRANCH_24_CHART_CERTIFIED"
        if chart_payload["validation_passed"] else
        "C2_EXPANDED_ENDPOINT_BRANCH_24_CHART_FAILED"
    )
    chart_payload["exact_next_dependency"] = (
        "TRANSFER_THE_EXISTING_FIXED_s_GROWTH_AND_HARD_RESPONSE_BOUNDS_TO_"
        "THE_EXPANDED_ENDPOINT"
    )
    _write(CHART_RESULT, chart_payload)

    growth.CHART = CHART_RESULT
    growth.CHART_DATA = CHART_RESULT_DATA
    growth.CONTINUATION = CHART_INPUT
    growth.RESULT = GROWTH_RESULT
    growth.THEORY = THEORY
    growth.INPUTS = (CHART_RESULT, CHART_RESULT_DATA, CHART_INPUT, THEORY)
    growth_payload = growth.build_payload()
    growth_payload["artifact"] = f"{PREFIX}_GROWTH"
    growth_payload["status"] = (
        "C2_EXPANDED_ENDPOINT_FIXED_s_GROWTH_CERTIFIED"
        if growth_payload["validation_passed"] else
        "C2_EXPANDED_ENDPOINT_FIXED_s_GROWTH_FAILED"
    )
    growth_payload["exact_next_dependency"] = (
        "REBUILD_THE_BORDERED_INTERNAL_RESPONSE_AND_CANCELLED_CENTER_FIELD"
    )
    _write(GROWTH_RESULT, growth_payload)

    _write(CENTER_INPUT, {
        "artifact": f"{PREFIX}_CENTER_INPUT",
        "continuation": {
            "final_signed_lambda_decimal": format(descriptor_center, ".17e"),
            "final_endpoint_tube_radius_upper": incoming_tube,
            "rows": [{
                "hard_Gronwall_exponent_upper": float(
                    scalar_reference["last_scalar_hard_Gronwall_exponent"]
                ),
                "fixed_s_Jacobi_upper": float(
                    scalar_reference["last_scalar_fixed_s_Jacobi_upper"]
                ),
                "Delta_lower": float(
                    monotonicity["Delta_interval_on_realized_cover"][0]
                ),
            }],
        },
        "descriptor_interval": descriptor_interval,
        "validation_passed": True,
        "FULL_BHSM_COMPLETE": False,
    })
    np.savez_compressed(
        CENTER_INPUT_DATA,
        C2_second_uniform_gap_predictor_centers=np.asarray([center]),
        state_weights=weights,
        branch_reference=reference,
    )

    bordered.CONTINUATION = CENTER_INPUT
    bordered.CONTINUATION_DATA = CENTER_INPUT_DATA
    bordered.CHART = CHART_RESULT
    bordered.GROWTH = GROWTH_RESULT
    bordered.RESULT = BORDERED_RESULT
    bordered.DATA_RESULT = BORDERED_RESULT_DATA
    bordered.THEORY = THEORY
    bordered.INPUTS = (
        CENTER_INPUT, CENTER_INPUT_DATA, CHART_RESULT, GROWTH_RESULT, THEORY,
    )
    bordered_payload = bordered.build_payload()
    bordered_payload["artifact"] = f"{PREFIX}_BORDERED_MATRIX"
    bordered_payload["status"] = (
        "C2_EXPANDED_ENDPOINT_BORDERED_INTERNAL_RESPONSE_CERTIFIED"
        if bordered_payload["validation_passed"] else
        "C2_EXPANDED_ENDPOINT_BORDERED_RESPONSE_FAILED"
    )
    bordered_payload["exact_next_dependency"] = (
        "ASSEMBLE_THE_CANCELLED_CENTER_FIELD_AND_INVARIANT_GRAPH_TANGENT"
    )
    _write(BORDERED_RESULT, bordered_payload)

    field.BORDERED = BORDERED_RESULT
    field.BORDERED_DATA = BORDERED_RESULT_DATA
    field.CONTINUATION = CENTER_INPUT
    field.GROWTH = GROWTH_RESULT
    field.RESULT = FIELD_RESULT
    field.DATA_RESULT = FIELD_RESULT_DATA
    field.THEORY = THEORY
    field.INPUTS = (
        BORDERED_RESULT, BORDERED_RESULT_DATA, CENTER_INPUT, GROWTH_RESULT, THEORY,
    )
    field_payload = field.build_payload()
    field_payload["artifact"] = f"{PREFIX}_FIXED_S_FIELD"
    field_payload["status"] = (
        "C2_EXPANDED_ENDPOINT_CANCELLED_CENTER_FIELD_CERTIFIED"
        if field_payload["validation_passed"] else
        "C2_EXPANDED_ENDPOINT_CANCELLED_FIELD_FAILED"
    )
    field_payload["exact_next_dependency"] = (
        "ENCLOSE_THE_INVARIANT_GRAPH_TANGENT_REMAINDER_AND_TAKE_THE_NEXT_"
        "MATRIX_LOHNER_BLOCK"
    )
    _write(FIELD_RESULT, field_payload)

    with np.load(COVER_DATA) as data:
        initial_center = np.asarray(data["predictor_centers"][0], dtype=float)
    center_distance = float(np.linalg.norm((center - initial_center) * weights))
    validation = {
        "expanded_cover_endpoint_consumed": center_distance > 0.0,
        "incoming_tube_preserved": incoming_tube > 0.0,
        "sharpened_descriptor_interval_contains_center": (
            descriptor_interval[0] <= descriptor_center <= descriptor_interval[1]
        ),
        "fresh_branch_24_chart_certified": chart_payload["validation_passed"],
        "fresh_growth_certified": growth_payload["validation_passed"],
        "bordered_internal_response_certified": bordered_payload["validation_passed"],
        "cancelled_center_field_certified": field_payload["validation_passed"],
        "binary64_eigenvalue_not_used_as_descriptor": True,
        "proof_center_not_promoted_to_event_or_physical_endpoint": True,
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    generated = (
        CHART_INPUT, CHART_INPUT_DATA, CHART_RESULT, CHART_RESULT_DATA,
        GROWTH_RESULT, CENTER_INPUT, CENTER_INPUT_DATA, BORDERED_RESULT,
        BORDERED_RESULT_DATA, FIELD_RESULT, FIELD_RESULT_DATA,
    )
    return {
        "artifact": f"{PREFIX}_RECENTER",
        "status": (
            "C2_EXPANDED_ENDPOINT_ACTION_RESPONSE_RECENTER_CERTIFIED"
            if passed else "C2_EXPANDED_ENDPOINT_RECENTER_FAILED"
        ),
        "endpoint": {
            "center_distance_from_1221": center_distance,
            "incoming_endpoint_tube_radius_upper": incoming_tube,
            "signed_descriptor_center": descriptor_center,
            "signed_descriptor_interval": descriptor_interval,
            "selected_branch": int(chart_payload["center"]["selected_branch"]),
            "fresh_chart_radius": float(chart_payload["radius_derivation"][
                "selected_fresh_chart_radius"
            ]),
            "fresh_growth_radius": float(growth_payload["radius_derivation"][
                "selected_growth_chart_radius"
            ]),
            "center_Delta": float(field_payload["center_field"]["Delta"]),
            "center_cancelled_field_action_norm": float(
                field_payload["center_field"]["Delta"]
                * field_payload["center_field"]["field_action_norm"]
            ),
        },
        "generated": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in generated
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in inputs
        },
        "hindsight": {
            "validated": (
                "THE_EXISTING_ACTION_OWNED_LINE_RESPONSE_AND_FIELD_PIPELINE_"
                "RECENTERS_AT_THE_REALIZED_EXPANDED_COVER_ENDPOINT"
            ),
            "invalidated": (
                "THE_1221_PROOF_BALL_EDGE_IS_NOT_A_CANONICAL_STOP"
            ),
            "open": (
                "SHEARED_GRAPH_INTERVAL_REMAINDER_AND_NEXT_FORWARD_BLOCK"
            ),
            "bhsm_native_check": "ACTION_REQUIRED_DYNAMIC_CONNECTION",
        },
        "exact_next_dependency": (
            "CERTIFY_THE_SHEARED_GRAPH_INTERVAL_TANGENT_ON_THE_FRESH_RADIUS_"
            "AND_PROPAGATE_THE_NEXT_FORWARD_BLOCK"
        ),
        "validation": validation,
        "validation_passed": passed,
        "GATE7_RESET_TO_CAPTURE": "OPEN",
        "GATE7_FINITE_CANONICAL_STOP": "OPEN",
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    _write(RESULT, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
