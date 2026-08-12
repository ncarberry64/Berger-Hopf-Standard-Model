import math

from bhsm.interface.aether_proper_time_joint_pushforward_v15_91 import (
    adm_derivation_contract,
    completion_payload,
    proper_time_cycle_pushforward,
    semantic_reclassification,
)


def test_one_proper_time_measure_generates_gauge_and_yukawa_outputs():
    result = proper_time_cycle_pushforward()
    assert math.isclose(result["proper_cycle_K_magnetic"], 813.476974796934, rel_tol=1e-11)
    assert math.isclose(result["proper_cycle_K_electric"], 2717.004292357736, rel_tol=1e-11)
    assert math.isclose(result["proper_cycle_Z_H"], 0.001766735510106, rel_tol=1e-11)
    assert math.isclose(result["proper_cycle_canonical_Yukawa"], 23.791084030763, rel_tol=1e-11)
    assert result["same_proper_time_measure_for_gauge_and_Yukawa"]


def test_proper_matching_scale_and_gauge_cone_are_derived():
    result = proper_time_cycle_pushforward()
    assert math.isclose(result["proper_matching_scale_in_ell_kappa_inverse"], 0.978372643589, rel_tol=1e-11)
    assert result["electric_to_magnetic_ratio"] > 3.3
    assert 0.54 < result["gauge_cone_speed_relative_to_boundary_metric"] < 0.56


def test_no_separate_normalization_and_no_lorentz_overclaim():
    derivation = adm_derivation_contract()
    semantics = semantic_reclassification()
    assert derivation["separate_gauge_normalization_inserted"] is False
    assert semantics["gauge_and_Yukawa_treated_as_unrelated_problems"] is False
    assert semantics["Lorentz_invariant_local_Maxwell_term_derived"] is False
    assert semantics["physical_absolute_cycle_values"].startswith("V15_91")


def test_payload_validates():
    assert completion_payload()["validation_passed"]
