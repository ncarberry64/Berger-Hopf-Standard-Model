"""Replay the local-trust second Hermite--Simpson midpoint residual."""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_n12_gate7_second_hermite_simpson_newton_midpoint_replay as replay  # noqa: E402
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_LOCAL_TRUST_SECOND_HS_MIDPOINT_REPLAY.json"


def main() -> None:
    replay.ENDPOINT = BASE / "BHSM_N12_GATE7_LOCAL_TRUST_SECOND_HS_ENDPOINT_CANDIDATE.json"
    replay.THEORY = ROOT / "theory" / "n12_gate7_local_trust_second_hs_midpoint_replay.md"
    replay.RESULT = RESULT; replay.DATA = RESULT.with_suffix(".npz"); replay.THIS_SCRIPT = Path(__file__).resolve()
    replay.main()
    p = json.loads(RESULT.read_text(encoding="utf-8")); p["artifact"] = "BHSM_N12_GATE7_LOCAL_TRUST_SECOND_HS_MIDPOINT_REPLAY"; p["status"] = "LOCAL_TRUST_SECOND_HS_RESIDUAL_REDUCED" if p["validation_passed"] else "LOCAL_TRUST_SECOND_HS_RESIDUAL_NOT_REDUCED"; p["exact_next_dependency"] = "IF_REDUCED,_CONTINUE_TRUST_REGION_BLOCK_NEWTON;_OTHERWISE_REPLACE_THE_STORED_GRAPH_DIRECTION_WITH_AN_EXACT_PROJECTED_RESIDUAL_DIRECTIONAL"
    RESULT.write_text(json.dumps(p, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__": main()
