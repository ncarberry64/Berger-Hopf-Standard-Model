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


def test_rayleigh_event_curvature_block_and_preconditioned_promotion() -> None:
    curvature = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_EVENT_CURVATURE_BLOCK_V20_87.json"
    ).read_text(encoding="utf-8"))
    assert curvature["validation_passed"]
    block = curvature["rayleigh_event_curvature_block"]
    assert block["support_dimension"] == 37
    assert block["raw_block_relative_asymmetry"] < 2.0e-2
    proposal = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_CURVATURE_PRECONDITIONED_PROPOSAL_V20_88.json"
    ).read_text(encoding="utf-8"))
    assert proposal["validation_passed"]
    result = proposal["rayleigh_curvature_preconditioned_proposal"]
    assert result["promotion"]["promoted"]
    assert result["exact_line_search"]["best"]["exact_reduction"] > 0.0
    assert result["promotion"]["child"]["all_pass"]


def test_weak_subspace_and_dual_metric_recovery() -> None:
    audit = json.loads(Path(
        "artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_AUDIT_V20_89.json"
    ).read_text(encoding="utf-8"))
    assert audit["validation_passed"]
    assert audit["curvature_singular_subspace_audit"]["child_compatible_tangent"]["rank_DcG"] == 14

    bounded = json.loads(Path(
        "artifacts/BHSM_N3_BOUNDED_RANGE_SPACE_PROPOSAL_V20_90.json"
    ).read_text(encoding="utf-8"))
    assert bounded["validation_passed"]
    assert bounded["bounded_range_space_proposal"]["outcome"] == "BOUNDED_RANGE_SPACE_NO_EXACT_DESCENT"

    for filename, key in (
        ("BHSM_N3_DUAL_METRIC_RANGE_SPACE_PROPOSAL_V20_91.json", "dual_metric_range_space_proposal"),
        ("BHSM_N3_DUAL_METRIC_RANGE_SPACE_CONTINUATION_V20_92.json", "dual_metric_range_space_continuation"),
    ):
        payload = json.loads(Path("artifacts", filename).read_text(encoding="utf-8"))
        assert payload["validation_passed"]
        assert payload[key]["promotion"]["promoted"]
        assert payload[key]["promotion"]["child"]["all_pass"]


def test_refreshed_curvature_recovery_and_one_time_ownership_audit() -> None:
    for filename in (
        "BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V20_93.json",
        "BHSM_N3_REFRESHED_DUAL_METRIC_PROPOSAL_V20_94.json",
        "BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION_V20_95.json",
        "BHSM_N3_RAYLEIGH_OWNERSHIP_AUDIT_V20_96.json",
        "BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V20_97.json",
        "BHSM_N3_REFRESHED_DUAL_METRIC_PROPOSAL_V20_98.json",
        "BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION_V20_99.json",
    ):
        payload = json.loads(Path("artifacts", filename).read_text(encoding="utf-8"))
        assert payload["validation_passed"]

    ownership = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_OWNERSHIP_AUDIT_V20_96.json"
    ).read_text(encoding="utf-8"))["rayleigh_ownership_audit"]
    assert ownership["classification"].startswith("E:")
    assert ownership["first_action_owned_blocker"] is None

    latest = json.loads(Path(
        "artifacts/BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION_V20_99.json"
    ).read_text(encoding="utf-8"))["refreshed_dual_metric_continuation"]
    assert latest["promotion"]["promoted"]
    assert latest["promotion"]["child"]["all_pass"]
    assert abs(latest["exact_search"]["best"]["exact_rayleigh_f376_l2"] - 0.782780987846174) < 5.0e-12
