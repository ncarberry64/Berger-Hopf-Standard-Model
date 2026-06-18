from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_existing_engine_branch_threshold import (  # noqa: E402
    ALLOWED_VERDICTS,
    BRANCH,
    build_payload,
    export_outputs,
)


def test_existing_engine_results_schema_and_verdicts() -> None:
    payload = export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "existing_engine_branch_threshold_results.json").read_text())

    assert parsed["status"] == "candidate_only"
    assert parsed["branch"] == BRANCH
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert set(parsed["inputs"]) == {
        "existing_engine_sources",
        "spectral_action_source",
        "reference_ratio_source",
    }
    assert parsed["read_only_existing_outputs"]
    assert parsed["branch_assignments"]
    assert set(parsed["invariant_diagnostics"]) == {
        "candidate_variables",
        "shape_associations",
        "rank_order_checks",
        "small_sample_warning",
    }
    assert parsed["threshold_family_diagnostics"]
    assert parsed["hidden_response_decomposition"]
    assert set(parsed["verdict_labels"]) <= ALLOWED_VERDICTS
    assert payload["summary"]["recommended_next_target"] == parsed["summary"]["recommended_next_target"]


def test_required_reports_exist_and_preserve_claim_boundaries() -> None:
    export_outputs(ROOT)
    paths = [
        ROOT / "theory" / "existing_engine_branch_threshold_audit.md",
        ROOT / "theory" / "existing_engine_branch_threshold_results.json",
        ROOT / "theory" / "existing_engine_hidden_invariant_summary.md",
        ROOT / "theory" / "nonlinear_threshold_law_candidates.md",
    ]
    for path in paths:
        assert path.exists()
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths if path.suffix == ".md")
    assert "candidate-only" in text
    assert "no new official mass formula" in text
    assert "not upgraded to derived" in text
    assert "derived full standard model" not in text


def test_summary_recommends_branch_aware_threshold_target() -> None:
    summary = build_payload(ROOT)["summary"]
    assert "branch_assignment" in summary["best_supported_missing_structure"]
    assert "nonlinear_threshold_behavior" in summary["best_supported_missing_structure"]
    assert "hidden_response_decomposition" in summary["best_supported_missing_structure"]
    assert summary["best_threshold_family"]["family"] == "branch_rank_threshold"
