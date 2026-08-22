import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FORWARD_INVARIANT_HISTORY_EXISTENCE_GATE.json"
)


def test_forward_return_existence_gate_fails_closed_at_singular_reset() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["validation_passed"] is True
    assert payload["exact_return_domain"]["nonempty_proved"] is False
    assert payload["exact_return_domain"]["empty_proved"] is False
    assert payload["localized_failure"]["first_retained_action_failure"] == (
        "ONE_SIDED_SINGULAR_ORDERED_EVENT_HITTING_AND_RESET_REGULARITY_NOT_ESTABLISHED"
    )
    assert payload["periodic_point_prerequisites"][
        "fixed_or_periodic_point_may_be_claimed"
    ] is False
    assert payload["claim_boundaries"]["formal_reversal_quotiented"] is False
    assert payload["claim_boundaries"]["trajectory_sampling_is_proof"] is False


def test_forward_singular_hitting_orientation_is_not_a_new_gate() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    lemma = payload["forward_singular_hitting_orientation"]

    assert lemma["identity"] == "LIM_D_DT(F(T)^2)=2*C_PSI*B_PSI"
    assert lemma["new_sign_gate"] is False
    assert lemma["formal_reflection_creates_a_forward_return"] is False
    assert lemma["formal_reflection_flips_hitting_orientation"] is True
    assert lemma["continuum_initial_child_side_independently_enclosed"] is True
    assert float(lemma["continuum_initial_child_event_value_lower"]) > 0.0
