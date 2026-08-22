import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CONTINUUM_CHILD_INITIAL_EVENT_SIDE.json"
)


def test_continuum_child_initial_event_side_is_positive_without_new_gate() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["validation_passed"] is True
    assert float(payload["finite_N12_root_ball"]["exact_root_value_lower"]) > 0.0
    assert float(payload["continuum_transfer"][
        "continuum_initial_child_event_value_lower"
    ]) > 0.0
    assert payload["consequence"]["return_exists"] is False
    assert payload["consequence"]["return_domain_nonempty"] is False
    assert payload["consequence"]["new_acceptance_condition"] is False
    assert payload["cross_quadrature_diagnostic"][
        "promoted_as_analytic_bound"
    ] is False
