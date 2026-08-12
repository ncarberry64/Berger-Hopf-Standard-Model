from bhsm.interface.aether_composite_higgs_channel_v15_64 import (
    completion_payload,
    composite_channel_ledger,
    composite_field_definition,
    deterministic_json,
    exact_gap_equation_target,
    hubbard_stratonovich_semantics,
)


def test_all_four_bilinear_channels_have_higgs_or_conjugate_higgs_charge():
    channels = composite_channel_ledger()["channels"]
    assert channels["up"]["hypercharge"] == 0.5
    assert channels["down"]["hypercharge"] == -0.5
    assert channels["neutrino"]["hypercharge"] == 0.5
    assert channels["charged_lepton"]["hypercharge"] == -0.5
    assert all(row["color_singlet_occurs"] for row in channels.values())


def test_composite_field_is_owned_without_reintroducing_elementary_parent_doublet():
    result = composite_field_definition()
    assert result["composite_representation_owned_by_derived_fermion_bundle"]
    assert result["elementary_parent_boson_required_for_representation_ownership"] is False
    assert result["condensate_selected"] is False


def test_gap_equation_is_the_next_definite_dynamical_gate():
    result = exact_gap_equation_target()
    assert result["linearized_gap_equation"] == "Delta=K_LR(mu_star)*Delta"
    assert result["critical_surface"] == "lambda_max(K_LR)=1"
    assert result["uses_bulk_to_boundary_DtN_kernel_instead"] is True
    assert result["nonzero_solution_claimed"] is False


def test_hubbard_stratonovich_field_does_not_hide_a_new_coupling():
    result = hubbard_stratonovich_semantics()
    assert result["arbitrary_four_fermion_G_inserted"] is False
    assert result["required_source_of_G"].startswith("the_action-owned")


def test_payload_is_deterministic_and_fail_closed():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
