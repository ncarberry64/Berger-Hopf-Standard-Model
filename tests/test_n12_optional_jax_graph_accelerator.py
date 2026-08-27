import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"


def _load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_optional_jax_action_realization_is_cross_validated() -> None:
    payload = _load("BHSM_N12_JAX_FULL_ACTION_EQUIVALENCE_AUDIT.json")
    assert payload["validation_passed"] is True
    assert payload["software"] == {
        "backend": "cpu",
        "jax": "0.11.1",
        "jaxlib": "0.11.1",
        "x64_enabled": True,
    }
    assert payload["validation"][
        "JAX_is_acceleration_only_and_retained_jet_remains_authority"
    ] is True


def test_hybrid_graph_is_only_a_reconnaissance_accelerator() -> None:
    payload = _load("BHSM_N12_HYBRID_GRAPH_JACOBIAN_EQUIVALENCE_AUDIT.json")
    assert payload["validation_passed"] is True
    assert payload["summary"]["maximum_graph_Jacobian_relative_residual"] < 2e-10
    assert payload["validation"][
        "hybrid_third_tensor_not_promoted_to_interval_authority"
    ] is True
    assert payload["validation"][
        "retained_directional_replay_remains_certificate_authority"
    ] is True
