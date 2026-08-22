import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FORWARD_INVARIANT_HISTORY_EXISTENCE_GATE.json"
)


def test_forward_return_existence_gate_fails_closed_at_first_missing_domain() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["validation_passed"] is True
    assert payload["exact_return_domain"]["nonempty_proved"] is False
    assert payload["exact_return_domain"]["empty_proved"] is False
    assert payload["localized_failure"]["first_retained_action_failure"] == (
        "NONEMPTY_ADMISSIBLE_FORWARD_FIRST_RETURN_DOMAIN_NOT_ESTABLISHED"
    )
    assert payload["periodic_point_prerequisites"][
        "fixed_or_periodic_point_may_be_claimed"
    ] is False
    assert payload["claim_boundaries"]["formal_reversal_quotiented"] is False
    assert payload["claim_boundaries"]["trajectory_sampling_is_proof"] is False


def test_forward_landing_chirality_is_conditional_not_a_new_gate() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    lemma = payload["forward_landing_chirality_lemma"]

    assert lemma["identity"] == "SIGN(D_T_F(TAU))=-SIGN(F(0))"
    assert lemma["new_sign_gate"] is False
    assert lemma["formal_reflection_creates_a_forward_return"] is False
    assert lemma["continuum_initial_child_side_independently_enclosed"] is True
    assert float(lemma["continuum_initial_child_event_value_lower"]) > 0.0
