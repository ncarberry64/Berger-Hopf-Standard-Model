import math

from bhsm.interface.aether_formation_imbalance_equivariance import (
    FULL_BHSM_COMPLETE,
    archive_route_exhaustion,
    completion_payload,
    equivariant_sigma_response_theorem,
    formation_imbalance_candidates,
    foundational_consistency_audit,
    hopf_factor_exchange,
    monomial_symmetry,
    response_magnitude_selection_audit,
)


def test_hopf_factor_exchange_reverses_join_orientation_only() -> None:
    result = hopf_factor_exchange()
    assert result["J_reverses"]
    assert result["zeta_reverses"]
    assert not result["sigma_reflection_performed_by_factor_exchange"]


def test_all_named_formation_candidates_are_sigma_reflection_even() -> None:
    result = formation_imbalance_candidates(0.14, 0.6)
    assert result["every_candidate_fixed_by_independent_sigma_reflection"]
    assert result["nonzero_oriented_candidate_present"]


def test_rho_qs_is_join_odd_but_sigma_even() -> None:
    plus = formation_imbalance_candidates(0.14, 0.6)
    minus = formation_imbalance_candidates(0.14, -0.6)
    p = plus["candidates"]["rho_qs"]
    m = minus["candidates"]["rho_qs"]
    assert p["sigma_reflection_parity"] == "even"
    assert p["join_factor_exchange_parity"] == "odd"
    assert math.isclose(p["value"], -m["value"], rel_tol=1.0e-13)


def test_sigma_times_imbalance_requires_new_diagonal_locking() -> None:
    source = monomial_symmetry(1, 1)
    assert not source["invariant_under_product_group"]
    assert source["invariant_only_after_diagonal_locking"]
    assert monomial_symmetry(2, 2)["invariant_under_product_group"]


def test_function_level_equivariance_forces_zero_sigma_response() -> None:
    theorem = equivariant_sigma_response_theorem()
    assert theorem["holds_for_every_deterministic_equivariant_function"]
    assert theorem["not_limited_to_polynomials_or_linear_response"]
    assert theorem["nonzero_sigma_response_from_current_formation_state"] is False


def test_archive_routes_do_not_supply_the_reverse_map() -> None:
    routes = archive_route_exhaustion()
    assert routes["v6_14_composite_level_set"]["reverse_map_defined"] is False
    assert routes["v6_18_threading_response"]["scalar_sign_dependence"] is False
    assert routes["route_produces_nonzero_action_owned_sigma_initial_state"] is False


def test_response_operator_magnitude_remains_independently_unselected() -> None:
    result = response_magnitude_selection_audit()
    assert result["inequivalent_retained_response_triples"] == 3
    assert result["same_sigma_zero_parent_and_first_variation"]
    assert result["G_sigma_or_scalar_g_selected"] is False


def test_completion_requirements_are_jointly_inconsistent() -> None:
    result = foundational_consistency_audit()
    assert result["logical_contradiction_proved"]
    assert result["requirements_are_jointly_satisfiable"] is False
    assert result["revision_present_in_retained_action_or_state_domain"] is False
    assert result["revision_implemented"] is False


def test_payload_fails_closed_without_retuning() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert FULL_BHSM_COMPLETE is False
    assert payload["no_retuning_certificate"]["new_action_terms"] == []
    assert payload["no_retuning_certificate"]["new_sigma_seeds"] == []
    assert payload["no_retuning_certificate"]["frozen_predictions_changed"] is False
