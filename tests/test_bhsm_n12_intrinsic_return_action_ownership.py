import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_INTRINSIC_RETURN_ACTION_OWNERSHIP_GATE.json"
)


def test_intrinsic_return_action_ownership_gate_fails_closed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["global_flow_audit"][
        "global_continuum_flow_theorem_in_audited_inputs"
    ] is False
    assert payload["global_flow_audit"][
        "blanket_eta_domain_invariance_may_be_assumed"
    ] is False
    assert payload["return_or_no_return_proof_obligations"][
        "recurrence_shortcut_available"
    ] is False
    assert payload["flagship_chain_consequence"][
        "matched_parent_Q_xi_or_Delta_H_authorized"
    ] is False
    assert payload["flagship_chain_consequence"][
        "intrinsic_return_observable_executable"
    ] is False
    assert payload["flagship_chain_consequence"][
        "numerical_trajectory_search_authorized_as_substitute"
    ] is False
    assert payload["flagship_chain_consequence"]["prediction_frozen"] is False
