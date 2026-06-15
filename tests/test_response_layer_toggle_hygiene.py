from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_response_layer_decomposition import (  # noqa: E402
    CONTROL_SCENARIOS,
    MAIN_EVIDENCE_SCENARIOS,
    build_response_payload,
)


def test_main_evidence_scenarios_exclude_forbidden_controls() -> None:
    payload = build_response_payload()
    scenario_ids = {row["scenario_id"] for row in payload["scenario_results"]}
    assert scenario_ids == set(MAIN_EVIDENCE_SCENARIOS)
    assert not (scenario_ids & set(CONTROL_SCENARIOS))
    assert all(row["main_evidence_allowed"] is True for row in payload["scenario_results"])


def test_forbidden_controls_are_cataloged_but_not_used_as_evidence() -> None:
    payload = build_response_payload()
    controls = {row["scenario_id"]: row for row in payload["control_scenarios"]}
    assert set(controls) == set(CONTROL_SCENARIOS)
    for scenario_id, status in CONTROL_SCENARIOS.items():
        assert controls[scenario_id]["control_status"] == status
        assert controls[scenario_id]["main_evidence_allowed"] is False
        assert controls[scenario_id]["used_as_evidence"] is False


def test_no_new_down_response_is_treated_as_official() -> None:
    payload = build_response_payload()
    for scenario in payload["scenario_results"]:
        if scenario["scenario_id"] in {"bare_only", "lepton_8_9_only", "up_half_only", "up_light_amp_only", "up_half_and_light_amp", "current_candidate_responses"}:
            for row in scenario["rows"]:
                if row["sector"] == "down":
                    assert row["response_factor_applied"] == 1.0


def test_claim_labels_include_guardrails() -> None:
    labels = set(build_response_payload()["claim_labels"])
    assert "NO_NEW_OFFICIAL_RESPONSE_GUARDRAIL" in labels
    assert "RESPONSE_TOGGLE_AUDIT_CANDIDATE" in labels
    assert "MISSING_DOWN_RESPONSE_SIGN_DIAGNOSTIC" in labels
