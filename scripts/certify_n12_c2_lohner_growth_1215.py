"""Transfer fixed-s growth bounds to the segment-1215 recenter."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_c2_fresh_chart_fixed_s_growth as growth  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
SEGMENT = int(os.environ.get("BHSM_N12_C2_LOHNER_SEGMENT", "1215"))
CHART = BASE / f"BHSM_N12_C2_LOHNER_RECENTER_{SEGMENT}.json"
CHART_DATA = BASE / f"BHSM_N12_C2_LOHNER_RECENTER_{SEGMENT}.npz"
CONTINUATION = BASE / f"BHSM_N12_C2_LOHNER_RECENTER_{SEGMENT}_INPUT.json"
RESULT = BASE / f"BHSM_N12_C2_LOHNER_GROWTH_{SEGMENT}.json"
THEORY = ROOT / "theory" / "n12_c2_lohner_growth_1215.md"


def main() -> None:
    inputs = (CHART, CHART_DATA, CONTINUATION, THEORY)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing 1215 growth inputs: " + ", ".join(missing))
    growth.CHART = CHART
    growth.CHART_DATA = CHART_DATA
    growth.CONTINUATION = CONTINUATION
    growth.RESULT = RESULT
    growth.THEORY = THEORY
    growth.INPUTS = inputs
    payload = growth.build_payload()
    payload["artifact"] = f"BHSM_N12_C2_LOHNER_GROWTH_{SEGMENT}"
    payload["status"] = (
        f"C2_LOHNER_SEGMENT_{SEGMENT}_FIXED_s_GROWTH_CERTIFIED"
        if payload["validation_passed"] else f"C2_LOHNER_GROWTH_{SEGMENT}_INVALID"
    )
    payload["exact_next_dependency"] = (
        "ASSEMBLE_THE_1215_BORDERED_RESPONSE,_EXACT_FIXED_s_FIELD_MATRIX,_"
        "AND_RELATIVE_TANGENT_TENSOR"
    )
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "radius": payload["radius_derivation"]["selected_growth_chart_radius"],
        "c_lower": payload["moving_cubic"]["ball_value_lower"],
        "birth_second": payload["birth_limit_generator"]["D2F0_action_operator_upper"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
