from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION.json"
)


def test_ae2_threshold_supersession_is_scoped() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["action_version"] == "BHSM-AE-2.0.0"
    assert payload["closed_here"]["nonfermion_critical_zero_graph"] == "EXCLUDED"
    assert payload["closed_here"]["strict_factorized_Wronskian_as_universal_prerequisite"] == "RETIRED_AS_OVERSTRONG"
    assert payload["preserved_open_objects"]["realized_factorized_source_weighted_limiting_absorption"] == "OPEN"
    assert payload["preserved_open_objects"]["zero_source_weak_geometry_force"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE_NOT_CLOSED"
    assert payload["FULL_BHSM_COMPLETE"] is False
