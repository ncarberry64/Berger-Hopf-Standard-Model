import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json"
)


def test_global_flow_coercive_control_gate_fails_closed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    sequence = payload["exact_unreduced_countersequence"]
    assert sequence["quadratic_value_for_every_k"] == 0.0
    assert sequence["norm_tends_to_infinity"] is True
    assert "UNREDUCED" in sequence["scope"]
    energy = payload["owned_and_missing_energy_structure"]
    assert energy["local_energy_is_complete_Q_xi"] is False
    assert energy["coercive_S2_bound_on_continuum_child_component"] is False
    consequence = payload["global_flow_consequence"]
    assert consequence["local_continuum_flow_remains_certified"] is True
    assert consequence[
        "globalization_by_unreduced_energy_conservation_allowed"
    ] is False
    assert consequence["numerical_sampling_alone_is_a_proof_route"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
