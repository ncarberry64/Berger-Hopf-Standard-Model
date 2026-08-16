import json
from pathlib import Path


def test_v20_78_blocker_isolated_to_legacy_event_covector() -> None:
    unresolved = json.loads(Path(
        "artifacts/BHSM_N3_DIRECT_RESPONSE_RESOLUTION_AUDIT_V20_78.json"
    ).read_text(encoding="utf-8"))
    assert unresolved["validation_passed"]
    assert unresolved["direct_response_resolution_audit"]["outcome"] == "DIRECT_RESPONSE_RESOLUTION_BLOCKER"
    resolved = json.loads(Path(
        "artifacts/BHSM_N3_DIRECTION_ADAPTIVE_EVENT_RESPONSE_V20_79.json"
    ).read_text(encoding="utf-8"))
    assert not resolved["validation_passed"]
    result = resolved["direction_adaptive_event_response"]
    assert result["outcome"] == "FINITE_DIFFERENCE_EVENT_COVECTOR_INCONSISTENCY_IDENTIFIED"
    assert not result["one_common_event_response_step_exists"]
    assert not result["physical_equations_changed"]
    assert not result["event_definition_changed"]
    assert not result["acceptance_gate_changed"]


def test_rayleigh_event_covector_replaces_only_invalid_numerical_derivative() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_EVENT_COVECTOR_V20_80.json"
    ).read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    result = payload["rayleigh_event_covector"]
    assert result["legacy_vs_rayleigh_relative_residual"] > 0.20
    assert result["numerical_event_derivative_corrected"]
    assert not result["physical_event_changed"]
    assert not result["physical_equations_changed"]
    assert not result["acceptance_gate_changed"]


def test_rayleigh_square_kkt_candidate_is_physically_promoted() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_SQUARE_KKT_PROPOSAL_V20_81.json"
    ).read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    result = payload["rayleigh_square_kkt_proposal"]
    assert result["response"]["resolved"]
    assert result["exact_line_search"]["best"]["exact_reduction"] > 0.0
    assert result["promotion"]["promoted"]
    assert result["promotion"]["child"]["all_pass"]
    assert not result["physical_equations_changed"]
    assert not result["event_definition_changed"]


def test_explicit_multiplier_continuation_is_promoted() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_MULTIPLIER_CONTINUATION_V20_82.json"
    ).read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    result = payload["rayleigh_multiplier_continuation"]
    assert result["event_multiplier_remains_explicit_376TH_UNKNOWN"]
    assert result["candidate"]["exact_reduction"] > 0.0
    assert result["promotion"]["promoted"]


def test_corrected_rayleigh_continuation_and_krylov_audit() -> None:
    for filename in (
        "BHSM_N3_RAYLEIGH_SQUARE_KKT_CONTINUATION_V20_83.json",
        "BHSM_N3_RAYLEIGH_MULTIPLIER_CONTINUATION_V20_84.json",
        "BHSM_N3_RAYLEIGH_SQUARE_KKT_CONTINUATION_V20_85.json",
        "BHSM_N3_RAYLEIGH_KRYLOV_RESTRICTION_AUDIT_V20_86.json",
    ):
        payload = json.loads(Path("artifacts", filename).read_text(encoding="utf-8"))
        assert payload["validation_passed"]
    audit = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_KRYLOV_RESTRICTION_AUDIT_V20_86.json"
    ).read_text(encoding="utf-8"))["rayleigh_krylov_restriction_audit"]
    assert audit["promotion"]["promoted"]
    assert not audit["promotion"]["child_attempts"][0]["all_pass"]
    assert audit["promotion"]["child_attempts"][1]["all_pass"]
    assert audit["response"]["krylov_restart_numerical_control"] == 24
