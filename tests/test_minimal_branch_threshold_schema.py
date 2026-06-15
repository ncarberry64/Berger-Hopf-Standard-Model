from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_minimal_branch_threshold import (  # noqa: E402
    ALLOWED_VERDICTS,
    BRANCH,
    build_payload,
    export_outputs,
)


def test_minimal_branch_threshold_schema_and_verdicts() -> None:
    payload = export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "minimal_branch_threshold_reconstruction_results.json").read_text())

    assert parsed["status"] == "candidate_only"
    assert parsed["branch"] == BRANCH
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert set(parsed["inputs"]) == {"existing_engine_sources", "reference_ratio_source", "base_branch"}
    assert parsed["read_only_existing_outputs"]
    assert parsed["branch_feature_table"]
    assert parsed["candidate_law_results"]
    assert set(parsed["best_candidate_law"]) >= {
        "law_id",
        "official",
        "parameter_count",
        "sample_count",
        "overfit_risk",
        "rms_log_error_to_existing_bare",
        "max_abs_log_error_to_existing_bare",
        "ordering_pass",
        "middle_vs_light_separation_pass",
        "coefficients",
    }
    assert parsed["hidden_response_decomposition"]
    assert set(parsed["verdict_labels"]) <= ALLOWED_VERDICTS
    assert payload["best_candidate_law"]["law_id"] == parsed["best_candidate_law"]["law_id"]


def test_required_reports_exist_and_are_candidate_only() -> None:
    export_outputs(ROOT)
    paths = [
        ROOT / "theory" / "minimal_branch_threshold_reconstruction.md",
        ROOT / "theory" / "minimal_branch_threshold_reconstruction_results.json",
        ROOT / "theory" / "branch_threshold_candidate_laws.md",
    ]
    for path in paths:
        assert path.exists()
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths if path.suffix == ".md")
    assert "candidate-only" in text
    assert "no new official mass formula" in text
    assert "not upgraded to derived" in text
    assert "derived full standard model" not in text


def test_best_candidate_law_is_logged_as_overfit_risk_diagnostic() -> None:
    best = build_payload(ROOT)["best_candidate_law"]
    assert best["law_id"] == "D_log_threshold_plus_type"
    assert best["official"] is False
    assert best["parameter_count"] == 4
    assert best["sample_count"] == 6
    assert best["overfit_risk"] is True
    assert best["ordering_pass"] is True
    assert best["middle_vs_light_separation_pass"] is True
