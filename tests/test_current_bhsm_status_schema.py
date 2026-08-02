from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_current_bhsm_status_json_schema() -> None:
    status = json.loads((ROOT / "docs" / "current_bhsm_status.json").read_text())
    assert status["status"] == "Full BHSM v1.0 Candidate"
    assert status["candidate_architecture_complete"] is True
    assert status["full_bhsm_proven"] is False
    assert status["standard_model_fully_derived"] is False
    assert status["current_version"] == "v11.2"
    assert status["current_exact_verdict"] == "BHSM_BIDIRECTIONAL_BUOYANCY_AND_FIXED_ENCLOSURE_ARCHITECTURE_DERIVED_CONDITIONALLY_BUT_ATTACHMENT_CHARACTER_REMAINS_UNFIXED"
    assert status["next_exact_object"] == "ACTION_OWNED_CORE_SURFACE_ATTACHMENT_TERM_FIXING_ATTACHMENT_CHARACTER_AND_EXCHANGE_CURRENT"
    assert status["frozen_predictions_changed"] is False
    assert status["official_predictions_changed"] is False


def test_current_status_markdown_contains_required_public_safe_wording() -> None:
    text = (ROOT / "docs" / "current_bhsm_status.md").read_text(encoding="utf-8")
    required = (
        "Full BHSM v1.0 Candidate is a repo-audited completion framework, "
        "not yet a completed replacement of the Standard Model."
    )
    assert required in text
    assert "replacement by derivation" in text
    assert "preserved infrared layer" in text
