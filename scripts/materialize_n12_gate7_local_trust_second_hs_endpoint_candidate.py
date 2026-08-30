"""Apply the local-trust second Hermite--Simpson correction."""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import materialize_n12_gate7_damped_second_hs_newton_endpoint_candidate as endpoint  # noqa: E402
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_LOCAL_TRUST_SECOND_HS_ENDPOINT_CANDIDATE.json"


def main() -> None:
    endpoint.PREDICTOR = BASE / "BHSM_N12_GATE7_SECOND_HS_NEWTON_LOCAL_TRUST_PREDICTOR.json"
    endpoint.THEORY = ROOT / "theory" / "n12_gate7_local_trust_second_hs_endpoint_candidate.md"
    endpoint.RESULT = RESULT; endpoint.DATA = RESULT.with_suffix(".npz"); endpoint.THIS_SCRIPT = Path(__file__).resolve()
    endpoint.main()
    p = json.loads(RESULT.read_text(encoding="utf-8")); p["artifact"] = "BHSM_N12_GATE7_LOCAL_TRUST_SECOND_HS_ENDPOINT_CANDIDATE"; p["status"] = "LOCAL_TRUST_SECOND_HS_ENDPOINTS_MATERIALIZED"; p["exact_next_dependency"] = "REPLAY_ALL_370_LOCAL_TRUST_COLLOCATION_MIDPOINTS"
    RESULT.write_text(json.dumps(p, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__": main()
