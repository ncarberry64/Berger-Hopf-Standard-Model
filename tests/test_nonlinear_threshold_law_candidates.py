from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_existing_engine_branch_threshold import build_payload, threshold_family_diagnostics  # noqa: E402


def test_threshold_families_are_candidate_only_and_nonofficial() -> None:
    diagnostics = threshold_family_diagnostics()
    families = {row["family"]: row for row in diagnostics}
    assert set(families) == {
        "exponential_action_control",
        "bounded_threshold",
        "logarithmic_threshold",
        "branch_rank_threshold",
        "branch_type_weighted_threshold",
    }
    assert all(row["official"] is False for row in diagnostics)
    assert families["branch_type_weighted_threshold"]["overfit_risk"] is True
    assert families["branch_type_weighted_threshold"]["parameter_policy"] == "universal_a_b_c_not_sector_specific"


def test_branch_rank_threshold_is_best_shape_diagnostic() -> None:
    best = build_payload(ROOT)["summary"]["best_threshold_family"]
    assert best["family"] == "branch_rank_threshold"
    assert best["parameter_policy"] == "single_universal_parameter"
    assert best["official"] is False


def test_threshold_docs_include_forbidden_tuning_rules() -> None:
    text = (ROOT / "theory" / "nonlinear_threshold_law_candidates.md").read_text(
        encoding="utf-8"
    )
    assert "Forbidden tuning rules" in text
    assert "no sector-specific parameters" in text
    assert "no per-particle response factors" in text
    assert "no retrofitting frozen predictions" in text


def test_no_threshold_family_claims_numerical_closure() -> None:
    labels = set(build_payload(ROOT)["verdict_labels"])
    assert "NONLINEAR_THRESHOLD_SIGNAL_INDICATED" in labels
    assert "NO_NUMERICAL_CLOSURE" in labels
    assert not any(label.endswith("_PROVEN") for label in labels)
