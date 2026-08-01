from __future__ import annotations

from bhsm.interface.envelopment import dynamic_action


def test_eta_action_is_a_bosonic_structural_postulate():
    action = dynamic_action.extended_action_ledger()
    assert action["classification"] == "STRUCTURAL_POSTULATE"
    assert action["eta_is_elementary_fermion"] is False
    assert action["eta_is_anticommuting"] is False
    assert action["p_energy_normalizations"] == {"p=2": "1/2", "p=8": "1/8"}
    assert action["new_continuous_coupling"] is False


def test_dimensional_audit_closes_every_bulk_density():
    row = dynamic_action.dimensional_audit()
    assert row["spacetime_dimension"] == 8
    assert row["X_eta_fourth_power_dimension"] == "L^-8"
    assert row["coupling_dimensions"]["kappa1"] == "L^-6"
    assert row["action_dimensionless"] is True


def test_variation_contains_p8_flux_constraint_and_sigma_source():
    row = dynamic_action.variational_equations()
    assert "kappa1+X_eta^3" in row["eta_equation"]
    assert "Lambda_eta eta" in row["eta_equation"]
    assert row["constraint"] == "<eta,eta>=1"
    assert "X_eta^4/4" in row["sigma_eta_source"]
    assert row["metric_variation_includes_induced_spin_connection"] is True


def test_mapping_space_z2_does_not_fabricate_physical_loops():
    row = dynamic_action.topology_audit()
    assert row["homotopy_group"] == "pi8(S7)=Z2"
    assert row["Z2_class_exists"] is True
    assert row["physical_2pi_rotation_loop"] is None
    assert row["two_texture_exchange_loop"] is None
    assert row["rotation_exchange_identified_with_generator"] is False


def test_current_is_owned_conditionally_and_not_a_ckm_proof():
    row = dynamic_action.spin_current_audit()
    assert "kappa1+X_eta^3" in row["current"]
    assert row["gauge_covariant"] is True
    assert row["Hermitian_action_requires_adjoint_pair"] is True
    assert row["neutral_current_centrality"] is None
    assert row["charged_current_compatibility"] is None
    assert row["physical_pullback_rank"] is None


def test_unit_spinor_supplies_candidate_g2_but_not_local_chirality():
    row = dynamic_action.g2_chirality_audit()
    assert row["unit_spinor_stabilizer_on_oriented_spin_7_slice"] == "G2"
    assert row["G2_structure_candidate_owned_by_eta"] is True
    assert row["bosonic_eta_is_local_fermion_carrier"] is False
    assert row["four_dimensional_chiral_transgression"] is None


def test_action_payload_passes_without_physical_current_promotion():
    payload = dynamic_action.action_payload()
    assert payload["validation_passed"] is True
    assert payload["physical_current_promoted"] is False
    assert payload["stratified_ownership"]["intrinsic_SM_from_metric_derived"] is False
