from scripts.audit_n12_c2_fixed_seed_upstream_force_owner import build_payload


def test_fixed_seed_kernel_is_the_embedded_preceding_event_tangent() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    witness = payload["dimension_and_subspace_witness"]
    assert witness["J_C2_rank"] == 32
    assert witness["J_E1_rank"] == 31
    assert witness["fixed_C2_E1_kernel_dimension"] == 67
    assert witness["stored_to_exact_projector_operator_residual"] < 1.0e-10
    assert witness["stored_fixed_seed_C2_component_operator_norm"] < 1.0e-12


def test_upstream_force_is_not_replaced_by_a_local_seam_force() -> None:
    payload = build_payload()
    adjudication = payload["adjudication"]
    assert adjudication["67_kernel_is_a_new_local_seam_degree_family"] is False
    assert adjudication["67_kernel_is_the_raw_fixed_C2_preceding_E1_tangent"] is True
    assert adjudication["fermion_surface_term_can_supply_a_missing_force"] is False
    assert adjudication["M_f_value_or_seam_invertibility_alone_supplies_the_force"] is False
    assert adjudication["separate_arbitrary_direct_seam_covector_should_be_invented"] is False
    assert adjudication["one_joint_history_adjoint_is_preferred"] is True
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
