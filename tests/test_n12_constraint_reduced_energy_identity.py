import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_constraint_reduced_legendre_energy_identity_is_fail_closed() -> None:
    artifact = json.loads(
        (ROOT / "artifacts" / "intrinsic_state_selection"
         / "BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json").read_text(
            encoding="utf-8"
        )
    )

    assert artifact["validation_passed"] is True
    assert artifact["exact_identity"]["restricted_identity"] == (
        "E_N|C_N_inverse_0=0"
    )
    assert artifact["action_ownership_consequence"][
        "constraint_energy_can_supply_a_positive_strong_S2_norm"
    ] is False
    assert artifact["action_ownership_consequence"][
        "constraint_energy_can_be_Delta_H_or_mass"
    ] is False
    assert artifact["action_ownership_consequence"][
        "no_parent_is_fabricated"
    ] is True
    assert artifact["flagship_chain"][
        "numerical_trajectory_campaign_is_not_a_substitute"
    ] is True


def test_aggregate_points_to_direct_continuation_or_exit_lemma() -> None:
    aggregate = json.loads(
        (ROOT / "artifacts" / "intrinsic_state_selection"
         / "BHSM_N12_INTRINSIC_RETURN_ACTION_OWNERSHIP_GATE.json").read_text(
            encoding="utf-8"
        )
    )

    assert aggregate["validation_passed"] is True
    assert "CONTINUUM_STRONG_S2_CONTINUATION_OR_PHYSICAL_DOMAIN_EXIT" in aggregate[
        "first_missing_action_owned_object"
    ]
    assert aggregate["validation"][
        "child_boundary_H_xi_ownership_no_go_is_localized"
    ] is True
    assert aggregate["validation"][
        "constraint_reduced_Legendre_energy_zero_identity_is_closed"
    ] is True
