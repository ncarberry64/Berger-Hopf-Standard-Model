from scripts.derive_n12_c2_1222_signed_adjoint_assembly import build_payload


def test_signed_finite_core_adjoint_is_assembled() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"][
        "signed_finite_core_adjoint_assembly"
    ] == "DERIVED"
    assert payload["exact_recurrence"]["forward_Jacobi_columns_required"] == 0
    assert payload["adjudication"]["moving_duration_included"] is True
    assert payload["adjudication"][
        "all_1222_interval_transposed_duration_actions"
    ] == "CLOSED"
    assert payload["adjudication"]["joint_heat_cotangent_reverse_seed"] == "CLOSED"
    assert payload["adjudication"][
        "direct_zeta_coefficient_cotangent"
    ].startswith("CLOSED")
    assert payload["adjudication"][
        "full_graded_heat_cotangent_seed"
    ] == "CERTIFIED_SUPPRESSED_NOT_ZEROED"
    assert payload["direct_zeta_coefficient_input"]["D_log_R4_shape"] == [1223]
    assert payload["direct_zeta_coefficient_input"]["D_proper_duration_shape"] == [1222]
    assert len(payload["actual_1222_coefficient_inputs"]) == 3


def test_assembly_does_not_promote_centers_source_force_or_tail() -> None:
    payload = build_payload()
    adjudication = payload["adjudication"]
    assert adjudication["proof_center_used_as_physical_history"] is False
    assert adjudication["numerical_parametric_or_interval_BHSM_adjoint"].startswith(
        "OPEN"
    )
    assert adjudication["complete_internal_upstream_history_covector"].startswith("OPEN")
    assert adjudication["actual_joint_graded_heat_minus_zeta_cotangent"] == (
        "FINITE_CORE_SEED_ENCLOSED_TRANSITION_PULLBACK_OPEN"
    )
    assert payload["exact_recurrence"]["additional_seam_source"] == "FORBIDDEN"
    assert payload["claim_boundary"]["actual_BHSM_signed_covector"] == "OPEN"
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
