from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_current_bhsm_status_json_schema() -> None:
    status = json.loads((ROOT / "docs" / "current_bhsm_status.json").read_text())
    assert status["schema_version"] == "2.0"
    assert status["canonical_public_status"] is True
    assert status["gate_7"]["status"] == "OPEN"
    assert status["UNCHANGED_AE2_LOCALIZATION_CARRIER_FOUND"] is False
    assert status["PHYSICAL_ENCAPSULATION_IDENTIFIED"] is False
    assert status["FULL_BHSM_COMPLETE"] is False
    assert status["observable_machinery_classification"] == (
        "IMPLEMENTED_BUT_PHYSICAL_PROMOTION_GATED"
    )
    assert status["frozen_predictions_changed"] is False
    assert status["official_predictions_changed"] is False


def test_current_status_markdown_contains_required_public_safe_wording() -> None:
    text = (ROOT / "docs" / "current_bhsm_status.md").read_text(encoding="utf-8")
    assert "Central physical-identification obstruction" in text
    assert "UNCHANGED_AE2_LOCALIZATION_CARRIER_FOUND = FALSE" in text
    assert "PHYSICAL_ENCAPSULATION_IDENTIFIED = FALSE" in text
    assert "FULL_BHSM_COMPLETE = FALSE" in text
    assert "implemented observable pipeline is gated infrastructure" in text
