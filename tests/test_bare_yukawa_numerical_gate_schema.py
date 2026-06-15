from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_bare_yukawa_gate import (  # noqa: E402
    BRANCH,
    CLAIM_LABELS,
    VERDICTS,
    build_gate_payload,
    export_gate_outputs,
)


def test_results_json_schema_and_allowed_verdict() -> None:
    payload = export_gate_outputs(ROOT)
    path = ROOT / "theory" / "bare_yukawa_numerical_closure_results.json"
    parsed = json.loads(path.read_text(encoding="utf-8"))

    assert parsed["status"] == "candidate_only"
    assert parsed["branch"] == BRANCH
    assert parsed["verdict"] in VERDICTS
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["main_scan"]["parameter_policy"] == "single_universal_parameter_set"
    assert set(parsed["main_scan"]["best_parameters"]) == {"epsilon", "tau0", "beta_eff", "xi"}
    assert isinstance(parsed["main_scan"]["rms_log_error"], float)
    assert isinstance(parsed["main_scan"]["max_abs_log_error"], float)
    assert isinstance(parsed["main_scan"]["ordering_pass"], bool)
    assert set(parsed["sector_results"]) == {"charged_lepton", "up", "down"}
    assert payload["verdict"] == parsed["verdict"]


def test_claim_labels_are_present_without_upgrading_base_candidate_claims() -> None:
    payload = build_gate_payload()
    for label in CLAIM_LABELS:
        assert label in payload["claim_labels"]
    text = (ROOT / "theory" / "bare_yukawa_numerical_closure_gate.md").read_text(
        encoding="utf-8"
    )
    assert "BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE` is not upgraded to derived" in text
    assert "FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE` is not upgraded to derived" in text


def test_markdown_reports_exist_and_preserve_claim_hygiene() -> None:
    export_gate_outputs(ROOT)
    paths = [
        ROOT / "theory" / "bare_yukawa_numerical_closure_gate.md",
        ROOT / "theory" / "full_bhsm_numerical_gate_summary.md",
        ROOT / "theory" / "bare_yukawa_numerical_closure_results.json",
    ]
    for path in paths:
        assert path.exists()

    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths[:2])
    assert "does not create official predictions" in text
    assert "does not change frozen outputs" in text
    assert "derived full standard model" not in text
    assert "hidden retuning" not in text
