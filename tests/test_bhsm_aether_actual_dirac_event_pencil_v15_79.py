import json

from bhsm.interface.aether_actual_dirac_event_pencil_v15_79 import (
    actual_event_pushforward_contract,
    completion_payload,
    deterministic_json,
    event_pencil_diagnostics,
)


def test_actual_event_is_full_dirac_not_eta_shell():
    row = event_pencil_diagnostics()
    assert row["soft_Dirac_eigenvalue"] < 0.0
    assert row["soft_eigenvalue_time_derivative"] > 0.0
    assert 0.0 < row["linearized_crossing_increment"] < 5.0e-5
    assert row["minimum_eta_Legendre_at_linearized_Dirac_event"] > 0.5
    assert row["minimum_eta_Legendre_time_derivative"] > 0.0
    assert row["dominant_component"] == "dot_w1"


def test_actual_pushforward_still_forbids_split_normalization():
    contract = actual_event_pushforward_contract()
    assert contract["same_parent_functional_required"]
    assert contract["split_normalization_forbidden"]
    assert "Gamma_cycle" in contract["absolute_gauge_residue"]
    assert "Gamma_cycle" in contract["canonical_Yukawa"]


def test_payload_is_valid_and_deterministic():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert not payload["supersession"][
        "off-orbit_L_eta_shell_crossing_promoted_to_physical"
    ]
    assert deterministic_json(payload) == deterministic_json(completion_payload())
    assert json.loads(deterministic_json(payload))["version"] == "v15.79"
