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
        "MAXIMAL_GRADED_COTANGENT_FINITE_CORE_SEED_CLOSED_SIGNED_CONTRACTION_AND_TAIL_OPEN"
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
    ] == "DIRECT_GENERATOR_CLOSED_ACTUAL_PARAMETRIC_VALUES_AND_MAXIMAL_TAIL_OPEN"
    assert payload["matching_audit"][
        "finite_core_direct_joint_operator_generator"
    ] == "VALID_MATCH"
    assert payload["matching_audit"][
        "full_graded_finite_core_heat_cotangent_seed"
    ] == "VALID_TRACE_NORM_LOG_SPACE_ENCLOSURE"
    assert payload["matching_audit"]["actual_finite_core_graded_cotangent_seed"] == (
        "ZETA_RESET_BALL_CLOSED_PLUS_UNIFORM_HEAT_TRACE_NORM_ENCLOSURE"
    )
    assert payload["matching_audit"]["direct_zeta_covector"] == (
        "CLOSED_COMPONENTWISE_FINITE_CORE_MATCH"
    )
    assert payload["matching_audit"]["C2_zeta_reset_cotangent_pullback"] == (
        "CERTIFIED_ACTION_DUAL_NORM_BALL"
    )
    assert payload["matching_audit"]["joint_KKT_information_gate"] == (
        "COMPONENTWISE_ZERO_TESTS_RETIRED"
    )
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
