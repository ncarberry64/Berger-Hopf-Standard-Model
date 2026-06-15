from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_minimal_branch_threshold import build_payload, fit_law  # noqa: E402


def test_branch_rank_only_is_coarse_but_orders_correctly() -> None:
    law = fit_law("A_branch_rank_only", ROOT)
    assert law["parameter_count"] == 2
    assert law["overfit_risk"] is False
    assert law["ordering_pass"] is True
    assert law["middle_vs_light_separation_pass"] is True
    assert law["rms_log_error_to_existing_bare"] > 1.0


def test_branch_type_and_nonlinear_laws_improve_shape_but_raise_overfit_risk() -> None:
    laws = {law["law_id"]: law for law in build_payload(ROOT)["candidate_law_results"]}
    assert laws["B_branch_rank_plus_type"]["rms_log_error_to_existing_bare"] < laws["A_branch_rank_only"]["rms_log_error_to_existing_bare"]
    assert laws["C_bounded_norm_plus_type"]["rms_log_error_to_existing_bare"] < laws["B_branch_rank_plus_type"]["rms_log_error_to_existing_bare"]
    assert laws["D_log_threshold_plus_type"]["rms_log_error_to_existing_bare"] < laws["C_bounded_norm_plus_type"]["rms_log_error_to_existing_bare"]
    assert laws["D_log_threshold_plus_type"]["overfit_risk"] is True


def test_hidden_response_remaining_is_reported_for_best_law() -> None:
    payload = build_payload(ROOT)
    hidden = {row["ratio_name"]: row for row in payload["hidden_response_decomposition"]}
    assert set(hidden) == {"mu/tau", "e/tau", "c/t", "u/t", "s/b", "d/b"}
    assert hidden["c/t"]["mode_type"] == "pure_fiber"
    assert hidden["s/b"]["mode_type"] == "pure_base"
    assert hidden["e/tau"]["diagnostic_only"] is True
    assert "HIDDEN_RESPONSE_REMAINS_INDICATED" in payload["verdict_labels"]


def test_verdicts_reflect_best_law_without_claiming_closure() -> None:
    labels = set(build_payload(ROOT)["verdict_labels"])
    assert "MINIMAL_BRANCH_THRESHOLD_RECONSTRUCTION_COMPLETE" in labels
    assert "LOG_THRESHOLD_SIGNAL_INDICATED" in labels
    assert "NO_NUMERICAL_CLOSURE" in labels
    assert "OVERFIT_RISK_WARNING" in labels
    assert not any(label.endswith("_PROVEN") for label in labels)
