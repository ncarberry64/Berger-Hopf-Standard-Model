"""Apply the second Hermite--Simpson block Newton correction."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import materialize_n12_gate7_hermite_simpson_newton_endpoint_candidate as endpoint  # noqa: E402

BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SECOND_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE.json"


def main() -> None:
    endpoint.CENTER = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE.json"
    endpoint.PREDICTOR = BASE / "BHSM_N12_GATE7_SECOND_HERMITE_SIMPSON_BLOCK_NEWTON_PREDICTOR.json"
    endpoint.THEORY = ROOT / "theory" / "n12_gate7_second_hermite_simpson_newton_endpoint_candidate.md"
    endpoint.RESULT = RESULT
    endpoint.DATA = RESULT.with_suffix(".npz")
    endpoint.THIS_SCRIPT = Path(__file__).resolve()
    endpoint.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_SECOND_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE"
    payload["status"] = "SECOND_HERMITE_SIMPSON_BLOCK_NEWTON_ENDPOINTS_MATERIALIZED"
    payload["exact_next_dependency"] = "EVALUATE_THE_EXACT_FIELD_AT_ALL_370_SECOND_ITERATION_COLLOCATION_MIDPOINTS"
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
