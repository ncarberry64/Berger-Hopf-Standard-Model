import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_EXISTING_PERSISTENCE_EVENT_RETURN_AUDIT.json"
)


def test_existing_persistence_event_return_audit_fails_closed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["scope"][
        "new_evolution_continuation_or_numerical_campaign"
    ] is False
    assert payload["summary"][
        "both_endpoints_positive_at_all_quadratures"
    ] is True
    assert payload["summary"][
        "final_endpoint_farther_from_zero_at_all_quadratures"
    ] is True
    conclusion = payload["action_ownership_conclusion"]
    assert conclusion["existing_witness_records_a_first_positive_return"] is False
    assert conclusion["unrecorded_interior_return_excluded"] is False
    assert conclusion["later_first_positive_return_proved_to_exist"] is False
    assert conclusion["return_domain_proved_empty"] is False
    assert conclusion["parent_stationary_section_restored"] is False
    assert conclusion["matched_parent_subtraction_authorized"] is False
    assert payload["prediction_frozen"] is False
    assert payload["held_out_comparison_performed"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
