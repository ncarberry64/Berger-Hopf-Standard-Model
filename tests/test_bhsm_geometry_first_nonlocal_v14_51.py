from fractions import Fraction

from bhsm.interface.completion.geometry_first_nonlocal_v14_51 import (
    GaugeTrace,
    berger_scale_stationarity_contract,
    canonical_sm_generation_trace,
    common_replication_invariance,
    completion_payload,
    curvature_response_lock,
    direct_trace_target_1_2_7_diagnostic,
    g2_seven_complexified_color_index,
    internal_trace_reconstruction,
    relative_zeta_scale_law,
    su2_peter_weyl_left_index,
)


def test_canonical_sm_trace_is_exact():
    assert canonical_sm_generation_trace() == GaugeTrace(Fraction(10, 3), 2, 2)


def test_common_bundle_factors_do_not_change_ratios():
    assert common_replication_invariance(canonical_sm_generation_trace(), [3, 2, 2, 1])


def test_g2_seven_contributes_index_one_not_dimension_seven():
    trace = g2_seven_complexified_color_index()
    assert trace == GaugeTrace(0, 0, 1)


def test_lowest_full_hopf_peter_weyl_block_has_index_one():
    assert su2_peter_weyl_left_index(1) == 1


def test_literal_1_2_7_target_does_not_emerge():
    diagnostic = direct_trace_target_1_2_7_diagnostic()
    assert diagnostic["single_G2_seven_diagnostic"] == {"u1": "1", "su2": "2", "su3": "3"}
    assert diagnostic["additional_vectorlike_3_plus_bar3_pairs_needed_after_G2"] == 4
    assert diagnostic["current_action_owns_those_states"] is False


def test_topological_winding_not_promoted_to_kinetic_weight():
    payload = internal_trace_reconstruction()
    assert payload["topological_winding_role"]["changes_local_F_wedge_star_F_trace_coefficient_by_itself"] is False
    assert payload["historical_1_2_7_emerges"] is False
    assert all(payload["validation"].values())


def test_relative_zeta_scale_gate_is_fail_closed():
    payload = relative_zeta_scale_law()
    assert payload["scale_derivative"] == "d Gamma_F_rel / d log L = zeta_rel(0;a)"
    assert payload["consequences"]["zeta_rel_nonzero_only"].endswith("no finite stable minimum")
    assert all(payload["validation"].values())


def test_full_Berger_and_scale_equations_are_coupled():
    payload = berger_scale_stationarity_contract()
    assert "F_a := d Gamma_rel_on_shell / da = 0" in payload["quantum_corrected_background_equations"]
    assert "F_L := d Gamma_rel_on_shell / d log L = 0" in payload["quantum_corrected_background_equations"]
    assert payload["current_status"]["absolute_scale_selected"] is False


def test_curvature_response_is_locked_to_zero():
    payload = curvature_response_lock()
    assert payload["selected_branch"] == "xi=0"
    assert payload["validation"]["spin_curvature_not_double_counted_as_xi"]
    assert all(payload["validation"].values())


def test_completion_gate_remains_fail_closed():
    payload = completion_payload()
    assert payload["gates"]["internal_trace_reconstructed"]
    assert not payload["gates"]["historical_1_2_7_derived"]
    assert payload["gates"]["xi_locked_to_zero"]
    assert not payload["gates"]["absolute_scale_selected"]
    assert not payload["gates"]["BHSM_physical_completion"]
    assert payload["validation_passed"]
