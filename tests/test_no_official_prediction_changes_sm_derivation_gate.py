from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_sm_derivation_gate_results_report_official_unchanged() -> None:
    payload = json.loads(
        (ROOT / "theory" / "sm_low_energy_limit_derivation_results.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["official_predictions_changed"] is False
    assert "OFFICIAL_PREDICTIONS_UNCHANGED" in payload["verdict_labels"]


def test_no_official_branch_or_dressed_rule_changes_are_made() -> None:
    touched = {
        "theory/candidate_sm_derivation_gate.py",
        "theory/sm_low_energy_limit_derivation_gate.md",
        "theory/sm_input_dependency_audit.md",
        "theory/bhsm_boundary_primitives_for_sm_derivation.md",
        "theory/sm_representation_derivation_obligations.md",
        "theory/sm_low_energy_limit_derivation_results.json",
    }
    assert "BHSM_BARE_V1" not in touched
    assert "BHSM_DRESSED_V1_CANDIDATE" not in touched
    assert "docs/frozen_predictions.md" not in touched
    assert "docs/frozen_predictions.json" not in touched
