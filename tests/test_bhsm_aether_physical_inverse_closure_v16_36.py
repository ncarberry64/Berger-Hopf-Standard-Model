from bhsm.interface.aether_physical_inverse_closure_v16_36 import (
    completion_payload,
    physical_requirement_matrix,
    two_tier_data_firewall,
)


def test_required_real_particle_rows_are_present():
    names = {row["particle_or_sector"] for row in physical_requirement_matrix()}
    assert {"electron", "muon", "tau", "neutrino_family", "photon", "W_plus_minus", "Z", "gluons"} <= names


def test_numeric_data_firewall_is_closed():
    firewall = two_tier_data_firewall()
    assert firewall["measured_numerical_values_embedded_in_this_artifact"] is False
    assert "empirical_Yukawa_matrix_insertion" in firewall["forbidden_uses"]


def test_inverse_closure_keeps_live_solve_and_shared_pushforward():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["active_calculation"] == "CONTINUE_THE_EXISTING_FRESH_N3_KKT_SOLVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
