from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.aether_backward_closure_existing_answer_audit_v15_8 import EXACT_NEXT_OBJECT, PRIMARY_VERDICT


ROOT = Path(__file__).resolve().parents[1]


def test_current_bhsm_status_json_schema() -> None:
    status = json.loads((ROOT / "docs" / "current_bhsm_status.json").read_text())
    assert status["status"] == "Full BHSM v1.0 Candidate"
    assert status["candidate_architecture_complete"] is True
    assert status["full_bhsm_proven"] is False
    assert status["standard_model_fully_derived"] is False
    assert status["current_version"] == "v15.8"
    assert status["current_exact_verdict"] == PRIMARY_VERDICT
    assert status["next_exact_object"] == EXACT_NEXT_OBJECT
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
