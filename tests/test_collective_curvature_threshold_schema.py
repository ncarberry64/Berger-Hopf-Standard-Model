from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_collective_curvature_threshold import (  # noqa: E402
    ALLOWED_VERDICT_LABELS,
    BRANCH,
    build_results_payload,
    export_outputs,
)


def test_collective_curvature_results_schema() -> None:
    payload = export_outputs(ROOT)
    parsed = json.loads(
        (ROOT / "theory" / "collective_curvature_threshold_results.json").read_text(
            encoding="utf-8"
        )
    )

    assert parsed == payload
    assert parsed["status"] == "candidate_only"
    assert parsed["branch"] == BRANCH
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["inputs"]["previous_best_branch_threshold_law"] == "D_log_threshold_plus_type"
    assert parsed["inputs"]["previous_rms_to_existing_bare"] == 0.510697459271581
    assert parsed["inputs"]["previous_max_abs_log_error"] == 1.0380747597108453
    assert parsed["candidate_layer"]["official"] is False
    assert set(parsed["verdict_labels"]) <= ALLOWED_VERDICT_LABELS


def test_required_collective_curvature_reports_exist() -> None:
    export_outputs(ROOT)
    required = [
        ROOT / "theory" / "collective_curvature_threshold_layer.md",
        ROOT / "theory" / "collective_curvature_threshold_results.json",
        ROOT / "theory" / "collective_curvature_dark_matter_interpretation.md",
        ROOT / "theory" / "collective_curvature_mass_engine_bridge.md",
    ]
    for path in required:
        assert path.exists(), path


def test_required_verdict_labels_are_present() -> None:
    labels = set(build_results_payload()["verdict_labels"])
    assert "COLLECTIVE_CURVATURE_THRESHOLD_LAYER_DOCUMENTED" in labels
    assert "MASS_AS_COLLECTIVE_THRESHOLD_RESPONSE_CANDIDATE" in labels
    assert "LOG_THRESHOLD_BRIDGE_DOCUMENTED" in labels
    assert "COLLECTIVE_CURVATURE_DARK_MATTER_INTERPRETATION_CANDIDATE" in labels
    assert "NO_DARK_MATTER_SOLUTION_CLAIM_GUARDRAIL" in labels
    assert "EMPIRICAL_GRAVITY_TESTS_REQUIRED_GUARDRAIL" in labels
    assert "NO_NUMERICAL_CLOSURE" in labels
