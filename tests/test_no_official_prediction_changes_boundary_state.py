from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_boundary_state_results_report_official_unchanged() -> None:
    payload = json.loads(
        (
            ROOT / "theory" / "boundary_state_primitive_derivation_results.json"
        ).read_text(encoding="utf-8")
    )
    assert payload["official_predictions_changed"] is False
    assert "OFFICIAL_PREDICTIONS_UNCHANGED" in payload["verdict_labels"]


def test_boundary_state_gate_does_not_touch_official_prediction_files() -> None:
    touched = {
        "theory/candidate_boundary_state_primitives.py",
        "theory/boundary_state_primitive_derivation_gate.md",
        "theory/boundary_state_primitive_registry.md",
        "theory/boundary_state_to_sm_bridge.md",
        "theory/boundary_state_primitive_derivation_results.json",
    }
    assert "docs/frozen_predictions.md" not in touched
    assert "docs/frozen_predictions.json" not in touched
    assert "BHSM_BARE_V1" not in touched
    assert "BHSM_DRESSED_V1_CANDIDATE" not in touched
