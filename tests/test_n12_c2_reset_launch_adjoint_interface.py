from scripts.derive_n12_c2_reset_launch_adjoint_interface import build_payload


def test_launch_adjoint_split_dimensions_and_kernel_identity() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    dimensions = payload["dimension_ledger"]
    assert dimensions["full_reset_tangent"] == 139
    assert dimensions["outgoing_C2_seed_image"] == 72
    assert dimensions["fixed_C2_seed_lift_kernel"] == 67
    assert dimensions["natural_C2_launch"] == 73
    assert payload["validation"][
        "downstream_C2_pullback_annihilates_fixed_seed_kernel"
    ] is True
    assert payload["validation"][
        "full_kernel_force_reduces_to_upstream_interface_covector"
    ] is True


def test_one_adjoint_supplies_the_launch_force_without_closing_gate7() -> None:
    payload = build_payload()
    adjudication = payload["adjudication"]
    assert adjudication["73_forward_Jacobi_columns_required_for_scalar_force"] is False
    assert adjudication["one_C2_adjoint_covector_required"] is True
    assert adjudication["67_kernel_directions_may_be_discarded_from_full_seam_saddle"] is False
    assert adjudication["67_kernel_upstream_interface_stationarity"] == (
        "OPEN_ACTUAL_EVALUATION"
    )
    assert payload["claim_boundary"]["C2_maximal_or_finite_endpoint_adjoint"] == (
        "OPEN_CURRENT_OWNER"
    )
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
