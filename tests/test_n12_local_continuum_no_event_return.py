import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_LOCAL_CONTINUUM_NO_EVENT_RETURN.json"
)


def test_local_continuum_interval_is_event_free_without_global_overclaim() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["validation_passed"] is True
    assert float(payload["event_enclosure"][
        "event_value_lower_throughout_interval"
    ]) > 0.0
    assert payload["consequence"][
        "first_forward_return_inside_certified_local_interval"
    ] is False
    assert payload["consequence"]["later_first_forward_return_exists"] is False
    assert payload["consequence"]["physical_domain_exit_proved"] is False
    assert payload["validation"][
        "no_new_event_gate_equation_selector_or_trajectory"
    ] is True
