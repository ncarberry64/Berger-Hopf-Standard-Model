import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_child_boundary_hamiltonian_gate_fails_closed() -> None:
    artifact = json.loads(
        (ROOT / "artifacts" / "intrinsic_state_selection"
         / "BHSM_N12_CHILD_BOUNDARY_HAMILTONIAN_OWNERSHIP_GATE.json").read_text(
            encoding="utf-8"
        )
    )

    assert artifact["validation_passed"] is True
    assert artifact["action_owned_inventory"][
        "complete_covariant_symplectic_potential"
    ] is False
    assert artifact["action_owned_inventory"][
        "selected_child_boundary_ensemble"
    ] is False
    assert artifact["parent_separation"][
        "no_parent_subtraction_fabricated"
    ] is True
    assert artifact["shortest_owned_flagship_path"][
        "numerical_trajectory_campaign_authorized"
    ] is False
    assert "CONTINUATION_OR_PHYSICAL_DOMAIN_EXIT" in artifact[
        "shortest_owned_flagship_path"
    ]["active_lemma"]
