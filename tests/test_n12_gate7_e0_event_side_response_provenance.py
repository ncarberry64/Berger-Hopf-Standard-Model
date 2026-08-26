from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_n12_gate7_e0_event_side_response_provenance.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_E0_EVENT_SIDE_RESPONSE_PROVENANCE_AUDIT.json"
)


def _run() -> bytes:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return RESULT.read_bytes()


def test_e0_event_side_response_provenance() -> None:
    payload = json.loads(_run())
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "E0_EVENT_SIDE_PROVENANCE_EXHAUSTED_REALIZED_PARENT_ARM_OPEN"
    )
    verdicts = {
        row["candidate"]: row["verdict"]
        for row in payload["candidate_matching_audit"]
    }
    assert verdicts["BHSM_N12_POSITIVE_DURATION_CALDERON_HISTORY"].endswith(
        "LOCAL_COEFFICIENT_COLLAR_ONLY"
    )
    assert verdicts["BHSM_N12_EVENT_NORMAL_WEYL_RICCATI"].endswith(
        "INVALID_AS_REALIZED_M_E0_VALUE"
    )
    assert verdicts["BHSM_N12_C2_1222_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY"] == (
        "INVALID_HISTORY_AND_ORIENTATION_MATCH"
    )
    assert payload["adjudication"]["new_operator_theory_required"] is False
    assert payload["adjudication"]["M_E0_and_first_jet"] == (
        "WAITING_ON_PARENT_REALIZATION"
    )
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_e0_event_side_response_provenance_is_deterministic() -> None:
    first = hashlib.sha256(_run()).hexdigest()
    second = hashlib.sha256(_run()).hexdigest()
    assert first == second
