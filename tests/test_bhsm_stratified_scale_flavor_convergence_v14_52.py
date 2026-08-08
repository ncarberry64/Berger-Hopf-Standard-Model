from bhsm.interface.completion.stratified_scale_flavor_convergence_v14_52 import (
    branch_decision,
    c3_projected_block_norm,
    completion_payload,
    lambda85_family_projection_no_go,
    one_power_log_stationary_point,
    power_log_berger_stationarity_contract,
    scale_weight,
    stratified_scale_weight_ledger,
)


def test_stratified_scale_weights_are_exact():
    assert scale_weight(8, 0) == 8
    assert scale_weight(8, 2) == 6
    assert scale_weight(8, 8) == 0
    assert scale_weight(5, 2) == 3
    assert scale_weight(4, 4) == 0


def test_existing_action_contains_nonzero_power_candidates():
    payload = stratified_scale_weight_ledger()
    assert payload["nonzero_candidate_power_weights"] == [3, 6, 8]
    assert all(payload["validation"].values())


def test_one_power_plus_log_has_exact_finite_stable_gate():
    point = one_power_log_stationary_point(6, 2.0, -3.0)
    assert point.exists
    assert point.scale_ratio is not None and point.scale_ratio > 0
    assert point.hessian_xx == 18.0
    assert point.stable_in_scale_direction


def test_wrong_sign_power_log_has_no_real_stationary_point():
    point = one_power_log_stationary_point(6, 2.0, 3.0)
    assert not point.exists
    assert point.scale_ratio is None


def test_power_log_berger_contract_keeps_absolute_unit_open():
    payload = power_log_berger_stationarity_contract()
    assert payload["current_evaluation_status"]["stationary_L_and_a_emitted"] is False
    assert payload["reference_scale_rule"]["zero_input_branch"].endswith("still required")
    assert all(payload["validation"].values())


def test_c3_equivariant_attachment_is_character_diagonal():
    for r in range(3):
        for s in range(3):
            if r != s:
                assert c3_projected_block_norm(2.0, 0.25 + 0.1j, r, s) < 1e-12


def test_lambda85_family_projection_is_fail_closed():
    payload = lambda85_family_projection_no_go()
    assert payload["numerical_exactness_diagnostic"]["passes"]
    assert payload["historical_beta_kappa_status"].startswith("mechanism diagnostics")
    assert all(payload["validation"].values())


def test_effective_and_zero_input_branches_are_separated():
    payload = branch_decision()
    assert payload["effective_one_scale_branch"]["status"] == "conditionally available"
    assert payload["zero_input_branch"]["status"] == "open"
    assert payload["flavor_branch"]["nontrivial_CKM"].startswith("blocked")


def test_completion_gate_remains_fail_closed():
    payload = completion_payload()
    assert payload["gates"]["preexisting_power_law_scale_term_identified"]
    assert not payload["gates"]["absolute_reference_unit_derived"]
    assert not payload["gates"]["sector_relative_C3_embedding_action_owned"]
    assert not payload["gates"]["physical_CKM_emitted"]
    assert not payload["gates"]["physical_scale_emitted"]
    assert not payload["gates"]["BHSM_physical_completion"]
    assert payload["validation_passed"]
