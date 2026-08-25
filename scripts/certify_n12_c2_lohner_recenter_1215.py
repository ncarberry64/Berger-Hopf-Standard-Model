"""Recenter the branch-24 descriptor chart at Lohner segment 1215."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_c2_fresh_descriptor_fiber_eigenline_chart as chart  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
PRIOR = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
PRIOR_DATA = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.npz"
ADAPTER = BASE / "BHSM_N12_C2_LOHNER_RECENTER_1215_INPUT.json"
ADAPTER_DATA = BASE / "BHSM_N12_C2_LOHNER_RECENTER_1215_INPUT.npz"
PRIOR_LINE = BASE / "BHSM_N12_C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART.json"
RESULT = BASE / "BHSM_N12_C2_LOHNER_RECENTER_1215.json"
DATA_RESULT = BASE / "BHSM_N12_C2_LOHNER_RECENTER_1215.npz"
THEORY = ROOT / "theory" / "n12_c2_lohner_recenter_1215.md"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def main() -> None:
    inputs = (PRIOR, PRIOR_DATA, PRIOR_LINE, THEORY)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing 1215 recenter inputs: " + ", ".join(missing))
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    prior_line = json.loads(PRIOR_LINE.read_text(encoding="utf-8"))
    if not prior["validation_passed"] or not prior_line["validation_passed"]:
        raise RuntimeError("validated Lohner segment and prior line required")
    with np.load(PRIOR_DATA) as data:
        center = np.asarray(data["endpoint_predictor_center"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    ADAPTER.write_text(json.dumps({
        "artifact": "BHSM_N12_C2_LOHNER_RECENTER_1215_INPUT",
        "continuation": {
            "final_endpoint_tube_radius_upper": prior["segment"]["endpoint_tube_radius_upper"],
            "total_certified_segments": prior["segment"]["total_certified_segments"],
        },
        "validation_passed": True,
        "FULL_BHSM_COMPLETE": False,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    np.savez_compressed(
        ADAPTER_DATA,
        C2_uniform_gap_predictor_centers=np.asarray([center]),
        state_weights=weights,
        branch_reference=reference,
    )
    chart.CONTINUATION = ADAPTER
    chart.CONTINUATION_DATA = ADAPTER_DATA
    chart.PRIOR_LINE = PRIOR_LINE
    chart.RESULT = RESULT
    chart.DATA_RESULT = DATA_RESULT
    chart.THEORY = THEORY
    chart.INPUTS = (ADAPTER, ADAPTER_DATA, PRIOR_LINE, THEORY)
    payload = chart.build_payload()
    payload["artifact"] = "BHSM_N12_C2_LOHNER_RECENTER_1215"
    payload["status"] = (
        "C2_LOHNER_SEGMENT_1215_FRESH_DESCRIPTOR_FIBER_CHART_CERTIFIED"
        if payload["validation_passed"] else "C2_LOHNER_RECENTER_1215_INVALID"
    )
    validation = payload["validation"]
    validation["incoming_1215_endpoint_tube_consumed"] = validation.pop(
        "incoming_1192_endpoint_tube_consumed"
    )
    payload["exact_next_dependency"] = (
        "REBUILD_THE_BORDERED_RESPONSE_AND_CANCELLED_FIXED_s_FIELD_AT_THE_"
        "1215_PREDICTOR_AND_ITERATE_THE_MATRIX_LOHNER_STEP"
    )
    payload["recenter_provenance"] = {
        "prior_segment": 1215,
        "prior_result_SHA256": _sha256(PRIOR),
        "prior_data_SHA256": _sha256(PRIOR_DATA),
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    radius = payload["radius_derivation"]
    print(json.dumps({
        "status": payload["status"],
        "incoming_tube": radius["incoming_endpoint_tube_upper"],
        "selected_radius": radius["selected_fresh_chart_radius"],
        "fresh_gap": radius["selected_chart_bounds"]["eigenline_gap_lower"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
