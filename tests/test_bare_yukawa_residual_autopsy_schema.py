from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_bare_yukawa_residual_autopsy import (  # noqa: E402
    ALLOWED_VERDICTS,
    BRANCH,
    PREVIOUS_VERDICT,
    build_autopsy_payload,
    export_autopsy_outputs,
)


def test_autopsy_results_schema_and_allowed_verdicts() -> None:
    payload = export_autopsy_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "bare_yukawa_residual_autopsy_results.json").read_text())

    assert parsed["status"] == "candidate_only"
    assert parsed["branch"] == BRANCH
    assert parsed["previous_gate_verdict"] == PREVIOUS_VERDICT
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["best_variant"]["verdict"] in ALLOWED_VERDICTS
    assert parsed["best_variant"]["parameter_policy"] == "single_universal_parameter_set"
    assert set(parsed["best_variant"]["best_parameters"]) == {"epsilon", "tau0", "beta_eff", "xi"}
    assert isinstance(parsed["variant_results"], list)
    assert parsed["variant_results"]
    assert set(parsed["residual_autopsy"]) >= {"worst_residuals", "sector_rms", "sign_pattern"}
    assert payload["best_variant"]["variant_id"] == parsed["best_variant"]["variant_id"]


def test_required_reports_exist_and_are_candidate_only() -> None:
    export_autopsy_outputs(ROOT)
    paths = [
        ROOT / "theory" / "bare_yukawa_residual_autopsy.md",
        ROOT / "theory" / "bare_yukawa_residual_autopsy_results.json",
        ROOT / "theory" / "bare_yukawa_invariant_action_alternatives.md",
    ]
    for path in paths:
        assert path.exists()

    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths if path.suffix == ".md")
    assert "candidate-only" in text
    assert "no official predictions are changed" in text
    assert "not upgraded to derived" in text
    assert "derived full standard model" not in text


def test_previous_tier_c_result_is_preserved_as_context() -> None:
    payload = build_autopsy_payload()
    assert payload["previous_gate_verdict"] == "BARE_YUKAWA_NUMERICAL_GATE_TIER_C_ORDERING_ONLY"
    assert payload["previous_raw_action_result"]["variant_id"] == "A_raw"
    assert payload["previous_raw_action_result"]["ordering_pass"] is True
