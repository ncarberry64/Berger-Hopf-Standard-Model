from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_response_layer_decomposition import (  # noqa: E402
    ALLOWED_VERDICTS,
    BRANCH,
    build_response_payload,
    export_response_outputs,
)


def test_response_results_schema_and_allowed_labels() -> None:
    payload = export_response_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "response_layer_residual_decomposition_results.json").read_text())

    assert parsed["status"] == "candidate_only"
    assert parsed["branch"] == BRANCH
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert set(parsed["verdict_labels"]) <= ALLOWED_VERDICTS
    assert set(parsed["baseline"]) >= {"source", "variant", "parameters", "rms_log_error", "max_abs_log_error"}
    assert parsed["baseline"]["variant"] == "A_raw"
    assert parsed["scenario_results"]
    assert parsed["best_evidence_scenario"]["scenario_id"] == payload["best_evidence_scenario"]["scenario_id"]
    assert set(parsed["response_effect_summary"]) >= {
        "lepton_8_9",
        "up_half",
        "up_light_amplitude",
        "down_missing_response_sign",
        "global_conclusion",
    }


def test_response_reports_exist_and_are_candidate_only() -> None:
    export_response_outputs(ROOT)
    paths = [
        ROOT / "theory" / "response_layer_residual_decomposition.md",
        ROOT / "theory" / "response_layer_residual_decomposition_results.json",
        ROOT / "theory" / "response_selector_diagnostic_summary.md",
    ]
    for path in paths:
        assert path.exists()
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths if path.suffix == ".md")
    assert "candidate-only" in text
    assert "no new official response factor is introduced" in text
    assert "not upgraded to derived" in text
    assert "derived full standard model" not in text


def test_best_evidence_scenario_is_lepton_only_not_closure() -> None:
    payload = build_response_payload()
    best = payload["best_evidence_scenario"]
    assert best["scenario_id"] == "lepton_8_9_only"
    assert best["ordering_pass"] is True
    assert best["rms_log_error"] < payload["baseline"]["rms_log_error"]
    assert "RESPONSE_LAYER_NO_CLOSURE" in payload["verdict_labels"]
