from scripts.derive_n12_c2_1222_signed_adjoint_assembly import build_payload


def test_signed_finite_core_adjoint_is_assembled() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"][
        "signed_finite_core_adjoint_assembly"
    ] == "DERIVED"
    assert payload["exact_recurrence"]["forward_Jacobi_columns_required"] == 0
    assert payload["adjudication"]["moving_duration_included"] is True
    assert len(payload["actual_1222_coefficient_inputs"]) == 3


def test_assembly_does_not_promote_centers_source_force_or_tail() -> None:
    payload = build_payload()
    adjudication = payload["adjudication"]
    assert adjudication["proof_center_used_as_physical_history"] is False
    assert adjudication["numerical_parametric_or_interval_BHSM_adjoint"].startswith(
        "OPEN"
    )
    assert adjudication["complete_upstream_history_covector"].startswith("OPEN")
    assert adjudication["actual_graded_heat_minus_zeta_contraction"].startswith(
        "OPEN"
    )
    assert payload["claim_boundary"]["actual_BHSM_signed_covector"] == "OPEN"
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
