import math

from bhsm.interface.aether_reset_hessian_matter_cones_v15_93 import (
    completion_payload,
    proper_fermion_cone,
    reset_second_variation_theorem,
    three_cone_comparison,
)


def test_constant_reset_has_no_hidden_quadratic_residue():
    result = reset_second_variation_theorem()
    assert result["first_Frechet_derivative"] == "D R_hat_s=0"
    assert result["second_Frechet_derivative"] == "D2 R_hat_s=0"
    assert result["Gamma_reset_gauge_quadratic_residue"] == 0.0
    assert result["reset_repairs_gauge_cone_mismatch"] is False


def test_proper_fermion_cone_is_derived_from_the_normalized_wall_mode():
    result = proper_fermion_cone()
    assert result["proper_temporal_residue"] == 1.0
    assert math.isclose(result["proper_cycle_spatial_residue"], 0.657256737598, rel_tol=1e-11)


def test_metric_gauge_and_fermion_cones_are_distinct():
    result = three_cone_comparison()
    assert result["metric_cone_speed"] == 1.0
    assert 0.54 < result["gauge_cone_speed"] < 0.56
    assert 0.65 < result["fermion_cone_speed"] < 0.67
    assert result["common_emergent_matter_metric_exists"] is False
    assert result["independent_sector_rescaling_allowed"] is False


def test_payload_validates():
    assert completion_payload()["validation_passed"]
