import hashlib

from bhsm.interface.ae31_c2_outer_calderon_action_no_go import (
    claim_boundary,
    fermion_selector_configuration_space,
    gauge_outer_response_exhaustion,
    outer_calderon_no_go_theorem,
)
from scripts.materialize_ae31_c2_outer_calderon_action_no_go import (
    TARGET,
    build_payload,
    main,
)


def test_retained_action_has_no_smooth_covariance_coordinate_or_equation():
    result = fermion_selector_configuration_space()
    assert result["independent_fermion_surface_action"] == "S_Sigma_F_AE2=0"
    assert not result["Cauchy_covariance_C_is_action_configuration_variable"]
    assert not result["smooth_bisolution_K_is_action_configuration_variable"]
    assert not result["Euler_Lagrange_equation_for_C_or_K_present"]
    assert result["nontrivial_covariance_distance_witness"] > 0.0
    assert result["witness_is_pure_self_dual"]
    assert result["continuum_preserves_reset_and_family_data"]
    assert result["continuum_shares_fixed_local_symbol"]
    assert not result["retained_classical_action_selects_smooth_covariance"]


def test_retained_coefficient_free_gauge_routes_are_exhausted():
    result = gauge_outer_response_exhaustion()
    assert result["coefficient_free_admissible_route_count"] == 1
    assert result["selected_two_sided_route_evaluated"]
    assert not result["two_sided_route_repairs_mismatch"]
    assert not result["common_local_F_squared_shift_repairs_mismatch"]
    assert result["required_delta_Zt_minus_delta_Zs"] > 0.0
    assert not result["retained_action_selects_one_noncommon_correction"]
    assert result["retained_coefficient_free_local_and_reflected_routes_exhausted"]
    assert not result["all_possible_global_or_microscopic_extensions_excluded"]


def test_no_go_leaves_exactly_global_domain_or_action_extension_classes():
    result = outer_calderon_no_go_theorem()
    assert len(result["live_exit_classes"]) == 2
    assert result["live_exit_classes"][0]["class"] == "GLOBAL_DOMAIN_COMPLETION"
    assert result["live_exit_classes"][1]["class"] == "MICROSCOPIC_ACTION_EXTENSION"
    assert not result["one_exit_class_selected_here"]
    assert not result["BHSM_as_a_whole_refuted"]


def test_claim_boundary_is_route_no_go_not_physical_completion():
    result = claim_boundary()
    assert result["CURRENT_AE31_RETAINED_ACTION_OUTER_CALDERON_COMPLETION_NO_GO_DERIVED"]
    assert result["CURRENT_AE31_FERMION_SMOOTH_STATE_SELECTOR_ABSENT_DERIVED"]
    assert result["CURRENT_AE3_COEFFICIENT_FREE_GAUGE_COMPLETION_ROUTES_EXHAUSTED"]
    assert result["BHSM_ROUTE_FAILURE_NOT_GLOBAL_REFUTATION"]
    assert not result["CURRENT_C2_PHYSICAL_GAUGE_SPINOR_GHOST_CALDERON_PROJECTOR_DERIVED"]
    assert not result["MUON_MAGNETIC_MOMENT_DERIVED"]


def test_artifact_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
