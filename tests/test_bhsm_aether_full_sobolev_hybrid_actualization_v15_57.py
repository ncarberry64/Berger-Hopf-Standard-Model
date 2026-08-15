import pytest

from bhsm.interface import aether_full_sobolev_hybrid_actualization_v15_57 as full


def test_seven_dimensional_sobolev_regular_event_space():
    result = full.sobolev_phase_space_contract()
    assert result["regularity"] > 5.5
    assert result["event_trace_well_defined"]
    with pytest.raises(ValueError):
        full.sobolev_phase_space_contract(5.5)


def test_event_quotient_keeps_carrier_but_no_continuous_metric_tangent():
    result = full.event_quotient_contract()
    assert result["selected_component_after_event_quotient"] == "{I_star}"
    assert "cobordism_domain" in result["surviving_regular_child_interior_means"]
    assert "continuous_metric" in result["surviving_regular_child_interior_does_not_mean"]
    assert result["continuous_event_tangent_after_Aether_quotient"] == "zero_space"


def test_constant_reset_is_zero_derivative_in_every_galerkin_witness():
    reset = full.full_reconstruction_operator()
    witness = full.constant_reset_witness()
    assert reset["single_valued"]
    assert reset["Lipschitz_constant"] == 0.0
    assert witness["all_reset_differences_zero"]
    assert {row["dimension"] for row in witness["Galerkin_rows"]} == {32, 128, 512}


def test_unique_actualization_on_selected_hybrid_event_basin():
    result = full.unique_actualization_theorem()
    assert result["fixed_point_cardinality"] == 1
    assert result["continuous_spectral_radius"] == 0.0
    assert result["continuous_spectrum"] == "{0}"
    payload = full.completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["unique_hybrid_actualization_on_selected_event_basin"]


def test_payload_json_is_deterministic():
    payload = full.completion_payload()
    assert full.deterministic_json(payload) == full.deterministic_json(
        full.completion_payload()
    )
