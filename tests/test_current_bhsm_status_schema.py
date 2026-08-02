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
    assert status["current_version"] == "v11.3"
    assert status["current_exact_verdict"] == "BHSM_RECIPROCAL_ATTACHMENT_ACTION_AND_CURRENT_DERIVED_WITH_THREE_MODE_DOMAIN_CONDITIONAL"
    assert status["next_exact_object"] == "ACTION_NORMALIZED_CORE_WALL_RESPONSE_GRAM_HESSIAN_ON_COMMON_ATTACHMENT_DOMAIN"
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
