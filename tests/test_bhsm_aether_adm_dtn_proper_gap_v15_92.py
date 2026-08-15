import math

from bhsm.interface.aether_adm_dtn_proper_gap_v15_92 import (
    adm_dtn_equations,
    completion_payload,
    proper_adm_dtn_residues,
    proper_composite_gap,
)


def test_adm_static_dtn_residues_are_positive_and_properly_averaged():
    result = proper_adm_dtn_residues()
    assert math.isclose(result["proper_cycle_lowest_transverse_DtN"], 2405.175268358851, rel_tol=1e-11)
    assert math.isclose(result["proper_cycle_lowest_Coulomb_DtN"], 3795.978188551599, rel_tol=1e-11)


def test_corrected_proper_gap_is_strictly_subcritical():
    result = proper_composite_gap()
    assert result["gap_operator_envelope"][1] < 6.8e-5
    assert math.isclose(result["proper_cycle_gap_operator"], 6.556416547995e-5, rel_tol=1e-10)
    assert result["quadratic_coefficient_envelope"][0] > 110.0
    assert result["nonzero_gap_solution_exists"] is False
    assert result["proper_cycle_Floquet_mass"] == 0.0
    assert "not_zero" in result["proper_cycle_Yukawa_vertex"]


def test_same_adm_operator_and_no_split_rescaling():
    equations = adm_dtn_equations()
    assert equations["same_event_weight"].startswith("W=")
    assert equations["independent_gauge_rescaling"] is False


def test_payload_validates():
    assert completion_payload()["validation_passed"]
