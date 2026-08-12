import math

import pytest

from bhsm.interface import aether_m5_m4_gauge_higgs_ownership_v15_60 as gate


def test_round_base_geometry_and_regular_profile_domain():
    assert gate.round_base_radius(0.0) == 0.0
    assert math.isclose(gate.round_base_radius(math.pi / 4), gate.RADIUS0 / 2)
    with pytest.raises(ValueError):
        gate.regular_profile(0.2, 0)


def test_electric_magnetic_radial_weights_fail_smooth_lorentz_matching():
    for power in (1, 2, 4, 8, 32):
        result = gate.radial_weight_integrals(power)
        assert abs(result["inferred_M4_coefficient_ratio"] - 2 * power / (2 * power + 1)) < 2e-12
        assert result["inferred_M4_coefficient_ratio"] < 1.0


def test_parent_field_bundle_has_no_higgs_doublet():
    result = gate.higgs_representation_ownership()
    assert result["required_Higgs_representation"] == "(SU3,Sp1,Y)=(1,2,1/2)"
    assert result["required_representation_occurs_in_active_parent_tangent_bundle"] is False
    assert result["fiber_coordinate_as_Higgs"] is False
    assert result["v15_53_Higgs_doublet_status"] == "FOUNDATIONAL_INTRINSIC_M4_FIELD"


def test_forced_boundary_action_keeps_unselected_data_explicit():
    result = gate.forced_intrinsic_M4_action_shape()
    assert result["coupling_ray_already_fixed"] == "K_Y:K_2:K_3=5/3:1:1"
    assert "Z_gauge" in result["independent_data_after_canonicalization"]
    assert result["these_data_selected_by_current_parent_child_action"] is False
    assert result["setting_them_to_observed_values_allowed"] is False


def test_payload_json_is_deterministic_and_valid():
    payload = gate.completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["smooth_bulk_gauge_pushforward_no_go_derived"]
    assert gate.deterministic_json(payload) == gate.deterministic_json(
        gate.completion_payload()
    )
