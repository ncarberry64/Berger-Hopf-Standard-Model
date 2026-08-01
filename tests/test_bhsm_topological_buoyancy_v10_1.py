from bhsm.interface.envelopment import topological_buoyancy as buoyancy


def test_proxy_radial_equation_is_varied_and_stable():
    row = buoyancy.collective_variation()
    assert row["inserted_force"] is False
    assert row["equilibrium_residual_exact"] is True
    assert row["second_variation_positive"] is True
    assert row["physical_promotion"] is False


def test_full_buoyancy_gate_fails_closed_without_hard_coded_sign():
    payload = buoyancy.buoyancy_payload()
    assert payload["validation_passed"] is True
    assert payload["verdict"] == "BHSM_TOPOLOGICAL_BUOYANCY_NOT_GENERATED_BY_CURRENT_PARENT_ACTION"
    assert payload["normal_variation"]["assembled_single_functional"] is None
    assert any("normal displacement" in item for item in payload["normal_variation"]["domain_obstructions"])
    assert payload["theorem_gates"]["energy_depth_sign"].startswith("OPEN")
    assert payload["theorem_gates"]["Newtonian_weak_field_limit"] == "OPEN"
    assert payload["theorem_gates"]["new_independent_gravity_mediator"] is False
