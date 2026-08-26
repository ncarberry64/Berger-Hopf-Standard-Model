from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_n12_gate7_maximal_graded_cotangent_matching.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_MAXIMAL_GRADED_COTANGENT_MATCHING_AUDIT.json"
)


def _run() -> bytes:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return RESULT.read_bytes()


def test_maximal_graded_cotangent_matching_audit() -> None:
    payload = json.loads(_run())
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "MAXIMAL_GRADED_COTANGENT_TYPE_AND_E1_C2_SEAM_CLOSED_VALUES_TAIL_OPEN"
    )
    ledger = payload["retained_graded_sector_ledger"]
    assert ledger["gauge_transverse"]["samples"]["2"] == 72
    assert ledger["Weyl"]["samples"]["0"] == -96
    assert ledger["Hubbard_Strattonovich"]["samples"]["1"] == 4
    assert ledger["gauge_longitudinal_complex_ghost"]["weight"] == 0
    assert payload["exact_cotangent_contract"]["external_source_term"] == (
        "ABSENT_AFTER_J_ext=0"
    )
    assert payload["matching_audit"][
        "actual_per_level_joint_operator_family"
    ] == "OPEN_E1_C2_GRADED_VALUES_AND_MAXIMAL_TAIL"
    assert payload["matching_audit"]["joint_internal_seam_assembly"] == (
        "VALID_MATCH_ONE_E1_C2_SEAM"
    )
    assert payload["matching_audit"]["physical_zero_source_incoming_Mf"] == (
        "VALID_MATCH_M11"
    )
    assert payload["matching_audit"]["E0_event_side_Calderon_and_first_jet"] == (
        "NOT_REQUIRED_CURRENT_GATE7"
    )
    assert payload["adjudication"]["new_grading_required"] is False
    assert payload["adjudication"]["new_external_or_seam_source_required"] is False
    assert payload["claim_boundary"]["actual_graded_cotangent_claimed"] is False
    assert payload["claim_boundary"]["Gate7"].startswith("ACTIVE")
    assert payload["claim_boundary"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_maximal_graded_cotangent_matching_is_deterministic() -> None:
    first = hashlib.sha256(_run()).hexdigest()
    second = hashlib.sha256(_run()).hexdigest()
    assert first == second
