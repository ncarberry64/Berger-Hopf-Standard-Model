from bhsm.interface.aether_unified_m5_m4_pushforward_v15_69 import (
    closure_rejection_gate,
    common_derivative_ledger,
    common_renormalization_contract,
    completion_payload,
    deterministic_json,
    finite_block_schur_witness,
    unified_parent_boundary_functional,
)


def test_one_parent_pushforward_generates_gauge_and_current_kernels():
    result = unified_parent_boundary_functional()
    assert result["one_pushforward_only"] is True
    assert "K_F^(5)" in result["tree_Schur_term"]
    assert "G_DtN" in result["tree_Schur_term"]


def test_all_local_gauge_higgs_and_yukawa_outputs_are_derivatives_of_one_gamma():
    result = common_derivative_ledger()
    assert result["same_Gamma_generates_every_entry"] is True
    assert result["absolute_local_gauge_residue"].startswith("Z_g=")
    assert result["Yukawa_residue"].startswith("Y_f=")


def test_split_normalization_or_yukawa_completions_are_rejected():
    renormalization = common_renormalization_contract()
    gate = closure_rejection_gate()
    assert renormalization["separate_gauge_and_Higgs_subtraction_scales_allowed"] is False
    assert renormalization["postcomparison_Yukawa_counterterm_allowed"] is False
    assert gate["candidate_A_bulk_DtN_plus_independent_intrinsic_Yukawa"].startswith("REJECTED")
    assert gate["absolute_gauge_and_nonzero_Yukawa_are_one_closure_gate"] is True


def test_single_bulk_inverse_schur_witness_is_positive_in_both_channels():
    result = finite_block_schur_witness()
    assert result["same_inverse_bulk_operator_used"] is True
    assert result["boundary_kernel_positive"] is True
    assert result["current_kernel_positive"] is True
    assert result["physical_coefficient_prediction"] is False


def test_payload_is_deterministic_and_fail_closed():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
